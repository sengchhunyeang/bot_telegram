import json
import logging
import os
import tempfile

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv("config.env")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Vercel's filesystem is read-only outside /tmp, and /tmp itself is not
# guaranteed to persist between invocations - subscriber storage there is
# best-effort. The group chat reminder (TELEGRAM_GROUP_CHAT_ID) is unaffected.
SUBSCRIBERS_FILE = (
    os.path.join(tempfile.gettempdir(), "subscribers.json")
    if os.getenv("VERCEL")
    else os.path.join(BASE_DIR, "subscribers.json")
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")
MEETING_LINK = os.getenv("MEETING_LINK", "")
MEETING_TIME = os.getenv("MEETING_TIME", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") or TOKEN
REMINDER_SECRET = os.getenv("REMINDER_SECRET", "")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def send_message(chat_id, text) -> dict:
    response = requests.post(
        f"{TELEGRAM_API}/sendMessage", data={"chat_id": chat_id, "text": text}
    )
    return response.json()


def load_subscribers() -> dict:
    if not os.path.exists(SUBSCRIBERS_FILE):
        return {}
    with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def add_subscriber(chat_id, username) -> None:
    subscribers = load_subscribers()
    subscribers[str(chat_id)] = username
    try:
        with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(subscribers, f, indent=2)
    except OSError:
        logger.warning("Could not persist subscriber %s (read-only filesystem?).", chat_id)


def build_reminder_message() -> str:
    return (
        "Dear student here link to join today\n"
        f"we start {MEETING_TIME}\n"
        f"Join: {MEETING_LINK}"
    )


@app.get("/")
def index():
    return jsonify({"status": "ok", "service": "telegram-bot"})


@app.post("/webhook/<secret>")
def webhook(secret):
    if secret != WEBHOOK_SECRET:
        return jsonify({"error": "forbidden"}), 403

    update = request.get_json(silent=True) or {}
    message = update.get("message")
    if not message:
        return jsonify({"ok": True})

    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    user = message.get("from", {})
    username = user.get("username") or user.get("first_name") or "there"

    if text == "/start":
        logger.info("User %s started the bot.", username)
        add_subscriber(chat_id, username)
        send_message(
            chat_id,
            f"Hi {username}! I am your Python Telegram Bot. "
            "Send me any message, and I will echo it back to you!",
        )
    elif text == "/help":
        send_message(
            chat_id,
            "Help Menu:\n/start - Start interacting with the bot\n/help - Show this help message",
        )
    elif text:
        logger.info("Received message: '%s' from user: %s", text, username)
        send_message(chat_id, f"You said: {text}")

    return jsonify({"ok": True})


@app.route("/send-reminder", methods=["GET", "POST"])
def trigger_reminder():
    if REMINDER_SECRET and request.args.get("secret") != REMINDER_SECRET:
        return jsonify({"error": "forbidden"}), 403

    message = build_reminder_message()
    sent, failed = [], []

    if CHAT_ID:
        result = send_message(CHAT_ID, message)
        if result.get("ok"):
            logger.info("Reminder sent to group chat %s.", CHAT_ID)
            sent.append(CHAT_ID)
        else:
            logger.error("Failed to send reminder to group %s: %s", CHAT_ID, result)
            failed.append({"chat_id": CHAT_ID, "detail": result})

    subscribers = load_subscribers()
    for sub_chat_id, sub_username in subscribers.items():
        result = send_message(sub_chat_id, message)
        if result.get("ok"):
            logger.info(
                "Reminder sent to %s (%s).", sub_username, sub_chat_id
            )
            sent.append(sub_chat_id)
        else:
            logger.error(
                "Failed to send reminder to %s (%s): %s",
                sub_username,
                sub_chat_id,
                result,
            )
            failed.append({"chat_id": sub_chat_id, "detail": result})

    if not sent and not failed:
        return jsonify({"error": "No group chat or /start subscribers configured"}), 500

    status = "sent" if not failed else ("partial" if sent else "failed")
    return jsonify({"status": status, "sent": sent, "failed": failed})


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is missing in config.env!")
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
