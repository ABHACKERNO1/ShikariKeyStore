import os
from io import BytesIO
from threading import Thread

import qrcode
import telebot

from flask import Flask

from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

# =========================
# ENV
# =========================

TOKEN = os.getenv("TOKEN")
UPI_ID = os.getenv("UPI_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# =========================
# BOT
# =========================

bot = telebot.TeleBot(TOKEN)

# =========================
# FLASK
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

Thread(target=run, daemon=True).start()

# =========================
# PRODUCTS
# =========================

PRODUCTS = {
    "alpha": "🔥 Alpha Premium",
    "nova": "⚡ Nova Ultra",
    "shadow": "🌑 Shadow Pro",
    "phantom": "👑 Phantom VIP"
}

# =========================
# PRICES
# =========================

PRICES = {
    "1d": 120,
    "3d": 250,
    "7d": 499,
    "30d": 699
}

# =========================
# USER DATA
# =========================

user_data = {}

# =========================
# START
# =========================

@bot.message_handler(commands=['start'])
def start(message):

    text = """
🎮 PREMIUM STORE

━━━━━━━━━━━━━━━━━━━
⚡ Instant Delivery
🔐 Secure System
💳 Easy Payment
━━━━━━━━━━━━━━━━━━━
"""

    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    # Row 1
    markup.add(
        KeyboardButton("🔥 Alpha"),
        KeyboardButton("⚡ Nova")
    )

    # Row 2
    markup.add(
        KeyboardButton("🌑 Shadow"),
        KeyboardButton("👑 Phantom")
    )

    # Row 3
    markup.add(
        KeyboardButton("📞 Support"),
        KeyboardButton("ℹ️ Help")
    )

    # Last Row
    markup.add(
        KeyboardButton("🔄 Refresh")
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )

# =========================
# BUTTON HANDLERS
# =========================

@bot.message_handler(func=lambda m: m.text == "🔥 Alpha")
def alpha_btn(message):
    open_product(message, "alpha")


@bot.message_handler(func=lambda m: m.text == "⚡ Nova")
def nova_btn(message):
    open_product(message, "nova")


@bot.message_handler(func=lambda m: m.text == "🌑 Shadow")
def shadow_btn(message):
    open_product(message, "shadow")


@bot.message_handler(func=lambda m: m.text == "👑 Phantom")
def phantom_btn(message):
    open_product(message, "phantom")


@bot.message_handler(func=lambda m: m.text == "📞 Support")
def support_btn(message):

    bot.send_message(
        message.chat.id,
        "📞 Support: @yourusername"
    )


@bot.message_handler(func=lambda m: m.text == "ℹ️ Help")
def help_btn(message):

    bot.send_message(
        message.chat.id,
        """
📌 HOW TO BUY

1️⃣ Select Product
2️⃣ Select Plan
3️⃣ Make Payment
4️⃣ Send Screenshot
5️⃣ Wait For Approval
"""
    )


@bot.message_handler(func=lambda m: m.text == "🔄 Refresh")
def refresh_btn(message):
    start(message)

# =========================
# OPEN PRODUCT
# =========================

def open_product(message, product):

    user_data[message.from_user.id] = {
        "product": product
    }

    text = f"""
{PRODUCTS[product]}

━━━━━━━━━━━━━━━━━━━
💎 Select Your Plan
━━━━━━━━━━━━━━━━━━━
"""

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "🔥 1 Day\n₹120",
            callback_data="plan_1d"
        ),

        InlineKeyboardButton(
            "⚡ 3 Day\n₹250",
            callback_data="plan_3d"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "💎 7 Day\n₹499",
            callback_data="plan_7d"
        ),

        InlineKeyboardButton(
            "👑 30 Day\n₹699",
            callback_data="plan_30d"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )

# =========================
# PLAN SELECT
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("plan_"))
def plan_select(call):

    plan = call.data.replace("plan_", "")

    user_data[call.from_user.id]["plan"] = plan

    amount = PRICES[plan]

    upi_link = f"upi://pay?pa={UPI_ID}&pn=PremiumStore&am={amount}"

    qr = qrcode.make(upi_link)

    bio = BytesIO()
    bio.name = "qr.png"

    qr.save(bio, "PNG")
    bio.seek(0)

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "📤 Send Screenshot",
            callback_data="send_ss"
        )
    )

    bot.send_photo(
        call.message.chat.id,
        bio,
        caption=f"""
💰 Amount: ₹{amount}

📲 Scan QR & Pay
📤 Send Screenshot After Payment
""",
        reply_markup=markup
    )

# =========================
# SEND SCREENSHOT
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "send_ss")
def send_ss(call):

    bot.send_message(
        call.message.chat.id,
        "📤 Send Payment Screenshot"
    )

# =========================
# SCREENSHOT HANDLER
# =========================

@bot.message_handler(content_types=['photo'])
def photo_handler(message):

    user_id = message.from_user.id

    if user_id not in user_data:
        return

    product = user_data[user_id]["product"]
    plan = user_data[user_id]["plan"]

    username = message.from_user.username

    if username:
        username = f"@{username}"
    else:
        username = "No Username"

    caption = f"""
💸 NEW PAYMENT

👤 User: {username}
🆔 ID: {user_id}

🛒 Product: {product}
📦 Plan: {plan}
"""

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "✅ Approve",
            callback_data=f"approve_{user_id}"
        ),

        InlineKeyboardButton(
            "❌ Reject",
            callback_data=f"reject_{user_id}"
        )
    )

    file_id = message.photo[-1].file_id

    bot.send_photo(
        ADMIN_ID,
        file_id,
        caption=caption,
        reply_markup=markup
    )

    bot.reply_to(
        message,
        "⏳ Waiting For Admin Approval"
    )

# =========================
# APPROVE
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])

    bot.send_message(
        user_id,
        """
🎉 Payment Approved

✅ Your order has been confirmed.
"""
    )

    bot.answer_callback_query(
        call.id,
        "Approved"
    )

# =========================
# REJECT
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])

    bot.send_message(
        user_id,
        """
❌ Payment Rejected
"""
    )

    bot.answer_callback_query(
        call.id,
        "Rejected"
    )

# =========================
# RUN
# =========================

print("Bot Running...")

bot.infinity_polling(skip_pending=True)
