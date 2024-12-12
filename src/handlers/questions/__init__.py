from aiogram import Router

from handlers.questions import messages


router = Router()
router.include_router(messages.router)
