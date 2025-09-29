from rest_framework import permissions


class IsOwnerOrReadOnlyForPublic(permissions.BasePermission):
    """
    Разрешение, позволяющее владельцу выполнять любые действия над своими привычками,
    а всем пользователям видеть публичные привычки (только для чтения).
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для всех запросов, если привычка публичная
        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True

        # Владельцу разрешено выполнять любые действия над своей привычкой
        return obj.user == request.user
