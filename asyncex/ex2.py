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


async def basic_async(num):
    for s in Seconds:
        print('[{0}]{1} starting..'.format(num, s[0]))
        r = await sleeping(*s)
        print('[{0}]{1} is finished.'.format(num, r))
    return True


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(basic_async(1))
    asyncio.ensure_future(basic_async(2))
    loop.run_forever()
