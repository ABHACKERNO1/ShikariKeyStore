import os
from io import BytesIO
from threading import Thread

import qrcode
import telebot

from flask import Flask
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
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
🎮 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗧𝗢𝗥𝗘

━━━━━━━━━━━━━━━━━━━
⚡ Instant Delivery
🔐 Secure System
💳 Easy Payment
━━━━━━━━━━━━━━━━━━━
"""

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "🛒 Products",
            callback_data="products"
        ),

        InlineKeyboardButton(
            "📞 Support",
            url="https://t.me/yourusername"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "📢 Updates",
            url="https://t.me/yourusername"
        ),

        InlineKeyboardButton(
            "ℹ️ Help",
            callback_data="help"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )

# =========================
# HELP
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_menu(call):

    text = """
📌 HOW TO BUY

1️⃣ Select Product
2️⃣ Select Plan
3️⃣ Make Payment
4️⃣ Send Screenshot
5️⃣ Get Delivery

⚠️ Fake Payments = Ban
"""

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "🔙 Back",
            callback_data="back_start"
        )
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# =========================
# PRODUCTS MENU
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "products")
def products(call):

    text = """
🛒 𝗦𝗘𝗟𝗘𝗖𝗧 𝗣𝗥𝗢𝗗𝗨𝗖𝗧

━━━━━━━━━━━━━━━━━━━
Choose Your Product
━━━━━━━━━━━━━━━━━━━
"""

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "🔥 Alpha",
            callback_data="product_alpha"
        ),

        InlineKeyboardButton(
            "⚡ Nova",
            callback_data="product_nova"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🌑 Shadow",
            callback_data="product_shadow"
        ),

        InlineKeyboardButton(
            "👑 Phantom",
            callback_data="product_phantom"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🔙 Back",
            callback_data="back_start"
        )
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# =========================
# BACK
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "back_start")
def back(call):

    try:
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
    except:
        pass

    start(call.message)

# =========================
# PRODUCT SELECT
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def product_select(call):

    product = call.data.replace("product_", "")

    user_data[call.from_user.id] = {
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

    markup.add(
        InlineKeyboardButton(
            "🔙 Back",
            callback_data="products"
        )
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
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
        """
📤 Send Payment Screenshot
"""
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
