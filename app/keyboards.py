from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

text_creation = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправить сообщение в чат", callback_data="text_creation")],
    ]
)

def get_ticket_kb(ticket_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Решено", callback_data=f"resolve:{ticket_id}"),
            InlineKeyboardButton(text="❌ Отклонено", callback_data=f"reject:{ticket_id}")
        ]
    ])

chat_setting_keyb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить чат", callback_data="add_chat",)],
        [InlineKeyboardButton(text="Удалить чат", callback_data="delete_chat")],
    ]
)