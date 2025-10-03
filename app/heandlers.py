from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.fs_machine import SupportForm
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers import load_tickets, save_ticket, get_next_ticket_id, get_chat
from app.keyboards import get_ticket_kb
SUPPORT_CHATS = {
    "repay": -4984467211,
    "tech": -1003177380600,
}
# SUPPORT_CHATS = get_chat()

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


@support_router.message(SupportForm.waiting_for_text, F.content_type == "text")
async def ask_for_file(message: types.Message, state: FSMContext):
    await state.set_state(SupportForm.waiting_for_text)
    await state.update_data(user_text=message.text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📎 Добавить файл", callback_data="add_file")],
        [InlineKeyboardButton(text="✅ Отправить обращение", callback_data="send_ticket")]
    ])

    await message.answer("Хотите добавить файл к обращению?", reply_markup=kb)


@support_router.callback_query(F.data == "add_file")
async def add_file(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📎 Отправьте файл (документ, фото или видео)")
    await state.set_state(SupportForm.waiting_for_file)


@support_router.callback_query(F.data == "send_ticket")
async def send_ticket(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text = data.get("user_text")
    chosen_chat = data.get("chosen_chat")

    if not chosen_chat or not user_text:
        await callback.answer("⚠️ Ошибка. Попробуйте заново.", show_alert=True)
        return

    ticket_id = get_next_ticket_id("resolved_tickets.json", "rejected_tickets.json")

    username = callback.from_user.username
    username_with_at = f"@{username}" if username else callback.from_user.full_name

    ticket_data = {
        "ticket_id": ticket_id,
        "chat": chosen_chat,
        "user_id": callback.from_user.id,
        "user_name": username_with_at,
        "text": user_text,
        "status": "new",
        "created_at": datetime.now().strftime("%d.%m %H:%M")
    }
    save_ticket(ticket_data)

    kb = get_ticket_kb(ticket_id)

    chat_id = SUPPORT_CHATS[chosen_chat]
    await callback.bot.send_message(
        chat_id=chat_id,
        text=f"📩 Новое обращение #{ticket_id}!\n\n"
             f"👤 Пользователь: {callback.from_user.full_name} {username_with_at}\n"
             f"💬 Сообщение: {user_text}",
        reply_markup=kb
    )

    await callback.message.answer("✅ Ваше обращение отправлено.")
    await state.clear()


@support_router.message(SupportForm.waiting_for_file, F.content_type.in_({"photo", "document", "video"}))
async def receive_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text = data.get("user_text")
    chosen_chat = data.get("chosen_chat")

    if not chosen_chat or not user_text:
        await message.answer("⚠️ Ошибка. Попробуйте заново.")
        return

    ticket_id = get_next_ticket_id("resolved_tickets.json", "rejected_tickets.json")

    username = message.from_user.username
    username_with_at = f"@{username}" if username else message.from_user.full_name

    ticket_data = {
        "ticket_id": ticket_id,
        "chat": chosen_chat,
        "user_id": message.from_user.id,
        "user_name": username_with_at,
        "text": user_text,
        "status": "new",
        "created_at": datetime.now().strftime("%d.%m %H:%M")
    }
    save_ticket(ticket_data)

    kb = get_ticket_kb(ticket_id)

    chat_id = SUPPORT_CHATS[chosen_chat]

    if message.content_type == "photo":
        await message.bot.send_photo(chat_id, photo=message.photo[-1].file_id,
                                     caption=f"📩 Новое обращение #{ticket_id} от {username_with_at}\n\n{user_text}",
                                     reply_markup=kb)
    elif message.content_type == "document":
        await message.bot.send_document(chat_id, document=message.document.file_id,
                                        caption=f"📩 Новое обращение #{ticket_id} от {username_with_at}\n\n{user_text}",
                                        reply_markup=kb)
    elif message.content_type == "video":
        await message.bot.send_video(chat_id, video=message.video.file_id,
                                     caption=f"📩 Новое обращение #{ticket_id} от {username_with_at}\n\n{user_text}",
                                     reply_markup=kb)

    await message.answer("✅ Ваше обращение отправлено с файлом.")
    await state.clear()
