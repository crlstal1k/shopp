from aiogram import Bot
from users import User

async def execute(bot: Bot, user: User, message_id: int):
   await bot.edit_message_text(
       chat_id=user.id,
       message_id=message_id,
       text="Text",
   ) 
