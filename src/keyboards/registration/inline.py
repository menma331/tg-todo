from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup


def get_user_login_markup() -> InlineKeyboardMarkup:
    """Получение registration клавиатуры для взятия логина из телеграма."""
    buttons = InlineKeyboardBuilder()

    buttons.button(
        text="Использовать логин телеграма🪧", callback_data="use_login_from_telegram"
    )

    return buttons.as_markup()
