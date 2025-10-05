from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.fs_machine import SupportState
from helpers import get_ticket, update_ticket, time_for_answer, add_new_chat, load_all, delete_chat
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
admin_router = Router()

@admin_router.callback_query(F.data.startswith(("resolve", "reject")))
async def handle_admin_answer(callback: CallbackQuery, state: FSMContext):
    action, ticket_id = callback.data.split(":")
    ticket_id = int(ticket_id)
    ticket = get_ticket(ticket_id)
    user_id = ticket["user_id"]
    await state.set_state(SupportState.waiting_answer_text)
    await state.update_data(ticket_id=ticket_id, action=action, user_id=user_id)

    await callback.message.answer("✍️ Напишите сообщение пользователю:")
    await callback.answer()


@admin_router.message(SupportState.waiting_answer_text)
async def support_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket_id = data["ticket_id"]
    action = data["action"]
    user_id = data["user_id"]
    ticket = get_ticket(ticket_id)
    
    if action == "resolve":
        ticket["status"] = "resolved"
        ticket = time_for_answer(ticket)
        text = "✅ Решён!"
        update_ticket(ticket, "resolved_tickets.json")
    else:
        ticket["status"] = "rejected"
        ticket = time_for_answer(ticket)
        text = "❌ Отклонён."
        update_ticket(ticket, "rejected_tickets.json")
    
    await message.bot.send_message(
        user_id, 
        f"Ваш запрос был отмечен как {text}.\n"
        f"Сообщение от поддержки: {message.text}"
    )

@admin_router.callback_query(F.data == "add_chat")
async def add_chat_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "🆕 Для добавления нового чата:\n\n"
        "1️⃣ Введите *название чата* (пример: `repay` или `support`).",
        parse_mode="Markdown"
    )
    await state.set_state(SupportState.add_chat)

@admin_router.message(SupportState.add_chat)
async def add_chat_name(message: Message, state: FSMContext):
    await state.update_data(chat_name=message.text.strip())
    await message.answer(
        "2️⃣ Теперь отправьте *Chat ID* чата поддержки (пример: `-1003177380600`).",
        parse_mode="Markdown"
    )
    await message.delete()
    await state.set_state(SupportState.add_chat_id)

@admin_router.message(SupportState.add_chat_id)
async def add_chat_id(message: Message, state: FSMContext):
    try:
        chat_id = int(message.text.strip())
        await state.update_data(chat_id=chat_id)
        await message.answer(
            "3️⃣ Отлично! Теперь отправьте *текстовое сообщение* для пользователей, "
            "которое будет показываться при выборе этого чата.",
            parse_mode="Markdown"
        )
        await message.delete()
        await state.set_state(SupportState.add_chat_message)
    except ValueError:
        await message.answer("Айди должно быть в формате -1003177380600")
        await message.delete()
        await state.set_state(SupportState.add_chat_id)

@admin_router.message(SupportState.add_chat_message)
async def add_chat_message(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_name = data["chat_name"]
    chat_id = data["chat_id"]
    chat_message = message.text.strip()

    new_chat = {
        chat_name: {
            "chat_id": chat_id,
            "message": chat_message
        }
    }

    add_new_chat(new_chat)

    await message.answer(
        f"✅ Новый чат успешно добавлен!\n\n"
        f"**Название:** {chat_name}\n"
        f"**Chat ID:** `{chat_id}`\n"
        f"**Сообщение:** {chat_message}",
        parse_mode="Markdown",
        callback_data="start"
    )
    await message.delete()
    await state.clear()


@admin_router.callback_query(F.data == "delete_chat")
async def start_delete_chat(callback: CallbackQuery, state: FSMContext):

    chats = load_all("chat.json")
    if not chats:
        await callback.message.answer("⚠️ Нет чатов для удаления.")
        return

    kb = InlineKeyboardBuilder()
    for chat_name in chats.keys():
        kb.button(text=f"❌ {chat_name.upper()}", callback_data=f"confirm_delete:{chat_name}")
    kb.adjust(1)

    await callback.message.answer("Выберите чат, который хотите удалить:", reply_markup=kb.as_markup())

@admin_router.callback_query(F.data.startswith("confirm_delete"))
async def delete_chat_confirm(callback: CallbackQuery, state: FSMContext):
    chat_name = callback.data.split(":", 1)[1]

    if not chat_name:
        await callback.message.answer("⚠️ Ошибка — чат не найден.")
        return

    if delete_chat(chat_name):
        await callback.message.answer(text=f"✅ Чат '{chat_name}' успешно удалён.", callback_data="start")
    else:
        await callback.message.answer(f"❌ Ошибка удаления чата '{chat_name}'.")
    await state.clear()
    
@admin_router.callback_query(F.data == "cancel_delete", SupportState.delete_chat)
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Удаление чата отменено.")
    await state.clear()
