# coding=utf8
import aiohttp
import asyncio
import ujson as json
from schematics.models import Model
from schematics.types import StringType, URLType, DecimalType, ListType

class Pokemon(Model):
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

    def __init__(self, data_stats,data_varaities):
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
        self.Image = "Pisia"
        if data_varaities:
            self.Varieties = [i['pokemon']['url'].split("/")[-2] for i in data_varaities["varieties"]]
        #self.var = data['varieties']

class PokemonFetch:
    def __init__(self):
        self.url_pok_stats = "https://pokeapi.co/api/v2/pokemon/{}/"
        self.url_pok_varaites = 'https://pokeapi.co/api/v2/pokemon-species/{}/'

    async def fetch(self, session, url):
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

    async def get_pokemon_id(self, id):
        async with aiohttp.ClientSession() as session:
            data_stats = await self.fetch(session, self.url_pok_stats.format(id))
            data_varaities = await self.fetch(session, self.url_pok_varaites.format(id))
            return Pokemon(data_stats , data_varaities)

async def main():
    pf = PokemonFetch()
    pok = await pf.get_pokemon_id(10036)
    print(pok.items())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
