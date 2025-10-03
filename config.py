from aiogram import Bot
import os
from dotenv import load_dotenv
load_dotenv()
from aiogram.client.default import DefaultBotProperties
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
