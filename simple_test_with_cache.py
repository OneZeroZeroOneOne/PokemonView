import asyncio
from PokemonModel import *

async def main():
    '''
    start_time = time.time()
    pok_count = 0
    for i in range(1, 10, 1):
        pok = await PokemonFetch.get_pokemon_id(i)
        #print(pok.ToString())
        pok_count +=1
        pok_forms = await pok.GetForms()
        for new_pokemon in pok_forms:
            pok_count +=1
            #print(new_pokemon.ToString())

    print("Времени понадобилось для первого вызова {}\nВсего покемонов создано {}".format(time.time() - start_time, pok_count))

    start_time = time.time()
    pok_count = 0
    for i in range(1, 10, 1):
        pok = await PokemonFetch.get_pokemon_id(i)
        pok_count +=1
        #print(pok.ToString())
        pok_forms = await pok.GetForms()
        for new_pokemon in pok_forms:
            pok_count +=1
            #print(new_pokemon.ToString())

    print("Времени понадобилось для второго вызова {}\nВсего покемонов создано {}".format(time.time() - start_time, pok_count))
    '''
    start_time = time.time()
    pokes = await PokemonFetch.get_pokemon_list(1)
    for i in pokes:
        print(i.ToString())
    print("Времени понадобилось для первого вызова {}".format(time.time() - start_time))
    start_time = time.time()
    pokes = await PokemonFetch.get_pokemon_list(1)
    for i in pokes:
        print(i.ToString())
    print("Времени понадобилось для второго вызова {}".format(time.time() - start_time))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
