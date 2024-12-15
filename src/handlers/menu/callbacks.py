import json
import time
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import (
    F,
    Router
)

from config import Config
from database.methods import User
from handlers.menu import messages
from methods.check import Verification
from states import (
    Questions,
    AdminPanel
)
from methods.messages import (
    text_replace,
    md_replace_text
)
from keyboard import (
    create_markup,
    create_button
)


router = Router()


@router.callback_query(F.data == "HELP")
@Verification.check()
async def help_callback_handler(callback: CallbackQuery) -> None:
    """
    Help callback handler

    :param callback: Telegram callback
    """

    await messages.send_help_message(callback.message, True)


@router.callback_query(F.data == "LETS_GO")
@Verification.check()
async def first_question_callback_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    First question callback handler

    :param callback: Telegram callback
    :param state: User's state
    """

    await state.set_state(Questions.steps)
    await state.set_data(
        {
            "step": 0,
            "results": {}
        }
    )

    await callback.message.edit_text(
        text_replace(
            Config.TEXTS["questions"]["step_transit"],
            current_index=1,
            all_count=len(Config.QUESTIONS_TOPICS),
            question=(
                Config.ALL_QUESTIONS[Config.QUESTIONS_TOPICS[0]]["question"]
            )
        ),
        reply_markup=create_markup(
            [
                create_button(
                    Config.TEXTS["keyboard"]["back"],
                    "BACK"
                )
            ]
        )
    )


@router.callback_query(Questions.steps, F.data == "BACK")
@Verification.check()
@router.callback_query(F.data == "ENTER_DATA")
async def enter_data_callback_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Enter data callback handler

    :param callback: Telegram callback
    :param state: User's state
    """

    await state.clear()

    if callback.data == "ENTER_DATA" and \
            Config.RELEASE_ABOUT_TIMESTAMP <= round(time.time()):
        await callback.answer(Config.TEXTS["errors"]["time_ended"])
        return

    user = await User(callback.from_user).get()

    if user.preferences is not None:
        await callback.answer("😬 Ты уже ввел свои предпочтения")
        await callback.message.delete()
        return

    await callback.message.edit_text(
        text_replace(
            Config.TEXTS["questions"]["initial"],
            questions_count=len(Config.ALL_QUESTIONS)
        ),
        reply_markup=create_markup(
            [
                create_button(
                    Config.TEXTS["keyboard"]["letsgo"],
                    "LETS_GO"
                )
            ],
            [
                create_button(
                    Config.TEXTS["keyboard"]["back"],
                    "BACK"
                )
            ]
        )
    )


@router.callback_query(F.data[:14] == "ADMIN_ACCCEPT_")
@router.callback_query(F.data[:14] == "ADMIN_DECLINE_")
@Verification.check()
async def admin_verification_callback_handler(callback: CallbackQuery) -> None:
    """
    Admin decline callback handler

    :param callback: Telegram callback
    """

    if str(callback.from_user.id) not in Config.ALL_ADMINS:
        return

    user = await User(user_id=callback.data[14:]).get()

    if user is None:
        await callback.answer(
            Config.TEXTS["errors"]["user_not_found"],
            True
        )
        await callback.message.delete()
        return

    text = (
        "verification_declined" if "DECLINE" in callback.data
        else "verification_accepted"
    )

    await callback.message.edit_text(
        text_replace(
            Config.TEXTS["admin"][text],
            full_name=md_replace_text(f"{user.first_name} {user.last_name}")
        ),
        reply_markup=None
    )

    if "ACCCEPT" in callback.data:
        await User(user_id=user.user_id).update(verified=True)

        if user.verified is None:
            await callback.bot.send_message(
                user.user_id,
                Config.TEXTS["verification"]["accepted"],
                reply_markup=create_markup(
                    [
                        create_button(
                            Config.TEXTS["keyboard"]["to_menu"],
                            "BACK"
                        )
                    ]
                )
            )
        return

    await User(user_id=user.user_id).update(verified=False)


@router.callback_query(F.data == "MY_PERSON")
@Verification.check()
async def my_person_callback_handler(callback: CallbackQuery) -> None:
    """
    My person callback handler

    :param callback: Telegram callback
    """

    user = await User(callback.from_user).get()
    prefer_user = await User(interal_id=user.user_for_gift_id).get()

    prefers: dict = json.loads(prefer_user.preferences)
    text = []

    for element in prefers:
        if Config.ALL_QUESTIONS.get(element) is None:
            continue

        text.append(
            f"*{md_replace_text(Config.ALL_QUESTIONS[element]['name'])}*: "
            f"`{md_replace_text(prefers[element])}`"
        )

    await callback.message.edit_text(
        text_replace(
            Config.TEXTS["my_person"]["general"],
            preferences_text="\n\n".join(text)
        ),
        reply_markup=create_markup(
            [
                create_button(
                    Config.TEXTS["keyboard"]["back"],
                    "BACK"
                )
            ]
        )
    )


@router.callback_query(F.data == "GIFT_DELIVERED")
@Verification.check()
async def gift_delivered_callback_handler(callback: CallbackQuery) -> None:
    """
    Gift delivered callback handler

    :param callback: Telegram callback
    """

    user = await User(user_id=callback.from_user.id).get()

    await callback.message.edit_text(
        text_replace(
            Config.TEXTS["gift_delivery"]["general"],
            code=user.id * (Config.SECRET_HASH + Config.SECRET_FACTOR)
        ),
        reply_markup=create_markup(
            [
                create_button(
                    Config.TEXTS["keyboard"]["back"],
                    "BACK"
                )
            ]
        )
    )


@router.callback_query(F.data == "BACK")
@router.callback_query(AdminPanel.panel, F.data == "BACK")
@Verification.check()
async def back_callback_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Back button callback handler

    :param callback: Telegram callback
    :param state: User's state
    """

    await state.clear()
    await messages.send_menu_message(callback.message, True)
