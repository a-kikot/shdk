import logging
import asyncio
import random
import nltk

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.types.message import ContentType
from aiogram.types import ParseMode
from aiogram.utils import exceptions
from settings import config

import text_util
from db import ShdkDatabase


# Configure logging
logging.basicConfig(level=logging.INFO, filename="info.logs")


# Initialize bot and dispatcher
bot = Bot(token=config["bot_token"])
dp = Dispatcher(bot, storage=MongoStorage(uri=config["mongo_uri"]))
db = ShdkDatabase()

admin_ids = config["admin_ids"]


class AdminInput(StatesGroup):
    questions_saving = State()


class PlayerInput(StatesGroup):
    pending_answer = State()
    answered = State()
    current_question = State()


@dp.message_handler(commands=['start'], state="*")
async def send_welcome(message: types.Message):
    logging.info(f"New user: { message.chat }")
    db.save_user(message.chat)
    await notify_admin(message, event="joined")
    await message.reply(f"Hey, {message.chat.first_name}.\nPlease, start with /get_question.")


@dp.message_handler(commands=['get_question'], state="*")
async def send_question(message: types.Message, state: FSMContext):
    logging.info(f"{message.chat.username}:{message.chat.first_name} requested a question.")
    await notify_admin(message, event="requested_question")
    current_question = db.get_current_question()
    await PlayerInput.pending_answer.set()
    async with state.proxy() as data:
        data["current_question"] = current_question
    await send_message(message.chat.id, current_question["question"])


@dp.message_handler(commands=['get_tip'], state=PlayerInput.pending_answer)
async def send_tip(message: types.Message, state: FSMContext):
    logging.info(f"{message.chat.username}:{message.chat.first_name} requested a tip.")
    excuses = [
        "¯\\_(ツ)_/¯",
        "No tips, no mercy"
    ]
    async with state.proxy() as data:
        await send_message(message.chat.id, data["current_question"].get("tip", random.choice(excuses)))


