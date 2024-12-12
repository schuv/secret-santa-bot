from aiogram.fsm.state import (
    State,
    StatesGroup
)


class Questions(StatesGroup):
    """
    States for questions
    """

    steps: State = State()
    loading: State = State()


class AdminPanel(StatesGroup):
    """
    States for admin panel
    """

    panel: State = State()
    enter_code: State = State()
