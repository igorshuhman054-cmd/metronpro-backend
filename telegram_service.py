import os
import requests
from dotenv import load_dotenv

# SOTA Fix: Force Python to read the .env file directly, bypassing Docker OS quirks
load_dotenv()

def send_telegram_alert(message: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print(f"SYSTEM ERROR: Telegram config missing. Token: {bool(token)}, Chat ID: {bool(chat_id)}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print("DEBUG: Telegram notification sent successfully.")
    except Exception as e:
        print(f"SYSTEM ERROR: Telegram failed. Reason: {e}")