from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать розыгрыш", callback_data="create_giveaway")],
        [InlineKeyboardButton(text="Мои розыгрыши", callback_data="my_giveaways")],
        [InlineKeyboardButton(text="Мои каналы", callback_data="my_channels")],
        [InlineKeyboardButton(text="👥 Управление участниками", callback_data="manage_participants")],
        [InlineKeyboardButton(text="✏️ Редактировать розыгрыш", callback_data="edit_giveaway")]
    ])


def get_user_greeting_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[])


def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


def get_button_text_variants():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Участвую!", callback_data="btn_variant_1")],
        [InlineKeyboardButton(text="Участвовать", callback_data="btn_variant_2")],
        [InlineKeyboardButton(text="Принять участие", callback_data="btn_variant_3")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


def get_participation_mode_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔘 Ручной режим", callback_data="mode_manual")],
        [InlineKeyboardButton(text="⚡️ Автоматический", callback_data="mode_auto")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


def get_channels_keyboard(additional_count: int = 0):
    total = additional_count + 1
    if total == 1:
        btn_text = "✅ Продолжить с 1 обязательной подпиской"
    else:
        btn_text = f"✅ Продолжить с {total} обязательными подписками"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_text, callback_data="no_additional_channels")],
        [InlineKeyboardButton(text="➕ Добавить еще канал", callback_data="add_more_channels")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


def get_publish_time_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Прямо сейчас", callback_data="publish_now")],
        [InlineKeyboardButton(text="📅 Запланировать публикацию", callback_data="schedule_publish")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


def get_end_condition_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ По времени", callback_data="end_by_time")],
        [InlineKeyboardButton(text="👥 По количеству участников", callback_data="end_by_count")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


def get_participate_keyboard(giveaway_id: int, button_text: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, callback_data=f"participate_{giveaway_id}")]
    ])


def get_participate_keyboard_with_channels(giveaway_id: int, button_text: str, channels_info: list):
    buttons = []
    for channel in channels_info:
        if channel.get('username'):
            buttons.append([InlineKeyboardButton(
                text=f"📢 Подписаться: {channel.get('title', channel['username'])}",
                url=f"https://t.me/{channel['username']}"
            )])
    buttons.append([InlineKeyboardButton(
        text=button_text, callback_data=f"participate_{giveaway_id}"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_channel_selection_keyboard(channels: list):
    buttons = []
    for channel in channels:
        name = channel.get('channel_username') or f"ID: {channel['channel_id']}"
        buttons.append([InlineKeyboardButton(
            text=name,
            callback_data=f"select_channel_{channel['channel_id']}"
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def get_giveaway_select_keyboard_manage(giveaways: list):
    buttons = []
    for g in giveaways:
        buttons.append([InlineKeyboardButton(
            text=f"ID {g['id']}: {g['text'][:35]}...",
            callback_data=f"mng_{g['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_manage_participants_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить участника", callback_data="add_participant")],
        [InlineKeyboardButton(text="➖ Удалить участника", callback_data="remove_participant")],
        [InlineKeyboardButton(text="👥 Просмотр участников", callback_data="view_participants")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


def get_participants_list_keyboard(participants: list, page: int, total_pages: int, view_only: bool = False):
    buttons = []
    for p in participants:
        uname = f"@{p['username']}" if p.get('username') else f"ID: {p['user_id']}"
        if not view_only:
            buttons.append([InlineKeyboardButton(
                text=f"❌ {uname}",
                callback_data=f"remove_user_{p['user_id']}"
            )])
        else:
            buttons.append([InlineKeyboardButton(
                text=uname,
                callback_data="noop"
            )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"pg_{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"pg_{page + 1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def get_giveaway_select_keyboard_edit(giveaways: list):
    buttons = []
    for g in giveaways:
        buttons.append([InlineKeyboardButton(
            text=f"ID {g['id']}: {g['text'][:35]}...",
            callback_data=f"edt_{g['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_edit_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Изменить текст", callback_data="edit_text")],
        [InlineKeyboardButton(text="🏆 Кол-во победителей", callback_data="edit_winners_count")],
        [InlineKeyboardButton(text="🔘 Текст кнопки", callback_data="edit_button_text")],
        [InlineKeyboardButton(text="⏰ Время завершения", callback_data="edit_end_time")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])