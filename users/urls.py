from django.urls import path
# from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import (TokenObtainPairView,
#                                             TokenRefreshView)

from users.apps import UsersConfig
from users.views import UserViewSet

app_name = UsersConfig.name  # Извлечение имени приложения из модуля users/apps.py

router = DefaultRouter()  # Создание экземпляра DefaultRouter для регистрации ViewSet
router.register(
    r"users", UserViewSet, basename="users"
)  # Регистрация ViewSet с именем users

urlpatterns = [
    path(
    #     "login/",
    #     TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
    #     name="login",
    # ),
    # path(
    #     "token/refresh/",
    #     TokenRefreshView.as_view(permission_classes=(AllowAny,)),
    #     name="token_refresh",
    ),
] + router.urls  # Добавление URL для ViewSet
