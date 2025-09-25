from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

text_creation = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправить сообщение в чат", callback_data="text_creation")],
    ]
)
