import asyncio
import random
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import pytz

from config import config
from handlers import routers
from database import db
from logger import logger


async def check_time_giveaways(bot: Bot):
    while True:
        try:
            tz = pytz.timezone(config.TIMEZONE)
            now = datetime.now(tz)

            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM giveaways WHERE status = 'published' AND end_type = 'time'"
            )
            rows = cursor.fetchall()
            conn.close()

            for (giveaway_id,) in rows:
                giveaway = db.get_giveaway(giveaway_id)
                if not giveaway:
                    continue

                end_dt = datetime.fromisoformat(giveaway['end_value'])
                if end_dt.tzinfo is None:
                    end_dt = tz.localize(end_dt)

                if now >= end_dt:
                    logger.info(f"Завершаю розыгрыш {giveaway_id} по времени")
                    await _finish_giveaway(bot, giveaway_id)

        except Exception as e:
            logger.error(f"Ошибка планировщика: {e}")

        await asyncio.sleep(30)


async def _finish_giveaway(bot: Bot, giveaway_id: int):
    giveaway = db.get_giveaway(giveaway_id)
    participants = db.get_participants(giveaway_id)

    if not participants:
        winner_text = "🎉 Розыгрыш завершен!\n\nК сожалению, участников не было."
    else:
        count = min(giveaway['winners_count'], len(participants))
        winners = random.sample(participants, count)
        winner_text = "🎉 Розыгрыш завершен!\n\n🏆 Победители:\n"
        for i, w in enumerate(winners, 1):
            uname = f"@{w['username']}" if w.get('username') else f"ID: {w['user_id']}"
            winner_text += f"{i}. {uname}\n"

    try:
        await bot.send_message(
            chat_id=giveaway['channel_id'],
            text=winner_text,
            reply_to_message_id=giveaway.get('message_id')
        )
    except Exception as e:
        logger.error(f"Не удалось отправить результаты розыгрыша {giveaway_id}: {e}")

    db.update_giveaway_status(giveaway_id, 'finished')


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    for router in routers:
        dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен")

    asyncio.create_task(check_time_giveaways(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())