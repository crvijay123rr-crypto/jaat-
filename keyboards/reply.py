from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)


def main_menu():

    keyboard = [
        [
            KeyboardButton(
                text="👤 Profile"
            ),
            KeyboardButton(
                text="🎁 Trial"
            )
        ],

        [
            KeyboardButton(
                text="🔑 Activate PIN"
            ),
            KeyboardButton(
                text="📂 Process File"
            )
        ],

        [
            KeyboardButton(
                text="🎯 Referral"
            ),
            KeyboardButton(
                text="💎 Plans"
            )
        ],

        [
            KeyboardButton(
                text="📞 Support"
            ),
            KeyboardButton(
                text="ℹ️ Help"
            )
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder=
        "🚀 Select an option..."
    )
