from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def answer_to_any_message(message: Message):
    await message.answer('Я не понимаю тебя, пожалуйста, вернись в меню и пользуйся кнопками!\n'
                         '/start - Вернуться в меню')
