from aiogram import Bot
from aiogram.types import ChatMemberOwner, ChatMemberAdministrator
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

async def check_bot_is_admin(bot: Bot, channel_id: int) -> bool:
    try:
        bot_member = await bot.get_chat_member(channel_id, bot.id)
        return isinstance(bot_member, (ChatMemberOwner, ChatMemberAdministrator))
    except (TelegramBadRequest, TelegramForbiddenError):
        return False

async def check_user_is_admin(bot: Bot, channel_id: int, user_id: int) -> bool:
    try:
        user_member = await bot.get_chat_member(channel_id, user_id)
        return isinstance(user_member, (ChatMemberOwner, ChatMemberAdministrator))
    except (TelegramBadRequest, TelegramForbiddenError):
        return False

async def check_user_subscribed(bot: Bot, channel_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except (TelegramBadRequest, TelegramForbiddenError):
        return False

async def get_channel_info(bot: Bot, channel_id: int):
    try:
        chat = await bot.get_chat(channel_id)
        return {
            'id': chat.id,
            'title': chat.title,
            'username': chat.username
        }
    except (TelegramBadRequest, TelegramForbiddenError):
        return None