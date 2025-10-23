# # Используем официальный slim-образ Python 3.12
# FROM python:3.12-slim
#
# # Устанавливаем зависимости системы
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         gcc \
#         libpq-dev && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*
#
# # Устанавливаем рабочую директорию в контейнере
# WORKDIR /app
#
# # Копируем файл зависимостей в контейнер
# COPY requirements.txt ./
#
# # Устанавливаем зависимости Python
# RUN pip install --no-cache-dir -r requirements.txt
#
# # Копируем исходный код приложения в контейнер
# COPY . .
#
# RUN mkdir -p static media
#
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего проекта
COPY . .

# Создание необходимых директорий
RUN mkdir -p static media

# Установка прав на выполнение для manage.py
RUN chmod +x manage.py

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
