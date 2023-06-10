from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import *
from functions import *
import db

bot = Bot(token=API_TOKEN, parse_mode='markdown')
dp = Dispatcher(bot=bot, storage=MemoryStorage())

@dp.message_handler(commands=['set'])
async def SettingDb(message: types.Message):
    if message.from_user.id in ADMIN_ID:
        try:
            db.createKanallar()
            for kanal in TELEGRAM_KANALLAR:
                subs = await bot.get_chat_members_count(kanal)
                db.add_channel(kanal, subs)
        except:
            db.drop_table("kanallar")
            db.createKanallar()
            for kanal in TELEGRAM_KANALLAR:
                subs = await bot.get_chat_members_count(kanal)
                db.add_channel(kanal, subs)
        
        await message.answer("*Homiy kanallarning joriy obunachi miqdorlari o'rnatildi*")



@dp.message_handler(text="⬅️Bekor qilish", state="*")
async def cancelState(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        await message.answer("*Bekor qilindi!*", reply_markup=menu)
        await state.finish()

class sendUser(StatesGroup):
    user_id = State()
    text = State()

menu_btn = [
    [
        KeyboardButton("🔗Referal havola")
    ],
    [
        KeyboardButton("📊Statistika"),
        KeyboardButton("❗️Qoidalar")
    ]
]
menu = ReplyKeyboardMarkup(menu_btn, resize_keyboard=True)

admin_panel = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
admin_panel.add("⭐️Homiy kanallar holati")
admin_panel.add("👤Foydalanuvchiga habar yuborish")
admin_panel.add("⬅️Chiqish")

bekor_qilish = ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️Bekor qilish")

channels = InlineKeyboardMarkup(row_width=1)
count = 1
for kanal in KANALLAR:
    channels.add(InlineKeyboardButton(text=f"{count} - HOMIY KANAL💫", url=kanal))
    count += 1

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    start_info = message.text.split()
    user_id = message.from_user.id
    users = db.get_users()

    kanallar = InlineKeyboardMarkup(row_width=1)
    count = 1
    for kanal in KANALLAR:
        kanallar.add(InlineKeyboardButton(text=f"{count} - HOMIY KANAL💫", url=kanal))
        count += 1
   
    if len(start_info) > 1:
        kanallar.add(InlineKeyboardButton(text="✅Tasdiqlash", url=f"{BOT}?start={start_info[-1]}"))
    else:
        kanallar.add(InlineKeyboardButton(text='✅Tasdiqlash', url=f"{BOT}?start=True"))

    if await check_follow(user_id):
        if user_id not in users:
            if len(start_info) > 1 and start_info[-1] != user_id:
                reffer = start_info[-1]
                db.set_ref(reffer)
                await bot.send_message(reffer, f"*🎉Tabriklaymiz, {message.from_user.full_name} sizning havolangiz orqali botga tashrif buyurdi va sizga referal bo'ldi, shu tartibda davom eting, Omad*")
                await message.answer(START_TEXT, reply_markup=menu)
                db.add_user(user_id)
            else:
                if user_id not in users:
                    db.add_user(user_id)
                await message.answer(START_TEXT, reply_markup=menu)
        else:
            await message.answer(text=START_TEXT, reply_markup=menu)
    else:
        await message.answer(text=ERRFOLLOW, reply_markup=kanallar)
    
@dp.message_handler(text="🔗Referal havola")
async def sendLink(message: types.Message):
    user_id = message.from_user.id
    if await check_follow(user_id):
        refs = db.get_ref(user_id)
        await message.answer(f"""*🔗Sizning referal havolangiz:\n{BOT}?start={user_id}\n\n📜Sizning referallaringiz: {refs} ta*""")    
    else:
        
        await message.answer(ERRFOLLOW, reply_markup=channels)

@dp.message_handler(text="❗️Qoidalar")
async def sendQoidalar(message: types.Message):
    user_id = message.from_user.id
    if await check_follow(user_id):
        await message.answer(QOIDA)
    else:
        await message.answer(ERRFOLLOW, reply_markup=channels)

@dp.message_handler(text="📊Statistika")
async def sendStaticsBot(message: types.Message):
    user_id = message.from_user.id
    if await check_follow(user_id):
        info = db.get_statics()
        c = 1
        txt = str()
        for i in info:
            txt += f"*{c}. {i[0]} - {i[-1]} ta🤩*\n"
            c += 1
        await message.answer(txt)
    else:
        await message.answer(ERRFOLLOW, reply_markup=channels)

@dp.message_handler(commands=['admin', 'panel'])
async def welcomeToAdminsplace(message: types.Message):
    if message.from_user.id in ADMIN_ID:
        await message.answer("*Riza, Xush kelibsiz!*", reply_markup=admin_panel)

@dp.message_handler(text="⬅️Chiqish")
async def exitAdminPanel(message: types.Message):
    if message.from_user.id in ADMIN_ID:
        await message.answer("*Bosh menyuga qaytdingiz!*", reply_markup=menu)

@dp.message_handler(text="⭐️Homiy kanallar holati")
async def viewAdminPartnerChannels(message: types.Message):
    if message.from_user.id in ADMIN_ID:
        txt = "*"
        kanallar = db.get_channels()
        for kanal in kanallar:
            new_subs = await bot.get_chat_members_count(kanal[0])
            txt += f"{kanal[0]} - {new_subs - kanal[-1]} ta"
        txt += "*"

        await message.answer(txt)
@dp.message_handler(text="👤Foydalanuvchiga habar yuborish")
async def sendToUser(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        await message.answer("*Habar yubormoqchi bo'lgan foydalanuvchingizni id raqamini yuboring:*", reply_markup=bekor_qilish)
        await sendUser.user_id.set()

@dp.message_handler(state=sendUser.user_id)
async def GetIdSendUser(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        await state.update_data(
            {
                'id': message.text
            }
        )
        await message.answer(f"*Yaxshi {message.from_user.full_name}, endi habar mantningizni (TEXT) kiriting: *")
        await sendUser.text.set()
@dp.message_handler(state=sendUser.text)
async def finishSendUserState(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        text = message.text
        await state.update_data(
            {
                'text': text
            }
        )
        data = await state.get_data()
        await state.finish()

        try:
            await bot.send_message(data['id'], data['text'])
            await message.answer("Yuborildi!", reply_markup=admin_panel)
        except Exception as e:
            await message.answer(f"*Id bo'yicha xato: {e}*", reply_markup=admin_panel)



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
