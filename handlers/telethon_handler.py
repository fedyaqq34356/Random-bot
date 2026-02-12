import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.giveaway import TelethonStates, BroadcastStates
from keyboards.inline import (
    get_cancel_keyboard, get_main_menu_keyboard,
    get_giveaway_select_keyboard_manage, get_confirm_keyboard
)
from services.telethon_auth import start_auth, verify_code, verify_password, cancel_auth, sessions
from services.telethon_scanner import scan_and_add_participants, broadcast_giveaway
from database import db
from logger import logger

router = Router()


@router.callback_query(F.data == "broadcast")
async def broadcast_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    giveaways = db.get_active_giveaways(callback.from_user.id)
    if not giveaways:
        await callback.message.answer("У вас нет активных розыгрышей для рассылки")
        return

    await callback.message.answer(
        "Выберите розыгрыш для рассылки:",
        reply_markup=get_giveaway_select_keyboard_manage(giveaways)
    )
    await state.set_state(BroadcastStates.selecting_giveaway)


@router.callback_query(BroadcastStates.selecting_giveaway, F.data.startswith("mng_"))
async def broadcast_giveaway_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    giveaway_id = int(callback.data.split("_")[1])
    giveaway = db.get_giveaway(giveaway_id)

    await state.update_data(purpose="broadcast", giveaway_id=giveaway_id)

    if callback.from_user.id in sessions:
        client = sessions[callback.from_user.id]["client"]
        if client.is_connected() and await client.is_user_authorized():
            await _confirm_broadcast(callback.message, state)
            return

    await callback.message.answer(
        f"📢 Рассылка для розыгрыша:\n{giveaway['text'][:80]}...\n\n"
        "Для рассылки нужна авторизация вашего аккаунта.\n\n"
        "Получить API ID и API Hash: https://my.telegram.org/auth\n\n"
        "Введите API ID:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(BroadcastStates.api_id)


@router.message(BroadcastStates.api_id)
async def broadcast_api_id(message: Message, state: FSMContext):
    try:
        api_id = int(message.text.strip())
        await state.update_data(api_id=api_id)
        await message.answer("Введите API Hash:")
        await state.set_state(BroadcastStates.api_hash)
    except ValueError:
        await message.answer("❌ API ID должен быть числом")


@router.message(BroadcastStates.api_hash)
async def broadcast_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_hash=message.text.strip())
    await message.answer("Введите номер телефона (+380XXXXXXXXX):")
    await state.set_state(BroadcastStates.phone)


@router.message(BroadcastStates.phone)
async def broadcast_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    status, msg = await start_auth(message.from_user.id, data["api_id"], data["api_hash"], message.text.strip())

    if status == "already":
        await state.update_data(authed=True)
        await _confirm_broadcast(message, state)
    elif status == "code_sent":
        await message.answer(f"✅ {msg}\n\nВведите код (через пробел или без):")
        await state.set_state(BroadcastStates.code)
    else:
        await message.answer(f"❌ {msg}", reply_markup=get_cancel_keyboard())


@router.message(BroadcastStates.code)
async def broadcast_code(message: Message, state: FSMContext):
    code = message.text.strip().replace(" ", "")
    if not code.isdigit() or len(code) not in (5, 6):
        await message.answer("❌ Код должен содержать 5 или 6 цифр")
        return

    result, msg = await verify_code(message.from_user.id, code)

    if result == "success":
        await _confirm_broadcast(message, state)
    elif result == "2fa":
        await message.answer(msg)
        await state.set_state(BroadcastStates.password)
    elif result == "retry":
        await message.answer(f"❌ {msg}")
    else:
        await cancel_auth(message.from_user.id)
        await state.clear()
        await message.answer(f"❌ {msg}", reply_markup=get_main_menu_keyboard())


@router.message(BroadcastStates.password)
async def broadcast_password(message: Message, state: FSMContext):
    result, msg = await verify_password(message.from_user.id, message.text.strip())
    if result == "success":
        await _confirm_broadcast(message, state)
    else:
        await cancel_auth(message.from_user.id)
        await state.clear()
        await message.answer(f"❌ {msg}", reply_markup=get_main_menu_keyboard())


async def _confirm_broadcast(message: Message, state: FSMContext):
    data = await state.get_data()
    giveaway = db.get_giveaway(data["giveaway_id"])
    await message.answer(
        f"✅ Авторизация успешна!\n\n"
        f"Готов разослать сообщения всем участникам канала о розыгрыше:\n"
        f"{giveaway['text'][:80]}...\n\n"
        "⚠️ Рассылка занимает время (задержка между сообщениями). Начать?",
        reply_markup=get_confirm_keyboard()
    )
    await state.set_state(BroadcastStates.confirming)


