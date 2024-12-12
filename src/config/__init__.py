import os
import json
import random
from loguru import logger
from dotenv import (
    load_dotenv,
    find_dotenv
)


load_dotenv(find_dotenv(".env"), override=True)

logger.add(
    sink="./logs/info.log",
    level="INFO",
    rotation="1 MB",
    format="[{time}][{level}]: {message} (line: {line})",
    compression="zip",
    delay=True,
    catch=True
)


class Cache:
    VERIFIED: list = []


class Config:
    DB_URL: str = os.environ["DB_URL"]
    BOT_TOKEN: str = os.environ["BOT_TOKEN"]
    TEXTS: dict = json.load(open("config/texts.json", "r", encoding="UTF-8"))

    RELEASE_TIMESTAMP: int = int(os.environ["RELEASE_TIMESTAMP"])
    RELEASE_ABOUT_TIMESTAMP: int = RELEASE_TIMESTAMP - 3600
    GIFT_BUY_UNTIL: int = int(os.environ["GIFT_BUY_UNTIL"])

    SECRET_HASH: int = random.randint(1000, 100000)
    SECRET_FACTOR: int = random.randint(100, 900)
    ADMINS_ID: list = os.environ["ADMINS_ID"].split()
    HOST_ADMINS_ID: list = os.environ["HOST_ADMINS_ID"].split()
    ALL_ADMINS: list = ADMINS_ID + HOST_ADMINS_ID

    TEXT_LIMIT: int = 500

    ALL_QUESTIONS: dict = json.load(
        open("config/questions.json", "r", encoding="UTF-8")
    )
    QUESTIONS_TOPICS: list = list(ALL_QUESTIONS.keys())
