from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserViewSetTestCase(APITestCase):
    """Базовый класс для тестирования UserViewSet"""

    def setUp(self):
        """Настройка тестовых данных"""

        # Создание тестовых пользователей
        self.regular_user = User.objects.create(
            email="regular@example.com",
            password="testpass123",
            first_name="Regular",
            last_name="User",
            city="Test City",
            phone="+79999999999",
            avatar="https://example.com/avatar.jpg",
            date_joined="2023-01-01",
        )
        self.regular_user.set_password("testpass123")  # Хешируем пароль
        self.regular_user.save()

        self.another_user = User.objects.create(
            email="another@example.com",
            password="testpass123",
            first_name="Another",
            last_name="User",
        )
        self.another_user.set_password("testpass123")  # Хешируем пароль
        self.another_user.save()

        # Создание модератора
        self.moderator = User.objects.create(
            email="moderator@example.com", password="modpass123", first_name="Moderator", last_name="User"
        )
        self.moderator.set_password("modpass123")
        self.moderator.save()

        # URL для тестирования
        self.register_url = reverse("users:users-list")
        self.user_list_url = reverse("users:users-list")
        self.profile_url = reverse("users:users-profile")
        self.login_url = reverse("users:login")

    def get_user_detail_url(self, user_id):
        """Получить URL для детального просмотра пользователя"""
        return reverse("users:users-detail", args=[user_id])

    def get_change_password_url(self, user_id):
        """Получить URL для смены пароля"""
        return reverse("users:users-change-password", args=[user_id])


