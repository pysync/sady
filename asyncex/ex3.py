import asyncio

Seconds = [
    ("first", 5),
    ("second", 0),
    ("third", 3)
]


async def sleeping(order, seconds, hook=None):
    await asyncio.sleep(seconds)
    if hook:
        hook(order)
    return order


async def parallel_by_gather():
    def notify(order):
        print('{0} has just finished.'.format(order))

    cors = [sleeping(s[0], s[1], hook=notify) for s in Seconds]
    results = await asyncio.gather(*cors)
    return results


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(parallel_by_gather())
    for r in results:
        print('asyncio.gather result: {0}'.format(r))