@dp.message_handler(state='*', commands='cancel')
async def cancel_state(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    logging.info(f"{message.chat.username}:{message.chat.first_name} requested a state cancellation.")
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Cancelled.')


@dp.message_handler(state=PlayerInput.pending_answer)
async def process_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        logging.info(f"{message.chat.username}:{message.chat.first_name} answered: {message.text}")

        await notify_admin(message, "answered")

        db.save_answer(message.chat.id, data["current_question"])

        user_answer = message.text.lower()
        right_answers = data["current_question"]["answers"]

        min_distance = min([nltk.edit_distance(right_answer, user_answer) for right_answer in right_answers])

        if min_distance <= min(text_util.distance_map):
            logging.info(f"{message.chat.username}:{message.chat.first_name} has answered correctly.")
            await notify_admin(message, event="guessed")
            db.save_answer(message.chat.id, data["current_question"], answered=True)
            await PlayerInput.answered.set()
            logging.info(f"{message.chat.username}:{message.chat.first_name}'s result has been saved.")

        for threshold, comment_list in text_util.distance_map.items():
            if min_distance <= threshold:
                random_comment = random.choice(comment_list)
                if random_comment["type"] == "text":
                    await message.reply(random_comment["content"])
                elif random_comment["type"] == "sticker":
                    await bot.send_sticker(message.chat.id, random_comment["content"])
                break


@dp.message_handler(state=PlayerInput.answered)
async def distract(message: types.Message, state: FSMContext):
    logging.info(f"{message.chat.username}:{message.chat.first_name} answered: {message.text}")
    random_comment = random.choice(text_util.answered_map)

    if random_comment["type"] == "text":
        await message.reply(random_comment["content"])
    elif random_comment["type"] == "sticker":
        await bot.send_sticker(message.chat.id, random_comment["content"])


# -----------------------------------------------------------

@dp.message_handler(state="*", commands=['log_users'], chat_id=admin_ids)
async def log_users(message: types.Message):
    db.log_all_users()
    await message.reply("Logged.")


@dp.message_handler(state="*", commands=["log_questions"], chat_id=admin_ids)
async def log_questions(message: types.Message):
    questions_list = db.get_questions_list()
    if questions_list:
        for question in questions_list:
            if question['status'] != 'past':
                await message.reply(question)
    else:
        await message.reply("No questions saved.")


@dp.message_handler(state="*", commands=["send_custom_text_to_user"], chat_id=admin_ids)
async def hey_you(message: types.Message):
    """
    /send_custom_text_to_user chat_id=123 your text
    or
    /send_custom_text_to_user username=name your text
    """
    command, recipient, text = message.text.split(" ", 2)
    recipient_link_type, recipient_link = recipient.split("=")
    if recipient_link_type == 'username':
        user_id = db.get_user_id(username=recipient_link)
    else:
        user_id = recipient_link
    logging.info(f"Sending text to { recipient }: { text }")
    await send_message(user_id, text)


@dp.message_handler(state="*", commands=["send_custom_text_to_all"], chat_id=admin_ids)
async def hey_yall(message: types.Message):
    command, text = message.text.split(" ", 1)
    logging.info(f"Sending custom text to all: { text }")
    await broadcast(text)


@dp.message_handler(state="*", commands=["show_answered_users"], chat_id=admin_ids)
async def get_answered_users(message: types.Message):
    logging.info(f"Getting answered users")
    answered_users = db.get_answered_users()
    current_question = db.get_current_question()
    if answered_users:
        answered_user_lines = [text_util.format_user_data(answered_users)]
    else:
        answered_user_lines = ["🏳️"]
    question_structure_lines = [
        f"    <b>Ответ:</b>",
        f"{', '.join(current_question['answers'])}",
        f"    <b>Комментарий:</b>",
        f"{current_question.get('comment', '—')}",
        f"    <b>Ответили:</b>"
    ]
    await send_message(
        message.chat.id,
        "\n".join(question_structure_lines + answered_user_lines),
        parse_mode=ParseMode.HTML
    )


@dp.message_handler(commands=["start_saving_questions"], chat_id=admin_ids)
async def start_saving_questions(message: types.Message):
    await AdminInput.questions_saving.set()
    await message.reply("Saving mode is on.")


@dp.message_handler(state=AdminInput.questions_saving, commands=['stop_saving_questions'], chat_id=admin_ids)
async def stop_saving_question(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Saving mode is off.")


@dp.message_handler(state=AdminInput.questions_saving, chat_id=admin_ids)
async def parse_question(message: types.Message):
    db.save_question(text_util.process_question(message.text))
    await message.reply("The question has been saved")


@dp.message_handler(state="*", commands=["next_question"], chat_id=admin_ids)
async def advance_to_the_next_question(message: types.Message):
    logging.info(f"Switching to the next question")
    current_question = db.get_current_question()
    answered_users = db.get_answered_users()
    if answered_users:
        answered_user_lines = [text_util.format_user_data(answered_users)]
    else:
        answered_user_lines = ["🏳️"]
    question_structure_lines = [
        f"    <b>Ответ:</b>",
        f"{', '.join(current_question['answers'])}",
        f"    <b>Комментарий:</b>",
        f"{current_question.get('comment', '—')}",
        f"    <b>Ответили:</b>"
    ]
    await broadcast(
        "\n".join(question_structure_lines + answered_user_lines),
        parse_mode=ParseMode.HTML
    )
    db.advance_to_the_next_question()
    await broadcast("/get_question")
    await message.reply("Success.")


@dp.message_handler(commands=["delete_question"], chat_id=admin_ids)
async def delete_question(message: types.Message):
    command, question_object_id = message.text.split(" ", 1)
    db.delete_question_by_id(question_object_id)
    logging.info(f"Deleted a question: {question_object_id}")
    await message.reply("Deleted.")


@dp.message_handler(commands=["drop_questions"], chat_id=admin_ids)
async def drop_questions(message: types.Message):
    db.drop_questions()
    logging.info("Dropped questions")
    await message.reply("Dropped.")


@dp.message_handler(commands=["drop_users"], chat_id=admin_ids)
async def drop_users(message: types.Message):
    db.drop_users()
    logging.info("Dropped users")
    await message.reply("Dropped.")


async def send_message(user_id: int, text: str, parse_mode=None, disable_notification: bool = False) -> bool:
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification, parse_mode=parse_mode)
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logging.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def notify_admin(user_reply, event=None):
    text = ""
    if event == "answered":
        text = f"<b>{user_reply.chat.username}:{user_reply.chat.first_name} " \
               f"answered:</b> {user_reply.text}"
    elif event == "guessed":
        text = f"<b>{user_reply.chat.username}:{user_reply.chat.first_name} +</b>"
    elif event == "requested_question":
        text = f"<b>{user_reply.chat.username}:{user_reply.chat.first_name}</b> requested question"
    elif event == "joined":
        text = f"<b>{user_reply.chat.username}:{user_reply.chat.first_name}</b> has joined the game"
    await broadcast(text, parse_mode=ParseMode.HTML, broadcast_mode="admins")


async def broadcast(text, parse_mode=None, broadcast_mode="users"):
    if broadcast_mode == "users":
        ids = db.get_all_chat_ids()
    elif broadcast_mode == "admins":
        ids = admin_ids
    else:
        ids = []

    count = 0
    try:
        for user_id in ids:
            if await send_message(user_id, text, parse_mode=parse_mode):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"{count} messages successfully sent.")

    return count

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