class UserRegistrationTests(UserViewSetTestCase):
    """Тестирование регистрации пользователей"""

    def test_user_registration_success(self):
        """Тест успешной регистрации пользователя"""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password2": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)  # 3 из setUp + 1 новый
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

        # Проверяем, что пароль хешируется
        user = User.objects.get(email="newuser@example.com")
        self.assertTrue(user.check_password("newpass123"))
        self.assertTrue(user.is_active)

    def test_user_registration_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password2": "differentpass",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_user_registration_duplicate_email(self):
        """Тест регистрации с существующим email"""
        data = {
            "email": "regular@example.com",  # Уже существует
            "password": "newpass123",
            "password2": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


class UserAuthenticationTests(UserViewSetTestCase):
    """Тестирование аутентификации"""

    def test_jwt_authentication_success(self):
        """Тест успешной JWT аутентификации"""
        data = {"email": "regular@example.com", "password": "testpass123"}

        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_authentication_invalid_credentials(self):
        """Тест аутентификации с неверными учетными данными"""
        data = {"email": "regular@example.com", "password": "wrongpassword"}

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTests(UserViewSetTestCase):
    """Тестирование профиля пользователя"""

    def test_get_own_profile_authenticated(self):
        """Тест получения своего профиля аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "regular@example.com")
        self.assertEqual(response.data["first_name"], "Regular")

    def test_get_own_profile_unauthenticated(self):
        """Тест (негативный) получения профиля без аутентификации"""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_own_profile_via_detail(self):
        """Тест получения своего профиля через детальный эндпоинт"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_user_detail_url(self.regular_user.id)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны быть все поля из UserProfileSerializer
        fields = [
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
        ]
        for field in fields:
            self.assertIn(field, response.data)

    def test_retrieve_other_user_profile(self):
        """Тест получения чужого профиля"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_user_detail_url(self.another_user.id)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны быть только поля из UserSerializer
        fields = ["city", "avatar", "first_name", "date_joined"]
        for field in fields:
            self.assertIn(field, response.data)

        self.assertNotIn("email", response.data)
        self.assertNotIn("last_login", response.data)
        self.assertNotIn("last_name", response.data)


class UserListTests(UserViewSetTestCase):
    """Тестирование списка пользователей"""

    def test_user_list_access_without_moderator_role(self):
        """Тест (негативный) доступа к списку пользователей без роли модератора"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.user_list_url)

        # Должен быть запрещен доступ, т.к. пользователь - не модератор
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_access_unauthenticated(self):
        """Тест (негативный) доступа к списку пользователей без аутентификации"""
        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserUpdateTests(UserViewSetTestCase):
    """Тестирование обновления пользователей"""

    def test_update_own_profile(self):
        """Тест обновления своего профиля"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_user_detail_url(self.regular_user.id)

        data = {"first_name": "Updated", "last_name": "Name", "city": "Updated City", "phone": "+77777777777"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()  # Получаем обновленный объект из БД
        self.assertEqual(self.regular_user.first_name, "Updated")
        self.assertEqual(self.regular_user.city, "Updated City")

    def test_update_other_user_profile(self):
        """Тест (негативный) попытки обновления чужого профиля"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_user_detail_url(self.another_user.id)

        data = {"first_name": "Hacked"}

        response = self.client.patch(url, data)

        # Должен быть запрещен доступ
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_email_not_allowed(self):
        """Тест, что свой email можно изменить через API"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_user_detail_url(self.regular_user.id)

        data = {"email": "newemail@example.com"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Email должен измениться
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, "newemail@example.com")


class UserPasswordChangeTests(UserViewSetTestCase):
    """Тестирование смены пароля"""

    def test_change_password_success(self):
        """Тест успешной смены пароля"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_change_password_url(self.regular_user.id)

        data = {"old_password": "testpass123", "new_password": "newsecurepass123", "new_password2": "newsecurepass123"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password("newsecurepass123"))

    def test_change_password_wrong_old_password(self):
        """Тест (негативный) смены пароля с неверным старым паролем"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_change_password_url(self.regular_user.id)

        data = {
            "old_password": "wrongpassword",
            "new_password": "newsecurepass123",
            "new_password2": "newsecurepass123",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)

    def test_change_password_mismatch(self):
        """Тест (негативный) смены пароля с несовпадающими новыми паролями"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_change_password_url(self.regular_user.id)

        data = {"old_password": "testpass123", "new_password": "newsecurepass123", "new_password2": "differentpass"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Новые пароли не совпадают")

    def test_change_other_user_password(self):
        """Тест (негативный) попытки смены чужого пароля"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_change_password_url(self.another_user.id)

        data = {"old_password": "testpass123", "new_password": "newsecurepass123", "new_password2": "newsecurepass123"}

        response = self.client.post(url, data)

        # Должен быть запрещен доступ
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserDeleteTests(UserViewSetTestCase):
    """Тестирование удаления пользователей"""

    def test_delete_own_account(self):
        """Тест удаления своего аккаунта"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_user_detail_url(self.regular_user.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.regular_user.id).exists())

    def test_delete_other_user_account(self):
        """Тест (негативный) попытки удаления чужого аккаунта"""
        self.client.force_authenticate(user=self.regular_user)
        url = self.get_user_detail_url(self.another_user.id)

        response = self.client.delete(url)

        # Должен быть запрещен доступ
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserSerializerTests(UserViewSetTestCase):
    """Тестирование сериализаторов"""

    def test_user_profile_serializer_fields(self):
        """Тест полей UserProfileSerializer"""
        from users.serializers import UserProfileSerializer

        serializer = UserProfileSerializer(self.regular_user)
        data = serializer.data

        # Должны присутствовать только публичные поля
        expected_fields = {
            "id",
            "email",
            "phone",
            "city",
            "avatar",
            "first_name",
            "last_name",
            "tg_chat_id",
            "date_joined",
            "last_login",
            "is_active",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_user_serializer_fields(self):
        """Тест полей UserSerializer"""
        from users.serializers import UserSerializer

        serializer = UserSerializer(self.regular_user)
        data = serializer.data

        # Должны присутствовать не все поля
        expected_fields = {"city", "avatar", "first_name", "date_joined"}
        self.assertEqual(set(data.keys()), expected_fields)
