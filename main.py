import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from app.heandlers import support_router, FSMContext
from app.keyboards import chat_setting_keyb
from aiogram.utils.keyboard import InlineKeyboardBuilder
from helpers import count_tickets, get_chat
from config import bot
from app.admin_headlers import admin_router
load_dotenv()

ADMIN_ID = [5431374795]


logging.basicConfig(level=logging.INFO)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(support_router)
dp.include_router(admin_router)

@dp.message(F.text.in_({"/start", "start"}))
async def cmd_start(message: types.Message, state: FSMContext):
    
    SUPPORT_CHATS, _ = get_chat()
    kb = InlineKeyboardBuilder()
    
    if message.from_user.id in ADMIN_ID:
        resolved = count_tickets("resolved_tickets.json")
        rejected = count_tickets("rejected_tickets.json")
        await message.answer(text=F"Кол-во решенных тикетов {resolved} \nКол-во нерешенных тикетов {rejected}", reply_markup=chat_setting_keyb)
        
    for key, chat_id in SUPPORT_CHATS.items():
        kb.button(text=f"💬 {key.upper()} SUPPORT", callback_data=f"choose_chat:{key}")
    kb.adjust(2)

    await message.answer("Выберите чат, куда хотите отправить обращение:", reply_markup=kb.as_markup())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
