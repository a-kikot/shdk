from prettytable import PrettyTable

distance_map = {
    1: [
        {
            "type": "text",
            "content": "🌟",
        },
        {
            "type": "text",
            "content": "⭐",
        },
        {
            "type": "text",
            "content": "🧡",
        },
        {
            "type": "text",
            "content": "💛",
        },
        {
            "type": "text",
            "content": "💚",
        },
        {
            "type": "text",
            "content": "🤍",
        },
        {
            "type": "text",
            "content": "💫",
        }
    ],
    2: [
        {
            "type": "text",
            "content": "Meh, quite close",
        },
        {
            "type": "text",
            "content": "Близко",
        },
        {
            "type": "text",
            "content": "Почти",
        },
        {
            "type": "sticker",
            "content": "CAACAgIAAxkBAAIDnWA9CCSbm50miLbkGwP8LMIqsvxGAAIiCAACfAUHG8JzFNgzeZsGHgQ"
        }
    ],
    999: [
        {
            "type": "text",
            "content": "Нет",
        },
        {
            "type": "text",
            "content": "-",
        },
        {
            "type": "text",
            "content": "Нет...",
        },
        {
            "type": "text",
            "content": "❌",
        },
        {
            "type": "text",
            "content": "Nein",
        },
        {
            "type": "text",
            "content": "Hi",
        },
        {
            "type": "text",
            "content": "Nej",
        }
    ]
}

answered_map = [
    {
        "type": "text",
        "content": "Шо ты дальше жмешь? Ответ засчитан"
    },
    {
        "type": "text",
        "content": "Иди отдохни"
    },
    {
        "type": "text",
        "content": "Гаси компухтер, интернет-зависимый"
    },
    {
        "type": "sticker",
        "content": "CAACAgIAAxkBAAID4mA9ZS3_nTPmKUfaJjZigv-I3wKzAAKIBQACIwUNAAGAByyt3cydxh4E"
    },
    {
        "type": "sticker",
        "content": "CAACAgIAAxkBAAID5GA9ZZsYKntEE7o_fatrpX7LlgUJAAKoAAOm02IXl-rkB9kRMGEeBA"
    },
    {
        "type": "sticker",
        "content": "CAACAgIAAxkBAAID5mA9Zb6aH6we8Yc7lBcTEMtGRCXRAAJ3AANlpe4TwHhRvioAAS02HgQ"
    }
]


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


def format_user_data(users_data: list) -> list:
    lines = []
    for user in users_data:
        if user["username"]:
            user["username"] = "@" + user["username"]
        else:
            user["username"] = ""
        username_part = user["username"].rjust(25 - len(user["username"]), ".")
        first_name_part = user["first_name"].ljust(25 - len(user["first_name"]))
        lines.append(first_name_part + username_part)

    lines = PrettyTable(['First name', 'Username'])
    for user in users_data:
        lines.add_row([user["first_name"], user["username"]])
    return "<pre>" + lines.get_string() + "</pre>"