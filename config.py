from dataclasses import dataclass
from environs import Env



@dataclass
class TgBot:
    token: str

@dataclass
class DataBase:
    host: str
    user: str
    password: str
    name: str


@dataclass
class Config:
    tgbot: TgBot
    db: DataBase

def load_conf(path=None):
    env = Env()
    env.read_env(path=path)
    return Config(tgbot=TgBot(token=env('BOT_TOKEN')),
                  db=DataBase(host=env('HOST'),
                              user=env('USER'),
                              password=env('PASSWORD'),
                              name=env('NAME')))

print('Конфигурация прошла успешно, бот запущен!')