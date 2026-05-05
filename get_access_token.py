import requests
import webbrowser
import urllib.parse
import json

# === НАСТРОЙКИ ===
CLIENT_ID = "69a9f8442b77475b946b06952e335d75"
CLIENT_SECRET = "832b9d685fed4d07a3dc9237f023rrd1"
CALLBACK_URL = "https://oauth.yandex.ru/verification_code"  # Должен совпадать с настройками приложения

# Используем актуальные права доступа directory:*
SCOPE = "directory:read_users directory:write_users"


def get_authorization_code():
    """Открывает страницу авторизации и получает код"""
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': CALLBACK_URL,
        'scope': SCOPE
    }
    auth_url = f"https://oauth.yandex.ru/authorize?{urllib.parse.urlencode(auth_params)}"

    print("Открываю страницу авторизации в браузере...")
    print(f"Если браузер не открылся, перейдите по ссылке:")
    print(auth_url)
    print("\nПосле авторизации скопируйте код из адресной строки браузера")

    webbrowser.open(auth_url)
    code = input("\nВведите код авторизации: ").strip()
    return code


def exchange_code_for_token(code):
    """Обменивает код авторизации на OAuth‑токен"""
    token_url = "https://oauth.yandex.ru/token"

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': CALLBACK_URL
    }

    try:
        response = requests.post(token_url, data=data)
        if response.status_code == 400:
            error_data = response.json()
            raise Exception(f"Ошибка OAuth: {error_data.get('error_description', 'Неизвестная ошибка')}")
        response.raise_for_status()
        token_data = response.json()
        return token_data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при получении токена: {e}")
    except json.JSONDecodeError:
        raise Exception(f"Не удалось распарсить ответ: {response.text}")


def save_tokens(token_data):
    """Сохраняет токены в файл"""
    with open('yandex_tokens.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    print("Токен сохранён в файл yandex_tokens.json")


def main():
    print("=== ПОЛУЧЕНИЕ OAUTH-ТОКЕНА ДЛЯ ЯНДЕКСА ===\n")

    try:
        # Шаг 1: Получаем код авторизации
        code = get_authorization_code()
        if not code:
            print("Код авторизации не введён!")
            return

        # Шаг 2: Обмениваем код на токен
        print("\nПолучаю OAuth‑токен...")
        token_data = exchange_code_for_token(code)

        # Шаг 3: Выводим результаты
        print("\n" + "=" * 50)
        print("✅ OAuth‑ТОКЕН ПОЛУЧЕН УСПЕШНО!")
        print("=" * 50)
        print(f"Access Token: {token_data['access_token']}")
        print(f"Refresh Token: {token_data.get('refresh_token', 'Не предоставлен')}")
        print(f"Срок действия: {token_data['expires_in']} секунд ({token_data['expires_in'] // 3600} часов)")

        save_tokens(token_data)

        print("\nТеперь вы можете использовать этот токен в других скриптах!")
        print("Пример использования:")
        print(f'headers = {{"Authorization": "OAuth {token_data["access_token"]}"}}')

    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")


if __name__ == '__main__':
    main()
