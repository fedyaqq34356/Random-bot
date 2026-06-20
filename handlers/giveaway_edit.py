from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from states.giveaway import GiveawayStates
from keyboards.inline import (
    get_giveaway_select_keyboard_edit, get_edit_menu_keyboard,
    get_cancel_keyboard, get_participate_keyboard_with_channels
)
from database import db
from utils.time_utils import parse_datetime, get_current_time
from utils.channel_utils import get_channel_info
from config import config
from logger import logger

router = Router()


async def _update_channel_message(bot: Bot, giveaway_id: int):
    giveaway = db.get_giveaway(giveaway_id)
    if not giveaway or not giveaway.get('message_id'):
        return

    channels_info = []
    for ch_id in giveaway.get('channels', []):
        info = await get_channel_info(bot, ch_id)
        if info:
            channels_info.append(info)

    keyboard = get_participate_keyboard_with_channels(
        giveaway_id, giveaway['button_text'], channels_info
    )

    try:
        await bot.edit_message_text(
            chat_id=giveaway['channel_id'],
            message_id=giveaway['message_id'],
            text=giveaway['text'],
            reply_markup=keyboard
        )
    except TelegramBadRequest as e:
        logger.warning(f"Не удалось обновить сообщение в канале: {e}")


@router.callback_query(F.data == "edit_giveaway")
async def edit_giveaway_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    all_giveaways = db.get_admin_giveaways(callback.from_user.id)
    giveaways = [g for g in all_giveaways if g['status'] in ('draft', 'published')]

    if not giveaways:
        await callback.message.answer("У вас нет розыгрышей для редактирования")
        return

    await callback.message.answer(
        "Выберите розыгрыш для редактирования:",
        reply_markup=get_giveaway_select_keyboard_edit(giveaways)
    )
    await state.set_state(GiveawayStates.selecting_giveaway_to_edit)


@router.callback_query(GiveawayStates.selecting_giveaway_to_edit, F.data.startswith("edt_"))
async def select_giveaway_to_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    giveaway_id = int(callback.data.split("_")[1])
    await state.update_data(editing_giveaway_id=giveaway_id)

    giveaway = db.get_giveaway(giveaway_id)
    text = (
        f"📝 Редактирование розыгрыша ID {giveaway_id}:\n\n"
        f"{giveaway['text'][:100]}...\n\n"
        f"Победителей: {giveaway['winners_count']}\n"
        f"Кнопка: {giveaway['button_text']}\n\n"
        "Что хотите изменить?"
    )

    await callback.message.answer(text, reply_markup=get_edit_menu_keyboard())
    await state.set_state(GiveawayStates.editing_giveaway)


@router.callback_query(GiveawayStates.editing_giveaway, F.data == "edit_text")
async def edit_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "✉️ Отправьте новый текст розыгрыша:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(GiveawayStates.editing_text)


@router.message(GiveawayStates.editing_text)
async def process_new_text(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    giveaway_id = data.get('editing_giveaway_id')

    db.update_giveaway_text(giveaway_id, message.text)
    await _update_channel_message(bot, giveaway_id)
    await message.answer("✅ Текст обновлен и сообщение в канале изменено")

    await state.set_state(GiveawayStates.editing_giveaway)
    giveaway = db.get_giveaway(giveaway_id)
    await message.answer(
        f"📝 Розыгрыш ID {giveaway_id}. Что ещё изменить?",
        reply_markup=get_edit_menu_keyboard()
    )


@router.callback_query(GiveawayStates.editing_giveaway, F.data == "edit_winners_count")
async def edit_winners_count(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "🏆 Введите новое количество победителей:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(GiveawayStates.editing_winners_count)


@router.message(GiveawayStates.editing_winners_count)
async def process_new_winners_count(message: Message, state: FSMContext):
    try:
        count = int(message.text)
        if count < 1:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите корректное число")
        return

    data = await state.get_data()
    giveaway_id = data.get('editing_giveaway_id')

    db.update_giveaway_winners_count(giveaway_id, count)
    await message.answer(f"✅ Количество победителей обновлено: {count}")

    await state.set_state(GiveawayStates.editing_giveaway)
    await message.answer(
        f"📝 Розыгрыш ID {giveaway_id}. Что ещё изменить?",
        reply_markup=get_edit_menu_keyboard()
    )


@router.callback_query(GiveawayStates.editing_giveaway, F.data == "edit_button_text")
async def edit_button_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "🔘 Введите новый текст кнопки:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(GiveawayStates.editing_button_text)


@router.message(GiveawayStates.editing_button_text)
async def process_new_button_text(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    giveaway_id = data.get('editing_giveaway_id')

    db.update_giveaway_button_text(giveaway_id, message.text)
    await _update_channel_message(bot, giveaway_id)
    await message.answer("✅ Текст кнопки обновлен и сообщение в канале изменено")

    await state.set_state(GiveawayStates.editing_giveaway)
    await message.answer(
        f"📝 Розыгрыш ID {giveaway_id}. Что ещё изменить?",
        reply_markup=get_edit_menu_keyboard()
    )


@router.callback_query(GiveawayStates.editing_giveaway, F.data == "edit_end_time")
async def edit_end_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    giveaway_id = data.get('editing_giveaway_id')
    giveaway = db.get_giveaway(giveaway_id)

    if giveaway['end_type'] != 'time':
        await callback.message.answer("❌ Этот розыгрыш завершается по количеству участников, а не по времени")
        return

    await callback.message.answer(
        "⏰ Введите новое время завершения (дд.мм.гггг чч:мм):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(GiveawayStates.editing_end_time)


@router.message(GiveawayStates.editing_end_time)
async def process_new_end_time(message: Message, state: FSMContext):
    dt = parse_datetime(message.text, config.TIMEZONE)

    if not dt:
        await message.answer("❌ Неверный формат. Используйте: дд.мм.гггг чч:мм")
        return

    if dt <= get_current_time(config.TIMEZONE):
        await message.answer("❌ Время должно быть в будущем")
        return

    data = await state.get_data()
    giveaway_id = data.get('editing_giveaway_id')

    db.update_giveaway_end_value(giveaway_id, dt.isoformat())
    await message.answer("✅ Время завершения обновлено")

    await state.set_state(GiveawayStates.editing_giveaway)
    await message.answer(
        f"📝 Розыгрыш ID {giveaway_id}. Что ещё изменить?",
        reply_markup=get_edit_menu_keyboard()
    )