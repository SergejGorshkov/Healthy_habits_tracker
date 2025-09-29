from django.urls import path

from habits_tracker.apps import HabitsTrackerConfig
from habits_tracker.views import HabitListCreateView, HabitRetrieveUpdateDestroyView, PublicHabitListView


# Извлечение имени приложения из модуля habits_tracker/apps.py
app_name = HabitsTrackerConfig.name

urlpatterns = [
    path('habits_tracker/', HabitListCreateView.as_view(), name='habits_tracker-list-create'),
    path('habits_tracker/<int:pk>/', HabitRetrieveUpdateDestroyView.as_view(), name='habits_tracker-detail'),
    path('habits_tracker/public/', PublicHabitListView.as_view(), name='public-habits_tracker-list'),
]
