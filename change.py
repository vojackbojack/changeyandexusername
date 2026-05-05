import json
import requests

# =========================
# ИЗМЕНЯЕМЫЕ ПАРАМЕТРЫ
# =========================
ACCESS_TOKEN = "y0_xDUukgYl-81IOblu78Sm24dFgB-EMyKkJyDdpBXHOhg9w"
ORG_ID = "9049222"  # ID организации
USER_LOGIN = "my@email.com"  # кого меняем
NEW_NICKNAME = "nick"  # новый логин/nickname, если поддерживается
NEW_FIRST_NAME = "First"
NEW_LAST_NAME = "Last"
NEW_DISPLAY_NAME = "First Last"  # пробуем как составное имя
NEW_ALIAS = ""  # например: "bojack", если хотите добавить алиас

# Базовые URL
API360_BASE = "https://api360.yandex.net/directory/v1/org"
OLD_API_BASE = "https://api.directory.yandex.net/v6"

HEADERS_JSON = {
    "Authorization": f"OAuth {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

HEADERS_OLD = {
    "Authorization": f"OAuth {ACCESS_TOKEN}",
    "X-Org-ID": str(ORG_ID),
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def pretty(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def get_users():
    url = f"{API360_BASE}/{ORG_ID}/users"
    r = requests.get(url, headers=HEADERS_JSON, timeout=30)
    print(f"GET {url} -> {r.status_code}")
    try:
        data = r.json()
    except Exception:
        print(r.text)
        raise
    return data


def find_user(users_data, login):
    items = []
    if isinstance(users_data, dict):
        if "users" in users_data and isinstance(users_data["users"], list):
            items = users_data["users"]
        elif "result" in users_data and isinstance(users_data["result"], list):
            items = users_data["result"]
        elif isinstance(users_data.get("data"), list):
            items = users_data["data"]

    for u in items:
        possible_values = [
            str(u.get("nickname", "")),
            str(u.get("email", "")),
            str(u.get("primary_email", "")),
            str(u.get("login", "")),
            str(u.get("name", "")),
        ]
        aliases = u.get("aliases", []) or []
        alias_names = [a.get("name", "") if isinstance(a, dict) else str(a) for a in aliases]

        if login in possible_values or login.split("@")[0] in possible_values or login.split("@")[0] in alias_names:
            return u

    for u in items:
        if str(u.get("nickname", "")).lower() == login.split("@")[0].lower():
            return u

    return None


def get_user(user_id):
    url = f"{API360_BASE}/{ORG_ID}/users/{user_id}"
    r = requests.get(url, headers=HEADERS_JSON, timeout=30)
    print(f"GET {url} -> {r.status_code}")
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text}


def patch_user(user_id, payload):
    url = f"{API360_BASE}/{ORG_ID}/users/{user_id}"
    r = requests.patch(url, headers=HEADERS_JSON, data=json.dumps(payload), timeout=30)
    print(f"PATCH {url} -> {r.status_code}")
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text}


def add_alias(user_id, alias_name):
    url = f"{OLD_API_BASE}/users/{user_id}/aliases/"
    payload = {"name": alias_name}
    r = requests.post(url, headers=HEADERS_OLD, data=json.dumps(payload), timeout=30)
    print(f"POST {url} -> {r.status_code}")
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text}


def main():
    users_data = get_users()
    user = find_user(users_data, USER_LOGIN)

    if not user:
        print("Пользователь не найден")
        pretty(users_data)
        return

    user_id = user.get("id") or user.get("uid") or user.get("userId")
    if not user_id:
        print("Не удалось определить user_id")
        pretty(user)
        return

    print("\n=== НАЙДЕН ПОЛЬЗОВАТЕЛЬ ===")
    pretty(user)

    print("\n=== ТЕКУЩИЕ ДАННЫЕ ===")
    status, current = get_user(user_id)
    pretty(current)

    # Пробуем обновить максимально вероятные поля.
    # Если какие-то поля API не примет, сервер вернет ошибку валидации.
    payload = {
        "nickname": "real_nickname",
        "name": {
            "first": "First",
            "last": "Last",
            "middle": ""
        },
        # Указываем нужное вам "публичное имя"
        "displayName": "newname"
    }

    print("\n=== PATCH PAYLOAD ===")
    pretty(payload)

    status, result = patch_user(user_id, payload)

    print("\n=== PATCH RESULT ===")
    pretty(result)

    if NEW_ALIAS:
        print("\n=== ADD ALIAS ===")
        status, alias_result = add_alias(user_id, NEW_ALIAS)
        pretty(alias_result)

    print("\n=== ДАННЫЕ ПОСЛЕ ИЗМЕНЕНИЯ ===")
    status, updated = get_user(user_id)
    pretty(updated)


if __name__ == "__main__":
    main()
