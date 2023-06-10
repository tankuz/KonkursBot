from config import *
from main import bot
import db

async def check_follow(user_id) -> bool:
    users = db.get_users()
    
    check = 0
    for kanal in TELEGRAM_KANALLAR:
        member = await bot.get_chat_member(kanal, user_id)
        if member.status not in ('creator', 'member', 'administrator'):
            check += 1

    if check == 0:
        return True
    else:
        return False
    
async def onechecker(kanal, user_id):
    member = await bot.get_chat_member(kanal, user_id)
    if member.status not in ('creator', 'member', 'administrator'):
        return False
    else:
        return True