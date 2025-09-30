from config import settings
import requests


def send_telegram_message(tg_chat_id, message):
    """ Отправка сообщения в телеграм """
    try:
        # Параметры для отправки сообщения
        params = {
            'chat_id': tg_chat_id,
            'text': message,
        }
        # формирование ссылки для отправки сообщения в Телеграм
        url = f'{settings.TELEGRAM_URL}{settings.TG_BOT_TOKEN}/sendMessage'
        response = requests.post(url, json=params, timeout=10)  # отправка запроса к боту Телеграм и сохранение ответа
        response.raise_for_status() # проверка на ошибки в ответе

        return True

    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки сообщения в Телеграм: {str(e)}")

        return False

    except Exception as e:
        print(f"Непредвиденная ошибка: {str(e)}")

        return False