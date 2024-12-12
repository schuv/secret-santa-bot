import functools
from aiogram import BaseMiddleware

from config import (
    Cache,
    Config
)
from database.methods import User


class Verification(BaseMiddleware):
    """
    Verification middleware
    """

    @staticmethod
    def check() -> callable:
        """
        Decorator to check whether user verified or not.

        Decorated function needs to have some class with ```from_user.id```
        (it could be ```CallbackQuery```, ```Message```, etc)
        and ```Bot``` instance in kwargs

        :return: wrapper function
        """

        def wrapper(func):
            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                if args[0].from_user.is_bot:
                    return

                if args[0].from_user.id not in Cache.VERIFIED:
                    user = await User(args[0].from_user).get()

                    if user is None:
                        await args[0].answer(
                            Config.TEXTS["errors"]["send_start"]
                        )
                        return

                    if user.verified is None:
                        await args[0].answer(
                            Config.TEXTS["verification"]["default"]
                        )
                        return

                    if not user.verified:
                        await args[0].answer(
                            Config.TEXTS["verification"]["decline"]
                        )
                        return

                return await func(*args, **kwargs)
            return wrapped
        return wrapper
