from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.giveaway import GiveawayStates, TelethonStates
from keyboards.inline import (
    get_cancel_keyboard, get_button_text_variants,
    get_channels_keyboard, get_publish_time_keyboard,
    get_end_condition_keyboard, get_channel_selection_keyboard,
    get_participate_keyboard_with_channels, get_main_menu_keyboard,
    get_participation_mode_keyboard
)
from database import db
from utils.time_utils import parse_datetime, get_example_times, get_current_time
from utils.channel_utils import check_user_is_admin, check_bot_is_admin, get_channel_info
from config import config
from logger import logger

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
    await message.answer(
        "✉️ Отправьте текст кнопки или выберите вариант:",
        reply_markup=get_button_text_variants()
    )
    await state.set_state(GiveawayStates.waiting_button_text)


@router.callback_query(GiveawayStates.waiting_button_text, F.data.startswith("btn_variant_"))
async def process_button_variant(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    variants = {
        "btn_variant_1": "Участвую!",
        "btn_variant_2": "Участвовать",
        "btn_variant_3": "Принять участие"
    }
    await state.update_data(button_text=variants[callback.data])
    await callback.message.answer("✅ Текст кнопки сохранен")
    await ask_for_participation_mode(callback.message, state)


@router.message(GiveawayStates.waiting_button_text)
async def process_custom_button_text(message: Message, state: FSMContext):
    await state.update_data(button_text=message.text)
    await message.answer("✅ Текст кнопки сохранен")
    await ask_for_participation_mode(message, state)


async def ask_for_participation_mode(message: Message, state: FSMContext):
    await message.answer(
        "👥 Выберите режим участия:\n\n"
        "🔘 Ручной — участники сами нажимают кнопку\n"
        "⚡️ Автоматический — все участники канала добавляются сразу (потребуется авторизация вашего аккаунта)",
        reply_markup=get_participation_mode_keyboard()
    )
    await state.set_state(GiveawayStates.waiting_participation_mode)


@router.callback_query(GiveawayStates.waiting_participation_mode, F.data == "mode_manual")
async def mode_manual(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(participation_mode="manual")
    await callback.message.answer("✅ Выбран ручной режим")
    await ask_for_main_channel(callback.message, state)


@router.callback_query(GiveawayStates.waiting_participation_mode, F.data == "mode_auto")
async def mode_auto(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(participation_mode="auto")
    await callback.message.answer("✅ Выбран автоматический режим")
    await ask_for_main_channel(callback.message, state)


async def ask_for_main_channel(message: Message, state: FSMContext):
    channels = db.get_admin_channels(message.from_user.id)
    if not channels:
        await message.answer(
            "📢 Добавьте бота в канал как администратора и отправьте @username или перешлите сообщение из канала:",
            reply_markup=get_cancel_keyboard()
        )
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
        except Exception:
            await message.answer("❌ Не удалось найти канал")
            return
    else:
        await message.answer("❌ Отправьте @username или перешлите сообщение из канала")
        return

    if not await check_user_is_admin(bot, channel_id, message.from_user.id):
        await message.answer("❌ Вы не являетесь администратором этого канала")
        return

    if not await check_bot_is_admin(bot, channel_id):
        await message.answer("❌ Бот не является администратором канала. Добавьте бота и попробуйте снова.")
        return

    await state.update_data(channel_id=channel_id)
    db.add_admin_channel(message.from_user.id, channel_id, channel_username)
    await message.answer(f"✅ Канал выбран: @{channel_username or channel_id}")
    await ask_for_additional_channels(message, state)


@router.callback_query(GiveawayStates.waiting_channel_selection, F.data.startswith("select_channel_"))
async def process_channel_selection(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    channel_id = int(callback.data.split("_")[2])

    if not await check_user_is_admin(bot, channel_id, callback.from_user.id):
        await callback.message.answer("❌ Вы не являетесь администратором этого канала")
        return

    if not await check_bot_is_admin(bot, channel_id):
        await callback.message.answer("❌ Бот не является администратором канала")
        return

    await state.update_data(channel_id=channel_id)
    await callback.message.answer("✅ Канал выбран")
    await ask_for_additional_channels(callback.message, state)


async def ask_for_additional_channels(message: Message, state: FSMContext):
    text = (
        "➕ Добавьте каналы для обязательной подписки (необязательно).\n\n"
        "❗️ Подписка на основной канал уже включена.\n\n"
        "Отправьте @username или перешлите сообщение из канала.\n\n"
        "Или нажмите кнопку для продолжения:"
    )
    data = await state.get_data()
    await message.answer(text, reply_markup=get_channels_keyboard(len(data.get('channels', []))))
    await state.update_data(channels=data.get('channels', []))
    await state.set_state(GiveawayStates.waiting_channels)


@router.callback_query(GiveawayStates.waiting_channels, F.data == "no_additional_channels")
async def skip_additional_channels(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    total = len(data.get('channels', [])) + 1
    await callback.message.answer(f"✅ Продолжаем с {total} обязательными подписками")
    await ask_for_winners_count(callback.message, state)


@router.callback_query(GiveawayStates.waiting_channels, F.data == "add_more_channels")
async def add_more_channels(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Отправьте @username канала или перешлите сообщение:",
        reply_markup=get_cancel_keyboard()
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
        except Exception:
            await message.answer("❌ Канал не найден")
            return
    else:
        await message.answer("❌ Отправьте @username или перешлите сообщение")
        return

    if not await check_bot_is_admin(bot, channel_id):
        await message.answer("❌ Бот не является администратором этого канала")
        return

    await state.update_data(temp_channel_id=channel_id, temp_channel_username=channel_username)
    await message.answer(
        f"✅ Канал найден: @{channel_username or channel_id}\n\n"
        "Теперь отправьте ссылку для подписки (например: https://t.me/your_channel):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(GiveawayStates.waiting_channel_link)


@router.message(GiveawayStates.waiting_channel_link)
async def process_channel_link(message: Message, state: FSMContext):
    link = message.text.strip()
    
    if not link.startswith('http'):
        await message.answer("❌ Ссылка должна начинаться с http:// или https://")
        return

    data = await state.get_data()
    channels = data.get('channels', [])
    
    channels.append({
        'channel_id': data['temp_channel_id'],
        'link': link
    })
    
    await state.update_data(channels=channels)
    
    await message.answer(
        f"✅ Канал добавлен с ссылкой: {link}",
        reply_markup=get_channels_keyboard(len(channels))
    )
    await state.set_state(GiveawayStates.waiting_channels)

async def ask_for_winners_count(message: Message, state: FSMContext):
    await message.answer("🏆 Сколько победителей?", reply_markup=get_cancel_keyboard())
    await state.set_state(GiveawayStates.waiting_winners_count)


@router.message(GiveawayStates.waiting_winners_count)
async def process_winners_count(message: Message, state: FSMContext):
    try:
        count = int(message.text)
        if count < 1:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите число от 1 и выше")
        return

    await state.update_data(winners_count=count)
    await message.answer(f"✅ Победителей: {count}")
    await message.answer(
        f"⏳ Когда публиковать розыгрыш?\n\nБот работает по ({config.GMT_OFFSET}) {config.TIMEZONE}",
        reply_markup=get_publish_time_keyboard()
    )
    await state.set_state(GiveawayStates.waiting_publish_time)


@router.callback_query(GiveawayStates.waiting_publish_time, F.data == "publish_now")
async def publish_now(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(publish_time=None)
    await callback.message.answer("✅ Публикуем сразу")
    await ask_end_condition(callback.message, state)


@router.callback_query(GiveawayStates.waiting_publish_time, F.data == "schedule_publish")
async def schedule_publish(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        f"📅 Укажите дату и время публикации (дд.мм.гггг чч:мм)\n\n"
        f"Примеры:\n{get_example_times(config.TIMEZONE)}",
        reply_markup=get_cancel_keyboard()
    )


@router.message(GiveawayStates.waiting_publish_time)
async def process_publish_time(message: Message, state: FSMContext):
    dt = parse_datetime(message.text, config.TIMEZONE)
    if not dt:
        await message.answer("❌ Неверный формат. Используйте: дд.мм.гггг чч:мм")
        return
    if dt <= get_current_time(config.TIMEZONE):
        await message.answer("❌ Время должно быть в будущем")
        return
    await state.update_data(publish_time=dt.isoformat())
    await message.answer("✅ Время публикации выбрано")
    await ask_end_condition(message, state)


async def ask_end_condition(message: Message, state: FSMContext):
    await message.answer("✍️ Как завершить розыгрыш?", reply_markup=get_end_condition_keyboard())
    await state.set_state(GiveawayStates.waiting_end_condition)


@router.callback_query(GiveawayStates.waiting_end_condition, F.data == "end_by_time")
async def end_by_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(end_type="time")
    await callback.message.answer(
        f"⏰ Когда завершить? (дд.мм.гггг чч:мм)\n\nПримеры:\n{get_example_times(config.TIMEZONE)}",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(GiveawayStates.waiting_end_value)


@router.callback_query(GiveawayStates.waiting_end_condition, F.data == "end_by_count")
async def end_by_count(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(end_type="count")
    await callback.message.answer(
        "👥 Сколько участников нужно для завершения?",
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
            await message.answer("❌ Неверный формат. Используйте: дд.мм.гггг чч:мм")
            return
        if dt <= get_current_time(config.TIMEZONE):
            await message.answer("❌ Время должно быть в будущем")
            return
        end_value = dt.isoformat()
        await message.answer(f"✅ Завершение: {message.text}")
    else:
        try:
            count = int(message.text)
            if count < 1:
                raise ValueError
            end_value = str(count)
            await message.answer(f"✅ Завершение при {count} участниках")
        except ValueError:
            await message.answer("❌ Введите корректное число")
            return

    giveaway_id = db.create_giveaway(
        admin_id=message.from_user.id,
        text=data['text'],
        button_text=data['button_text'],
        channels=data.get('channels', []),
        winners_count=data['winners_count'],
        channel_id=data['channel_id'],
        publish_time=data.get('publish_time'),
        end_type=end_type,
        end_value=end_value,
        participation_mode=data.get('participation_mode', 'manual')
    )

    if data.get('publish_time'):
        await message.answer("✅ Розыгрыш создан! Будет опубликован в запланированное время.", reply_markup=get_main_menu_keyboard())
        await state.clear()
    else:
        await publish_giveaway(bot, giveaway_id)

        if data.get('participation_mode') == 'auto':
            await message.answer("✅ Розыгрыш создан и опубликован!")
            await state.set_state(TelethonStates.api_id)
            await state.update_data(giveaway_id=giveaway_id, purpose="auto")
            await message.answer(
                "⚡️ Теперь авторизуйте свой аккаунт для сканирования участников канала.\n\n"
                "Получить API ID и API Hash: https://my.telegram.org/auth\n\n"
                "Введите API ID:",
                reply_markup=get_cancel_keyboard()
            )
        else:
            await message.answer("✅ Розыгрыш создан и опубликован!", reply_markup=get_main_menu_keyboard())
            await state.clear()


async def publish_giveaway(bot: Bot, giveaway_id: int):
    giveaway = db.get_giveaway(giveaway_id)
    if not giveaway:
        return

    channels_info = []
    for ch in giveaway.get('channels', []):
        if isinstance(ch, dict):
            channels_info.append({
                'id': ch['channel_id'],
                'link': ch['link']
            })
        else:
            try:
                info = await get_channel_info(bot, ch)
                if info:
                    if info.get('username'):
                        link = f"https://t.me/{info['username']}"
                    else:
                        clean_id = str(ch).replace('-100', '')
                        link = f"https://t.me/c/{clean_id}"
                    channels_info.append({
                        'id': ch,
                        'link': link
                    })
            except Exception as e:
                logger.error(f"Ошибка канала {ch}: {e}")

    keyboard = get_participate_keyboard_with_channels(
        giveaway_id, giveaway['button_text'], channels_info
    )

    sent = await bot.send_message(
        chat_id=giveaway['channel_id'],
        text=giveaway['text'],
        reply_markup=keyboard
    )

    db.update_giveaway_message_id(giveaway_id, sent.message_id)
    db.update_giveaway_status(giveaway_id, 'published')