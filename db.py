from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
import datetime
from settings import config

# Configure logging
logging.basicConfig(level=logging.INFO, filename="info.logs")

admin_ids = config["admin_ids"]


class ShdkDatabase:

    def __init__(self):
        mongo_uri = config["mongo_uri"]
        _client = MongoClient(mongo_uri)
        _db = _client.shdk_database

        self.users_collection = _db.users
        self.questions_collection = _db.questions
        self.answers_history_collection = _db.answers_history

    def save_user(self, user_info) -> None:
        # todo: сделать сесурно
        user_dict = {
            "id": user_info.id,
            "first_name": user_info.first_name,
            "username": user_info.username,
            "type": user_info.type,
            "active": True
        }
        self.users_collection.update_one({"id": user_info.id}, {"$set": user_dict}, upsert=True)
        logging.info("New user has been saved")

    def get_user_id(self, username):
        user = self.users_collection.find_one({"username": username})
        if user:
            return user["id"]
        else:
            logging.error("Username isn't present in db")

    def save_question(self, structured_question) -> None:
        # todo: сделать сесурно
        self.questions_collection.insert_one(structured_question)
        logging.info("The question has been added")

    def advance_to_the_next_question(self) -> None:
        self.questions_collection.update_one({"status": "current"}, {"$set": {"status": "past"}})
        self.questions_collection.update_one({"status": "future"}, {"$set": {"status": "current"}})

    def save_answer(self, user_id, question_data, answered=False):
        if user_id in admin_ids:
            return
        answer_data = {
            "question_id": question_data["_id"],
            "user_id": user_id,
            "answered": answered,
            "datetime": datetime.datetime.now()
        }

        upsert_mode = "$setOnInsert"
        if answered:
            upsert_mode = "$set"

        self.answers_history_collection.update_one(
            {
                "question_id": question_data["_id"],
                "user_id": user_id
            },
            {
                upsert_mode: answer_data
            },
            upsert=True
        )

    def get_answered_ratio(self, question_id=None, current_question=True):
        if current_question:
            question_id = self.questions_collection.find_one({"status": "current"})["_id"]

        if_answered_list = [
            answer["answered"] for answer in self.answers_history_collection.find(
                {
                    "question_id": question_id
                }
            )
        ]

        ratio = if_answered_list.count(True) / len(if_answered_list)
        return ratio

    def log_all_users(self) -> None:
        for user in self.users_collection.find():
            logging.info(f"Found user: {user}")

    def get_current_question(self) -> dict:
        question = self.questions_collection.find_one({"status": "current"})
        return question

    def get_questions_list(self) -> list:
        questions = [question for question in self.questions_collection.find()]
        return questions

    def get_all_chat_ids(self) -> list:
        chat_ids = [chat["id"] for chat in self.users_collection.find()]
        return chat_ids

    def drop_users(self) -> None:
        self.users_collection.drop()

    def drop_questions(self) -> None:
        self.questions_collection.drop()

    def delete_question_by_id(self, question_object_id) -> None:
        self.questions_collection.delete_one({'_id': ObjectId(question_object_id)})
