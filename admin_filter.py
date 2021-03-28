from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from main import dp
import typing


class ChatIdFilter(BoundFilter):
    key = 'chat_id'

    def __init__(self, chat_id: typing.Union[typing.Iterable, int]):
        if isinstance(chat_id, int):
            chat_id = [chat_id]
        self.chat_id = chat_id

    def check(self, message: types.Message) -> bool:
        return message.chat.id in self.chat_id


dp.filters_factory.bind(ChatIdFilter, event_handlers=[dp.message_handlers])
