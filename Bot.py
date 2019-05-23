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

logging.basicConfig(level=logging.INFO)

API_TOKEN = config.bot_token

loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


pokemon_cb = CallbackData('pokemon', 'id', 'action')  # pokemon:<id>:<action>
into_cb = CallbackData('into', 'into_cb','id')
otmena_cb = CallbackData('otmena','Otm','id')
otmena_in_cb = CallbackData('otmena_in','Otmena_in','id')

class Form(StatesGroup):
    stapList = State()  # Will be represented in storage as 'Form:name'
      # Will be represented in storage as 'Form:gender'


"""
норм
так же?
"""

async def get_pokemon_varieties_keyboard(pok_forms_mid, state: FSMContext) -> types.InlineKeyboardMarkup:
    #токо в оцьой хуйны -->
    varieties_forms = await pok_forms_mid.GetForms()
    print(varieties_forms)
    markup =  types.InlineKeyboardMarkup()
    if len(varieties_forms)>=1:
        markup.add(types.InlineKeyboardButton("Возможные трансформации:", callback_data = into_cb.new(into_cb = 'trans',id = pok_forms_mid.ID)))
    evolution = await pok_forms_mid.GetEvolutions()
    if evolution:
        if evolution['from']:
            eflist = list()
            eflist.append(types.InlineKeyboardButton("Евол. ИЗ:", callback_data = 's'))
            for i in evolution['from']:
                eflist.append(types.InlineKeyboardButton("{}".format(i.Name), callback_data = pokemon_cb.new(id=i.ID, action='view')))
            markup.row(*eflist)
        if evolution['into']:
            eilist = list()
            eilist.append(types.InlineKeyboardButton("Евол. В:", callback_data ="s"))
            for i in evolution['into']:
                eilist.append(types.InlineKeyboardButton("{}".format(i.Name),
                 callback_data = pokemon_cb.new(id=i.ID,action='view')))
            markup.row(*eilist)
    mark_list = list()
    async with state.proxy() as data:
        if len(data.get('stapList'))>=2:
            mark_list.append(types.InlineKeyboardButton("Назад", callback_data = otmena_cb.new(Otm ='Otmena',id = data.get('stapList')[len(data['stapList'])-2])))

        else:
            mark_list.append(types.InlineKeyboardButton("Назад", callback_data = otmena_in_cb.new(Otmena_in ='otmena',id = data.get('List'))))
    mark_list.append(types.InlineKeyboardButton("В список", callback_data = otmena_in_cb.new(Otmena_in ='otmena',id = data.get('List'))))
    markup.row(*mark_list)
    return markup


async def get_trans_list_keyboard(id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    Pokemon = await PokemonFetch.get_pokemon_id(id)
    varieties = await Pokemon.GetForms()
    varietiesList = list()
    for i in varieties:
        varietiesList.append(types.InlineKeyboardButton("{}".format(i.Name), callback_data = pokemon_cb.new(id=i.ID, action='view')))
    markup.add(*varietiesList)
    return markup





async def get_pokemon_list_keyboard(start_pok_id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    pokes = await PokemonFetch().get_pokemon_list(start_pok_id)
    print(*pokes)
    for i in pokes:
        markup.add(
        types.InlineKeyboardButton(
                i.Name,
                callback_data=pokemon_cb.new(id=i.ID, action='view')))


    prev_button = types.InlineKeyboardButton("<< Prev", callback_data=pokemon_cb.new(id=start_pok_id - 6, action='page'))
    next_button = types.InlineKeyboardButton("Next >>", callback_data=pokemon_cb.new(id=start_pok_id + 6, action='page'))
    if  start_pok_id>=802:
        markup.row(prev_button)
    elif start_pok_id<=1:
        markup.row(next_button)
    else:
        markup.row(prev_button, next_button)
    return markup

@dp.message_handler(commands='pokemons')
async def cmd_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.get_args().isdigit():
            argument = message.get_args()
            data['List'] = argument
        if not data.get('stapList'):#ваще ідеал писать отакз
            Listok = list()
            data['stapList'] = Listok
    id_pok = message.get_args()
    if id_pok.isdigit():
        await message.reply("Page", reply_markup=await get_pokemon_list_keyboard(int(id_pok)))

@dp.callback_query_handler(pokemon_cb.filter(action='page'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    start_id = int(callback_data['id'])
    async with state.proxy() as data:
        data['List'] = start_id
    print(start_id)
    await query.message.edit_text('{} Page'.format(int(start_id // 6) + 1), reply_markup=await get_pokemon_list_keyboard(int(start_id)))


@dp.callback_query_handler(pokemon_cb.filter(action='view'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    start_id = int(callback_data['id'])
    async with state.proxy() as data:
        if data.get('stapList'):
            data.get('stapList').append(start_id)
        else:
            Listok = list()
            data['stapList'] = Listok
            data.get('stapList').append(start_id)
    Pokemon = await PokemonFetch().get_pokemon_id(start_id)
    await query.message.edit_text(Pokemon.ToString(), parse_mode = 'Markdown',
    reply_markup = await get_pokemon_varieties_keyboard(Pokemon, state))


@dp.callback_query_handler(into_cb.filter(into_cb='trans'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    Pokemon = await PokemonFetch().get_pokemon_id(callback_data['id'])
    await query.message.edit_text("*Трансформации:*", parse_mode = 'Markdown',
    reply_markup = await get_trans_list_keyboard(str(Pokemon.ID)))

@dp.callback_query_handler(otmena_cb.filter(Otm ='Otmena'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    Pokemon = await PokemonFetch().get_pokemon_id(callback_data['id'])
    await query.message.edit_text(Pokemon.ToString(), parse_mode = 'Markdown',
    reply_markup = await get_pokemon_varieties_keyboard(Pokemon, state))

@dp.callback_query_handler(otmena_in_cb.filter(Otmena_in ='otmena'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await query.message.edit_text('{} Page'.format(int(int(callback_data['id']) // 6) + 1), reply_markup=await get_pokemon_list_keyboard(int(callback_data['id'])))



if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
