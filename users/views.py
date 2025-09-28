from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.permissions import IsModerator, IsOwner
from users.serializers import UserRegisterSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    """Создание CRUD для пользователя"""

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        """Получение прав для действий с пользователями"""

        if self.action == "create":
            self.permission_classes = [AllowAny]
        elif self.action in ["list"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "retrieve", "destroy"]:
            self.permission_classes = [IsAuthenticated & (IsModerator | IsOwner)]
        else:
            # Запасной вариант
            self.permission_classes = [IsAuthenticated]

        return [
            permission() for permission in self.permission_classes
        ]  # возвращаем разрешения в виде списка объектов

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == "create":  # если действие - создание пользователя
            return UserRegisterSerializer  # сериализатор только с email, password и ID телеграмма
        else:
            return UserSerializer  # иначе - обычный сериализатор

    def perform_create(self, serializer):
        """Изменение данных пользователя (т.к. в модели User переопределили логин с username на email)"""
        user = serializer.save(
            is_active=True
        )  # создание пользователя и его активация в БД
        user.set_password(user.password)  # хеширование пароля пользователя
        user.save()  # сохранение изменений для пользователя в БД
