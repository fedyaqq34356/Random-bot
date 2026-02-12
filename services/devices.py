import random

DEVICE_MODELS = [
    "Honor HONOR 70", "Samsung Galaxy S21", "Xiaomi Mi 11", "Google Pixel 6",
    "OnePlus 9", "Sony Xperia 5", "Huawei P50", "Nokia X20", "Motorola Edge 20",
    "Apple iPhone 13", "Apple iPhone 14", "Apple iPhone 15", "PC"
]
SYSTEM_VERSIONS = [
    "SDK 35", "SDK 34", "SDK 33", "SDK 32", "SDK 31", "SDK 30",
    "SDK 29", "SDK 28", "SDK 27", "iOS 15.4", "iOS 16.0", "iOS 17.0",
    "Windows 11", "Ubuntu 22.04", "Arch Linux", "Fedora 38"
]
APP_VERSIONS = [
    "Telegram Android 11.13.1", "Telegram Android 11.12.0", "Telegram Android 11.11.0",
    "Telegram Android 11.10.0", "Telegram Android 11.9.0", "Telegram Android 11.8.0",
    "Telegram Android 11.7.0", "Telegram Android 11.6.0", "Telegram Android 11.5.0",
    "Telegram iOS 10.4.1", "Telegram iOS 10.0.0", "Telegram iOS 11.0.0", "1.0"
]


def get_random_device() -> dict:
    return {
        "device_model": random.choice(DEVICE_MODELS),
        "system_version": random.choice(SYSTEM_VERSIONS),
        "app_version": random.choice(APP_VERSIONS),
        "lang_code": "ru",
        "system_lang_code": "ru-RU"
    }