import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv("config.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") or TOKEN


def main():
    if len(sys.argv) != 2:
        print("Usage: python set_webhook.py https://<your-app>.up.railway.app")
        sys.exit(1)
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in config.env!")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    webhook_url = f"{base_url}/webhook/{WEBHOOK_SECRET}"

    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        data={"url": webhook_url},
    )
    data = response.json()
    if data.get("ok"):
        print(f"Webhook set successfully: {webhook_url}")
    else:
        print(f"Failed to set webhook: {data}")
        sys.exit(1)


if __name__ == "__main__":
    main()
