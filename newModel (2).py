# coding=utf8
import aiohttp
import asyncio
import json

class Pokemon:
    def __init__(self, data):
        self.id = data['id']
        self.name = data["name"]
        #self.var = data['varieties']

class PokemonFetch:
    def __init__(self):
        self.url = "https://pokeapi.co/api/v2/pokemon/{}/"

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def get_pokemon_id(self, id):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, self.url.format(id))
            data = json.loads(html)
            return Pokemon(data)

async def main():
    pf = PokemonFetch()
    pok = await pf.get_pokemon_id(10034)
    print(pok.id)
    print(pok.name)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
