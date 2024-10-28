from aiogram import F
from responses import base as base_responses
from aiogram.dispatcher.router import Router
from aiogram.types import Message
from keyboards.base.reply import get_menu_markup
from dao import UsersDAO
from states import reg_states, base_states
from utils import fsm
from responses import registration as registration_responses

base_router = Router()

async def check_user_registration(message: Message) -> bool:
    """Проверка регистрации пользователя и установка данных или состояния в FSM.

    :param message: Сообщение от пользователя.
    :return: True, если пользователь зарегистрирован; иначе False.
    """
    telegram_id = message.from_user.id
    user = UsersDAO.get_one_or_none(telegram_id=telegram_id)

    if user:
        # Сохраняем данные пользователя в FSM для быстрого доступа
        for key, value in user.items():
            fsm.set_data(telegram_id=telegram_id, key=key, value=value)
        fsm.set_state(telegram_id=telegram_id, state=base_states.IN_MENU)
        return True

    # Если пользователь не зарегистрирован, переводим в состояние регистрации
    await message.answer(text=registration_responses.USER_IS_NOT_REGISTERED)
    await message.answer(text=registration_responses.REQUEST_FOR_USER_NAME)
    fsm.set_state(telegram_id=telegram_id, state=reg_states.WAIT_FOR_NAME)
    return False


@base_router.message(F.text == "/start")
async def handle_start_command(message: Message) -> None:
    """Обработчик команды старт."""
    await message.answer(
        text=base_responses.START_MESSAGE,
        disable_web_page_preview=True,
    )

    # Проверяем регистрацию и отправляем меню, если пользователь зарегистрирован
    if await check_user_registration(message):
        await message.answer(
            text=base_responses.CHOOSE_MENU_ITEM, reply_markup=get_menu_markup()
        )


@base_router.message(F.text == "/menu")
async def handle_menu_command(message: Message) -> None:
    """Обработчик команды меню. Если пользователь не зарегистрирован, предложит регистрацию."""
    # Проверяем регистрацию и отправляем меню, если пользователь зарегистрирован
    if await check_user_registration(message):
        await message.answer(
            text=base_responses.CHOOSE_MENU_ITEM, reply_markup=get_menu_markup()
        )
