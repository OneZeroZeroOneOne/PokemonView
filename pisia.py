import random
import json
import aiohttp
import asyncio

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()


def sortir(Spisok):
    peple = [i['first_name']+" "+i['last_name'] for i in Spisok['data']]
    return peple


async def main():
    DataList = await fetch("https://reqres.in/api/users?page=2")
    #print(DataList)
    peple = list()
    #print(sortir(DataList))
    #print([random.randint(-100, 100) for i in range(0,random.randint(0, 100),1)])
    #print(ord('c'))
    #print([ord('a')+i for i in range(0,24,1)])
    print(dict.fromkeys([chr(ord('a')+i) for i in range(0,24,1)], ord(dict.keys()) ))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
