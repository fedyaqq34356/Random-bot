from pathlib import Path
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

from services.devices import get_random_device
from logger import logger

sessions: dict = {}


def _make_client(user_id: int, api_id: int, api_hash: str) -> TelegramClient:
    Path("sessions").mkdir(exist_ok=True)
    device = get_random_device()
    return TelegramClient(
        f"sessions/{user_id}",
        api_id,
        api_hash,
        device_model=device["device_model"],
        system_version=device["system_version"],
        app_version=device["app_version"],
        lang_code=device["lang_code"],
        system_lang_code=device["system_lang_code"]
    )


async def start_auth(user_id: int, api_id: int, api_hash: str, phone: str):
    try:
        client = _make_client(user_id, api_id, api_hash)
        await client.connect()

        if await client.is_user_authorized():
            sessions[user_id] = {"client": client, "phone": phone, "api_id": api_id, "api_hash": api_hash}
            return "already", "Аккаунт уже авторизован"

        await client.send_code_request(phone)
        sessions[user_id] = {"client": client, "phone": phone, "api_id": api_id, "api_hash": api_hash}
        logger.info(f"Код отправлен для user_id={user_id}")
        return "code_sent", "Код отправлен на ваш Telegram"
    except Exception as e:
        logger.error(f"start_auth error: {e}")
        return "error", str(e)


async def verify_code(user_id: int, code: str):
    if user_id not in sessions:
        return "error", "Сессия не найдена"
    session = sessions[user_id]
    try:
        await session["client"].sign_in(session["phone"], code)
        return "success", "Успешно"
    except SessionPasswordNeededError:
        return "2fa", "Введите пароль двухфакторной аутентификации:"
    except PhoneCodeInvalidError:
        return "retry", "Неверный код, попробуйте снова:"
    except Exception as e:
        logger.error(f"verify_code error: {e}")
        return "error", str(e)


async def verify_password(user_id: int, password: str):
    if user_id not in sessions:
        return "error", "Сессия не найдена"
    try:
        await sessions[user_id]["client"].sign_in(password=password)
        return "success", "Успешно"
    except Exception as e:
        logger.error(f"verify_password error: {e}")
        return "error", str(e)


async def get_client(user_id: int) -> TelegramClient | None:
    if user_id in sessions:
        client = sessions[user_id]["client"]
        if client.is_connected():
            return client

    Path("sessions").mkdir(exist_ok=True)
    session_file = Path(f"sessions/{user_id}.session")
    if not session_file.exists():
        return None

    from database import db
    giveaways = db.get_admin_giveaways(user_id)
    return None


async def get_or_restore_client(user_id: int, api_id: int, api_hash: str) -> TelegramClient | None:
    if user_id in sessions:
        client = sessions[user_id]["client"]
        if not client.is_connected():
            await client.connect()
        if await client.is_user_authorized():
            return client

    Path("sessions").mkdir(exist_ok=True)
    session_file = Path(f"sessions/{user_id}.session")
    if not session_file.exists():
        return None

    try:
        client = _make_client(user_id, api_id, api_hash)
        await client.connect()
        if await client.is_user_authorized():
            sessions[user_id] = {"client": client, "api_id": api_id, "api_hash": api_hash, "phone": ""}
            return client
        await client.disconnect()
        return None
    except Exception as e:
        logger.error(f"get_or_restore_client error: {e}")
        return None


async def cancel_auth(user_id: int):
    if user_id in sessions:
        try:
            if sessions[user_id]["client"].is_connected():
                await sessions[user_id]["client"].disconnect()
        except Exception:
            pass
        del sessions[user_id]