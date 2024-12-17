import random
from aiogram import Bot
from datetime import datetime

from config import Config
from database.methods import User
from methods.messages import text_replace
from keyboard import (
    create_markup,
    create_button
)


async def create_santa_results(bot: Bot) -> None:
    """
    Creates Santa results

    :param bot: Current bot instance
    """

    users = await User.get_users()
    participants = []
    result = {}

    for user in users:
        if user.preferences is not None and user.verified \
                and user.user_for_gift_id is None:
            participants.append(user.id)

    participants = random.sample(participants, len(participants))

    for participant in range(0, len(participants)):
        try:
            result[participants[participant]] = participants[participant + 1]
        except IndexError:
            result[participants[participant]] = participants[0]

    for user in result:
        user_data = await User(interal_id=user).get()

        await User(user_id=user_data.user_id).update(
            user_for_gift_id=result[user]
        )
        await bot.send_message(user_data.user_id, "🎅")
        await bot.send_message(
            user_data.user_id,
            text_replace(
                Config.TEXTS["results"]["general"],
                date=datetime.fromtimestamp(
                    int(Config.GIFT_BUY_UNTIL)
                ).strftime("%d\\.%m %H:%M")
            ),
            reply_markup=create_markup(
                [
                    create_button(
                        Config.TEXTS["keyboard"]["person"],
                        "MY_PERSON"
                    )
                ]
            )
        )
