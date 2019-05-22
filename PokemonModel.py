# coding=utf8
import aiohttp
import asyncio
import json
import time
import logging

import asyncpool
import config

from aiocache import cached
from aiocache.serializers import PickleSerializer

from schematics.models import Model
from schematics.types import StringType, URLType, DecimalType, ListType, IntType


class Pokemon(Model):
    ID = IntType(required = True)
    Name = StringType(required = True)
    Weight = IntType(required = True)
    HP = IntType(required = True)
    Attack = IntType(required = True)
    Defense = IntType(required = True)
    Speed = IntType(required = True)
    SpecialAttack = IntType(required = True)
    SpecialDefense = IntType(required = True)
    Types = ListType(StringType)
    Image = URLType(required = True)
    Varieties = ListType(IntType)

    EvolutionChainUrl = URLType()

    BackSprite = URLType()
    FrontSprite = URLType()

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


        self.BackSprite = data_stats['sprites']['back_default']
        self.FrontSprite = data_stats['sprites']['front_default']

        self.EvolutionChainUrl = data_varaities['evolution_chain']['url']
        self.Varieties = [i['pokemon']['url'].split("/")[-2] for i in data_varaities["varieties"]][1:]

        self.validate()

    async def GetForms(self):
        return await PokemonFetch.Instance().get_pokemon_id_list(self.Varieties)


    async def GetEvolutions(self):
        """
            return dictionary
            ['from'] - from who this pokemon evoltion
            ['into'] - in which this pokemon can evolute
        """
        from_list = []
        into_list = []
        evolution_list = self.flat_evolution_list(
                        await PokemonFetch.Instance().get_pokemon_evolution_chain(self.EvolutionChainUrl),
                        new_l = [])

        for n, i in enumerate(evolution_list):
            if str(self.ID) in i:
                if n-1!=-1:
                    from_list = evolution_list[n-1]
                if n+1!=len(evolution_list):
                    into_list = evolution_list[n+1]
        """
            я хз чі код ниже асінхронний треба переробить
            хз
        """
        return {"from":await PokemonFetch.Instance().get_pokemon_id_list(from_list),
                "into":await PokemonFetch.Instance().get_pokemon_id_list(into_list)}


    def DefenseType(self):
        return self.Types[0]


    def AttackType(self):
        if len(self.Types)==1:
            return ""
        return self.Types[1]


    def ToString(self):
        return config.pokemon_description.format(self.Name, '123', self.Attack,
        self.HP, self.Defense, ', '.join(self.Types),
        self.SpecialAttack, self.SpecialDefense, self.Speed,
        'володя дороби поколеніє', 'ВОЛО', self.ID,self.Image)

    def __str__(self):
        return "<Pokemon ID: {}>".format(self.ID)

    def __repr__(self):
        return str(self)

    def flat_evolution_list(self, l, new_l = [], pos = 0):
        if (pos==0):
            new_l.append([l['species']['url'].split("/")[-2]])
        else:
            new_l[-1].append(l['species']['url'].split("/")[-2])
        if l['evolves_to']:
            for n, i in enumerate(l['evolves_to']):
                self.flat_evolution_list(i, new_l = new_l, pos = n)

        return new_l


class PokemonFetch:
    url_pok_stats = "https://pokeapi.co/api/v2/pokemon/{}/"
    me = None

    def __init__(self):
        """
            ???
        """
        pass

    async def fetch(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None

    async def result_reader_list(self, queue, start_id):
        poks = [None for i in range(0, config.pokemons_per_page, 1)]
        while True:
            value = await queue.get()
            if value is None:
                break
            #print("Got value! -> {}".format(value))
            poks[int(value.ID)-start_id] = value

        return poks

    async def result_reader_id_list(self, queue):
        poks = []
        while True:
            value = await queue.get()
            if value is None:
                break
            #print("Got value! -> {}".format(value))
            poks.append(value)

        return poks

    def key_builder_id(*args):
        return args[2]

    @staticmethod
    def Instance():
        if PokemonFetch.me is None:
            PokemonFetch.me = PokemonFetch()
        return PokemonFetch.me


    @cached(key_builder = key_builder_id, namespace = "get_pokemon_evol_chain")
    async def get_pokemon_evolution_chain(self, url):
        """
            return pokemon evol chain
        """
        chain = await self.fetch(url)
        return chain['chain']


    @cached(key_builder = key_builder_id, namespace = "get_pokemon_id")
    async def get_pokemon_id(self, id):
        data_stats = await self.fetch(PokemonFetch.url_pok_stats.format(id))
        data_varaities = await self.fetch(data_stats['species']['url'])
        return Pokemon(data_stats, data_varaities)


    @cached(key_builder = key_builder_id, namespace = "_get_pokemon_id")
    async def _get_pokemon_id(self, id, result_queue):
        data_stats = await self.fetch(PokemonFetch.url_pok_stats.format(id))
        data_varaities = await self.fetch(data_stats['species']['url'])
        await result_queue.put(Pokemon(data_stats, data_varaities))


    @cached(key_builder = key_builder_id, namespace = "get_pokemon_list")
    async def get_pokemon_list(self, start_id):
        """
            in: start_id(where from to start offset): 1
            return: list of pokemons instances start_id + pok_per_page: 1+6
            so it be pokemons with id: [1, 2, 3, 4, 5, 6]
            sorted
        """
        result_queue = asyncio.Queue()
        reader_future = asyncio.ensure_future(self.result_reader_list(result_queue, start_id), loop=asyncio.get_running_loop())

        async with asyncpool.AsyncPool(asyncio.get_running_loop(), num_workers=config.pokemons_per_page, name="GetPokemonListPool",
                                logger=logging.getLogger("PokemonListPool"),
                                worker_co=self._get_pokemon_id, max_task_time=config.pool_task_time,
                                log_every_n=10) as pool:
            for i in range(start_id, start_id + config.pokemons_per_page, 1):
                await pool.push(i, result_queue)

        await result_queue.put(None)
        return await reader_future


    @cached(key_builder = key_builder_id, namespace = "get_pokemon_id_list")
    async def get_pokemon_id_list(self, id_list):
        """
            in: list with ids [1, 100, 120, 90, ....]
            return: pokemons instances with this ids
            warn: return not sorted list
        """
        result_queue = asyncio.Queue()
        reader_future = asyncio.ensure_future(self.result_reader_id_list(result_queue), loop=asyncio.get_running_loop())

        async with asyncpool.AsyncPool(asyncio.get_running_loop(), num_workers=len(id_list)+1, name="GetPokemonListPool",
                                logger=logging.getLogger("PokemonListIdPool"),
                                worker_co=self._get_pokemon_id, max_task_time=config.pool_task_time,
                                log_every_n=10) as pool:
            for i in id_list:
                await pool.push(i, result_queue)

        await result_queue.put(None)
        return await reader_future
