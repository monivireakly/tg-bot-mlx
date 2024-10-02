# Telegram Transcription and Summarization Bot

This Telegram bot can transcribe YouTube videos and voice messages, and then summarize the transcriptions using a language model.

## Features

- Transcribe YouTube videos
- Transcribe voice messages
- Summarize transcriptions
- Display original transcriptions

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your Telegram Bot Token:
   ```
   BOT_TOKEN=your_bot_token_here
   ```
4. Run the bot:
   ```
   python main.py
   ```

## Usage

1. Start a chat with the bot and use the `/start` command
2. Choose between YouTube link or voice message transcription
3. Send a YouTube link or voice message
4. After transcription, choose to summarize or view the original transcription

## Dependencies

See `requirements.txt` for a full list of dependencies.

## License

This project is licensed under the MIT License.
