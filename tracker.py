import os
import time
import requests

# Считываем секреты из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Настройки Telegram
#TELEGRAM_TOKEN = "8798375277:AAGaTJk-Elca_wefMY261WEAPU12yAcqlJ4"
#TELEGRAM_CHAT_ID = "985267897"

# Данные запроса
URL = "https://admin.realtyprotech.com/api/v1/public/instances/32050?first_token=uyutny"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,he;q=0.7",
    "Origin": "https://rpt.realting.com",
    "Priority": "u=1, i",
    "Referer": "https://rpt.realting.com/",
    "Sec-Ch-Ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    "X-Accept-Language": "1",
}
TARGET_ID = 32050
CHECK_INTERVAL_SECONDS = 300  # Проверка каждые 5 минут


def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: Переменные TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не заданы!")
        return

    telegram_url = (
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    )
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(telegram_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

def check_status():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Сервер вернул код {response.status_code}")
            return False

        json_data = response.json()
        instance = json_data.get("data", {}).get("instance", {})

        current_id = instance.get("id")
        status_info = instance.get("status", {})
        status_type = status_info.get("type")
        status_name = status_info.get("name")
        flat_number = instance.get("number")

        print(
            f"Проверка квартиры №{flat_number} (ID {current_id}): Статус = {status_name} (type: {status_type})"
        )

        # Если статус изменился (стал 1 или "Свободно")
        if current_id == TARGET_ID and (
            status_type == 1 or status_name == "Свободно"
        ):
            msg = (
                f"🎉 <b>Квартира №{flat_number} СВОБОДНА!</b>\n"
                f"ID: {current_id}\n"
                f"Цена: {instance.get('price')} BYN\n"
                f"Ссылка: https://rpt.realting.com/"
            )
            send_telegram_message(msg)
            return True

    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")

    return False


if __name__ == "__main__":
    check_status()
