import asyncio
from urllib.request import urlopen
from time import time
from time import sleep

urls = [
    'http://google.com',
    'http://github.com',
    'http://mazii.net',
]


# this sis a synchronous function
# it will block until data available
def sync_get_url(url):
    sleep(2)
    return urlopen(url).read()


# wrap for get url by return data in future
async def async_download(url, callback=None):
    future = loop.run_in_executor(None, sync_get_url, url)
    future.add_done_callback(callback)
    return await future


async def parallel_by_gather(urls):
    start_time = time()
    print('func start at: {0}'.format(start_time))

    def notify(future):
        try:
            r = future.result()
            print('done after: {0}'.format(time() - start_time))
        except Exception as e:
            print('exception: {0}'.format(e))

    cors = [async_download(url, callback=notify) for url in urls]
    ret = await asyncio.gather(*cors)
    print('total time: {0}'.format(time() - start_time))
    return ret

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(parallel_by_gather(urls))
    for r in results:
        print('asyncio.gather result: {0}'.format(r))

    start_time = time()
    print('func start at: {0}'.format(start_time))
    result = loop.run_until_complete(async_download('http://nhaccuatui.com',
                                                    lambda r: print('r: {0}'.format(r.result()))))
    print('done after: {0}'.format(time() - start_time))

