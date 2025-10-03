from django.db.models import Q
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView

from habits_tracker.models import Habit
from habits_tracker.pagination import HabitPagination
from habits_tracker.permissions import IsOwnerOrReadOnlyForPublic
from habits_tracker.serializers import HabitSerializer, PublicHabitSerializer


class HabitListCreateView(ListCreateAPIView):
    """Представление для списка привычек и создания привычек."""

    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        """Получение списка привычек."""
        # Пользователь видит свои привычки и публичные привычки других пользователей
        return Habit.objects.filter(Q(user=self.request.user) | Q(is_public=True))

    def perform_create(self, serializer):
        """Создание привычки."""
        serializer.save(user=self.request.user)  # Добавление пользователя к привычке при ее создании


class HabitRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Представление для деталей, обновления и удаления привычки."""

    serializer_class = HabitSerializer
    permission_classes = [IsOwnerOrReadOnlyForPublic]

    def get_queryset(self):
        """Получение конкретной привычки."""
        # Пользователь видит только свои привычки
        return Habit.objects.all()


class PublicHabitListView(ListAPIView):
    """Представление для списка публичных привычек"""

    serializer_class = PublicHabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        # Все пользователи видят публичные привычки
        return Habit.objects.filter(is_public=True)
