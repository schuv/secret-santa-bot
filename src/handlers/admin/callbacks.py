from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import (
    F,
    Router
)

from config import Config
from states import AdminPanel
from database.methods import User
from methods.messages import text_replace
from handlers.admin.messages import send_panel_message
from keyboard import (
    create_markup,
    create_button
)


router = Router()


@router.callback_query(F.data == "RECEIVE_CODE")
async def receive_code_callback_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Receive code callback handler

    :param callback: Telegram callback
    :param state: User's state
    """

    await state.set_state(AdminPanel.enter_code)
    await callback.message.edit_text(
        Config.TEXTS["admin"]["panel"]["enter_code"],
        reply_markup=create_markup(
            [
                create_button(
                    Config.TEXTS["keyboard"]["back"],
                    "ADMIN_PANEL"
                )
            ]
        )
    )


@router.callback_query(F.data[:18] == "ADMIN_USER_DELETE_")
async def delete_user_callback_handler(callback: CallbackQuery) -> None:
    """
    Delete answer callback handler

    :param message: Telegram message
    """

    user = await User(user_id=callback.data[18:]).get()

    if user is None:
        return

    await User(user_id=user.user_id).update(verified=False)
    await callback.answer(
        Config.TEXTS["admin"]["panel"]["user_deleted"],
        True
    )
    await callback.message.delete()


@router.callback_query(F.data[:20] == "ADMIN_DELETE_ANSWER_")
async def delete_answer_callback_handler(callback: CallbackQuery) -> None:
    """
    Delete answer callback handler

    :param message: Telegram message
    """

    user = await User(user_id=callback.data[20:]).get()

    if user is None:
        return

    await User(user_id=user.user_id).update(preferences="None")
    await callback.message.edit_text(
        text_replace(
            Config.TEXTS["admin"]["panel"]["user_answer_deleted"],
            full_name=f"{user.first_name} {user.last_name}"
        )
    )


@router.callback_query(AdminPanel.enter_code, F.data == "ADMIN_PANEL")
@router.callback_query(F.data == "ADMIN_PANEL")
async def admin_callback_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Admin callback handler

    :param callback: Telegram callback
    """

    if str(callback.from_user.id) not in Config.ALL_ADMINS:
        return

    await state.set_state(AdminPanel)
    await send_panel_message(callback.message, True)
