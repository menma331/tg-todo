from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup


def get_confirmation_keyboard_markup() -> InlineKeyboardMarkup:
    """Получение registration клавиатуры для подтверждения имени пользователя."""
    buttons = InlineKeyboardBuilder()
    buttons.button(text="✅", callback_data="confirm")
    buttons.button(text="❌", callback_data="cancel")

    buttons.adjust(2)

    return buttons.as_markup()
