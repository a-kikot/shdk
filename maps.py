DISTANCES = {
    "SHORT_ANSWER":
        {
            0: "answered",
            999: "fail"
        },
    "LONG_ANSWER":
        {
            1: "answered",
            2: "close_to_answer",
            999: "fail"
        }
}

ANSWER_CHECKING_MAP = {
    "answered": [
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
    "close_to_answer": [
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
    "fail": [
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

DISTRACTION_MAP = [
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