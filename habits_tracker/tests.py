from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits_tracker.models import Habit
from users.models import User


class HabitTestCase(APITestCase):
    """
    Базовый класс для тестирования привычек.
    Создает тестовых пользователей и привычки.
    Настраивает различные сценарии для тестирования.
    """

    def setUp(self):
        """Настройка тестовых данных"""
        # Создание двух тестовых пользователей
        self.user1 = User.objects.create(email="user1@test.com", password="testpass123")
        self.user2 = User.objects.create(email="user2@test.com", password="testpass123")

        # Создание "приятной" публичной привычки для user1
        self.pleasant_habit = Habit.objects.create(
            user=self.user1,
            place="дом",
            time="20:00:00",
            action="чтение книги",
            is_pleasant=True,
            time_to_complete=120,
            is_public=True,
        )

        # Создание "полезной" публичной привычки для user1 со связанной "приятной" привычкой
        self.useful_habit_user1 = Habit.objects.create(
            user=self.user1,
            place="парк",
            time="19:00:00",
            action="прогулка",
            is_pleasant=False,
            related_habit=self.pleasant_habit,
            periodicity=1,
            time_to_complete=110,
            is_public=True,
        )

        # Создание приватной "полезной" привычки для user1
        self.private_habit_user1 = Habit.objects.create(
            user=self.user1,
            place="дом",
            time="21:00:00",
            action="медитация",
            is_pleasant=False,
            reward="чай с медом",
            periodicity=1,
            time_to_complete=100,
            is_public=False,
        )

        # Создание "полезной" публичной привычки для user2
        self.habit_user2 = Habit.objects.create(
            user=self.user2,
            place="спортзал",
            time="18:00:00",
            action="тренировка",
            is_pleasant=False,
            reward="протеиновый коктейль",
            periodicity=2,
            time_to_complete=95,
            is_public=True,
        )


class HabitListCreateViewTestCase(HabitTestCase):
    """
    Тестирование списка и создания привычек.
    Получение списка своих привычек.
    Создание новых привычек.
    Валидация данных при создании.
    """

    def test_get_habits_authenticated(self):
        """Тест получения списка привычек аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)  # Принудительная аутентификация для user1

        url = reverse("habits_tracker:habits_tracker-list-create")  # Получение URL для списка привычек
        response = self.client.get(url)  # Выполнение GET запроса на URL списка привычек

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)  # user1 имеет 3 привычки + 1 публичная у user2

        # Проверяем, что возвращаются только привычки текущего пользователя
        habit_actions = [habit["action"] for habit in response.data["results"]]
        self.assertIn("прогулка", habit_actions)
        self.assertIn("медитация", habit_actions)
        self.assertIn("чтение книги", habit_actions)
        self.assertIn("тренировка", habit_actions)  # привычка user2 должна быть в списке, т.к. она публичная

    def test_get_habits_unauthenticated(self):
        """Тест получения списка привычек неаутентифицированным пользователем"""
        url = reverse("habits_tracker:habits_tracker-list-create")
        response = self.client.get(url)  # Выполнение GET запроса на URL списка привычек без аутентификации

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_habit_authenticated(self):
        """Тест создания привычки аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-list-create")
        data = {
            "place": "офис",
            "time": "15:00:00",
            "action": "растяжка",
            "is_pleasant": False,
            "periodicity": 1,
            "reward": "кофе",
            "time_to_complete": 60,
            "is_public": True,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 5)  # 4 было +1 новая привычка
        self.assertEqual(response.data["user"], self.user1.id)  # пользователь автоматически проставляется
        self.assertEqual(response.data["action"], "растяжка")

    def test_create_habit_with_related_habit(self):
        """Тест создания привычки со связанной "приятной" привычкой"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-list-create")
        data = {
            "place": "дом",
            "time": "16:00:00",
            "action": "уборка",
            "is_pleasant": False,
            "related_habit": self.pleasant_habit.id,
            "periodicity": 1,
            "time_to_complete": 90,
            "is_public": False,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["related_habit"], self.pleasant_habit.id)

    def test_create_habit_validation_error(self):
        """Тест (негативный) валидации при создании привычки"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-list-create")
        data = {
            "place": "дом",
            "time": "16:00:00",
            "action": "тест",
            "is_pleasant": False,
            "related_habit": self.pleasant_habit.id,
            "reward": "конфета",  # Нельзя одновременно related_habit и reward
            "periodicity": 1,
            "time_to_complete": 60,
            "is_public": False,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0], "Нельзя одновременно указывать связанную привычку и вознаграждение."
        )

    def test_create_pleasant_habit_with_reward_error(self):
        """Тест (негативный) создания приятной привычки с вознаграждением."""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-list-create")
        data = {
            "place": "дом",
            "time": "22:00:00",
            "action": "просмотр фильма",
            "is_pleasant": True,
            "reward": "попкорн",  # У приятной привычки не может быть вознаграждения
            "periodicity": 1,
            "time_to_complete": 100,
            "is_public": False,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], 'У "приятной" привычки не может быть вознаграждения.')


