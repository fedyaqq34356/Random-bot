from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from database import db
from utils.channel_utils import check_user_subscribed, get_channel_info

router = Router()

@router.callback_query(F.data.startswith("participate_"))
async def participate_in_giveaway(callback: CallbackQuery, bot: Bot):
    giveaway_id = int(callback.data.split("_")[1])
    
    giveaway = db.get_giveaway(giveaway_id)
    
    if not giveaway:
        await callback.answer("❌ Розыгрыш не найден", show_alert=True)
        return
    
    if giveaway['status'] != 'published':
        await callback.answer("❌ Розыгрыш не активен", show_alert=True)
        return
    
    required_channels = [giveaway['channel_id']] + giveaway.get('channels', [])
    
    not_subscribed = []
    not_subscribed_names = []
    
    for channel_id in required_channels:
        try:
            is_subscribed = await check_user_subscribed(bot, channel_id, callback.from_user.id)
            if not is_subscribed:
                not_subscribed.append(channel_id)
                channel_info = await get_channel_info(bot, channel_id)
                if channel_info and channel_info.get('username'):
                    not_subscribed_names.append(f"@{channel_info['username']}")
                else:
                    not_subscribed_names.append(f"ID: {channel_id}")
        except Exception as e:
            print(f"Ошибка при проверке канала {channel_id}: {e}")
            continue
    
    if not_subscribed:
        channels_text = ", ".join(not_subscribed_names)
        await callback.answer(
            f"❌ Вы должны быть подписаны на все каналы!\n\nПодпишитесь на: {channels_text}",
            show_alert=True
        )
        return
    
    success = db.add_participant(
        giveaway_id=giveaway_id,
        user_id=callback.from_user.id,
        username=callback.from_user.username
    )
    
    if success:
        participants_count = db.get_participants_count(giveaway_id)
        await callback.answer(
            f"✅ Вы успешно зарегистрированы! Участников: {participants_count}",
            show_alert=True
        )
        
        if giveaway['end_type'] == 'count':
            target_count = int(giveaway['end_value'])
            if participants_count >= target_count:
                await finish_giveaway(bot, giveaway_id)
    else:
        await callback.answer("ℹ️ Вы уже участвуете в этом розыгрыше", show_alert=True)

async def finish_giveaway(bot: Bot, giveaway_id: int):
    import random
    
    giveaway = db.get_giveaway(giveaway_id)
    participants = db.get_participants(giveaway_id)
    
    if len(participants) < giveaway['winners_count']:
        winners = participants
    else:
        winners = random.sample(participants, giveaway['winners_count'])
    
    winner_text = "🎉 Розыгрыш завершен!\n\n🏆 Победители:\n"
    for i, winner in enumerate(winners, 1):
        username = f"@{winner['username']}" if winner['username'] else f"ID: {winner['user_id']}"
        winner_text += f"{i}. {username}\n"
    
    await bot.send_message(
        chat_id=giveaway['channel_id'],
        text=winner_text,
        reply_to_message_id=giveaway.get('message_id')
    )
    
    db.update_giveaway_status(giveaway_id, 'finished')