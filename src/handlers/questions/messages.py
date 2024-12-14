import time
import json
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from config import Config
from states import Questions
from database.methods import User
from methods.messages import (
    text_replace,
    md_replace_text
)
from keyboard import (
    create_markup,
    create_button
)


router = Router()


@router.message(Questions.steps)
async def messages_handler(message: Message, state: FSMContext) -> None:
    """
    All the messages handler

    :param message: Telegram message
    :param state: User's state
    """

    if not message.text:
        await message.answer(
            Config.TEXTS["errors"]["no_message"],
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

    if len(message.text) > Config.TEXT_LIMIT:
        await message.answer(
            text_replace(
                Config.TEXTS["errors"]["text_too_much"],
                count=Config.TEXT_LIMIT
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
        return

    await state.set_state(Questions.loading)

    current_data = await state.get_data()

    if current_data is None:
        await state.clear()
        return

    topic = Config.QUESTIONS_TOPICS[current_data["step"]]
    current_data["results"][topic] = message.text

    if current_data["step"] + 1 >= len(Config.QUESTIONS_TOPICS):
        if Config.RELEASE_ABOUT_TIMESTAMP <= round(time.time()):
            await state.clear()
            await message.answer(
                Config.TEXTS["errors"]["time_ended"],
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

        await User(user_id=message.chat.id).update(
            preferences=json.dumps(
                current_data["results"],
                ensure_ascii=False
            )
        )
        await state.clear()
        await message.answer(
            Config.TEXTS["questions"]["finish"],
            reply_markup=create_markup(
                [
                    create_button(
                        Config.TEXTS["keyboard"]["to_menu"],
                        "BACK"
                    )
                ]
            )
        )

        report_text = []

        for title in current_data["results"]:
            report_text.append(
                f"*{Config.ALL_QUESTIONS[title]['question']} "
                f"\\({Config.ALL_QUESTIONS[title]['name']}\\)*: "
                f"{md_replace_text(current_data['results'][title])}"
            )

        for admin in Config.HOST_ADMINS_ID:
            try:
                await message.bot.send_message(
                    admin,
                    text_replace(
                        Config.TEXTS["admin"]["panel"]["questions_report"],
                        full_name=message.chat.full_name,
                        report_text="\n".join(report_text)
                    ),
                    reply_markup=create_markup(
                        [
                            create_button(
                                f"{Config.TEXTS['keyboard']['delete_answer']}",
                                f"ADMIN_DELETE_ANSWER_{message.chat.id}"
                            )
                        ],
                        [
                            create_button(
                                f"{Config.TEXTS['keyboard']['delete_user']}",
                                f"ADMIN_USER_DELETE_{message.chat.id}"
                            )
                        ]
                    )
                )
            except TelegramBadRequest:
                continue
        return

    current_data["step"] += 1

    await state.set_data(current_data)
    await state.set_state(Questions.steps)

    topic = Config.QUESTIONS_TOPICS[current_data["step"]]

    await message.answer(
        text_replace(
            Config.TEXTS["questions"]["step_transit"],
            current_index=current_data["step"] + 1,
            all_count=len(Config.QUESTIONS_TOPICS),
            question=Config.ALL_QUESTIONS[topic]["question"]
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
