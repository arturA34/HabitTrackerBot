from aiogram import Bot, Dispatcher
from handlers import user_handlers, other_handlers
from config import Config, load_conf
import asyncio
import asyncpg
from HabitTrackerBot.handlers.database import create_table
from handlers.user_handlers import remind_habit
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.keyboards import first_time, second_time, third_time


async def main():

    # Получаем всю информацию для запуска бота в объект класса Config

    config: Config = load_conf()

    # Инициализируем Bot и Dispatcher

    bot = Bot(token=config.tgbot.token)
    dp = Dispatcher()

    # Открываем пул соединений с базой данных

    pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            database=config.db.name,
            host=config.db.host,
            min_size=1,
            max_size=10
    )

    # Инициализируем scheduler и добавляем задачи под каждое время

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()

    scheduler.add_job(
        func=remind_habit,
        trigger='cron',
        hour=7,
        minute=0,
        args=(bot, pool, first_time)
    )

    scheduler.add_job(
        func=remind_habit,
        trigger='cron',
        hour=12,
        minute=0,
        args=(bot, pool, second_time)
    )

    scheduler.add_job(
        func=remind_habit,
        trigger='cron',
        hour=19,
        minute=0,
        args=(bot, pool, third_time)
    )
    # Отправляем в хранилище пул соединений, чтобы взаимодействовать с ним в хэндлерах

    dp.workflow_data.update(dp_pool=pool)

    # Создаем таблицы в базе данных, если она еще не создана

    await create_table(pool=pool)

    # Подключаем роутеры из модулей

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # Запускаем бота

    try:
        await dp.start_polling(bot)
    finally:
        await pool.close()

if __name__ == '__main__':
    asyncio.run(main())
