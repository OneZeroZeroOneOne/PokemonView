import asyncio
from PokemonModel import *

async def main():

    start_time = time.time()
    pok_count = 0
    pok = await PokemonFetch.get_pokemon_id(1)
    print(pok.ToString())

    print("Времени понадобилось для первого вызова {}\nВсего покемонов создано {}".format(time.time() - start_time, pok_count))
    start_time = time.time()
    pokes = await PokemonFetch.get_pokemon_list(1)
    for i in pokes:
        print(i)
    print("Времени понадобилось для второго вызова {}".format(time.time() - start_time))
    start_time = time.time()
    pokes = await PokemonFetch.get_pokemon_list(1)
    for i in pokes:
        print(i)
    print("Времени понадобилось для третьего вызова {}".format(time.time() - start_time))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
