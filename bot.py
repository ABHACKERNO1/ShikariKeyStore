import os
import telebot
import qrcode

from io import BytesIO
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# =========================
# ENV VARIABLES
# =========================

TOKEN = os.getenv("TOKEN")
UPI_ID = os.getenv("UPI_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# =========================
# FLASK SERVER
# =========================

app = Flask(__name__)

@app.route('/')
def home():
    return "Shikari Bot Running"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

Thread(target=run, daemon=True).start()

# =========================
# BOT START
# =========================

bot = telebot.TeleBot(TOKEN)

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
# START COMMAND
# =========================

@bot.message_handler(commands=['start'])
def start(message):

    text = """
𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝙎𝙝𝙞𝙠𝙖𝙧𝙞 𝙆𝙚𝙮 𝙎𝙩𝙤𝙧𝙚 👋

━━━━━━━━━━━━━━━━━━

𝐇𝐞𝐫𝐞 𝐘𝐨𝐮 𝐂𝐚𝐧 𝐏𝐮𝐫𝐜𝐡𝐚𝐬𝐞
𝐀𝐥𝐥 𝐓𝐆 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐇𝐚𝐜𝐤

⚡ Instant Delivery
🔐 Secure System
💳 Easy Payment

━━━━━━━━━━━━━━━━━━
"""

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "🎮 SELECT LOADER",
            callback_data="loader_menu"
        ),

        InlineKeyboardButton(
            "📞 SUPPORT",
            url="https://t.me/Shikari067"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "⚠️ ANY PROBLEM CONTACT",
            url="https://t.me/Shikari067"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )

# =========================
# LOADER MENU
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "loader_menu")
def loader_menu(call):

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "💀 X Silent",
            callback_data="loader_xsilent"
        ),

        InlineKeyboardButton(
            "⚡ Ztrax Bypass",
            callback_data="loader_ztrax"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🧠 Nebula ESP",
            callback_data="loader_nebula"
        ),

        InlineKeyboardButton(
            "👑 King Android",
            callback_data="loader_king"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🔙 BACK",
            callback_data="back_start"
        )
    )

    bot.edit_message_text(
        "🎮 Select Your Loader",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# =========================
# BACK BUTTON
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "back_start")
def back_start(call):

    try:
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
    except:
        pass

    start(call.message)

# =========================
# LOADER SELECT
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("loader_"))
def select_loader(call):

    loader = call.data.replace("loader_", "")

    user_data[call.from_user.id] = {
        "loader": loader
    }

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "🔥 1 Day - ₹120",
            callback_data="plan_1d"
        ),

        InlineKeyboardButton(
            "⚡ 3 Day - ₹250",
            callback_data="plan_3d"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "💎 7 Day - ₹499",
            callback_data="plan_7d"
        ),

        InlineKeyboardButton(
            "👑 30 Day - ₹699",
            callback_data="plan_30d"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🔙 BACK",
            callback_data="loader_menu"
        )
    )

    bot.edit_message_text(
        f"""
💀 {loader.upper()} Selected

━━━━━━━━━━━━━━━━━━
⚡ Choose Your Plan
━━━━━━━━━━━━━━━━━━
""",
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

    upi_link = f"upi://pay?pa={UPI_ID}&pn=Shikari&am={amount}"

    qr = qrcode.make(upi_link)

    bio = BytesIO()
    bio.name = "qr.png"

    qr.save(bio, "PNG")
    bio.seek(0)

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "📤 SEND SCREENSHOT",
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

⚠️ Any Problem Contact
@Shikari067
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

⚠️ Fake Payment = Permanent Ban
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

    loader = user_data[user_id]["loader"]
    plan = user_data[user_id]["plan"]

    username = message.from_user.username

    if username:
        username = f"@{username}"
    else:
        username = "No Username"

    caption = f"""
💸 NEW PAYMENT REQUEST

👤 User: {username}
🆔 ID: {user_id}

🎮 Loader: {loader}
📦 Plan: {plan}
"""

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "✅ APPROVE",
            callback_data=f"approve_{user_id}"
        ),

        InlineKeyboardButton(
            "❌ REJECT",
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
        """
⏳ Payment Submitted

Please Wait For Admin Approval
"""
    )

# =========================
# GET KEY
# =========================

def get_key(loader, plan):

    filename = f"{loader}_{plan}.txt"

    if not os.path.exists(filename):
        return None

    with open(filename, "r") as f:
        keys = f.readlines()

    if len(keys) == 0:
        return None

    key = keys[0].strip()

    with open(filename, "w") as f:
        f.writelines(keys[1:])

    return key

# =========================
# APPROVE
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])

    loader = user_data[user_id]["loader"]
    plan = user_data[user_id]["plan"]

    key = get_key(loader, plan)

    if not key:

        bot.send_message(
            call.message.chat.id,
            "❌ No Keys Available"
        )

        return

    text = f"""
🎉 Payment Approved

🔑 KEY:
{key}

⚡ Loader: {loader}
📦 Plan: {plan}

⚠️ Any Problem Contact
@Shikari067
"""

    bot.send_message(
        user_id,
        text
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

⚠️ Any Problem Contact
@Shikari067
"""
    )

    bot.answer_callback_query(
        call.id,
        "Rejected"
    )

# =========================
# RUN BOT
# =========================

print("Bot Running...")

bot.infinity_polling(skip_pending=True)
