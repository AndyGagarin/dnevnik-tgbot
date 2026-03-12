from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def token_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Получить токен", url='https://androsovpavel.pythonanywhere.com/')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)