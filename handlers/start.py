from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import get_main_menu_keyboard
from database import db

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    text = (
        "✋ Приветствуем!\n\n"
        "Наш бот поможет Вам провести розыгрыш в канале или чате.\n\n"
        "Готовы создать новый розыгрыш?"
    )
    
    await message.answer(text, reply_markup=get_main_menu_keyboard())

@router.callback_query(F.data == "my_giveaways")
async def show_my_giveaways(callback: CallbackQuery):
    await callback.answer()
    
    giveaways = db.get_admin_giveaways(callback.from_user.id)
    
    if not giveaways:
        await callback.message.answer("У вас пока нет розыгрышей")
        return
    
    text = "📋 Ваши розыгрыши:\n\n"
    for g in giveaways:
        status_emoji = "✅" if g['status'] == 'published' else "📝"
        text += f"{status_emoji} ID {g['id']}: {g['text']}\n"
        text += f"   Победителей: {g['winners_count']}\n\n"
    
    await callback.message.answer(text)

@router.callback_query(F.data == "my_channels")
async def show_my_channels(callback: CallbackQuery):
    await callback.answer()
    
    channels = db.get_admin_channels(callback.from_user.id)
    
    if not channels:
        await callback.message.answer("У вас пока нет добавленных каналов")
        return
    
    text = "📺 Ваши каналы:\n\n"
    for ch in channels:
        channel_name = ch['channel_username'] or f"ID: {ch['channel_id']}"
        text += f"• {channel_name}\n"
    
    await callback.message.answer(text)

@router.callback_query(F.data == "cancel")
async def cancel_operation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "❌ Операция отменена",
        reply_markup=get_main_menu_keyboard()
    )
