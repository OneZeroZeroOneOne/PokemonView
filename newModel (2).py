# coding=utf8
import aiohttp
import asyncio
import json
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



    def __init__(self, data,data_varaities):
        Stats = data['stats']
        self.ID = data['id']
        self.Name = data["name"]
        self.Weight = data["weight"]
        self.HP =  Stats[5]['base_stat']
        self.Attack =  Stats[4]['base_stat']
        self.Defense =  Stats[3]['base_stat']
        self.Speed =  Stats[0]['base_stat']
        self.SpecialAttack = Stats[2]['base_stat']
        self.SpecialDefense = Stats[1]['base_stat']
        self.Types = data["types"]
        self.Image = "Pisia"
        self.Varieties = data_varaities["varieties"]
        #self.var = data['varieties']

class PokemonFetch:
    def __init__(self):
        self.url_pok_stats = "https://pokeapi.co/api/v2/pokemon/{}/"
        self.url_pok_varaites = 'https://pokeapi.co/api/v2/pokemon-species/{}/'
    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def get_pokemon_id(self, id):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, self.url_pok_stats.format(id))
            data = json.loads(html)
            data_varaities = await self.fetch(session, self.url_pok_varaites.format(id))
            data_varaities = json.loads(data_varaities)
            return Pokemon(data , data_varaities)

async def main():
    pf = PokemonFetch()
    pok = await pf.get_pokemon_id(4)
    print(pok.ID)
    print(pok.Name)
if __name__ == "__main__":
    main()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
