import nltk
from maps import DISTANCES


def process_question(question_text):
    question_parts = [item for item in question_text.split("\n") if item]

    question_structure_map = {
        "вопрос": "question",
        "ответ": "first_answer",
        "зачёт": "additional_answers",
        "зачет": "additional_answers",
        "комментарий": "comment",
        "подсказка": "tip",
    }

    structured_question = {}
    for text in question_parts:
        for keyword_ru, keyword_en in question_structure_map.items():
            if text.lower().startswith(keyword_ru):
                structured_question[keyword_en] = text.split(":", 1)[-1].strip()
                continue

    additional_answers = structured_question.get("additional_answers", [])
    if additional_answers:
        additional_answers = additional_answers.replace(';', ',')
        additional_answers = additional_answers.split(",")
    answers = [structured_question["first_answer"]] + additional_answers
    answers = [answer.strip(",.;").lower() for answer in answers if answer]

    to_be_ignored = [
        "точный ответ"
    ]
    answers = [answer for answer in answers if answer not in to_be_ignored]
    structured_question["answers"] = answers
    structured_question["status"] = "future"

    return structured_question


def check_answer_status(right_answers: list, user_answer: str) -> (bool, str):
    statuses = []

    for right_answer in right_answers:
        answer_length = "SHORT_ANSWER" if len(right_answer) <= 3 else "LONG_ANSWER"
        actual_distance = nltk.edit_distance(right_answer, user_answer)
        for threshold, answer_status in DISTANCES[answer_length].items():
            if actual_distance <= threshold:
                statuses.append(answer_status)

    if "answered" in statuses:
        return "answered"
    elif "close_to_answer" in statuses:
        return "close_to_answer"
    return "fail"

