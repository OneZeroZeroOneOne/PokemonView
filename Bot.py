import asyncio
import logging
import random
import uuid
import config
from PokemonModel import PokemonFetch


from aiogram import Bot, Dispatcher, executor, md, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified, Throttled

logging.basicConfig(level=logging.INFO)

API_TOKEN = config.bot_token

loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

pokemon_cb = CallbackData('pokemon', 'id', 'action')  # pokemon:<id>:<action>

async def get_pokemon_list_keyboard(start_pok_id) -> types.InlineKeyboardMarkup:
    """
    Generate keyboard with list of pok
    """
    markup = types.InlineKeyboardMarkup()
    pokes = await PokemonFetch.get_pokemon_list(start_pok_id)
    for i in pokes:
        markup.add(
        types.InlineKeyboardButton(
                i.Name,
                callback_data=pokemon_cb.new(id=i.ID, action='view'))
        )


    prev_button = types.InlineKeyboardButton("<< Prev", callback_data=pokemon_cb.new(id=start_pok_id - 6, action='page'))
    next_button = types.InlineKeyboardButton("Next >>", callback_data=pokemon_cb.new(id=start_pok_id + 6, action='page'))
    if start_pok_id<800 and start_pok_id>1:
        markup.row(prev_button, next_button)
    elif start_pok_id>800:
        markup.row(prev_button)
    elif start_pok_id<=1:
        markup.row(next_button)
    return markup

@dp.message_handler(commands='pokemons')
async def cmd_start(message: types.Message):
    id_pok = message.get_args()
    if id_pok.isdigit():
        await message.reply("1 Page", reply_markup=await get_pokemon_list_keyboard(int(id_pok)))

@dp.callback_query_handler(pokemon_cb.filter(action='page'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict):
    start_id = int(callback_data['id'])
    print(start_id)
    await query.message.edit_text('{} Page'.format(int(start_id // 6) + 1), reply_markup=await get_pokemon_list_keyboard(int(start_id)))


@dp.callback_query_handler(pokemon_cb.filter(action='view'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict):
    """
        зроби отут шоб показувало отдельного покемона і шоб була кнопка назад
        і кнопки наступна форма і след форма
        і кнопка можливі еволюції
    """


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
