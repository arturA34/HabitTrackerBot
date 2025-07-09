import asyncio

from asyncpg import Pool
from datetime import datetime, date


async def add_user(pool: Pool, user_id: int, user_name: str, timezone: str = 'MSK'):
    sql = '''
    INSERT INTO users(id, name, timezone)
    VALUES ($1, $2, $3)
    ON CONFLICT (id) DO NOTHING;'''
    async with pool.acquire() as con:
        await con.execute(sql, user_id, user_name, timezone)


async def add_habit(pool: Pool, user_id: int, name: str, time: str):
    sql = '''
    INSERT INTO habits(user_telegram_id, name, reminder_time)
    VALUES ($1, $2, $3)
    '''
    async with pool.acquire() as con:
        await con.execute(sql, user_id, name, time)


def parse_time(time_str: str):
    parsed = datetime.strptime(time_str, "%H:%M")
    return parsed.time()


async def create_table(pool: Pool):
    async with pool.acquire() as con:
        await con.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id bigint PRIMARY KEY,
                        name VARCHAR(20) NOT NULL,
                        timezone VARCHAR(50)
                    );
                    CREATE TABLE IF NOT EXISTS  habits (
                        id SERIAL PRIMARY KEY,
                        user_telegram_id bigint NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        reminder_time TIME NOT NULL,
                        FOREIGN KEY (user_telegram_id) REFERENCES users(id) ON DELETE CASCADE
                    );
                    CREATE TABLE IF NOT EXISTS completions (
                        id SERIAL PRIMARY KEY,
                        habit_id INT NOT NULL,
                        completion_date DATE NOT NULL,
                        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE);
                """)


async def show_habits(pool: Pool, user_id: int):
    async with pool.acquire() as con:
        habits = await con.fetch('''
        SELECT name, reminder_time, id FROM habits
        WHERE user_telegram_id = $1
        ''', user_id)
    return habits


async def get_all_habits(pool: Pool, time: datetime):
    async with pool.acquire() as con:
        all_habits = await con.fetch('''
        SELECT * FROM habits
        WHERE reminder_time = $1
        ''', time)
    return all_habits

async def add_complete(pool: Pool, habit_id: int):
    date_now = date.today()
    async with pool.acquire() as con:
        await con.execute('''
        INSERT INTO completions(habit_id, completion_date)
        VALUES ($1, $2)
        ''', habit_id, date_now)

async def show_complete(pool: Pool, habit_ids: list):
    if not habit_ids:
        return []
    async with pool.acquire() as con:
        complete_habits = await con.fetch('''
        SELECT
                completions.*,
                habits.name
            FROM
                completions
            JOIN
                habits ON completions.habit_id = habits.id
            WHERE
                completions.habit_id = ANY($1)
        ''', habit_ids)
    return complete_habits
