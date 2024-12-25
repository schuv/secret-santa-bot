import asyncio
from loguru import logger
from datetime import datetime
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import default_state
from aiogram.enums.parse_mode import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import (
    F,
    Bot,
    Dispatcher
)

from config import Config
from database.methods import User
from methods.crons import (
    send_quick_reminder,
    create_santa_results
)
from methods.messages import (
    text_replace,
    md_replace_text
)
from keyboard import (
    create_markup,
    create_button
)
from handlers import (
    menu,
    admin,
    questions
)


dp = Dispatcher()


@dp.message(default_state, CommandStart())
async def start_message_handler(message: Message) -> None:
    """
    Start message handler

    :param message: Telegram message
    """

    user_created = await User(message.from_user).add()

    if not isinstance(user_created, str) and user_created.verified is None:
        await message.answer(Config.TEXTS["verification"]["start"])

        for admin_user in Config.ADMINS_ID:
            try:
                await message.bot.send_message(
                    admin_user,
                    text_replace(
                        Config.TEXTS["admin"]["verification_request"],
                        user_id=message.chat.id,
                        full_name=f"{md_replace_text(message.chat.full_name)}",
                        username=f"{md_replace_text(message.chat.username)}"
                    ),
                    reply_markup=create_markup(
                        [
                            create_button(
                                Config.TEXTS["keyboard"]["admin_accept"],
                                f"ADMIN_ACCCEPT_{message.chat.id}"
                            ),
                            create_button(
                                Config.TEXTS["keyboard"]["admin_decline"],
                                f"ADMIN_DECLINE_{message.chat.id}"
                            )
                        ]
                    )
                )
            except TelegramBadRequest:
                continue
        return

    await menu.messages.send_menu_message(message)


@dp.startup()
async def startup_handler(bot: Bot) -> None:
    """
    Start event handler

    :param bot: Current bot instance
    """

    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(
        create_santa_results,
        "date",
        args=(bot, ),
        run_date=datetime.fromtimestamp(Config.RELEASE_TIMESTAMP)
    )
    scheduler.add_job(
        send_quick_reminder,
        "date",
        args=(bot, ),
        run_date=datetime.fromtimestamp(Config.GIFT_REMINDER_TIMESTAMP)
    )

    logger.info("Bot started")
    logger.info(f"SECRET_HASH is {Config.SECRET_HASH}")
    logger.info(f"SECRET_FACTOR is {Config.SECRET_FACTOR}")


async def main() -> None:
    """
    Entry point
    """

    await User.update_users()

    dp.include_router(menu.router)
    dp.include_router(admin.router)
    dp.include_router(questions.router)

    dp.message.filter(F.chat.type == "private")

    await dp.start_polling(
        Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.MARKDOWN_V2,
                link_preview_is_disabled=True
            )
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
