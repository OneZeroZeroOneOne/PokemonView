# coding=utf8
import aiohttp
import asyncio
import ujson as json
import time

from aiocache import cached
from aiocache.serializers import PickleSerializer

from schematics.models import Model
from schematics.types import StringType, URLType, DecimalType, ListType

pokemon_description = """*Имя покемона:* {0}
*В общем:* {1}
*Атака:* {2}
*HP:* {3}
*Защита:* {4}
*Типы*: {5}
*Доп.Атк:* {6}
*Доп.Защ:* {7}
*Скорость:* {8}
*Поколение:* {9}
*Легендарность:* {10}

*ID:* {11}"""

class Pokemon(Model):
    FatherID = DecimalType()
    ID = DecimalType()
    Name = StringType()
    Weight = DecimalType()
    HP = DecimalType()
    Attack = DecimalType()
    Defense = DecimalType()
    Speed = DecimalType()
    SpecialAttack = DecimalType()
    SpecialDefense = DecimalType()
    Types = ListType(StringType)
    Image = StringType()
    Varieties = ListType(DecimalType)

    def __init__(self, data_stats = None, data_varaities = None):
        super(Pokemon, self).__init__()
        Stats = data_stats['stats']

        self.ID = data_stats['id']
        self.Name = data_stats["name"]
        self.Weight = data_stats["weight"]
        self.HP =  Stats[5]['base_stat']
        self.Attack =  Stats[4]['base_stat']
        self.Defense =  Stats[3]['base_stat']
        self.Speed =  Stats[0]['base_stat']
        self.SpecialAttack = Stats[2]['base_stat']
        self.SpecialDefense = Stats[1]['base_stat']
        self.Types = [i['type']['name'] for i in data_stats["types"]]
        self.Image = "https://img.pokemondb.net/artwork/{}.jpg".format(self.Name)
        if data_varaities:
            self.Varieties = [i['pokemon']['url'].split("/")[-2] for i in data_varaities["varieties"]][1:]

    async def GetForms(self):
        forms = []
        if self.Varieties:
            for i in self.Varieties:
                forms.append(await PokemonFetch.get_pokemon_id(i))

        return forms

    def ToString(self):
        return pokemon_description.format(self.Name, '123', self.Attack,
        self.HP, self.Defense, ', '.join(self.Types),
        self.SpecialAttack, self.SpecialDefense, self.Speed,
        'володя дороби поколеніє', 'ВОЛОДЯ ДОРОБИ ЛЕГЕНДАРНОСТЬ', self.ID)

class PokemonFetch:
    url_pok_stats = "https://pokeapi.co/api/v2/pokemon/{}/"
    url_pok_varaites = 'https://pokeapi.co/api/v2/pokemon-species/{}/'

    async def fetch(session, url):
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


    @staticmethod
    @cached()
    async def get_pokemon_id(id):
        async with aiohttp.ClientSession() as session:
            data_stats = await PokemonFetch.fetch(session, PokemonFetch.url_pok_stats.format(id))
            data_varaities = await PokemonFetch.fetch(session, PokemonFetch.url_pok_varaites.format(id))
            return Pokemon(data_stats , data_varaities)
