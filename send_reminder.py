import logging
import os
import sys
import requests
from dotenv import load_dotenv

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.env")
load_dotenv(CONFIG_PATH)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")
MEETING_LINK = os.getenv("MEETING_LINK", "")
MEETING_TIME = os.getenv("MEETING_TIME", "")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def build_message() -> str:
    return (
        "Dear student here link to join today\n"
        f"we start {MEETING_TIME}\n"
        f"Join: {MEETING_LINK}"
    )


def send_reminder() -> None:
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing in config.env!")
        sys.exit(1)
    if not CHAT_ID:
        logger.error(
            "TELEGRAM_GROUP_CHAT_ID is missing in config.env! Run get_chat_id.py first."
        )
        sys.exit(1)

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": build_message()}

    response = requests.post(url, data=payload)
    data = response.json()

    if data.get("ok"):
        logger.info("Reminder sent successfully to chat %s.", CHAT_ID)
    else:
        logger.error("Failed to send reminder: %s", data)
        sys.exit(1)


if __name__ == "__main__":
    send_reminder()
