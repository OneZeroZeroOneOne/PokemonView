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


pokemon_cb = CallbackData('pokemon', 'id', 'action','Del')  # pokemon:<id>:<action>
into_cb = CallbackData('into','into_cb','id')
back_cb = CallbackData('back','back_cb')

class Form(StatesGroup):
    StorageList = State()


@dp.message_handler(commands='pokemons')
async def cmd_start(message: types.Message, state: FSMContext):# нехуя не узазуеться не якый блять state в пизду
    if message.get_args().isdigit():
        args = message.get_args()#get_args шо вертаэ? строку ілі масів строк? да пізда якого хуя ти провіряєш чі весь масів це інт коли ти должен провірять токо один елемент
        page = int(message.get_args())*6 - 5#
    async with state.proxy() as data:
        #.get() - бля якшо существуэ то верне существующый якшо немає то верне новий пустий
        l = data.get('StorageList', [])
        data['StorageList'] = l
        data['StorageList'].insert(0, page)#вродіби так інсертить на 0 позіцию твої данні
        print("data[st..]-->>")
        print(data['StorageList'][0])
        data['StorageList'][0] = page
    await message.reply("Page:{}".format(int(args)//6+1), reply_markup=await get_pokemon_list_keyboard(int(page)))


@dp.callback_query_handler(pokemon_cb.filter(action='page'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    start_id = int(callback_data['id'])
    async with state.proxy() as data:
        print(data['StorageList'][0])
        data['StorageList'][0] = start_id
    print(data['StorageList'][0] )
    await query.message.edit_text('Page:{}'.format(int(start_id)//6+1), reply_markup = await get_pokemon_list_keyboard(int(start_id)))


@dp.callback_query_handler(pokemon_cb.filter(action='view'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    start_id = int(callback_data['id'])
    async with state.proxy() as data:
        if callback_data['Del'] == 'yes':
            print("Srabotolo Del______________")
            data['StorageList'].pop(-1)
            data['StorageList'].pop(-1)
        data['StorageList'].append(start_id)
        print("Posledniy ELEMENT SorageLista:")
        print(data['StorageList'])
        print(data['StorageList'][-1])
    Pokemon = await PokemonFetch().get_pokemon_id(start_id)
    markup =  types.InlineKeyboardMarkup()
    butList = await get_posible_variete_keyboard(Pokemon)
    if butList:
        markup.add(butList)
    butList = await get_posible_evolution_keyboard(start_id)
    markup.add(butList)
    butList = await get_back_keyboard(state)# оце
    markup.add(*butList)
    print("POKAHO VSE ZAEBOK3")
    print(markup)
    await query.message.edit_text(Pokemon.ToString(), parse_mode = 'Markdown', reply_markup = markup )


@dp.callback_query_handler(into_cb.filter(into_cb='trans'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict):
    id = callback_data['id']
    print("!!!!!!!!!!!!!!nashata trans!!!!!!!!!!!!!!!!")
    await query.message.edit_text("*Трансформации*", parse_mode = 'Markdown', reply_markup = await get_variete_pokList_keyboard(id))


@dp.callback_query_handler(into_cb.filter(into_cb='evol'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict):
    await query.message.edit_text("*Еволюлии:*", parse_mode = 'Markdown', reply_markup = await get_evolution_keyboard(callback_data['id']))


###########################################################################



async def get_back_keyboard(state: FSMContext) -> list:
    backListBut = list()
    async with state.proxy() as data:
        if len(data['StorageList']) == 2:
            backListBut.append(types.InlineKeyboardButton("Назад", callback_data=pokemon_cb.new(id=data['StorageList'][-2], action='page',Del = "yes")))
        else:
            backListBut.append(types.InlineKeyboardButton("Назад", callback_data=pokemon_cb.new(id=data['StorageList'][-2], action='view',Del = "yes")))
        backListBut.append(types.InlineKeyboardButton("В список", callback_data = 'InList'))
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!SSSSSSSSSSSSSSS")
    print(backListBut)
    return backListBut


async def get_posible_evolution_keyboard(id_pok) -> list:
    posibleBut = list()
    posibleBut = types.InlineKeyboardButton("Еволюции:", callback_data = into_cb.new(into_cb = 'evol',id = id_pok))
    print(posibleBut)
    return posibleBut

async def get_evolution_keyboard(id_pok) -> types.InlineKeyboardMarkup:
    Pokemon = await PokemonFetch().get_pokemon_id(id_pok)
    evolution = await Pokemon.GetEvolutions()
    markup = types.InlineKeyboardMarkup()
    if evolution:
        evolList = list()
        if evolution['from']:
            evolList.append(types.InlineKeyboardButton("Евол. ИЗ:", callback_data = 's'))
            for i in evolution['from']:
                evolList.append(types.InlineKeyboardButton("{}".format(i.Name),
                 callback_data = pokemon_cb.new(id=i.ID, action='view',Del = 'no')))
            markup.row(*evolList)
            evolList.clear()
        if evolution['into']:
            evolList.append(types.InlineKeyboardButton("Евол. В:", callback_data ="s"))
            for i in evolution['into']:
                evolList.append(types.InlineKeyboardButton("{}".format(i.Name),
                 callback_data = pokemon_cb.new(id=i.ID,action='view',Del = "no")))
            markup.row(*evolList)
        return markup


async def get_variete_pokList_keyboard(id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    Pokemon = await PokemonFetch().get_pokemon_id(id)
    varieties_form = await Pokemon.GetForms()
    varietiesList = list()
    for i in varieties_form:
        varietiesList.append(types.InlineKeyboardButton("{}".format(i.Name), callback_data = pokemon_cb.new(id=i.ID, action='view',Del = "no")))
    markup.add(*varietiesList)
    return markup



async def get_posible_variete_keyboard(pok_forms_mid) -> list:
    varieties_forms = await pok_forms_mid.GetForms()
    print(varieties_forms)
    if len(varieties_forms)>=1:
        possibleVarieteButt = types.InlineKeyboardButton("Возможные трансформации:",
         callback_data = into_cb.new(into_cb = 'trans',id = pok_forms_mid.ID))
        print(possibleVarieteButt)
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
                callback_data=pokemon_cb.new(id=i.ID, action='view',Del = "no")))
    prev_button = types.InlineKeyboardButton("<< Prev", callback_data=pokemon_cb.new(id=start_pok_id - 6, action='page',Del = 'no'))
    next_button = types.InlineKeyboardButton("Next >>", callback_data=pokemon_cb.new(id=start_pok_id + 6, action='page',Del = 'no'))
    if  start_pok_id == 1:
        markup.add(next_button)
    elif start_pok_id == 803:
        markup.add(prev_button)
    else:
        markup.row(prev_button, next_button)
    return markup



if __name__ == '__main__':
        executor.start_polling(dp, loop=loop, skip_updates=True)
