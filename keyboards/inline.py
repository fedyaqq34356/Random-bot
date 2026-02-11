from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать розыгрыш", callback_data="create_giveaway")],
        [InlineKeyboardButton(text="Мои розыгрыши", callback_data="my_giveaways")],
        [InlineKeyboardButton(text="Мои каналы", callback_data="my_channels")]
    ])

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

def get_channels_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Продолжить с одной обязательной подпиской", callback_data="no_additional_channels")],
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
    
    if channels_info:
        for channel in channels_info:
            if channel.get('username'):
                channel_url = f"https://t.me/{channel['username']}"
                channel_name = channel.get('title', f"@{channel['username']}")
                buttons.append([
                    InlineKeyboardButton(
                        text=f"📢 Подписаться: {channel_name}", 
                        url=channel_url
                    )
                ])
    
    buttons.append([
        InlineKeyboardButton(text=button_text, callback_data=f"participate_{giveaway_id}")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_channel_selection_keyboard(channels: list):
    buttons = []
    for channel in channels:
        channel_name = channel.get('channel_username', f"ID: {channel['channel_id']}")
        buttons.append([InlineKeyboardButton(
            text=channel_name, 
            callback_data=f"select_channel_{channel['channel_id']}"
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)