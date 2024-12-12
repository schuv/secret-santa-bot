from aiogram import Router

from handlers.menu import (
    messages,
    callbacks
)


router = Router()
router.include_router(messages.router)
router.include_router(callbacks.router)
