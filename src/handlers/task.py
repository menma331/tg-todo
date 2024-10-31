from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.task.inline import get_task_manager_markup
from dao import TaskDAO
from keyboards.base.reply import get_menu_markup
from states import base_states, task_states
from utils import fsm
from responses import task as task_responses
from keyboards.base.inline import get_confirmation_keyboard_markup

task_router = Router()


# ------------------- region Добавление новой задачи -------------------
@task_router.message(
    F.text == "Добавить задачу➕",
    lambda message: fsm.get_state(message.from_user.id) == base_states.IN_MENU,
)
async def handle_wait_for_task_title(message: Message) -> None:
    """Обработчик ожидания заголовка новой задачи.

    Когда пользователь нажимает на кнопку "Добавить задачу", бот запрашивает заголовок задачи.
    """
    telegram_id = message.from_user.id

    fsm.set_state(telegram_id=telegram_id, state=task_states.WAIT_FOR_TASK_TITLE)

    await message.answer(text=task_responses.REQUEST_FOR_TASK_TITLE)


@task_router.message(
    F.content_type == "text",
    lambda message: fsm.get_state(message.from_user.id) == task_states.WAIT_FOR_TASK_TITLE,
)
async def handle_task_title(message: Message) -> None:
    """Обработка и переход к запросу описания задачи.

    После получения заголовка задачи, бот проверяет его длину и запрашивает описание.
    """
    task_title = message.text
    telegram_id = message.from_user.id

    if len(task_title) > 80:
        await message.answer(text=task_responses.LEN_OF_TITLE_CANT_BE_MORE_THAN_EIGHTY)
        return None

    fsm.set_data(telegram_id=telegram_id, key="task_title", value=task_title)
    fsm.set_state(telegram_id=telegram_id, state=task_states.SUBMIT_TITLE)

    await message.answer(
        text="Вы уверены в заголовке задачи ?",
        reply_markup=get_confirmation_keyboard_markup(),
    )


@task_router.callback_query(
    F.data.in_(["confirm", "cancel"]),
    lambda callback: fsm.get_state(callback.from_user.id) == task_states.SUBMIT_TITLE,
)
async def handle_confirm_or_cancel_task_title(callback: CallbackQuery) -> None:
    """Подтверждение или отмена заголовка задачи.

    Если заголовок подтвержден, бот запрашивает описание задачи. В противном случае,
    возвращается к запросу заголовка.
    """
    telegram_id = callback.from_user.id

    if callback.data == "confirm":
        fsm.set_state(
            telegram_id=telegram_id, state=task_states.WAIT_FOR_TASK_DESCRIPTION
        )
        await callback.message.answer(text=task_responses.REQUEST_FOR_TASK_DESCRIPTION)
        await callback.answer()
    else:
        fsm.set_state(telegram_id=telegram_id, state=task_states.WAIT_FOR_TASK_TITLE)
        await callback.message.answer(text=task_responses.REQUEST_FOR_TASK_TITLE)
        await callback.answer()


@task_router.message(
    F.content_type == "text",
    lambda message: fsm.get_state(message.from_user.id) == task_states.WAIT_FOR_TASK_DESCRIPTION,
)
async def handle_task_description(message: Message) -> None:
    """Обработка полученного описания задачи.

    После получения описания, бот запрашивает подтверждение перед добавлением задачи.
    """
    task_description = message.text
    telegram_id = message.from_user.id

    fsm.set_data(
        telegram_id=telegram_id, key="task_description", value=task_description
    )
    fsm.set_state(telegram_id=telegram_id, state=task_states.SUBMIT_DESCRIPTION)

    await message.answer(
        text="Вы уверены в описании задачи ?",
        reply_markup=get_confirmation_keyboard_markup(),
    )


@task_router.callback_query(
    F.data.in_(["confirm", "cancel"]),
    lambda callback: fsm.get_state(callback.from_user.id) == task_states.SUBMIT_DESCRIPTION,
)
async def handle_confirm_or_cancel_task_description(callback: CallbackQuery) -> None:
    """Подтверждение или отмена описания задачи.

    Если описание подтверждено, задача добавляется в базу данных. В противном случае
    возвращается к запросу описания.
    """
    telegram_id = callback.from_user.id

    if callback.data == "confirm":
        data_for_task = {
            "task_title": fsm.get_data(telegram_id, key="task_title"),
            "task_description": fsm.get_data(telegram_id, key="task_description"),
        }
        TaskDAO.add_new_task(telegram_id=telegram_id, data=data_for_task)
        fsm.set_state(telegram_id=telegram_id, state=base_states.IN_MENU)
        await callback.message.answer(
            text=task_responses.TASK_SUCCESSFULLY_ADDED, reply_markup=get_menu_markup()
        )
        await callback.answer()
    else:
        fsm.set_state(
            telegram_id=telegram_id, state=task_states.WAIT_FOR_TASK_DESCRIPTION
        )
        await callback.message.answer(text=task_responses.REQUEST_FOR_TASK_DESCRIPTION)
        await callback.answer()


# ------------------- endregion Добавление новой задачи -------------------

