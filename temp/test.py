import time
import aiofile


async def main():
    now = time.perf_counter()
    with open("./temp/f.py", "r") as f:
        g = f.read()

    print(time.perf_counter() - now)

    now = time.perf_counter()
    with open("./temp/f.py", "r") as f:
        g = ""
        for i in f:
            g += i

    print(time.perf_counter() - now)

    now = time.perf_counter()
    async with aiofile.async_open("./temp/f.py", "r") as f:
        g = await f.read()

    print(time.perf_counter() - now)

    now = time.perf_counter()
    async with aiofile.async_open("./temp/f.py", "r") as f:
        async for i in f:
            g += i

    print(time.perf_counter() - now)


import asyncio

asyncio.run(main())
