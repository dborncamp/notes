"""_summary_ A Python testing function for the tester since `nc` is not available everywhere.
"""

import asyncio
import random

import aioudp


async def recieve(queue):
    """Asyncrinously produce UDP messages by using an async queue
    """
    while True:
        connection = await queue.get()
        data = await connection.recv()
        print(f"Recieved: {data}")


async def producer(queue):
    """Asyncrinously produce UDP messages by using an async queue
    """
    sentinel = 0
    # while True:
    i = random.randint(0, 100)
    print(f"Sending random number: {i}")
    async with aioudp.connect("127.0.0.1", 8080) as connection:
        await connection.send(bytes(str(i), 'utf-8'))
        await queue.put(connection)
        await asyncio.sleep(1)
        # sentinel += 1
        # if sentinel > 10:
        #     break


async def main():
    """Start testing"""
    queue = asyncio.Queue()

    producers = [asyncio.create_task(producer(queue))
                 for _ in range(30)]
    recievers = [asyncio.create_task(recieve(queue))
                 for _ in range(30)]

    # with both producers and consumers running, wait for
    # the producers to finish
    await asyncio.gather(*producers)
    # await asyncio.gather(*recievers)
    print('---- done producing')

    # wait for the remaining tasks to be processed
    await queue.join()

    # cancel the consumers, which are now idle
    for r in recievers:
        r.cancel()

if __name__ == '__main__':
    asyncio.run(main())
