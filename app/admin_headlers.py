from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.fs_machine import SupportState
from helpers import get_ticket, update_ticket, time_for_answer
from aiogram.types import CallbackQuery, Message
from config import bot

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
        text = "✅ Ваш тикет решён!"
        update_ticket(ticket, "resolved_tickets.json")
    else:
        ticket["status"] = "rejected"
        ticket = time_for_answer(ticket)
        text = "❌ Ваш тикет отклонён."
        update_ticket(ticket, "rejected_tickets.json")
    
    await message.bot.send_message(
        user_id, 
        f"Ваш тикет #{ticket_id} был отмечен как {action.upper()}.\n"
        f"Сообщение от поддержки: {message.text}"
    )
