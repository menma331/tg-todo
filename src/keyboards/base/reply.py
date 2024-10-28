from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup


def get_menu_markup() -> ReplyKeyboardMarkup:
    """Получение меню клавиатуры."""
    buttons = ReplyKeyboardBuilder()

    buttons.button(text="Добавить задачу➕")
    buttons.button(text="Список задач🗓")
    buttons.adjust(1, repeat=False)

    return buttons.as_markup(resize_keyboard=True, one_time_keyboard=True)