@router.callback_query(BroadcastStates.confirming, F.data == "confirm_yes")
async def run_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    giveaway_id = data["giveaway_id"]
    giveaway = db.get_giveaway(giveaway_id)

    if callback.from_user.id not in sessions:
        await callback.message.answer("❌ Сессия истекла, начните заново", reply_markup=get_main_menu_keyboard())
        await state.clear()
        return

    client = sessions[callback.from_user.id]["client"]

    await callback.message.answer("🚀 Рассылка запущена, это может занять несколько минут...")

    channel_id = giveaway["channel_id"]
    message_id = giveaway.get("message_id")

    try:
        channel_info = await client.get_entity(channel_id)
        channel_username = getattr(channel_info, 'username', None)
    except Exception:
        channel_username = None

    sent, failed = await broadcast_giveaway(client, channel_id, message_id, channel_username)

    await state.clear()
    await callback.message.answer(
        f"✅ Рассылка завершена!\n\n"
        f"📨 Отправлено: {sent}\n"
        f"❌ Не удалось: {failed}",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(BroadcastStates.confirming, F.data == "confirm_no")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer("❌ Рассылка отменена", reply_markup=get_main_menu_keyboard())


@router.message(TelethonStates.api_id)
async def auto_api_id(message: Message, state: FSMContext):
    try:
        api_id = int(message.text.strip())
        await state.update_data(api_id=api_id)
        await message.answer("Введите API Hash:")
        await state.set_state(TelethonStates.api_hash)
    except ValueError:
        await message.answer("❌ API ID должен быть числом")


@router.message(TelethonStates.api_hash)
async def auto_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_hash=message.text.strip())
    await message.answer("Введите номер телефона (+380XXXXXXXXX):")
    await state.set_state(TelethonStates.phone)


@router.message(TelethonStates.phone)
async def auto_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    status, msg = await start_auth(message.from_user.id, data["api_id"], data["api_hash"], message.text.strip())

    if status in ("already", "code_sent"):
        if status == "already":
            await _run_auto_scan(message, state)
        else:
            await message.answer(f"✅ {msg}\n\nВведите код (через пробел или без):")
            await state.set_state(TelethonStates.code)
    else:
        await message.answer(f"❌ {msg}", reply_markup=get_cancel_keyboard())


@router.message(TelethonStates.code)
async def auto_code(message: Message, state: FSMContext):
    code = message.text.strip().replace(" ", "")
    if not code.isdigit() or len(code) not in (5, 6):
        await message.answer("❌ Код должен содержать 5 или 6 цифр")
        return

    result, msg = await verify_code(message.from_user.id, code)

    if result == "success":
        await _run_auto_scan(message, state)
    elif result == "2fa":
        await message.answer(msg)
        await state.set_state(TelethonStates.password)
    elif result == "retry":
        await message.answer(f"❌ {msg}")
    else:
        await cancel_auth(message.from_user.id)
        await state.clear()
        await message.answer(f"❌ {msg}", reply_markup=get_main_menu_keyboard())


@router.message(TelethonStates.password)
async def auto_password(message: Message, state: FSMContext):
    result, msg = await verify_password(message.from_user.id, message.text.strip())
    if result == "success":
        await _run_auto_scan(message, state)
    else:
        await cancel_auth(message.from_user.id)
        await state.clear()
        await message.answer(f"❌ {msg}", reply_markup=get_main_menu_keyboard())


async def _run_auto_scan(message: Message, state: FSMContext):
    data = await state.get_data()
    giveaway_id = data.get("giveaway_id")
    giveaway = db.get_giveaway(giveaway_id)

    if message.from_user.id not in sessions:
        await message.answer("❌ Сессия истекла", reply_markup=get_main_menu_keyboard())
        await state.clear()
        return

    client = sessions[message.from_user.id]["client"]

    await message.answer("🔍 Сканирую участников канала, подождите...")

    added = await scan_and_add_participants(client, giveaway_id, giveaway["channel_id"])

    await state.clear()
    await message.answer(
        f"✅ Готово! Добавлено участников: {added}\n"
        f"Всего в розыгрыше: {db.get_participants_count(giveaway_id)}",
        reply_markup=get_main_menu_keyboard()
    )