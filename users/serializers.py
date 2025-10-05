from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""

    password = serializers.CharField(
        max_length=128,
        write_only=True,  # Запись только в поле password (не в базу)
        required=True,  # Обязательное поле
        validators=[validate_password],  # Валидация пароля по стандарту Django
        style={"input_type": "password"},  # Стиль для поля ввода пароля в браузере
        help_text="Пароль",
    )
    password2 = serializers.CharField(
        max_length=128,
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Подтверждение пароля",
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "password2",
            "phone",
            "city",
            "avatar",
            "tg_chat_id",
            "first_name",
            "last_name",
        )
        extra_kwargs = {  # Поля с дополнительными настройками
            "email": {"required": True},  # Обязательное поле
            "first_name": {"required": False},  # Необязательное поле
            "last_name": {"required": False},
        }

    def validate(self, attrs):
        """Проверка совпадения паролей"""
        if attrs["password"] != attrs["password2"]:  # Если введенные при регистрации пароли 1 и 2 не совпадают, ошибка
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        """Создание пользователя с хешированием пароля"""
        validated_data.pop("password2")  # Удаляем подтверждение пароля из валидированных данных
        password = validated_data.pop("password")  # Получаем пароль из валидированных данных

        user = User.objects.create(**validated_data)
        user.set_password(password)  # Хеширование пароля
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""

    class Meta:
        model = User
        fields = (
            "city",
            "avatar",
            "first_name",
            "date_joined",
        )
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя"""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "city",
            "avatar",
            "tg_chat_id",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "last_login",
        )
        read_only_fields = (
            "id",
            "date_joined",
            "last_login",
        )


class UserPasswordChangeSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля"""

    old_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}, help_text="Текущий пароль"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],  # Валидация пароля по стандарту Django
        style={"input_type": "password"},
        help_text="Новый пароль",
    )
    new_password2 = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}, help_text="Подтверждение нового пароля"
    )

    def validate_old_password(self, value):
        """Проверка текущего пароля"""
        user = self.context["request"].user  # Получение текущего пользователя из контекста запроса
        if not user.check_password(value):  # Если пароль не совпадает с текущим паролем пользователя -> ошибка
            raise serializers.ValidationError("Неверный текущий пароль")
        return value

    def validate(self, attrs):
        """Проверка совпадения новых паролей"""
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError("Новые пароли не совпадают")
        return attrs

    def save(self, **kwargs):
        """Сохранение нового пароля"""
        password = self.validated_data["new_password"]
        user = self.context["request"].user
        user.set_password(password)
        user.save()
        return user
