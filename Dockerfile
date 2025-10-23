# Используем официальный slim-образ Python 3.12
FROM python:3.12-slim

# Устанавливаем зависимости системы
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt ./

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения в контейнер
COPY . .

RUN mkdir -p static media

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# RUN python manage.py collectstatic --noinput
# CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]