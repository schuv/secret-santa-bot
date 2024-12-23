from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import Config
from states import AdminPanel
from database.methods import User
from methods.messages import text_replace
from keyboard import (
    create_markup,
    create_button
)


router = Router()


async def send_panel_message(message: Message, edit: bool = False) -> None:
    """
    Send admin panel message

    :param message: Telegram message
    :param edit: Wether this message should be edited or not. Optional
    """

    reply_markup = create_markup(
        [
            create_button(
                Config.TEXTS["keyboard"]["receive_code"],
                "RECEIVE_CODE"
            )
        ],
        [
            create_button(
                Config.TEXTS["keyboard"]["back"],
                "BACK"
            )
        ]
    )

    if edit:
        await message.edit_text(
            Config.TEXTS["admin"]["panel"]["general"],
            reply_markup=reply_markup
        )
        return

    await message.answer(
        Config.TEXTS["admin"]["panel"]["general"],
        reply_markup=reply_markup
    )


@router.message(AdminPanel.enter_code)
async def enter_code_message_handler(
    message: Message,
    state: FSMContext
) -> None:
    """
    Enter code message handler

    :param message: Telegram message
    """

    try:
        int(message.text)
    except ValueError:
        await message.answer(
            Config.TEXTS["errors"]["no_message_int"],
            reply_markup=create_markup(
                [
                    create_button(
                        Config.TEXTS["keyboard"]["back"],
                        "ADMIN_PANEL"
                    )
                ]
            )
        )
        return

    user_id = int(message.text) / (Config.SECRET_FACTOR + Config.SECRET_HASH)

    if user_id < 1 or user_id % round(user_id) != 0:
        await message.answer(
            Config.TEXTS["errors"]["no_such_code"],
            reply_markup=create_markup(
                [
                    create_button(
                        Config.TEXTS["keyboard"]["back"],
                        "ADMIN_PANEL"
                    )
                ]
            )
        )
        return

    user = await User(
        interal_id=(
            int(message.text) / (Config.SECRET_FACTOR + Config.SECRET_HASH)
        )
    ).get()

    if user is None:
        await message.answer(
            Config.TEXTS["errors"]["no_such_code"],
            reply_markup=create_markup(
                [
                    create_button(
                        Config.TEXTS["keyboard"]["back"],
                        "ADMIN_PANEL"
                    )
                ]
            )
        )
        return

    await User(user_id=user.user_id).update(gift_delivered=True)

    await message.bot.send_message(user.user_id, "😎")
    await message.bot.send_message(
        user.user_id,
        Config.TEXTS["gift_delivery"]["delivered"]
    )

    await message.answer(
        text_replace(
            Config.TEXTS["admin"]["panel"]["code_received"],
            receiver_id=user.user_for_gift_id,
            ss_id=user.id
        )
    )
    await message.answer(
        Config.TEXTS["admin"]["panel"]["back_to_menu"],
        reply_markup=create_markup(
            [
                create_button(
                    Config.TEXTS["keyboard"]["back"],
                    "ADMIN_PANEL"
                )
            ]
        )
    )
    await state.set_state(AdminPanel.panel)


@router.message(AdminPanel.panel)
async def message_handler(message: Message) -> None:
    """
    All the messages handler

    :param message: Telegram message
    """

    await send_panel_message(message)
