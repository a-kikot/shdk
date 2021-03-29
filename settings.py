import os
import json

config = {
    "bot_token": os.environ["BOT_TOKEN"],
    "mongo_uri": os.environ["MONGO_URI"],
    "admin_ids": json.loads(os.environ["ADMIN_IDS"])
}
