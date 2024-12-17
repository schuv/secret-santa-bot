import time
from datetime import datetime
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import default_state

from config import Config
from database.methods import User
from methods.check import Verification
from methods.messages import text_replace
from keyboard import (
    create_markup,
    create_button
)


router = Router()


async def send_menu_message(message: Message, edit: bool = False) -> None:
    """
    Send menu message

    :param message: Telegram message
    :param edit: Wether this message should be edited or not. Optional
    """

    user = await User(user_id=message.chat.id).get()

    text = text_replace(
        Config.TEXTS["menu"]["general"],
        id=user.id
    )

    reply_markup = []

    if not user.gift_delivered:
        if user.user_for_gift_id is None \
                and Config.RELEASE_ABOUT_TIMESTAMP > round(time.time()):
            text += text_replace(
                f"\n{Config.TEXTS['menu']['general_date_release']}",
                date=datetime.fromtimestamp(
                    int(Config.RELEASE_TIMESTAMP)
                ).strftime("%d\\.%m %H:%M"),
                date_closed=datetime.fromtimestamp(
                    int(Config.RELEASE_ABOUT_TIMESTAMP)
                ).strftime("%d\\.%m %H:%M")
            )

        if user.preferences is not None:
            if user.user_for_gift_id is not None:
                text += text_replace(
                    f"\n{Config.TEXTS['menu']['general_gift_release']}",
                    date=datetime.fromtimestamp(
                        int(Config.GIFT_BUY_UNTIL)
                    ).strftime("%d\\.%m %H:%M")
                )
                text += f"\n\n{Config.TEXTS['menu']['general_date_released']}"
                reply_markup = [
                    [
                        create_button(
                            Config.TEXTS["keyboard"]["person"],
                            "MY_PERSON"
                        ),
                        create_button(
                            Config.TEXTS["keyboard"]["gift_delivered"],
                            "GIFT_DELIVERED"
                        )
                    ],
                ]
            else:
                text += f"\n\n{Config.TEXTS['menu']['general_data_entered']}"
        else:
            reply_markup.append(
                [
                    create_button(
                        Config.TEXTS["keyboard"]["enter_data"],
                        "ENTER_DATA"
                    )
                ]
            )
    else:
        text += f"\n\n{Config.TEXTS['menu']['general_date_released']}"

    reply_markup.append(
        [
            create_button(
                Config.TEXTS["keyboard"]["help"],
                "HELP"
            )
        ]
    )

    if str(message.chat.id) in Config.HOST_ADMINS_ID:
        reply_markup.append(
            [
                create_button(
                    Config.TEXTS["keyboard"]["adminpanel"],
                    "ADMIN_PANEL"
                )
            ]
        )

    if edit:
        await message.edit_text(
            text,
            reply_markup=create_markup(*reply_markup)
        )
        return

    await message.answer(
        text,
        reply_markup=create_markup(*reply_markup)
    )


async def send_help_message(message: Message, edit: bool = False) -> None:
    """
    Send help message

    :param message: Telegram message
    :param edit: Wether this message should be edited or not. Optional
    """

    if edit:
        await message.edit_text(
            Config.TEXTS["help"],
            reply_markup=create_markup(
                [
                    create_button(
                        Config.TEXTS["keyboard"]["back"],
                        "BACK"
                    )
                ]
            )
        )
        return

    await message.answer(
        Config.TEXTS["help"],
        reply_markup=create_markup(
            [
                create_button(
                    Config.TEXTS["keyboard"]["back"],
                    "BACK"
                )
            ]
        )
    )


@router.message(Command(commands="help"))
@Verification.check()
async def help_command_handler(message: Message) -> None:
    """
    Help command handler

    :param message: Telegram message
    """

    await send_help_message(message)


@router.message(default_state)
@Verification.check()
async def message_handler(message: Message) -> None:
    """
    All the messages handler

    :param message: Telegram message
    """

    await send_menu_message(message)
