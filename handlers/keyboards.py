from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .database import parse_time

builder1 = InlineKeyboardBuilder()

builder1.row(InlineKeyboardButton(text='🆕 Создать привычку', callback_data='create'))
builder1.row(InlineKeyboardButton(text='📊 Мои привычки', callback_data='get'))
builder1.row(InlineKeyboardButton(text='🏆 Статистика', callback_data='stats'))
builder1.row(InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings'))


def get_start_message(name: str) -> str:
    message = f'👋 Привет, {name}! Я твой персональный тренер привычек\nПомогу сформировать полезные ритуалы через микрошаги и игровые механики.\nВыбери действие:'
    return message


start_keyboard = builder1.as_markup()

menu_button = InlineKeyboardButton(text='🔙Вернуться в меню', callback_data='menu')
builder2 = InlineKeyboardBuilder()
builder2.row(menu_button)
menu_keyboard = builder2.as_markup()

builder3 = InlineKeyboardBuilder()
builder3.row(InlineKeyboardButton(text='🌅 Утро (07:00)', callback_data='morning'),
                 InlineKeyboardButton(text='☀️ День (12:00)', callback_data='afternoon'),
                 InlineKeyboardButton(text='🌙 Вечер (19:00)', callback_data='evening'),
             width=1)
time_dict = {'morning': '7:00',
             'afternoon': '12:00',
             'evening': '19:00'}

set_time = builder3.as_markup()

builder4 = InlineKeyboardBuilder()
builder4.row(InlineKeyboardButton(text='✅Все верно', callback_data='accept'), InlineKeyboardButton(text='🔄Создать привычку заново', callback_data='create'), width=1)
accepting_button = builder4.as_markup()

first_time = parse_time(time_dict['morning'])
second_time = parse_time(time_dict['afternoon'])
third_time = parse_time(time_dict['evening'])


def gen_remind_keyboard(habit_id: int):
    builder5 = InlineKeyboardBuilder()
    builder5.row(InlineKeyboardButton(text='✅Выполнено', callback_data=f'done_{habit_id}'))
    return builder5.as_markup()

