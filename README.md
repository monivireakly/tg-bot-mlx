# Telegram Transcription and Summarization Bot

This Telegram bot can transcribe YouTube videos and voice messages, and then summarize the transcriptions using a language model. It's optimized for Apple Silicon chips using the MLX framework.

## Features

- Transcribe YouTube videos
- Transcribe voice messages
- Summarize transcriptions using MLX-powered LLM
- Display original transcriptions
- Optimized performance on Apple Silicon chips

## Technology Stack

- Python 3.8+
- MLX framework for efficient machine learning on Apple Silicon
- Telegram Bot API
- yt-dlp for YouTube video downloading
- MLX Whisper for audio transcription
- Llama 3.2 1B model for text summarization

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/your-username/telegram-transcription-bot.git
   cd telegram-transcription-bot
   ```

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

1. Start a chat with the bot on Telegram and use the `/start` command
2. Choose between YouTube link or voice message transcription
3. Send a YouTube link or voice message
4. After transcription, choose to summarize or view the original transcription
5. View the processing times for transcription and summarization

## MLX Framework and Apple Silicon Optimization

This bot utilizes the MLX framework, which is specifically designed to leverage the power of Apple Silicon chips. MLX provides:

- Efficient execution of machine learning models on Apple Silicon
- Optimized performance for audio transcription and text summarization tasks
- Reduced memory usage and faster inference times

By using MLX, this bot can perform transcription and summarization tasks more quickly and efficiently on devices with Apple Silicon chips, such as Macs with M1, M2, or later processors.

## Dependencies

See `requirements.txt` for a full list of dependencies. Key dependencies include:
`pip install -r requirements.txt`


## License

This project is licensed under the MIT License.

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.