class HabitRetrieveUpdateDestroyViewTestCase(HabitTestCase):
    """
    Тестирование деталей, обновления и удаления привычек.
    Доступ к своим и чужим привычкам.
    Права на изменение и удаление.
    Проверка permissions.
    """

    def test_get_habit_owner(self):
        """Тест получения привычки владельцем"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-detail", kwargs={"pk": self.useful_habit_user1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.useful_habit_user1.id)  # Проверка ID привычки в ответе
        self.assertEqual(response.data["action"], "прогулка")

    def test_get_habit_other_user(self):
        """Тест получения чужой публичной привычки (должен иметь доступ)"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-detail", kwargs={"pk": self.habit_user2.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_habit_owner(self):
        """Тест обновления привычки владельцем"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-detail", kwargs={"pk": self.useful_habit_user1.id})
        data = {
            "place": "лес",
            "time": "19:00:00",
            "action": "прогулка в лесу",
            "is_pleasant": False,
            "related_habit": self.pleasant_habit.id,
            "periodicity": 1,
            "time_to_complete": 120,
            "is_public": True,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.useful_habit_user1.refresh_from_db()  # Обновление объекта из БД для проверки изменений
        self.assertEqual(self.useful_habit_user1.place, "лес")
        self.assertEqual(self.useful_habit_user1.action, "прогулка в лесу")

    def test_update_habit_other_user(self):
        """Тест (негативный) обновления чужой привычки"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-detail", kwargs={"pk": self.habit_user2.id})
        data = {"action": "бездельничать"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_habit_owner(self):
        """Тест удаления привычки владельцем"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-detail", kwargs={"pk": self.private_habit_user1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 3)  # одна привычка удалена = 2 свои + 1 публичная остались

    def test_delete_habit_other_user(self):
        """Тест (негативный) удаления чужой привычки"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:habits_tracker-detail", kwargs={"pk": self.habit_user2.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Habit.objects.count(), 4)  # все привычки остались (3 свои + 1 публичная user2)


class PublicHabitListViewTestCase(HabitTestCase):
    """
    Тестирование списка публичных привычек.
    Доступ для аутентифицированных и неаутентифицированных пользователей.
    Пагинация. Фильтрация только публичных привычек.
    """

    def test_get_public_habits_authenticated(self):
        """Тест получения публичных привычек аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:public-habits_tracker-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Публичные привычки
        public_habits_count = Habit.objects.filter(is_public=True).count()
        self.assertEqual(len(response.data["results"]), public_habits_count)

        # Проверка, что приватные привычки не возвращаются
        habit_actions = [habit["action"] for habit in response.data["results"]]
        self.assertIn("прогулка", habit_actions)  # публичная
        self.assertIn("тренировка", habit_actions)  # публичная
        self.assertIn("чтение книги", habit_actions)  # публичная
        self.assertNotIn("медитация", habit_actions)  # приватная

    def test_get_public_habits_unauthenticated(self):
        """Тест (негативный) получения публичных привычек неаутентифицированным пользователем"""
        url = reverse("habits_tracker:public-habits_tracker-list")
        response = self.client.get(url)  # Выполнение GET запроса на URL списка привычек без аутентификации

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination(self):
        """Тест пагинации в списке публичных привычек"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("habits_tracker:public-habits_tracker-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)


class HabitValidationTestCase(APITestCase):
    """
    Тестирование валидации модели Habit.
    Проверка правил модели.
    Валидация времени выполнения, периодичности, связанных привычек.
    """

    def setUp(self):
        self.user = User.objects.create(email="test@test.com", password="testpass123")
        self.client.force_authenticate(user=self.user)

        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="дом",
            time="20:00:00",
            action="приятная привычка",
            is_pleasant=True,
            time_to_complete=60,
        )

    def test_time_to_complete_validation(self):
        """Тест (негативный) валидации времени выполнения (не более 120 секунд)"""
        url = reverse("habits_tracker:habits_tracker-list-create")
        data = {
            "place": "дом",
            "time": "15:00:00",
            "action": "тест",
            "is_pleasant": False,
            "periodicity": 1,
            "reward": "награда",
            "time_to_complete": 121,  # больше 120 секунд
            "is_public": False,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0], "Время выполнения привычки не может быть больше 120 секунд."
        )

    def test_periodicity_validation(self):
        """Тест (негативный) валидации периодичности (не более 7 дней)"""
        url = reverse("habits_tracker:habits_tracker-list-create")
        data = {
            "place": "дом",
            "time": "15:00:00",
            "action": "тест",
            "is_pleasant": False,
            "periodicity": 8,  # больше 7 дней
            "reward": "награда",
            "time_to_complete": 60,
            "is_public": False,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        habit = Habit(
            user=self.user,
            place="Дом",
            time="10:00",
            action="Тестовая привычка",
            periodicity=10,  # Неправильное значение
            time_to_complete=60,
        )

        # При вызове save() должен автоматически вызываться clean()
        with self.assertRaises(ValidationError) as context:
            habit.save()

        self.assertIn("Нельзя выполнять привычку реже, чем 1 раз в 7 дней", str(context.exception))

    def test_related_habit_validation(self):
        """Тест (негативный) валидации связанной привычки (должна быть приятной)"""
        useful_habit = Habit.objects.create(
            user=self.user,
            place="парк",
            time="19:00:00",
            action="полезная привычка",
            is_pleasant=False,
            time_to_complete=60,
        )

        url = reverse("habits_tracker:habits_tracker-list-create")
        data = {
            "place": "дом",
            "time": "15:00:00",
            "action": "тест",
            "is_pleasant": False,
            "related_habit": useful_habit.id,  # "полезная" привычка связана с "полезной" привычкой (ошибка)
            "periodicity": 1,
            "time_to_complete": 60,
            "is_public": False,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], 'Связанная привычка должна быть "приятной".')
