from flask import Flask, request
import requests
from datetime import datetime, timedelta
import math
import os  # ✅ Import os for environment port

app = Flask(__name__)

# 🔐 Telegram Config
TELEGRAM_TOKEN = "7969311368:AAHuzF7wHgS4KQ-2PEOaNuXN3GRnquFmGfo"
CHAT_ID = "7896009480"

def nearest_strike(price):
    return round(price / 50) * 50

def get_expiry():
    today = datetime.now()
    days_ahead = (3 - today.weekday()) % 7  # Thursday expiry
    expiry = today + timedelta(days=days_ahead)
    return expiry.strftime("%d-%b-%Y")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415

    data = request.get_json()

    try:
        price = float(data.get("price"))
        direction = data.get("direction")
        conf = data.get("confidence")
        forecast = data.get("forecast")

        strike = nearest_strike(price)
        expiry = get_expiry()
        tp = round(price + 2.5 if direction == "CALL" else price - 2.5, 2)
        sl = round(price - 1.5 if direction == "CALL" else price + 1.5, 2)

        eta = f"~{abs(tp - price) * 6:.1f} pts in 30m"

        message = f"""🚨 *OPTIONS SIGNAL*
*{direction} {strike} {expiry}*

• Entry: {price}
• TP: {tp}
• SL: {sl}
• ETA: {eta}
• Confidence: {conf}/5
• Forecast: {forecast}
"""

        send_telegram(message)
        return {"status": "ok"}, 200

    except Exception as e:
        return {"error": str(e)}, 400

# ✅ Production-ready host and port config
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
