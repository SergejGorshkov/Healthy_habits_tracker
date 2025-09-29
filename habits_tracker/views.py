from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from habits_tracker.models import Habit
from habits_tracker.serializers import HabitSerializer, PublicHabitSerializer
from habits_tracker.pagination import HabitPagination
from habits_tracker.permissions import IsOwnerOrReadOnlyForPublic


class HabitListCreateView(ListCreateAPIView):
    """ Представление для списка привычек и создания привычек. """
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        """ Получение списка привычек. """
        # Пользователь видит только свои привычки
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """ Создание привычки. """
        serializer.save(user=self.request.user) # Добавление пользователя к привычке при ее создании


class HabitRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """ Представление для деталей, обновления и удаления привычки. """
    serializer_class = HabitSerializer
    permission_classes = [IsOwnerOrReadOnlyForPublic]

    def get_queryset(self):
        """ Получение конкретной привычки. """
        # Пользователь видит только свои привычки
        return Habit.objects.filter(user=self.request.user)


class PublicHabitListView(ListAPIView):
    """ Представление для списка публичных привычек """
    serializer_class = PublicHabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        # Все пользователи видят публичные привычки
        return Habit.objects.filter(is_public=True)
