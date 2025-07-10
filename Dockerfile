FROM python:3.12-alpine

# Создаём рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем библиотеку requests
RUN pip install -r requirements.txt

# Запускаем скрипт
CMD ["python3", "bot.py"]