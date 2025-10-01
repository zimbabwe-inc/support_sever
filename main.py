import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from app.heandlers import support_router, FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from helpers import get_ticket, update_ticket, time_for_answer, count_tickets
from aiogram.types import CallbackQuery
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
        resolved = count_tickets("resolved_tickets.json")
        rejected = count_tickets("rejected_tickets.json")
        await message.answer(text=F"Кол-во решенных тикетов {resolved} \nКол-во нерешенных тикетов {rejected}")
        
    kb = InlineKeyboardBuilder()
    for key, chat_id in SUPPORT_CHATS.items():
        kb.button(text=f"💬 {key.upper()} SUPPORT", callback_data=f"choose_chat:{key}")
    kb.adjust(1)

    await message.answer("Выберите чат, куда хотите отправить обращение:", reply_markup=kb.as_markup())
    await state.clear()

@dp.callback_query(F.data.startswith(("resolve", "reject")))
async def handle_admin_action(callback: CallbackQuery):
    action, ticket_id = callback.data.split(":")
    ticket = get_ticket(ticket_id)

    if not ticket:
        await callback.answer("❌ Тикет не найден", show_alert=True)
        return

    user_id = ticket["user_id"]

    if action == "resolve":
        ticket["status"] = "resolved"
        ticket = time_for_answer(ticket)
        text = "✅ Ваш тикет решён!"
        update_ticket(ticket, "resolved_tickets.json")
    else:
        ticket["status"] = "rejected"
        ticket = time_for_answer(ticket)
        text = "❌ Ваш тикет отклонён."
        update_ticket(ticket, "rejected_tickets.json")


    
    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        await callback.message.answer(f"⚠️ Не удалось отправить сообщение пользователю: {e}")

    if callback.message.text:
        await callback.message.edit_text(
            f"Тикет #{ticket_id} ({ticket['user_name']})\n"
            f"Статус: {ticket['status'].upper()}"
        )
    else:
        await callback.message.edit_caption(
            caption=f"Тикет #{ticket_id} ({ticket['user_name']})\n"
                    f"Статус: {ticket['status'].upper()}"
        )

    await callback.answer("✅ Решение отправлено пользователю")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
