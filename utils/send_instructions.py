from config import CHANNEL_ID, INSTRUCTION_VOICE_MESSAGE_ID

async def send_voice_instructions(bot, user_id: int):
    await bot.forward_message(
        chat_id=user_id,
        from_chat_id=CHANNEL_ID,
        message_id=INSTRUCTION_VOICE_MESSAGE_ID
    )
