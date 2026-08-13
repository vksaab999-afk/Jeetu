import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Aapka diya hua Bot Token yaha set hai
BOT_TOKEN = "8836710838:AAFPNULu7qvH2ZFMZGgJElNjawMR0NaDg3I"

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # Check karein ki message me kya hai aur uska ID nikal kar bhejein
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        await message.reply_text(f"📁 **Document File ID:**\n`{file_id}`\n\nName: {file_name}", parse_mode="Markdown")
        
    elif message.video:
        file_id = message.video.file_id
        await message.reply_text(f"🎬 **Video File ID:**\n`{file_id}`", parse_mode="Markdown")
        
    elif message.audio:
        file_id = message.audio.file_id
        await message.reply_text(f"🎵 **Audio File ID:**\n`{file_id}`", parse_mode="Markdown")
        
    elif message.photo:
        # Photo me multiple sizes hote hain, sabse badi wali ka ID lete hain
        file_id = message.photo[-1].file_id
        await message.reply_text(f"🖼 **Photo File ID:**\n`{file_id}`", parse_mode="Markdown")
        
    elif message.text:
        await message.reply_text(f"💬 **Text Message:**\n{message.text}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Har tarah ke message ko pakadne ke liye handler
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, get_file_id))
    
    print("ID Finder Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
