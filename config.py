import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_URL = os.getenv("DATABASE_URL")

ADMINS = [
    int(x)
    for x in os.getenv("ADMINS", "").split(",")
    if x.strip()
]

BACKUP_CHAT_ID = int(
    os.getenv("BACKUP_CHAT_ID", "0")
)

BOT_USERNAME = os.getenv(
    "BOT_USERNAME",
    ""
)

SUPPORT_USERNAME = os.getenv(
    "SUPPORT_USERNAME",
    ""
)

TRIAL_DAYS = int(
    os.getenv("TRIAL_DAYS", "1")
)

TRIAL_FILES = int(
    os.getenv("TRIAL_FILES", "10")
)
