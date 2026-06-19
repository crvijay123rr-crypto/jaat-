from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


def main_menu():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👤 Profile"),
                KeyboardButton(text="🎁 Trial")
            ],
            [
                KeyboardButton(text="🔑 Activate PIN"),
                KeyboardButton(text="📂 Process File")
            ],
            [
                KeyboardButton(text="🎯 Referral"),
                KeyboardButton(text="💎 Plans")
            ],
            [
                KeyboardButton(text="📞 Support")
            ]
        ],
        resize_keyboard=True
    )
