import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv
import mlx_whisper
import yt_dlp
from mlx_lm import load, generate
from langchain_core.prompts import ChatPromptTemplate
import time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

class Summarizer:
    def __init__(self, model_name="mlx-community/Llama-3.2-1B-Instruct-4bit"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None

    def load_model(self):
        if self.model is None or self.tokenizer is None:
            self.model, self.tokenizer = load(self.model_name)

    def invoke(self, prompt):
        self.load_model()  # Ensure model is loaded
        if hasattr(self.tokenizer, "apply_chat_template") and self.tokenizer.chat_template is not None:
            messages = [{"role": "user", "content": prompt}]
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        
        response = generate(self.model, self.tokenizer, prompt=prompt, verbose=True, max_tokens=1024)
        return response

    def summarize_text(self, text: str) -> str:
        prompt = ChatPromptTemplate.from_template(
            "Please summarize the following text in 3-5 bullet points:\n\n{text}\n\nSummary:"
        )
        formatted_prompt = prompt.format(text=text)
        summary = self.invoke(formatted_prompt)
        return summary.strip()

summarizer = Summarizer()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("YouTube Link", callback_data='youtube'),
                 InlineKeyboardButton("Voice Message", callback_data='voice')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose transcription method:', reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data in ['youtube', 'voice']:
        await query.edit_message_text(f"Please send the {'YouTube URL' if query.data == 'youtube' else 'voice message'} to transcribe.")
    elif query.data in ['summarize', 'original']:
        transcription = context.user_data.get('transcription', '')
        transcription_time = context.user_data.get('transcription_time', 0)
        if transcription:
            if query.data == 'summarize':
                await query.edit_message_text("Summarizing the transcription... This may take a moment.")
                start_time = time.time()
                text = summarizer.summarize_text(transcription)
                summarization_time = time.time() - start_time
                await query.edit_message_text(f"Summary complete in {summarization_time:.2f} seconds. Sending results...")
            else:
                text = transcription
                await query.edit_message_text("Sending original transcription...")
            
            await send_long_message(query.message.chat, text)
            if query.data == 'summarize':
                await query.message.chat.send_message(f"Transcription took {transcription_time:.2f} seconds. Summarization took {summarization_time:.2f} seconds.")
            else:
                await query.message.chat.send_message(f"Transcription took {transcription_time:.2f} seconds.")
            await query.message.delete()
        else:
            await query.edit_message_text(f"No {'transcription' if query.data == 'summarize' else 'original transcription'} available.")

async def send_long_message(chat, text: str):
    MAX_LENGTH = 4000
    if len(text) <= MAX_LENGTH:
        # If the text is short enough, send it as a single message
        await chat.send_message(text)
    else:
        # If the text is too long, split it into parts
        parts = [text[i:i+MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
        for i, part in enumerate(parts, 1):
            try:
                await chat.send_message(f"Part {i}/{len(parts)}:\n\n{part}")
            except Exception as e:
                logger.error(f"Error sending message part {i}: {e}")
                await chat.send_message(f"Error sending part {i}. Please try again.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'youtube.com' in update.message.text or 'youtu.be' in update.message.text:
        await update.message.reply_text("Downloading and transcribing YouTube audio...")
        try:
            start_time = time.time()
            ydl_opts = {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}], 'outtmpl': 'youtube_audio.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([update.message.text])
            result = mlx_whisper.transcribe("youtube_audio.wav", path_or_hf_repo="mlx-community/whisper-turbo")
            transcription_time = time.time() - start_time
            context.user_data['transcription'] = result['text']
            context.user_data['transcription_time'] = transcription_time
            keyboard = [[InlineKeyboardButton("Summarize", callback_data='summarize'), InlineKeyboardButton("Original", callback_data='original')]]
            await update.message.reply_text(f"Transcription complete in {transcription_time:.2f} seconds. Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard))
            os.remove("youtube_audio.wav")
        except Exception as e:
            logger.error(f"Error in handle_text: {e}")
            await update.message.reply_text(f"An error occurred: {str(e)}")
    else:
        await update.message.reply_text("Please use the /start command to choose a transcription method.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice = await update.message.voice.get_file()
    await voice.download_to_drive('voice_message.ogg')
    await update.message.reply_text("Transcribing your voice message...")
    try:
        start_time = time.time()
        result = mlx_whisper.transcribe("voice_message.ogg", path_or_hf_repo="mlx-community/whisper-turbo")
        transcription_time = time.time() - start_time
        context.user_data['transcription'] = result['text']
        context.user_data['transcription_time'] = transcription_time
        keyboard = [[InlineKeyboardButton("Summarize", callback_data='summarize'), InlineKeyboardButton("Original", callback_data='original')]]
        await update.message.reply_text(f"Transcription complete in {transcription_time:.2f} seconds. Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard))
        os.remove("voice_message.ogg")
    except Exception as e:
        logger.error(f"Error in handle_voice: {e}")
        await update.message.reply_text(f"An error occurred: {str(e)}")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.run_polling()

if __name__ == '__main__':
    main()