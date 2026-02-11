from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.giveaway import GiveawayStates
from keyboards.inline import (
    get_cancel_keyboard, get_button_text_variants,
    get_channels_keyboard, get_publish_time_keyboard,
    get_end_condition_keyboard, get_channel_selection_keyboard,
    get_participate_keyboard_with_channels, get_main_menu_keyboard
)
from database import db
from utils.time_utils import parse_datetime, get_example_times, get_current_time
from utils.channel_utils import check_user_is_admin, check_bot_is_admin, get_channel_info
from config import config

router = Router()

@router.callback_query(F.data == "create_giveaway")
async def start_creating_giveaway(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    text = (
        "Создание розыгрыша:\n\n"
        "✉️ Отправьте текст для розыгрыша.\n\n"
        "Бот для проведения конкурсов полностью бесплатный, прозрачный и ему будет приятно, "
        "если в конкурсном посте Вы укажите на него ссылку, спасибо. @randomizergod1488_bot"
    )
    
    await callback.message.answer(text, reply_markup=get_cancel_keyboard())
    await state.set_state(GiveawayStates.waiting_text)

@router.message(GiveawayStates.waiting_text)
async def process_giveaway_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("✅ Текст добавлен")
    
    text = "✉️ Отправьте текст, который будет отображаться на кнопке, или выберите один из вариантов кнопкой:"
    
    await message.answer(text, reply_markup=get_button_text_variants())
    await state.set_state(GiveawayStates.waiting_button_text)

@router.callback_query(GiveawayStates.waiting_button_text, F.data.startswith("btn_variant_"))
async def process_button_variant(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    variants = {
        "btn_variant_1": "Участвую!",
        "btn_variant_2": "Участвовать",
        "btn_variant_3": "Принять участие"
    }
    
    button_text = variants[callback.data]
    await state.update_data(button_text=button_text)
    
    await callback.message.answer("✅ Текст кнопки сохранен")
    await ask_for_main_channel(callback.message, state)

@router.message(GiveawayStates.waiting_button_text)
async def process_custom_button_text(message: Message, state: FSMContext):
    await state.update_data(button_text=message.text)
    await message.answer("✅ Текст кнопки сохранен")
    await ask_for_main_channel(message, state)

async def ask_for_main_channel(message: Message, state: FSMContext):
    channels = db.get_admin_channels(message.from_user.id)
    
    if not channels:
        text = (
            "📢 Сначала добавьте бота в канал, где будет проходить розыгрыш.\n\n"
            "1. Добавьте бота как администратора в ваш канал\n"
            "2. Отправьте @username канала или перешлите сообщение из канала"
        )
        await message.answer(text, reply_markup=get_cancel_keyboard())
        await state.set_state(GiveawayStates.waiting_main_channel)
    else:
        await message.answer(
            "📢 В каком канале публикуем розыгрыш?",
            reply_markup=get_channel_selection_keyboard(channels)
        )
        await state.set_state(GiveawayStates.waiting_channel_selection)

@router.message(GiveawayStates.waiting_main_channel)
async def process_main_channel(message: Message, state: FSMContext, bot: Bot):
    channel_username = None
    channel_id = None
    
    if message.forward_from_chat:
        channel_id = message.forward_from_chat.id
        channel_username = message.forward_from_chat.username
    elif message.text and message.text.startswith('@'):
        channel_username = message.text[1:]
        try:
            chat = await bot.get_chat(f"@{channel_username}")
            channel_id = chat.id
        except:
            await message.answer("❌ Не удалось найти канал. Проверьте правильность username.")
            return
    else:
        await message.answer("❌ Пожалуйста, отправьте канал в формате @username или перешлите сообщение из канала.")
        return
    
    is_user_admin = await check_user_is_admin(bot, channel_id, message.from_user.id)
    if not is_user_admin:
        await message.answer("❌ Вы не являетесь администратором этого канала")
        return
    
    is_bot_admin = await check_bot_is_admin(bot, channel_id)
    if not is_bot_admin:
        await message.answer(
            "❌ Бот был удален из канала или не является администратором. "
            "Добавьте бота в канал как администратора и попробуйте снова."
        )
        return
    
    await state.update_data(channel_id=channel_id)
    db.add_admin_channel(message.from_user.id, channel_id, channel_username)
    
    await message.answer(f"✅ Основной канал выбран: @{channel_username if channel_username else channel_id}")
    await ask_for_additional_channels(message, state)

@router.callback_query(GiveawayStates.waiting_channel_selection, F.data.startswith("select_channel_"))
async def process_channel_selection(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    
    channel_id = int(callback.data.split("_")[2])
    
    is_user_admin = await check_user_is_admin(bot, channel_id, callback.from_user.id)
    if not is_user_admin:
        await callback.message.answer("❌ Вы не являетесь администратором этого канала")
        return
    
    is_bot_admin = await check_bot_is_admin(bot, channel_id)
    if not is_bot_admin:
        await callback.message.answer("❌ Бот был удален из канала или не является администратором")
        return
    
    await state.update_data(channel_id=channel_id)
    await callback.message.answer("✅ Основной канал выбран")
    await ask_for_additional_channels(callback.message, state)

async def ask_for_additional_channels(message: Message, state: FSMContext):
    text = (
        "➕ Добавьте дополнительные каналы для проверки подписки (необязательно).\n\n"
        "❗️Подписка на основной канал обязательна по умолчанию.\n\n"
        "Чтобы добавить канал:\n"
        "1. Добавьте бота как администратора в канал\n"
        "2. Отправьте @username канала или перешлите сообщение\n\n"
        "💬 Или нажмите кнопку для продолжения:"
    )
    
    await message.answer(text, reply_markup=get_channels_keyboard())
    await state.update_data(channels=[])
    await state.set_state(GiveawayStates.waiting_channels)

@router.callback_query(GiveawayStates.waiting_channels, F.data == "no_additional_channels")
async def skip_additional_channels(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("✅ Продолжаем с одной обязательной подпиской")
    await ask_for_winners_count(callback.message, state)

@router.callback_query(GiveawayStates.waiting_channels, F.data == "add_more_channels")
async def add_more_channels(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Отправьте @username канала или перешлите сообщение из канала:",
        reply_markup=get_channels_keyboard()
    )

@router.message(GiveawayStates.waiting_channels)
async def process_additional_channel(message: Message, state: FSMContext, bot: Bot):
    channel_username = None
    channel_id = None
    
    if message.forward_from_chat:
        channel_id = message.forward_from_chat.id
        channel_username = message.forward_from_chat.username
    elif message.text and message.text.startswith('@'):
        channel_username = message.text[1:]
        try:
            chat = await bot.get_chat(f"@{channel_username}")
            channel_id = chat.id
        except:
            await message.answer("❌ Не удалось найти канал. Проверьте правильность username.")
            return
    else:
        await message.answer("❌ Пожалуйста, отправьте канал в формате @username или перешлите сообщение из канала.")
        return
    
    is_bot_admin = await check_bot_is_admin(bot, channel_id)
    if not is_bot_admin:
        await message.answer(
            "❌ Бот был удален из канала или не является администратором. "
            "Добавьте бота в канал как администратора и попробуйте снова."
        )
        return
    
    data = await state.get_data()
    channels = data.get('channels', [])
    channels.append(channel_id)
    await state.update_data(channels=channels)
    
    await message.answer(
        f"✅ Канал добавлен: @{channel_username if channel_username else channel_id}\n\n"
        "Добавьте еще или нажмите кнопку для продолжения:",
        reply_markup=get_channels_keyboard()
    )

async def ask_for_winners_count(message: Message, state: FSMContext):
    await message.answer("🏆 Сколько победителей выбрать боту?", reply_markup=get_cancel_keyboard())
    await state.set_state(GiveawayStates.waiting_winners_count)

@router.message(GiveawayStates.waiting_winners_count)
async def process_winners_count(message: Message, state: FSMContext):
    try:
        count = int(message.text)
        if count < 1:
            raise ValueError
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число (от 1 и выше)")
        return
    
    await state.update_data(winners_count=count)
    await message.answer(f"✅ Количество победителей сохранено: {count}")
    
    text = (
        f"⏳ Когда нужно опубликовать розыгрыш?\n\n"
        f"Бот живет по времени ({config.GMT_OFFSET}) {config.TIMEZONE}"
    )
    
    await message.answer(text, reply_markup=get_publish_time_keyboard())
    await state.set_state(GiveawayStates.waiting_publish_time)

@router.callback_query(GiveawayStates.waiting_publish_time, F.data == "publish_now")
async def publish_now(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(publish_time=None)
    await callback.message.answer("✅ Время публикации выбрано")
    await ask_end_condition(callback.message, state)

@router.callback_query(GiveawayStates.waiting_publish_time, F.data == "schedule_publish")
async def schedule_publish(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    text = (
        f"🔚 Когда нужно опубликовать розыгрыш?\n\n"
        f"Укажите время в формате дд.мм.гг чч:мм\n\n"
        f"Бот живет по времени ({config.GMT_OFFSET}) {config.TIMEZONE}\n\n"
        f"Примеры:\n{get_example_times(config.TIMEZONE)}"
    )
    
    await callback.message.answer(text, reply_markup=get_cancel_keyboard())

@router.message(GiveawayStates.waiting_publish_time)
async def process_publish_time(message: Message, state: FSMContext):
    dt = parse_datetime(message.text, config.TIMEZONE)
    
    if not dt:
        await message.answer("❌ Неверный формат времени. Используйте формат: дд.мм.гггг чч:мм")
        return
    
    if dt <= get_current_time(config.TIMEZONE):
        await message.answer("❌ Время публикации должно быть в будущем")
        return
    
    await state.update_data(publish_time=dt.isoformat())
    await message.answer("✅ Время публикации выбрано")
    await ask_end_condition(message, state)

async def ask_end_condition(message: Message, state: FSMContext):
    text = "✍️ Как завершить розыгрыш?"
    await message.answer(text, reply_markup=get_end_condition_keyboard())
    await state.set_state(GiveawayStates.waiting_end_condition)

@router.callback_query(GiveawayStates.waiting_end_condition, F.data == "end_by_time")
async def end_by_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(end_type="time")
    
    text = (
        f"⏰ Когда завершить розыгрыш?\n\n"
        f"Укажите время в формате дд.мм.гг чч:мм\n\n"
        f"Примеры:\n{get_example_times(config.TIMEZONE)}"
    )
    
    await callback.message.answer(text, reply_markup=get_cancel_keyboard())
    await state.set_state(GiveawayStates.waiting_end_value)

@router.callback_query(GiveawayStates.waiting_end_condition, F.data == "end_by_count")
async def end_by_count(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(end_type="count")
    
    await callback.message.answer(
        "👥 Введите количество участников для завершения розыгрыша:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(GiveawayStates.waiting_end_value)

@router.message(GiveawayStates.waiting_end_value)
async def process_end_value(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    end_type = data.get('end_type')
    
    if end_type == "time":
        dt = parse_datetime(message.text, config.TIMEZONE)
        if not dt:
            await message.answer("❌ Неверный формат времени. Используйте формат: дд.мм.гггг чч:мм")
            return
        
        if dt <= get_current_time(config.TIMEZONE):
            await message.answer("❌ Время завершения должно быть в будущем")
            return
        
        end_value = dt.isoformat()
        await message.answer(f"✅ Время подведения результатов: {message.text}")
    else:
        try:
            count = int(message.text)
            if count < 1:
                raise ValueError
            end_value = str(count)
            await message.answer(f"✅ Количество участников для подведения результатов сохранено: {count}")
        except ValueError:
            await message.answer("❌ Пожалуйста, введите корректное число")
            return
    
    await state.update_data(end_value=end_value)
    
    giveaway_id = db.create_giveaway(
        admin_id=message.from_user.id,
        text=data['text'],
        button_text=data['button_text'],
        channels=data.get('channels', []),
        winners_count=data['winners_count'],
        channel_id=data['channel_id'],
        publish_time=data.get('publish_time'),
        end_type=end_type,
        end_value=end_value
    )
    
    await publish_giveaway(bot, giveaway_id)
    
    await message.answer(
        "✅ Розыгрыш создан и опубликован!",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

async def publish_giveaway(bot: Bot, giveaway_id: int):
    giveaway = db.get_giveaway(giveaway_id)
    
    if not giveaway:
        return
    
    text = giveaway['text']
    
    channels_info = []
    for channel_id in giveaway.get('channels', []):
        try:
            channel_info = await get_channel_info(bot, channel_id)
            if channel_info:
                channels_info.append(channel_info)
        except Exception as e:
            print(f"Ошибка получения информации о канале {channel_id}: {e}")
    
    keyboard = get_participate_keyboard_with_channels(
        giveaway_id, 
        giveaway['button_text'],
        channels_info
    )
    
    sent_message = await bot.send_message(
        chat_id=giveaway['channel_id'],
        text=text,
        reply_markup=keyboard
    )
    
    db.update_giveaway_message_id(giveaway_id, sent_message.message_id)
    db.update_giveaway_status(giveaway_id, 'published')