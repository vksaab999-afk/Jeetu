from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8836710838:AAFPNULu7qvH2ZFMZGgJElNjawMR0NaDg3I"

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        print(f"Document ID: {file_id}") # Terminal me print hoga
        await message.reply_text(f"📁 **Document File ID:**\n`{file_id}`\n\nName: {file_name}", parse_mode="Markdown")
        
    elif message.video:
        file_id = message.video.file_id
        print(f"Video ID: {file_id}")
        await message.reply_text(f"🎬 **Video File ID:**\n`{file_id}`", parse_mode="Markdown")
        
    elif message.audio:
        file_id = message.audio.file_id
        print(f"Audio ID: {file_id}")
        await message.reply_text(f"🎵 **Audio File ID:**\n`{file_id}`", parse_mode="Markdown")
        
    elif message.photo:
        file_id = message.photo[-1].file_id
        print(f"Photo ID: {file_id}")
        await message.reply_text(f"🖼 **Photo File ID:**\n`{file_id}`", parse_mode="Markdown")
        
    elif message.text:
        await message.reply_text(f"💬 **Text Message:**\n{message.text}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, get_file_id))
    
    print("ID Finder Bot is running and waiting for messages...")
    application.run_polling()

if __name__ == "__main__":
    main()