# ------------------- region Просмотр задач -------------------
@task_router.message(
    F.text == "Список задач🗓",
    lambda message: fsm.get_state(message.from_user.id) == base_states.IN_MENU,
)
async def handle_get_list_of_tasks(message: Message):
    """Обработка получения всех задач пользователя.

    Бот запрашивает список задач и отображает первую задачу с возможностью навигации.
    """
    telegram_id = message.from_user.id
    tasks = TaskDAO.get_all_tasks(telegram_id=telegram_id)
    fsm.set_state(telegram_id=telegram_id, state=task_states.LOOK_AT_TASKS)

    if not tasks:
        await message.answer(text=task_responses.YOU_HAVE_NOT_ANY_TASK)
        return

    # Отображаем первую задачу
    current_task_number = 1
    await display_task(message, tasks, current_task_number)


async def display_task(message: Message, tasks: list, current_task_number: int):
    """Функция для отображения задачи с пагинацией.

    Отправляет текст с текущей задачей и клавиатурой навигации.
    """
    last_task_number = len(tasks)

    task_title = tasks[current_task_number - 1]['title']
    task_description = tasks[current_task_number - 1]['description']

    await message.answer(
        text=f"Задача: <b>{task_title}</b>\n\n"
             f"Описание: {task_description}",
        reply_markup=get_task_manager_markup(current_task_number, last_task_number),
    )


@task_router.callback_query(
    F.data.in_(["back", "next", "task_completed", "delete_task", "confirm", "cancel"]),
    lambda callback: fsm.get_state(callback.from_user.id) == task_states.LOOK_AT_TASKS,
)
async def handle_task_navigation(callback: CallbackQuery):
    """Обработка пагинации."""
    telegram_id = callback.from_user.id
    tasks = TaskDAO.get_all_tasks(telegram_id=telegram_id)
    last_task_number = len(tasks)

    # Получаем текущий номер задачи из состояния
    current_task_number = fsm.get_data(telegram_id, key="current_task_number") or 1

    task_id = tasks[current_task_number - 1]["id"]

    if callback.data == "delete_task":
        fsm.set_data(telegram_id, key="current_task_number", value=current_task_number)
        fsm.set_data(telegram_id, key="last_task_number", value=last_task_number)
        fsm.set_data(telegram_id, key="task_id_to_delete", value=task_id)
        task_title = tasks[current_task_number - 1]['title']

        await callback.message.answer(
            text=f"Вы уверены, что хотите удалить задачу: \n\n<b>{task_title}</b> ?",
            reply_markup=get_confirmation_keyboard_markup(),
        )
        fsm.set_state(telegram_id=telegram_id, state=task_states.SUBMIT_DELETE_TASK)
        await callback.answer()
        return

    if callback.data == "task_completed":
        # Обновляем статус задачи
        TaskDAO.mark_task_as_completed(telegram_id=telegram_id, task_id=task_id)
        fsm.set_data(telegram_id, key="current_task_number", value=current_task_number)
        fsm.set_data(telegram_id, key="last_task_number", value=last_task_number)
        await callback.message.answer(text=task_responses.TASK_SUCCESSFULLY_COMPLETED, reply_markup=get_menu_markup())
        await callback.answer()
        return
    # Обновляем сообщение с новой задачей и клавиатурой
    task_title = tasks[current_task_number - 1]['title']
    task_description = tasks[current_task_number - 1]['description']

    # Изменяем current_task_number на основе действия
    if callback.data == "next":
        current_task_number += 1 if current_task_number < last_task_number else 0
    elif callback.data == "back":
        current_task_number -= 1 if current_task_number > 1 else 0

    # Сохраняем обновленный номер задачи в состоянии
    fsm.set_data(telegram_id, key="current_task_number", value=current_task_number)

    await callback.message.edit_text(
        text=f"Задача: <b>{task_title}</b>\n\n"
             f"Описание: {task_description}",
        reply_markup=get_task_manager_markup(current_task_number, last_task_number),
    )
    await callback.answer()


# Обработка подтверждения или отмены удаления задачи
@task_router.callback_query(
    F.data.in_(["confirm", "cancel"]),
    lambda callback: fsm.get_state(callback.from_user.id) == task_states.SUBMIT_DELETE_TASK,
)
async def handle_confirm_or_cancel_delete_task(callback: CallbackQuery) -> None:
    """Подтверждение или отмена удаления задачи.

    Если задача удалена, бот уведомляет пользователя, иначе восстанавливает клавиатуру.
    """
    telegram_id = callback.from_user.id

    # Извлекаем сохраненные значения для восстановления клавиатуры
    current_task_number = fsm.get_data(telegram_id, key="current_task_number")
    last_task_number = fsm.get_data(telegram_id, key="last_task_number")

    if callback.data == "confirm":
        task_id = fsm.get_data(telegram_id, key="task_id_to_delete")
        TaskDAO.delete_task(telegram_id=telegram_id, task_id=task_id)
        fsm.set_state(telegram_id=telegram_id, state=base_states.IN_MENU)
        await callback.message.answer(
            text=task_responses.TASK_SUCCESSFULLY_DELETED, reply_markup=get_menu_markup()
        )
    else:
        fsm.set_state(telegram_id=telegram_id, state=task_states.LOOK_AT_TASKS)
        await callback.message.answer(
            "Удаление отменено.",
            reply_markup=get_task_manager_markup(current_task_number, last_task_number)
        )

    await callback.answer()
# ------------------- endregion Просмотр задач -------------------
