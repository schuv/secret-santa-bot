from typing import Any
from config import Config
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(Config.DB_URL)
session = sessionmaker(bind=engine, autoflush=False)

logger.info("Connecting to database")
engine.connect()


def db_commit(db_session, to_add: Any = None) -> str:
    """
    Commit database things

    :param db_session: Current DB session
    :param to_add: Insert this object
    :return: None on success
    """

    if to_add is not None:
        try:
            db_session.add(to_add)
            db_session.commit()
            db_session.refresh(to_add)
        except Exception as e:
            logger.warning(f"Error while adding object: {e}")
            db_session.rollback()
            return "Error while adding new setting"

        return

    try:
        db_session.commit()
    except Exception as e:
        logger.warning(f"Error while commiting: {e}")
        db_session.rollback()
        return "Error while commiting"
