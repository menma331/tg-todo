from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.types import Message, CallbackQuery

from utils import fsm
from dao import UsersDAO
from states import reg_states, base_states
from keyboards.base.reply import get_menu_markup
from responses import registration as registration_responses
from keyboards.registration.inline import get_user_login_markup
from keyboards.base.inline import get_confirmation_keyboard_markup

registration_router = Router()

# -------------- region register user name --------------
@registration_router.message(
    F.content_type == "text",
    lambda message: fsm.get_state(message.from_user.id) == reg_states.WAIT_FOR_NAME,
)
async def handle_user_name(message: Message) -> None:
    """Обработчик для ввода имени пользователя."""
    if not message.text.strip():
        await message.answer(registration_responses.INVALID_NAME)
        return

    text_for_answer = f"Отлично! Вы уверены в имени <b>{message.text}</b>?"
    telegram_id = message.from_user.id
    fsm.set_state(telegram_id=telegram_id, state=reg_states.SUBMIT_NAME)
    fsm.set_data(telegram_id=telegram_id, key="user_name", value=message.text)
    await message.answer(
        text=text_for_answer,
        reply_markup=get_confirmation_keyboard_markup(),
    )


@registration_router.callback_query(
    F.data.in_(["confirm", "cancel"]),
    lambda callback: fsm.get_state(callback.from_user.id) == reg_states.SUBMIT_NAME,
)
async def handle_confirm_user_name(callback: CallbackQuery) -> None:
    """Обработчик подтверждения или отмены имени пользователя."""
    telegram_id = callback.from_user.id

    if callback.data == "confirm":
        fsm.set_state(telegram_id=telegram_id, state=reg_states.WAIT_FOR_LOGIN)
        await callback.message.answer(
            text=registration_responses.REQUEST_FOR_USER_LOGIN,
            reply_markup=get_user_login_markup(),
        )
    else:
        fsm.set_state(telegram_id=telegram_id, state=reg_states.WAIT_FOR_NAME)
        await callback.message.answer(text=registration_responses.REQUEST_FOR_USER_NAME)

    await callback.answer()


# -------------- endregion register user name --------------


# -------------- region register login --------------
@registration_router.message(
    F.text,
    lambda message: fsm.get_state(message.from_user.id) == reg_states.WAIT_FOR_LOGIN,
)
async def handle_user_login(message: Message) -> None:
    """Обработчик для ввода логина пользователя."""
    login = message.text.strip()
    if not login:
        await message.answer(registration_responses.INVALID_LOGIN)
        return

    user = UsersDAO.get_one_or_none(login=login)
    if user:
        await message.answer(text=registration_responses.LOGIN_ALREADY_EXISTS)
        return

    text_for_answer = f"Хорошо! Вы уверены в логине <b>{login}</b>?"
    telegram_id = message.from_user.id
    fsm.set_state(telegram_id=telegram_id, state=reg_states.SUBMIT_LOGIN)
    fsm.set_data(telegram_id=telegram_id, key="login", value=login)
    await message.answer(
        text=text_for_answer,
        reply_markup=get_confirmation_keyboard_markup(),
    )


@registration_router.callback_query(
    F.data == "use_login_from_telegram",
    lambda callback: fsm.get_state(callback.from_user.id) == reg_states.WAIT_FOR_LOGIN,
)
async def handle_getting_login_from_telegram(callback: CallbackQuery) -> None:
    """Обработчик для использования логина из Telegram."""
    login = callback.from_user.username or f"user_{callback.from_user.id}"
    await callback.message.answer(
        text=f"Вы уверены в логине <b>{login}</b>?",
        reply_markup=get_confirmation_keyboard_markup(),
    )
    fsm.set_state(callback.from_user.id, reg_states.SUBMIT_LOGIN)
    fsm.set_data(telegram_id=callback.from_user.id, key="login", value=login)
    await callback.answer()


@registration_router.callback_query(
    F.data.in_(["confirm", "cancel"]),
    lambda callback: fsm.get_state(callback.from_user.id) == reg_states.SUBMIT_LOGIN,
)
async def handle_confirmation_login(callback: CallbackQuery) -> None:
    """Обработчик подтверждения или отмены логина пользователя."""
    telegram_id = callback.from_user.id

    if callback.data == "confirm":
        fsm.set_state(telegram_id=telegram_id, state=base_states.DEFAULT)
        user_data = fsm.get_data(telegram_id=telegram_id)
        user_data["telegram_id"] = telegram_id
        UsersDAO.add_new_user(data=user_data)
        fsm.set_state(telegram_id=telegram_id, state=base_states.IN_MENU)
        await callback.message.answer(
            text=registration_responses.SUCCESSFULLY_REGISTERED,
            reply_markup=get_menu_markup(),
        )
    else:
        fsm.set_state(telegram_id=telegram_id, state=reg_states.WAIT_FOR_LOGIN)
        await callback.message.answer(
            text=registration_responses.REQUEST_FOR_USER_LOGIN,
            reply_markup=get_user_login_markup(),
        )

    await callback.answer()


# -------------- endregion register login --------------
