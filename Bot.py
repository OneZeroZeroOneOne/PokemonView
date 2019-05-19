token = "858185563:AAEIh49GYHAEGb_1PK4K2VQuFftBto5zEpU"
import sqlite3
import settings
import ButtonUpDown
import DBworker
from models import PokemonModel
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
ReplyKeyboardMarkup, InlineKeyboardMarkup, \
InlineKeyboardButton
import random



from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware


DB = DBworker.DB()

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['pokemon'])
async def process_pokemon_command(message: types.Message):
    argument = message.get_args()
    print(argument)
    if argument.isdigit():
        Pok = PokemonModel.Pokemon(int(argument),DB)
        strng = Pok.ToString()
        image = Pok.Image
        print(strng)
        await bot.send_photo(chat_id = message.chat.id, \
        photo = types.InputFile(image)\
        , caption = strng, parse_mode = 'Markdown')

@dp.message_handler(commands=['pokemons'])
async def process_pokemons_command(message: types.Message):
    argument = message.get_args()
    print(argument)
    if argument.isdigit():
        markup = ButtonUpDown.ButtnUPDOWN(int(argument))
        await message.reply("Pokemon list",reply_markup = markup)
        
        


@dp.callback_query_handler()
async def query_InPok_proceed(call: types.CallbackQuery):
    strcalldata = call.data.split('/')
    print(strcalldata[0],strcalldata[1],"ss") 
    if strcalldata[0] == 'NAZ':
        print(strcalldata[1])
        markup = ButtonUpDown.ButtnUPDOWN(int(strcalldata[1])-6)
        await call.message.edit_text("Pokemon list", reply_markup = markup) 
        
         
    elif strcalldata[0] == 'VPERED':
        print(strcalldata[1])
        markup = ButtonUpDown.ButtnUPDOWN(int(strcalldata[1])+6)
        await call.message.edit_text("Pokemon list", reply_markup = markup)
        
        
    elif strcalldata[0] == 'CANS':
        
        markup = ButtonUpDown.ButtnUPDOWN(int(strcalldata[1]))
        print("cans nashat markup est'")
        await call.message.reply("Pokemon list",reply_markup = markup)
        
         
    elif strcalldata[0] == 'PRED':
        Pok = PokemonModel.Pokemon(int(strcalldata[1])-1,DB)
        strng = Pok.ToString()
        image = Pok.Image
        markup = ButtonUpDown.CansBut(int(strcalldata[1])-1)
        print(strng)
        await bot.send_photo(chat_id = call.from_user.id, \
        photo = types.InputFile(image)\
        , caption = strng, parse_mode = 'Markdown',reply_markup = markup)
        
        
    elif strcalldata[0] == 'NEXT':
        Pok = PokemonModel.Pokemon(int(strcalldata[1])+1,DB)
        strng = Pok.ToString()
        image = Pok.Image
        markup = ButtonUpDown.CansBut(int(strcalldata[1]+7)+1)
        print(strng)
        await bot.send_photo(chat_id = call.from_user.id, \
        photo = types.InputFile(image)\
        , caption = strng, parse_mode = 'Markdown',reply_markup = markup)
        
        
    elif strcalldata[0] == 'ID':
        print(strcalldata[1])
        Pok = PokemonModel.Pokemon(int(strcalldata[1]),DB)
        strng = Pok.ToString()
        image = Pok.Image
        print(strng)
        markup = ButtonUpDown.CansBut(int(strcalldata[1]))
        await bot.send_photo(chat_id = call.from_user.id, \
        photo = types.InputFile(image)\
        , caption = strng, parse_mode = 'Markdown',reply_markup = markup)
        

if __name__ == "__main__":
    executor.start_polling(dp)
