import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, ChannelParticipantsAdmins
from telethon.errors import (
    FloodWaitError, UserPrivacyRestrictedError, InputUserDeactivatedError,
    PeerIdInvalidError, UserIsBlockedError, ChatWriteForbiddenError
)

from database import db
from logger import logger


async def scan_and_add_participants(client: TelegramClient, giveaway_id: int, channel_id: int) -> int:
    added = 0
    offset = 0
    limit = 200

    try:
        entity = await client.get_entity(channel_id)
    except Exception as e:
        logger.error(f"Не удалось получить канал {channel_id}: {e}")
        return 0

    admin_ids = set()
    try:
        admins_result = await client(GetParticipantsRequest(
            channel=entity,
            filter=ChannelParticipantsAdmins(),
            offset=0,
            limit=100,
            hash=0
        ))
        admin_ids = {user.id for user in admins_result.users}
        logger.info(f"Найдено {len(admin_ids)} администраторов канала")
    except Exception as e:
        logger.warning(f"Не удалось получить список администраторов: {e}")

    while True:
        try:
            participants = await client(GetParticipantsRequest(
                channel=entity,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))
        except FloodWaitError as e:
            logger.warning(f"FloodWait {e.seconds}s")
            await asyncio.sleep(e.seconds)
            continue
        except Exception as e:
            logger.error(f"Ошибка получения участников: {e}")
            break

        if not participants.users:
            break

        for user in participants.users:
            if user.bot or user.deleted or user.id in admin_ids:
                continue
            success = db.add_participant(giveaway_id, user.id, user.username)
            if success:
                added += 1

        offset += len(participants.users)

        if len(participants.users) < limit:
            break

        await asyncio.sleep(1)

    logger.info(f"Розыгрыш {giveaway_id}: добавлено {added} участников из канала {channel_id}")
    return added


async def broadcast_giveaway(
    client: TelegramClient,
    channel_id: int,
    message_id: int,
    channel_username: str | None
) -> tuple[int, int]:
    sent = 0
    failed = 0
    offset = 0
    limit = 200

    if channel_username:
        channel_link = f"https://t.me/{channel_username}/{message_id}"
    else:
        channel_link = f"https://t.me/c/{str(channel_id).replace('-100', '')}/{message_id}"

    text = (
        f"🎉 Привет! В канале проходит розыгрыш!\n\n"
        f"Нажмите кнопку «Участвовать» чтобы принять участие:\n"
        f"{channel_link}"
    )

    try:
        entity = await client.get_entity(channel_id)
    except Exception as e:
        logger.error(f"Не удалось получить канал для рассылки: {e}")
        return 0, 0

    while True:
        try:
            participants = await client(GetParticipantsRequest(
                channel=entity,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))
        except FloodWaitError as e:
            logger.warning(f"FloodWait {e.seconds}s при рассылке")
            await asyncio.sleep(e.seconds)
            continue
        except Exception as e:
            logger.error(f"Ошибка при рассылке: {e}")
            break

        if not participants.users:
            break

        for user in participants.users:
            if user.bot or user.deleted:
                continue
            try:
                await client.send_message(user.id, text)
                sent += 1
                await asyncio.sleep(2)
            except FloodWaitError as e:
                logger.warning(f"FloodWait {e.seconds}s при отправке пользователю {user.id}")
                await asyncio.sleep(e.seconds)
                try:
                    await client.send_message(user.id, text)
                    sent += 1
                    await asyncio.sleep(2)
                except Exception:
                    failed += 1
            except (UserPrivacyRestrictedError, InputUserDeactivatedError, PeerIdInvalidError, 
                    UserIsBlockedError, ChatWriteForbiddenError):
                failed += 1
            except Exception as e:
                logger.warning(f"Не удалось отправить {user.id}: {type(e).__name__} - {e}")
                failed += 1

        offset += len(participants.users)
        if len(participants.users) < limit:
            break

        await asyncio.sleep(2)

    logger.info(f"Рассылка завершена: отправлено {sent}, не удалось {failed}")
    return sent, failed