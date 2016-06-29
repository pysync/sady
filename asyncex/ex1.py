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


async def basic_async():
    for s in Seconds:
        print('{0} starting..'.format(s[0]))
        r = await sleeping(*s)
        print('{0} is finished.'.format(r))
    return True


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(basic_async())
