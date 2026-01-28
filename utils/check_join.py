from aiogram import Bot
from aiogram.types import ChatMember
from config import CHANNEL_ID


async def is_user_joined(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in [
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER
        ]
    except:
        return False
