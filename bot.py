import os
import logging
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient
from flask import Flask
import threading

# --- CONFIGURATION ---
BOT_TOKEN = "8836710838:AAFPNULu7qvH2ZFMZGgJElNjawMR0NaDg3I"
MONGO_URI = "mongodb+srv://Jeetu:jeetul122@jeetu.86vxzav.mongodb.net/?appName=Jeetu"

# Aapki Admin Telegram User IDs (Yahan aur bhi IDs baad me comma lagakar jod sakte hain)
ADMIN_IDS = [
    5785924075,
    # Example: 123456789, 987654321  (Aise aur likh sakte ho)
]

# Aapke diye hue File IDs / Message IDs jo user ko join karte hi milenge
MATERIAL_IDS = [
    "18",  # 1st material
    "14",  # 2nd material
    "16"   # 3rd material
]

# --- MONGODB SETUP ---
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_bot_db"]
users_collection = db["users"]

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. JOIN REQUEST HANDLER ---
async def join_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.chat_join_request
    user = query.from_user
    user_id = user.id

    # User ko database me save karein (agar pehle se nahi hai)
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({
            "user_id": user_id,
            "first_name": user.first_name,
            "username": user.username
        })

    # Request automatically approve karein
    try:
        await query.approve()
    except Exception as e:
        logger.error(f"Failed to approve join request: {e}")

    # User ko personal chat (DM) me welcome message aur material bhejein
    try:
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"Hello {user.first_name}!\n\nHamare channel par swagat hai. Aapka material niche diya ja raha hai:"
        )
        
        # Ek-ek karke aapke diye hue IDs/Materials user ko send honge
        for item_id in MATERIAL_IDS:
            try:
                await context.bot.send_message(chat_id=user_id, text=f"Material ID: {item_id}")
            except Exception as inner_e:
                logger.error(f"Failed to send item {item_id}: {inner_e}")
                
    except Exception as e:
        logger.error(f"Failed to send DM to {user_id}: {e}")

# --- 2. ADMIN BROADCAST SYSTEM ---
async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    message = update.message
    if not message.reply_to_message and len(context.args) == 0 and not message.caption and not message.photo and not message.video and not message.document:
        await message.reply_text("Kripya broadcast karne ke liye koi message bhejein ya kisi message ko reply karein!")
        return

    target_message = message.reply_to_message if message.reply_to_message else message
    all_users = users_collection.find({})
    success = 0
    failed = 0

    status_msg = await message.reply_text("📢 Broadcast shuru ho gaya hai...")

    for user in all_users:
        user_id = user["user_id"]
        try:
            await target_message.copy(chat_id=user_id)
            success += 1
        except Exception:
            failed += 1

    await status_msg.edit_text(f"✅ Broadcast Complete!\n\nSuccessful: {success}\nFailed: {failed}")

# --- 3. STATS COMMAND ---
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    total_users = users_collection.count_documents({})
    await update.message.reply_text(f"📊 Total Users in Database: {total_users}")

# --- 4. RENDER UPTIME SERVER (Flask) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is active and running!"

def run_web():
    web_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

# --- MAIN FUNCTION ---
def main():
    t = threading.Thread(target=run_web)
    t.start()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(ChatJoinRequestHandler(join_request_handler))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.User(ADMIN_IDS) & ~filters.COMMAND, broadcast_message))

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
