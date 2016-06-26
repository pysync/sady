import logging
from sady.store import Track
from sady import config

import soundcloud
import threading
from Queue import Queue
import requests
import tempfile
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 512 * 1024
MAX_THREADS = 4


def __to_tracks(resources):
    """
    convert from sound cloud track resource to local store track
    :param resources:
    :return:
    """
    return [Track(id=resource.id,
                  title=resource.title,
                  playback_count=resource.playback_count,
                  genre=resource.genre,
                  synced=False,
                  local_uri=None,
                  stream_url=resource.stream_url,
                  download_url=resource.download_url,
                  ) for resource in resources if hasattr(resource, 'id')]


client = soundcloud.Client(client_id=config.CLIENT_ID)


def search(query):
    """
    search by query string via sound cloud service
    :param query:
    :return: list of track
    """
    logger.info('>> search track with q=%s' % query)
    resources = client.get('/tracks', q=query, limit=config.SEARCH_RESULT_LIMIT)
    tracks = __to_tracks(resources)
    logger.info('>> result count %s' % len(tracks))
    return tracks


def __extract_stream_url(track):
    """
    get downloadable stream url from track
    :param track:
    :return: download url
    """
    resource = client.get(track.stream_url,
                          allow_redirects=False)
    return resource.location


def download(track):
    """
    download track by stream url or download url
    :param track:
    :return: saved file path
    """
    download_url = track.download_url or __extract_stream_url(track)

    request = requests.get(download_url)

    (fd, filename) = tempfile.mkstemp(prefix='track_', dir=config.TRACK_DIR)
    try:
        fh = os.fdopen(fd, 'wb')
        for chunk in request.iter_content(CHUNK_SIZE):
            if chunk:
                fh.write(chunk)
        fh.close()
    except IOError as e:
        logger.error('failed for download %s' % e)

    return filename


class Worker(threading.Thread):
    def __init__(self, thread_id, thread_group, func, callback, *args, **kwargs):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.thread_group = thread_group
        self.func = func
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def run(self):
        logger.info('[%s-%s] starting..' % (self.thread_group, self.thread_id))
        result = self.func(*self.args, **self.kwargs)
        logger.info('[%s-%s] ending with: %s' % (self.thread_group, self.thread_id, result))

        if self.callback:
            self.callback(self.thread_id, self.thread_group, result)
        return result

    def start_with_callback(self, callback):
        self.callback = callback
        self.start()


class DownloadTask(object):
    def __init__(self, track, on_finish):
        self.track = track
        self.on_finish = on_finish


class Downloader(object):
    def __init__(self, finish_handler):
        self.finish_handler = finish_handler
        self.queue = Queue(maxsize=0)
        self.workers = []

    def __init_workers__(self):
        for i in range(MAX_THREADS):
            worker = threading.Thread(target=self.exec_download, args=())
            worker.setDaemon(True)
            worker.start()

    def exec_download(self):
        while True:
            task = self.queue.get()
            local_uri = download(task.track)
            task.track.update(local_uri=local_uri, synced=True)

            if task.on_finish:
                task.on_finish(task.track)
            self.queue.task_done()

    def add_tasks(self, tasks):
        if not self.workers:
            self.__init_workers__()

        for task in tasks:
            self.queue.put(task)
        self.queue.join()

        if self.finish_handler:
            self.finish_handler()
