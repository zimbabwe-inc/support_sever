import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from app.heandlers import support_router
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from app.fs_machine import SupportForm
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

ADMIN_ID = [5431374795]

SUPPORT_CHATS = {
    "repay": -4984467211,
    "tech": -1003177380600,
}

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(support_router)

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        kb = InlineKeyboardBuilder()
        
    kb = InlineKeyboardBuilder()
    for key, chat_id in SUPPORT_CHATS.items():
        kb.button(text=f"💬 {key.upper()} SUPPORT", callback_data=f"choose_chat:{key}")
    kb.adjust(1)

    await message.answer("Выберите чат, куда хотите отправить обращение:", reply_markup=kb.as_markup())
    await state.clear()



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
