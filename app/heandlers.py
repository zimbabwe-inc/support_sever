from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.fs_machine import SupportForm
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers import load_tickets, save_ticket
SUPPORT_CHATS = {
    "repay": -4984467211,
    "tech": -1003177380600,
}

support_router = Router()

@support_router.callback_query(F.data == "text_creation")
async def text_create(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("✍️ Напишите суть обращения для поддержки")
    await state.set_state(SupportForm.waiting_for_text)


@support_router.callback_query(F.data.startswith("choose_chat:"))
async def choose_chat(callback: types.CallbackQuery, state: FSMContext):
    _, chat_key = callback.data.split(":")
    if chat_key not in SUPPORT_CHATS:
        await callback.message.answer("⚠️ Выбран неверный чат.")
        return

    await state.update_data(chosen_chat=chat_key)
    await callback.message.answer(
        f"✍️ Напишите суть обращения для поддержки ({chat_key})"
    )
    await state.set_state(SupportForm.waiting_for_text)


from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@support_router.message(SupportForm.waiting_for_text)
async def save_and_send_support_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text = message.text
    chosen_chat = data.get("chosen_chat")

    if not chosen_chat or chosen_chat not in SUPPORT_CHATS:
        await message.answer("⚠️ Вы не выбрали чат для поддержки.")
        return

    tickets = load_tickets()
    ticket_id = len(tickets) + 1

    username = message.from_user.username
    username_with_at = f"@{username}" if username else message.from_user.full_name

    ticket_data = {
        "ticket_id": ticket_id,
        "chat": chosen_chat,
        "user_id": message.from_user.id,
        "user_name": username_with_at,
        "text": user_text,
        "status": "new",
        "created_at": datetime.now().isoformat()
    }
    save_ticket(ticket_data)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Решено", callback_data=f"resolve:{ticket_id}"),
            InlineKeyboardButton(text="❌ Отклонено", callback_data=f"reject:{ticket_id}")
        ]
    ])

    chat_id = SUPPORT_CHATS[chosen_chat]
    await message.bot.send_message(
        chat_id=chat_id,
        text=f"📩 Новое обращение #{ticket_id}!\n\n"
             f"👤 Пользователь: {message.from_user.full_name} {username_with_at}\n"
             f"💬 Сообщение: {user_text}",
        reply_markup=kb
    )

    await message.answer("✅ Ваше обращение отправлено.")



@support_router.message()
async def debug_chat_id(message: types.Message):
    print(message.chat.id)
