import asyncio
from

async def main():
    start_time = time.time()
    pok = await PokemonFetch.get_pokemon_id(6)
    print(pok.ToString())
    pok_forms = await pok.GetForms()
    for new_pokemon in pok_forms:
        print(new_pokemon.ToString())

    print("Времени понадобилось для первого вызова {}".format(time.time() - start_time))

    start_time = time.time()
    pok = await PokemonFetch.get_pokemon_id(6)
    print(pok.ToString())
    pok_forms = await pok.GetForms()
    for new_pokemon in pok_forms:
        print(new_pokemon.ToString())

    print("Времени понадобилось для второго вызова {}".format(time.time() - start_time))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
