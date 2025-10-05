from django.contrib import admin

from habits_tracker.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    # Отображаемые в админке поля
    list_display = (
        "user",
        "place",
        "time",
        "action",
        "is_pleasant",
        "related_habit",
        "periodicity",
        "reward",
    )
    list_filter = (
        "user",
        "is_pleasant",
        "related_habit",
        "reward",
        "is_public",
    )  # возможность фильтрации
    search_fields = (
        "reward",
        "related_habit",
    )  # поиск объектов по заданным полям
