import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from src.transcription import transcribe_audio, handle_audio_message
from src.gemini import process_with_gemini
from src.notion import update_notion_document

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    user = update.effective_user
    username = user.first_name if user.first_name else "there"
    await update.message.reply_text(f'👋 Welcome, {username}! \nSend me an audio message to document your ideas easily in Notion. 🎙️')

async def handle_audio(update: Update, context):
    user = update.effective_user
    logger.info(f"Received audio message from {user.id}")
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Send a "processing" message immediately
    processing_message = await update.message.reply_text("⏳ Processing your audio... Please wait. ⏳")

    try:
        # Download and save the audio file
        audio_file = await handle_audio_message(update.message.voice)

        transcript = transcribe_audio(audio_file)

        gemini_output = process_with_gemini(transcript)

        # Update Notion document
        notion_url = update_notion_document(gemini_output)

        # Edit the processing message with the success message
        await processing_message.edit_text(
            f"✅ **Audio processed successfully!** 🎉\n\nYour insights have been documented in Notion: {notion_url} 📄\n\nHave a productive day! ✨"
        )

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        # Edit the processing message with the error message
        await processing_message.edit_text(
            "⚠️ **Oops! An error occurred.** 😞\n\nWe couldn't process your audio. Please try again later. If the problem persists, contact support. 🙏" 
        )

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()