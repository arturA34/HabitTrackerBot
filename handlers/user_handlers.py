from aiogram import Router, Bot, F, Dispatcher
from aiogram.types import Message
from aiogram.types import ChatMemberUpdated, Chat, CallbackQuery
from aiogram.filters import ChatMemberUpdatedFilter, Command, StateFilter
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters.chat_member_updated import IS_NOT_MEMBER, ADMINISTRATOR
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from dataclasses import dataclass
from aiogram.exceptions import TelegramBadRequest
from asyncpg import Pool
from asyncpg.pool import PoolAcquireContext
from .database import (add_user, add_habit, parse_time, show_habits, get_all_habits,
                       add_complete, show_complete)
from .keyboards import (start_keyboard, menu_keyboard, get_start_message,
                        set_time, time_dict, accepting_button, gen_remind_keyboard)
from random import choice


router = Router()

async def remind_habit(bot: Bot, pool: Pool, time):
    all_habits = await get_all_habits(pool=pool, time=time)
    for habit in all_habits:
        await bot.send_message(chat_id=habit['user_telegram_id'], text=f'🔔Напоминание:\n{habit['name']}', reply_markup=gen_remind_keyboard(habit['id']))


class FSM_habit(StatesGroup):
    wait_name = State()
    wait_time = State()
    accepting = State()


@dataclass
class Habit:
    name: str
    time: str



# Получаем dp_pool из workflow_data, который добавили в точке входа

@router.message(Command(commands='start'))
async def process_start(message: Message, dp_pool: Pool):
    await add_user(pool=dp_pool, user_id=message.from_user.id, user_name=message.from_user.first_name)
    await message.answer(get_start_message(message.from_user.first_name),
                         reply_markup=start_keyboard)



@router.callback_query(F.data == 'create')
async def create_new_habit(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(FSM_habit.wait_name)
        last_message = await callback.message.edit_text(text='✍️Введи название привычки (например, "Пить воду утром"):',
                                        reply_markup=menu_keyboard)
        await state.update_data(last_message_id=last_message.message_id)
    except TelegramBadRequest:
        await callback.answer()


@router.message(StateFilter(FSM_habit.wait_name))
async def add_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(habit_name=message.text.capitalize())
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get('last_message_id'))
    await state.set_state(FSM_habit.wait_time)
    await message.answer(text='🕓Теперь выбери время для этой привычки:', reply_markup=set_time)


@router.callback_query(StateFilter(FSM_habit.wait_time))
async def add_time(callback: CallbackQuery, state: FSMContext):
    await state.update_data(time=time_dict[callback.data])
    data = await state.get_data()
    await state.set_state(FSM_habit.accepting)
    await callback.message.edit_text(text=f'📝Твоя новая привычка:\n'
                                          f'Название: {data['habit_name']}\n'
                                          f'Время напоминания: {data['time']}', reply_markup=accepting_button)

@router.callback_query(StateFilter(FSM_habit.accepting))
async def accept(callback: CallbackQuery, state: FSMContext, dp_pool: Pool):
    data = await state.get_data()
    await state.clear()
    await add_habit(pool=dp_pool, user_id=callback.from_user.id, name=data['habit_name'], time=parse_time(data['time']))
    await callback.message.edit_text(text='Записал!\nТеперь каждый день ты будешь получать уведомление об этой привычке', reply_markup=menu_keyboard)

@router.callback_query(F.data == 'menu')
async def menu(callback: CallbackQuery):
    try:
        await callback.message.edit_text(get_start_message(callback.from_user.first_name),
                         reply_markup=start_keyboard)
    except TelegramBadRequest:
        await callback.answer()

@router.callback_query(F.data == 'get')
async def process_get(callback: CallbackQuery, dp_pool: Pool):
    habits = await show_habits(pool=dp_pool, user_id=callback.from_user.id)
    if habits:
        ans_str = 'Вот список твоих привычек:\n'
        i = 1
        for habit in habits:
            ans_str += (f'{i}) {habit['name']} - Напоминание в {habit['reminder_time']}\n')
        await callback.message.edit_text(text=ans_str, reply_markup=menu_keyboard)
    else:
        await callback.answer(text='У тебя еще нет ни одной привычки!\nЧтобы создать привычку, выбери в меню "Создать привычку"', show_alert=True)

@router.callback_query(F.data == 'stats')
async def show_stats(callback: CallbackQuery, dp_pool: Pool):
    id_list = []
    habits = await show_habits(user_id=callback.from_user.id, pool=dp_pool)
    for habit in habits:
        id_list.append(habit['id'])
    complete = await show_complete(pool=dp_pool, habit_ids=id_list)
    data = {}
    for habit in complete:
        data[habit['name']] = data.get(habit['name'], 0) + 1
    ans = 'Вот твоя статистика выполнения привычек:\n'
    for name, count in data.items():
        ans += f'{name} - {count} раз\n'
    await callback.message.edit_text(text=ans, reply_markup=menu_keyboard)

    #await callback.message.edit_text(text='Вот статистика выполнения привычек:\n', reply_markup=menu_keyboard)

@router.callback_query(F.data == 'settings')
async def settings(callback: CallbackQuery):
    await callback.message.edit_text(text='Тут будут настройки бота', reply_markup=menu_keyboard)

responses = (
    "Есть! 💪",
    "Круто! ✅",
    "В копилочку! ✨",
    "Засчитано! 🚀",
    "Так! ⚡️",
    "Супер! 🔥"
)


@router.callback_query(F.data[0:5] == 'done_')
async def process_done(callback: CallbackQuery, dp_pool: Pool):
    await add_complete(pool=dp_pool, habit_id=int(callback.data[5:]))
    await callback.message.edit_text(text=choice(responses), reply_markup=menu_keyboard)