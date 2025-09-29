from django.core.exceptions import ValidationError
from django.db import models

from config import settings


class Habit(models.Model):
    """ Модель привычки """
    PERIODICITY_CHOICES = [
        (1, 'Ежедневно'),
        (2, 'Раз в 2 дня'),
        (3, 'Раз в 3 дня'),
        (4, 'Раз в 4 дня'),
        (5, 'Раз в 5 дней'),
        (6, 'Раз в 6 дней'),
        (7, 'Раз в неделю'),
    ]

    user = models.ForeignKey(  # связь с моделью User
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    place = models.CharField(
        max_length=255,
        verbose_name='Место выполнения привычки'
    )
    time = models.TimeField(
        verbose_name='Время выполнения привычки'
    )
    action = models.CharField(
        max_length=255,
        verbose_name='Действие при выполнении привычки'
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Признак "приятной" привычки'
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Связанная привычка',
        help_text='Можно указывать, если не выбрано вознаграждение или это описание "приятной" привычки'
    )
    periodicity = models.PositiveIntegerField(
        choices=PERIODICITY_CHOICES,
        default=1,
        verbose_name='Периодичность выполнения привычки (в днях)'
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Вознаграждение',
        help_text='Можно указывать, если не выбрана связанная "приятная" привычка'
    )
    time_to_complete = models.PositiveIntegerField(
        verbose_name='Время на выполнение (в секундах)',
        default=120,
        help_text='Должно быть не более 120 секунд'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Признак публичности привычки'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """ Валидация данных для заполнения полей модели """
        # Нельзя одновременно указывать связанную привычку и вознаграждение
        if self.related_habit and self.reward:
            raise ValidationError('Нельзя одновременно указывать связанную привычку и вознаграждение.')

        # Время выполнения привычки - не больше 120 секунд
        if self.time_to_complete > 120:
            raise ValidationError('Время выполнения привычки не может быть больше 2 минут.')

        # В связанные привычки могут попадать только "приятные" привычки (не полезные)
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError('Связанная привычка должна быть "приятной" (не должна быть "полезной").')

        # У "приятной" привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant:
            if self.reward:
                raise ValidationError('У "приятной" привычки не может быть вознаграждения.')
            if self.related_habit:
                raise ValidationError('У "приятной" привычки не может быть связанной привычки.')

        # Периодичность выполнения привычки - не реже, чем 1 раз в 7 дней
        if self.periodicity > 7:
            raise ValidationError('Нельзя выполнять привычку реже, чем 1 раз в 7 дней.')

    def save(self, *args, **kwargs):
        """ Переопределение метода сохранения модели для валидированных данных """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """ Переопределение метода отображения модели в админке """
        return f"{self.action} в {self.time} в/на {self.place}"

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
