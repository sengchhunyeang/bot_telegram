import os
import requests
from dotenv import load_dotenv

# Load the environment variables from config.env
load_dotenv("config.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def get_chat_id():
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in config.env!")
        return

    print("Fetching recent updates from Telegram...")
    print("(Make sure you added the bot to the group and someone sent a message there.)\n")

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    data = response.json()

    if not data.get("ok"):
        print(f"Error from Telegram API: {data}")
        return

    results = data.get("result", [])
    if not results:
        print("No updates found yet. In the group, send any message (or re-add the bot),")
        print("then run this script again.")
        return

    seen = {}
    for update in results:
        message = update.get("message") or update.get("my_chat_member") or {}
        chat = message.get("chat")
        if not chat:
            continue
        seen[chat["id"]] = chat

    print("Chats found:\n")
    for chat_id, chat in seen.items():
        title = chat.get("title") or chat.get("username") or chat.get("first_name") or "(unknown)"
        print(f"  Chat ID: {chat_id}   Type: {chat.get('type')}   Name: {title}")

    print("\nCopy the Chat ID for your 'Alertbot' group into config.env as TELEGRAM_GROUP_CHAT_ID.")


if __name__ == "__main__":
    get_chat_id()
