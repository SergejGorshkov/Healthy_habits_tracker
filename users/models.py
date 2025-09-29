from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Модель пользователя. """
    username = None
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Введите ваш email"
    )
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Введите ваш телефон",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Введите ваш город",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите ваш аватар",
    )
    tg_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="ID чата в Telegram",
        help_text="Введите ID чата в Telegram"
    )

    USERNAME_FIELD = (
        "email"  # означает, что мы хотим использовать email в качестве логина
    )
    REQUIRED_FIELDS = (
        []
    )  # означает, что мы не хотим использовать username в качестве обязательного поля

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
