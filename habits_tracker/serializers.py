from rest_framework import serializers
from habits_tracker.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """ Сериализатор привычки для создания, редактирования, удаления и детального просмотра """
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def validate(self, data):
        """ Проверка данных при создании привычки """
        if data.get('related_habit') and data.get('reward'):
            raise serializers.ValidationError(
                'Нельзя одновременно указывать связанную привычку и вознаграждение.'
            )

        if data.get('time_to_complete', 0) > 120:
            raise serializers.ValidationError(
                'Время выполнения "полезной" привычки не может быть больше 120 секунд.'
            )

        related_habit = data.get('related_habit')
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                'Связанная привычка должна быть "приятной".'
            )

        if data.get('is_pleasant', False):
            if data.get('reward'):
                raise serializers.ValidationError(
                    'У "приятной" привычки не может быть вознаграждения.'
                )
            if data.get('related_habit'):
                raise serializers.ValidationError(
                    'У "приятной" привычки не может быть связанной привычки.'
                )

        if data.get('periodicity', 1) > 7:
            raise serializers.ValidationError(
                'Нельзя выполнять привычку реже, чем 1 раз в 7 дней.'
            )

        return data


class PublicHabitSerializer(serializers.ModelSerializer):
    """ Сериализатор привычки для публичного просмотра """
    user = serializers.StringRelatedField()  # Возвращает результат метода __str__() у модели пользователя вместо id

    class Meta:
        model = Habit
        fields = ('id', 'user', 'place', 'time', 'action', 'periodicity',
                  'time_to_complete', 'created_at')
        read_only_fields = fields
