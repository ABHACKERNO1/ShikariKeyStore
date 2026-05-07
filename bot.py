import os
import telebot
import qrcode
from io import BytesIO
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "YOUR_BOT_TOKEN"
UPI_ID = "YOUR_UPI_ID"
ADMIN_ID = 123456789

bot = telebot.TeleBot(TOKEN)

PRICES = {
    "1d": 120,
    "3d": 250,
    "7d": 499,
    "30d": 699
}

user_data = {}

# START
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
        InlineKeyboardButton("🎮 SELECT LOADER", callback_data="loader_menu"),
        InlineKeyboardButton("📞 SUPPORT", url="https://t.me/SHIKARI067")
    )

    bot.send_message(message.chat.id, text, reply_markup=markup)

# LOADER MENU
@bot.callback_query_handler(func=lambda call: call.data == "loader_menu")
def loader_menu(call):

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton("💀 X Silent", callback_data="loader_xsilent"),
        InlineKeyboardButton("⚡ Ztrax Bypass", callback_data="loader_ztrax")
    )

    markup.add(
        InlineKeyboardButton("🧠 Nebula ESP", callback_data="loader_nebula"),
        InlineKeyboardButton("👑 King Android", callback_data="loader_king")
    )

    markup.add(
        InlineKeyboardButton("🔙 BACK", callback_data="back_start")
    )

    bot.edit_message_text(
        "🎮 Select Your Loader",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# BACK
@bot.callback_query_handler(func=lambda call: call.data == "back_start")
def back_start(call):
    start(call.message)

# LOADER SELECT
@bot.callback_query_handler(func=lambda call: call.data.startswith("loader_"))
def select_loader(call):

    loader = call.data.replace("loader_", "")

    user_data[call.from_user.id] = {
        "loader": loader
    }

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton("🔥 1 Day - ₹120", callback_data="plan_1d"),
        InlineKeyboardButton("⚡ 3 Day - ₹250", callback_data="plan_3d")
    )

    markup.add(
        InlineKeyboardButton("💎 7 Day - ₹499", callback_data="plan_7d"),
        InlineKeyboardButton("👑 30 Day - ₹699", callback_data="plan_30d")
    )

    markup.add(
        InlineKeyboardButton("🔙 BACK", callback_data="loader_menu")
    )

    bot.edit_message_text(
        f"💀 {loader.upper()} Selected\n\n⚡ Choose Your Plan",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# PLAN SELECT
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
        InlineKeyboardButton("📤 SEND SCREENSHOT", callback_data="send_ss")
    )

    bot.send_photo(
        call.message.chat.id,
        bio,
        caption=f"💰 Amount: ₹{amount}\n\n📲 Scan QR & Pay\n📤 Send Screenshot After Payment",
        reply_markup=markup
    )

# SEND SCREENSHOT BUTTON
@bot.callback_query_handler(func=lambda call: call.data == "send_ss")
def send_ss(call):

    bot.send_message(
        call.message.chat.id,
        "📤 Send Payment Screenshot"
    )

# SCREENSHOT HANDLER
@bot.message_handler(content_types=['photo'])
def photo_handler(message):

    user_id = message.from_user.id

    if user_id not in user_data:
        return

    loader = user_data[user_id]["loader"]
    plan = user_data[user_id]["plan"]

    caption = f"""
💸 NEW PAYMENT REQUEST

👤 User: @{message.from_user.username}
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
        "⏳ Payment Submitted\n\nPlease Wait For Admin Approval"
    )

# GET KEY

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

# APPROVE
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
||{key}||

⚡ Loader: {loader}
📦 Plan: {plan}
"""

    bot.send_message(
        user_id,
        text,
        parse_mode="MarkdownV2"
    )

    bot.answer_callback_query(call.id, "Approved")

# REJECT
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])

    bot.send_message(
        user_id,
        "❌ Payment Rejected"
    )

    bot.answer_callback_query(call.id, "Rejected")

print("Bot Running...")

bot.infinity_polling()