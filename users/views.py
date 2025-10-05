from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.permissions import IsModerator, IsUserOwner
from users.serializers import (UserPasswordChangeSerializer,
                               UserProfileSerializer,
                               UserRegisterSerializer,
                               UserSerializer)


class UserViewSet(ModelViewSet):
    """Создание CRUD для пользователя"""

    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("-date_joined")

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == "create":  # создание пользователя
            return UserRegisterSerializer
        elif self.action == "change_password":  # изменение пароля пользователя
            return UserPasswordChangeSerializer
        # обновление и просмотр своего профиля = все поля
        elif (self.action in ["update", "partial_update",
                              "profile", "retrieve"] and self.request.user == self.get_object()):
            return UserProfileSerializer
        elif self.action == "retrieve":  # просмотр профиля другого пользователя
            return UserSerializer
        return UserSerializer  # все остальные действия

    def get_permissions(self):
        """Получение прав для действий с пользователями"""

        if self.action == "create":
            permission_classes = [AllowAny]  # Регистрация доступна всем
        elif self.action in ["list"]:
            permission_classes = [IsAuthenticated & IsModerator]  # Список пользователей - только для модераторов
        elif self.action in ["update", "partial_update", "destroy", "change_password", "profile"]:
            permission_classes = [
                IsAuthenticated & (IsModerator | IsUserOwner)
            ]  # Изменение и удаление - только для модераторов и владельцев
        elif self.action in [
            "retrieve",
        ]:
            permission_classes = [IsAuthenticated]  # Просмотр - только для авторизованных пользователей
        else:
            permission_classes = [IsAuthenticated]  # Запасной вариант - только для авторизованных пользователей

        return [permission() for permission in permission_classes]  # возврат разрешений в виде списка объектов

    def perform_create(self, serializer):
        """Изменение данных пользователя (т.к. в модели User переопределили логин с username на email)"""
        user = serializer.save(is_active=True)  # создание пользователя и его активация в БД

    @action(detail=False, methods=["get"])
    def profile(self, request):
        """Получить профиль текущего пользователя"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def change_password(self, request, pk=None):
        """Изменение пароля"""
        user = self.get_object()
        serializer = UserPasswordChangeSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"message": "Пароль изменен"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
