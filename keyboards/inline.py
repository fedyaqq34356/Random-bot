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

def get_no_channels_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Розыгрыш без обязательных подписок", callback_data="no_required_channels")],
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
