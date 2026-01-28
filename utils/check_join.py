from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from config import CHANNEL_ID


async def is_user_joined(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status != ChatMemberStatus.LEFT
    except Exception as e:
        return False
