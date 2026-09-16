import os
import requests
from dotenv import load_dotenv

# Load the environment variables from config.env
load_dotenv("config.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def check_bot():
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in config.env!")
        return

    print("Connecting to Telegram Bot API...")
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data["result"]
                print("\n✅ Connection Successful!")
                print(f"Bot ID: {bot_info.get('id')}")
                print(f"First Name: {bot_info.get('first_name')}")
                print(f"Username: @{bot_info.get('username')}")
                print(f"Can Join Groups: {bot_info.get('can_join_groups')}")
                print(f"Can Read All Group Messages: {bot_info.get('can_read_all_group_messages')}")
                print(f"Supports Inline Queries: {bot_info.get('supports_inline_queries')}")
            else:
                print(f"\n❌ Error: API response not OK. Details: {data}")
        elif response.status_code == 401:
            print("\n❌ Error: Unauthorized. Your bot token is invalid or has expired.")
        else:
            print(f"\n❌ Error: Received status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Failed to connect: {e}")

if __name__ == "__main__":
    check_bot()
