import os
import time
import requests

# Считываем секреты из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Список ID квартир для отслеживания
TARGET_IDS = [32050, 32045]

# Шаблон URL (вместо конкретного ID подставляется {flat_id})
BASE_URL = "https://admin.realtyprotech.com/api/v1/public/instances/{flat_id}?first_token=uyutny"

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
    for target_id in TARGET_IDS:
        url = BASE_URL.format(flat_id=target_id)
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"Ошибка HTTP {response.status_code} для ID {target_id}")
                continue

            json_data = response.json()
            instance = json_data.get("data", {}).get("instance", {})

            current_id = instance.get("id")
            status_info = instance.get("status", {})
            status_type = status_info.get("type")
            status_name = status_info.get("name")
            flat_number = instance.get("number")
            price = instance.get("price")

            print(
                f"Проверка квартиры №{flat_number} (ID {current_id}): Статус = {status_name} (type: {status_type})"
            )

            # Если статус изменился (стал 1 или "Свободно")
            # if status_type == 1 or status_name == "Свободно":
            if status_type == 2 or status_name == "Бронь":
                msg = (
                    f"🎉 <b>Квартира №{flat_number} СВОБОДНА!</b>\n"
                    f"ID: {current_id}\n"
                    f"Цена: {price} BYN\n"
                    f"Ссылка: https://rpt.realting.com/"
                )
                send_telegram_message(msg)

        except Exception as e:
            print(f"Ошибка выполнения запроса для ID {target_id}: {e}")

        # Небольшая пауза между запросами
        time.sleep(10)


if __name__ == "__main__":
    check_status()
