from celery import shared_task
from django.utils import timezone

# from datetime import datetime, time, timedelta
from habits_tracker.models import Habit
from habits_tracker.services import send_telegram_message


@shared_task
def send_reminder_message():
    """Отправка напоминания о выполнении привычки в Телеграм"""
    now = timezone.now()
    current_time = now.time()  # Текущее время
    current_date = now.date()  # Текущая дата

    # Получаем все привычки пользователей, имеющих связанные с ними чаты в Телеграме
    habits = Habit.objects.filter(user__tg_chat_id__isnull=False)

    for habit in habits:
        # Проверяем, нужно ли отправлять напоминание для этой привычки сегодня
        if should_send_reminder(habit, current_date, current_time):
            message = f"Напоминание! Я буду {habit.action} в {habit.time.strftime('%H:%M')} в(на) {habit.place}"
            send_telegram_message(habit.user.tg_chat_id, message)


def should_send_reminder(habit, current_date, current_time):
    """Проверяет, нужно ли отправлять напоминание для привычки"""
    # Проверяем точное совпадение по времени
    habit_time_minutes = habit.time.hour * 60 + habit.time.minute
    current_time_minutes = current_time.hour * 60 + current_time.minute

    if habit_time_minutes != current_time_minutes:
        return False  # Если время не совпадает, то не нужно отправлять напоминание

    # Проверяем периодичность (в днях), если время совпадает
    days_since_creation = (current_date - habit.created_at.date()).days  # Количество дней с момента создания привычки

    if days_since_creation % habit.periodicity != 0:
        return False  # Если периодичность не совпадает, то не нужно отправлять напоминание

    return True  # Если время и периодичность совпадают, то нужно отправлять напоминание
