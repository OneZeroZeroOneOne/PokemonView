import asyncio
import logging
import random
import uuid
import config
from PokemonModel import PokemonFetch
import aiogram.utils.markdown as md
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram import Bot, Dispatcher, executor, md, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified, Throttled

API_TOKEN = config.bot_token

loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


pokemon_cb = CallbackData('pokemon', 'id', 'action')  # pokemon:<id>:<action>


class Form(StatesGroup):
    StorageList = State()


@dp.message_handler(commands='pokemons')
async def cmd_start(message: types.Message, state: FSMContext):
    if message.get_args().isdigit():
        page = messega.get_args()*6
    async with state.proxy() as data:
        if not data['StorageList']:
            Listok = list()
            data['StorageList'] = Listok
        data['StorageList'][0] = page
    await message.reply("Page:{}".format(int(page)), reply_markup=await get_pokemon_list_keyboard(int(id_pok)))


@dp.callback_query_handler(pokemon_cb.filter(action='page'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    start_id = int(callback_data['id'])
    async with state.proxy() as data:
        data['StorageList'][0] = start_id
    print(start_id)
    await query.message.edit_text('Page:{}'.format(int(start_id)), reply_markup = await get_pokemon_list_keyboard(int(start_id)))


@dp.callback_query_handler(pokemon_cb.filter(action='view'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    start_id = int(callback_data['id'])
    async with state.proxy() as data:
        data['stapList'].append(start_id)
    Pokemon = await PokemonFetch().get_pokemon_id(start_id)
    markup.add(get_possible_variete_keyboard(Pokemon))
    markup.add(get_possible_evolution_keyboard(Pokemon))


async def get_м_keyboard(pok_forms_mid, state: FSMContext) -> types.InlineKeyboardMarkup:


async def get_possible_evolution_keyboard(pok_forms_mid, state: FSMContext) -> types.InlineKeyboardMarkup:
    evolution = await pok_forms_mid.GetEvolutions()
    if evolution:
        evolList = list()
        if evolution['from']:
            evolList.append(types.InlineKeyboardButton("Евол. ИЗ:", callback_data = 's'))
            for i in evolution['from']:
                evolList.append(types.InlineKeyboardButton("{}".format(i.Name),
                 callback_data = pokemon_cb.new(id=i.ID, action='view')))
        if evolution['into']:
            evolList.append(types.InlineKeyboardButton("Евол. В:", callback_data ="s"))
            for i in evolution['into']:
                evolList.append(types.InlineKeyboardButton("{}".format(i.Name),
                 callback_data = pokemon_cb.new(id=i.ID,action='view')))
        return evolList


async def get_possible_variete_keyboard(pok_forms_mid, state: FSMContext) -> types.InlineKeyboardMarkup:
    varieties_forms = await pok_forms_mid.GetForms()
    print(varieties_forms)
    if len(varieties_forms)>=1:
        possibleVarieteButt = (types.InlineKeyboardButton("Возможные трансформации:", callback_data = into_cb.new(into_cb = 'trans',id = pok_forms_mid.ID))
        return possibleVarieteButt


async def get_pokemon_list_keyboard(start_pok_id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    if start_pok_id < 1:
        start_pok_id = 1
    if start_pok_id > 803:
        start_pok_id = 803
    pokes = await PokemonFetch().get_pokemon_list(start_pok_id)
    print(*pokes)
    for i in pokes:
        markup.add(
        types.InlineKeyboardButton(
                i.Name,
                callback_data=pokemon_cb.new(id=i.ID, action='view')))
    prev_button = types.InlineKeyboardButton("<< Prev", callback_data=pokemon_cb.new(id=start_pok_id - 6, action='page'))
    next_button = types.InlineKeyboardButton("Next >>", callback_data=pokemon_cb.new(id=start_pok_id + 6, action='page'))
    if  start_pok_id = 1:
        markup.row(next_button)
    elif start_pok_id = 803:
        markup.row(prev_button)
    else:
        markup.row(prev_button, next_button)
    return markup
