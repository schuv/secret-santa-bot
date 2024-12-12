import time
from loguru import logger
from aiogram.types import User as TelegramUser

from database.models import UserModel
from config import (
    Cache,
    Config
)
from database import (
    session,
    db_commit
)


class User:
    user_id: int = None
    user: TelegramUser = None
    interal_id: int = None

    def __init__(
        self,
        user: TelegramUser = None,
        user_id: int = None,
        interal_id: int = None
    ) -> None:
        """
        User class initialization

        :param user: Telegram User data
        :param user_id: Telegram User ID
        :param interal_id: ID from the DB

        Must be at least one argument
        """

        if user_id:
            self.user_id = int(user_id)

        if user and not user.is_bot:
            self.user = user
            self.user_id = int(user.id)

        if interal_id:
            self.interal_id = int(interal_id)

    async def _check_data(self, query: UserModel) -> None:
        """
        Checks Telegram user data if there is so

        :param query: Current User's DB
        """

        if self.user is None or query is None:
            return

        username = None
        first_name = None
        last_name = None

        if self.user.username != query.username:
            username = self.user.username

        if self.user.first_name != query.first_name:
            first_name = self.user.first_name

        if self.user.last_name != query.last_name:
            last_name = self.user.last_name

        await self.update(
            username=username,
            first_name=first_name,
            last_name=last_name
        )

    @staticmethod
    async def update_users() -> None:
        """
        Update users in cache
        """

        logger.info("Updating users")

        users = await User.get_users()

        for user in users:
            if user.verified and user.user_id not in Cache.VERIFIED:
                Cache.VERIFIED.append(user.user_id)

    async def update(
        self,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        preferences: str = None,
        verified: bool = None,
        gift_delivered: bool = None,
        user_for_gift_id: bool = None
    ) -> str:
        """
        Update User's data. Provide at least one argument

        :param username: User's new username Optional
        :param first_name: User's new first name Optional
        :param last_name: User's new last name Optional
        :param preferences: User's new preferences Optional
        :param verified: Wether user verified or not Optional
        :param gift_delivered: Wether user delivered gift or not Optional
        :param user_for_gift_id: User's new gift ID Optional
        :return: None on success
        """

        to_update = {}

        if username is not None:
            to_update["username"] = username

        if preferences is not None or preferences == "None":
            to_update["preferences"] = (
                None if preferences == "None" else preferences
            )

        if verified is not None:
            to_update["verified"] = verified

            if verified:
                if self.user_id not in Cache.VERIFIED:
                    Cache.VERIFIED.append(self.user_id)
            else:
                if self.user_id in Cache.VERIFIED:
                    Cache.VERIFIED.remove(self.user_id)

        if user_for_gift_id is not None:
            to_update["user_for_gift_id"] = user_for_gift_id

        if first_name is not None:
            to_update["first_name"] = first_name

        if gift_delivered is not None:
            to_update["gift_delivered"] = gift_delivered

        if last_name is not None:
            to_update["last_name"] = last_name

        if len(to_update) <= 0:
            return

        with session() as db:
            logger.info(f"Updating {self.user_id}")

            db.query(UserModel).filter(
                UserModel.user_id == self.user_id
            ).update(to_update)

            return db_commit(db)

    async def get(self, recheck=True, **kwargs) -> UserModel:
        """
        Get User's information

        :param recheck: Wether data should be rechecked. Optional
        :param kwargs: Search parameters
        :return: User model or None
        """

        with session() as db:
            if self.user_id:
                result = db.query(UserModel).filter(
                    UserModel.user_id == self.user_id
                ).filter_by(**kwargs).one_or_none()
            elif self.interal_id:
                result = db.query(UserModel).filter(
                    UserModel.id == self.interal_id
                ).filter_by(**kwargs).one_or_none()

            if recheck:
                await self._check_data(result)

            return result

    async def add(self) -> UserModel:
        """
        Add user to DB

        :param bot: Current bot instance
        :return: Created user model on success
        """

        is_exists = await self.get()

        if is_exists is not None:
            logger.warning(f"[{is_exists.user_id}] User already exist")
            return "User already exist"

        if self.user is None:
            logger.warning("No Telegram data in user provided")
            return "No Telegram data in user provided"

        if self.user.language_code is None:
            logger.warning("No language_code in user provided")
            return "No language_code in user provided"

        with session() as db:
            logger.info(f"New user: {self.user_id}")

            user_model = UserModel(
                user_id=self.user.id,
                first_name=self.user.first_name,
                last_name=self.user.last_name,
                username=self.user.username,
                verified=(str(self.user.id) in Config.ALL_ADMINS) or None,
                timestamp=round(time.time())
            )

            db_commit(db, user_model)
            return user_model

    @staticmethod
    async def get_users(**kwargs) -> list[UserModel]:
        """
        Get all the users in the bot

        :param kwargs: Search parametrs
        :return: List of UserModels
        """

        with session() as db:
            return db.query(UserModel).filter_by(
                **kwargs
            ).order_by(
                UserModel.id
            ).all()
