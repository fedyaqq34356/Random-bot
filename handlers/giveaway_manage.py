from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.giveaway import GiveawayStates
from keyboards.inline import (
    get_giveaway_select_keyboard_manage, get_manage_participants_keyboard,
    get_participants_list_keyboard, get_cancel_keyboard
)
from database import db
from logger import logger

router = Router()


@router.callback_query(F.data == "manage_participants")
async def manage_participants_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    giveaways = db.get_active_giveaways(callback.from_user.id)

    if not giveaways:
        await callback.message.answer("У вас нет активных розыгрышей")
        return

    await callback.message.answer(
        "Выберите розыгрыш для управления участниками:",
        reply_markup=get_giveaway_select_keyboard_manage(giveaways)
    )
    await state.set_state(GiveawayStates.selecting_giveaway_to_manage)


@router.callback_query(GiveawayStates.selecting_giveaway_to_manage, F.data.startswith("mng_"))
async def select_giveaway_to_manage(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    giveaway_id = int(callback.data.split("_")[1])
    await state.update_data(managing_giveaway_id=giveaway_id)

    await _show_manage_menu(callback.message, giveaway_id)
    await state.set_state(GiveawayStates.managing_participants)


async def _show_manage_menu(message, giveaway_id: int):
    giveaway = db.get_giveaway(giveaway_id)
    count = db.get_participants_count(giveaway_id)
    text = (
        f"📊 Розыгрыш: {giveaway['text'][:50]}...\n"
        f"👥 Участников: {count}\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=get_manage_participants_keyboard())


@router.callback_query(GiveawayStates.managing_participants, F.data == "add_participant")
async def add_participant_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "👤 Отправьте ID пользователя для добавления:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(GiveawayStates.waiting_participant_to_add)


@router.message(GiveawayStates.waiting_participant_to_add)
async def add_participant_process(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    giveaway_id = data.get('managing_giveaway_id')

    user_id = None
    username = None

    if message.text.startswith('@'):
        username = message.text[1:]
        try:
            user = await bot.get_chat(f"@{username}")
            user_id = user.id
        except Exception:
            await message.answer("❌ Не удалось найти пользователя")
            return
    else:
        try:
            user_id = int(message.text)
        except ValueError:
            await message.answer("❌ Неверный формат.Отправтье ID")
            return

    success = db.add_participant(giveaway_id, user_id, username)
    if success:
        await message.answer(f"✅ Участник добавлен. Всего: {db.get_participants_count(giveaway_id)}")
    else:
        await message.answer("ℹ️ Участник уже в списке")

    await _show_manage_menu(message, giveaway_id)
    await state.set_state(GiveawayStates.managing_participants)


@router.callback_query(GiveawayStates.managing_participants, F.data == "view_participants")
async def view_participants(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    giveaway_id = data.get('managing_giveaway_id')
    participants = db.get_participants(giveaway_id)

    if not participants:
        await callback.message.answer("Нет участников")
        return

    await state.update_data(current_page=0)
    await _show_participants_page(callback.message, giveaway_id, 0, view_only=True)
    await state.set_state(GiveawayStates.viewing_participants)


@router.callback_query(GiveawayStates.managing_participants, F.data == "remove_participant")
async def remove_participant_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    giveaway_id = data.get('managing_giveaway_id')
    participants = db.get_participants(giveaway_id)

    if not participants:
        await callback.message.answer("Нет участников для удаления")
        return

    await state.update_data(current_page=0)
    await _show_participants_page(callback.message, giveaway_id, 0, view_only=False)
    await state.set_state(GiveawayStates.removing_participant)


async def _show_participants_page(message, giveaway_id: int, page: int, view_only: bool = False):
    participants = db.get_participants(giveaway_id)
    page_size = 10
    total_pages = max(1, (len(participants) + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))

    start = page * page_size
    page_participants = participants[start:start + page_size]

    text = f"👥 Участники (стр. {page + 1}/{total_pages}):\n\n"
    for p in page_participants:
        uname = f"@{p['username']}" if p.get('username') else f"ID: {p['user_id']}"
        text += f"• {uname}\n"

    await message.answer(
        text,
        reply_markup=get_participants_list_keyboard(page_participants, page, total_pages, view_only)
    )


@router.callback_query(GiveawayStates.removing_participant, F.data.startswith("remove_user_"))
async def remove_participant_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    giveaway_id = data.get('managing_giveaway_id')

    success = db.remove_participant(giveaway_id, user_id)
    if success:
        await callback.message.answer("✅ Участник удалён")
    else:
        await callback.message.answer("❌ Ошибка при удалении")

    page = data.get('current_page', 0)
    participants = db.get_participants(giveaway_id)
    if participants:
        await _show_participants_page(callback.message, giveaway_id, page, view_only=False)
    else:
        await callback.message.answer("Список пуст")
        await _show_manage_menu(callback.message, giveaway_id)
        await state.set_state(GiveawayStates.managing_participants)


@router.callback_query(GiveawayStates.removing_participant, F.data.startswith("pg_"))
async def remove_change_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    page = int(callback.data.split("_")[1])
    data = await state.get_data()
    await state.update_data(current_page=page)
    await _show_participants_page(callback.message, data.get('managing_giveaway_id'), page, view_only=False)


@router.callback_query(GiveawayStates.viewing_participants, F.data.startswith("pg_"))
async def view_change_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    page = int(callback.data.split("_")[1])
    data = await state.get_data()
    await state.update_data(current_page=page)
    await _show_participants_page(callback.message, data.get('managing_giveaway_id'), page, view_only=True)


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()