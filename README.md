# bot_telegram

A Flask-based Telegram bot that sends meeting reminders to a group chat and replies to `/start`, `/help`, and any text message via webhook.

## Deploy to Vercel

1. Push this repo to GitHub, then import it in the Vercel dashboard (or run `vercel` from this directory with the Vercel CLI).
2. In the Vercel project's **Settings > Environment Variables**, set:
   - `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
   - `TELEGRAM_GROUP_CHAT_ID` — get it via `get_chat_id.py` after adding the bot to the group
   - `MEETING_LINK`, `MEETING_TIME` — reminder content
   - `WEBHOOK_SECRET` — random string used as the webhook path secret (defaults to the bot token if unset)
   - `REMINDER_SECRET` — random string required as `?secret=` to trigger `/send-reminder`
3. Deploy. Then point Telegram's webhook at your deployment:
   ```
   python set_webhook.py https://<your-project>.vercel.app
   ```
4. Trigger a reminder manually (or via a scheduled Vercel Cron Job hitting this URL):
   ```
   https://<your-project>.vercel.app/send-reminder?secret=<REMINDER_SECRET>
   ```

Note: Vercel's filesystem is ephemeral, so per-user `/start` subscribers (`subscribers.json`) are best-effort there and may not persist across invocations. The group chat reminder (`TELEGRAM_GROUP_CHAT_ID`) is unaffected and remains the primary delivery path.