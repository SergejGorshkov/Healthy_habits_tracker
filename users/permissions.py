from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Класс для проверки, является ли пользователь модератором"""

    message = "Вы должны быть модератором для выполнения этого действия"  # сообщение в случае ошибки

    def has_permission(self, request, view):
        user = request.user
        return user.groups.filter(name="Moderators").exists()


class IsUserOwner(BasePermission):
    """Класс для проверки, является ли пользователь владельцем аккаунта"""
    def has_object_permission(self, request, view, obj):
        return obj == request.user
