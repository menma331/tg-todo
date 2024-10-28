from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup


def get_task_manager_markup(
    current_task_number: int, last_task_number: int
) -> InlineKeyboardMarkup:
    """Получение меню для управления задачей."""
    buttons = InlineKeyboardBuilder()

    # Верхний ряд кнопок
    buttons.button(text="Задача выполнена ✅", callback_data="task_completed")
    buttons.button(text="Удалить задачу 🗑", callback_data="delete_task")

    # Нижний ряд кнопок
    buttons.button(text="⬅ Назад", callback_data="back")
    buttons.button(
        text=f"{current_task_number}/{last_task_number}",
        callback_data="pagination_info",
    )
    buttons.button(text="Вперед ➡", callback_data="next")

    # Располагаем кнопки в два ряда
    buttons.adjust(2, 3)
    return buttons.as_markup()
