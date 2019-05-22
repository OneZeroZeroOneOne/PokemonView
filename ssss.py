import asyncio
from typing import Optional

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

API_TOKEN = "858185563:AAEIh49GYHAEGb_1PK4K2VQuFftBto5zEpU"

loop = asyncio.get_event_loop()

bot = Bot(token=API_TOKEN, loop=loop)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

rainbow_color = ["Синій","Красний","Жовтий","Оранжевий","Зельоний","Голубий","Фіолетовий"]
my_tg_adress = "https://t.me/ms_ebalo"

# States
class Form(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    color = State()  # Will be represented in storage as 'Form:age'
    santimeters = State()  # Will be represented in storage as 'Form:gender'


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    await Form.name.set()

    await message.reply("Я предсказую будущє, токо сначала тобі треба отвітить на несколько вапросов. Як тебе звать?")


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(lambda message: message.text.lower() == 'cancel', state='*')
async def cancel_handler(message: types.Message, state: FSMContext, raw_state: Optional[str] = None):
    """
    Allow user to cancel any action
    """
    if raw_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Canceled.', reply_markup=types.ReplyKeyboardRemove())
#золотий поняв



@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(*rainbow_color)
    await message.reply("Якій цвет радугі твій любімий?",reply_markup=markup)


# Check age. Age gotta be digit
@dp.message_handler(lambda message: message.text not in rainbow_color, state=Form.color)
async def failed_process_age(message: types.Message):
    """
    If age is invalid
    """
    return await message.reply("Ты додік я для чого кнопкі зробив блять??")

@dp.message_handler(state=Form.color)
async def process_gender(message: types.Message, state: FSMContext):
    if message.text == "Голубий":
        await message.reply("Сам ти блять голубий")
    if message.text == "Синій":
        await message.reply("Синій це Шах послі двух чарок")
    async with state.proxy() as data:
        data['color'] = message.text
        await Form.next()
        markup = types.ReplyKeyboardRemove()
        await message.reply("Ану скіко твій песюн сантіметров?",reply_markup = markup)


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.santimeters)
async def failed_process_age(message: types.Message):
    """
    If age is invalid
    """
    return await message.reply("Палюдські напиши курва матка")



@dp.message_handler(lambda message: message.text.isdigit(),state=Form.santimeters)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['santimeters'] = message.text
        if int(message.text) >=23:
            await message.reply("Ого у тебе залупа, як у коня!")
        if int(message.text) <= 14 :#так без ього не як
            await message.reply("Тю блять шо це нацюцюрник такій малий, шо ти їм робиш? В ушах ковиряешся? ")
        if int(message.text) > 14 and int(message.text) < 23:
            await message.reply("Ну так нормальний такій аншльохен!")
#да похуй всьоравно памилка тіпа указує осюда
#скрін дай
#ну
        await bot.send_message(message.chat.id, "Хаха ноебал ніякій я не екстрасенс пашов нахуй. Тепер одмен знае про твій хуй")
        print(message.chat.username)
        #запусти
        strng = str(message.chat.username)
        descr = """от кого: {}
        цвет: {}
        дліна песюна: {}
        """.format(message.chat.username, data['color'], data['santimeters'])
        await bot.send_message(chat_id = 400717618, text = descr)

            #пробуй
            #покажеш шо виведе
        # Finish conversation
        data.state = None


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
