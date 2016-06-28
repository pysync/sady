import logging
import soundcloud
import requests
import tempfile
import os
from sady.store import Track
from sady import config
from sady import thread_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 512 * 1024

client = soundcloud.Client(client_id=config.CLIENT_ID)


def search(query):
    """
    search by query string via sound cloud service
    :param query:
    :return: list of track
    """
    logger.info('>> search track with q={0}'.format(query))
    resources = client.get('/tracks', q=query, limit=config.SEARCH_RESULT_LIMIT)
    tracks = __to_tracks(resources)
    logger.info('>> result count {0}'.format(len(tracks)))
    return tracks


def __download(args):
    """
    download track by stream url or download url
    :param track:
    :param handler:
    :return: saved file path
    """
    print ("it's work")
    return 1
    # track, handler = args
    # print "start downloading.........."
    # download_url = track.download_url or __extract_stream_url(track)
    #
    # request = requests.get(download_url)
    #
    # (fd, filename) = tempfile.mkstemp(prefix='track_', dir=config.TRACK_DIR)
    # try:
    #     fh = os.fdopen(fd, 'wb')
    #     for chunk in request.iter_content(CHUNK_SIZE):
    #         if chunk:
    #             fh.write(chunk)
    #     fh.close()
    # except IOError as e:
    #     logger.error('failed for download %s' % e)
    #
    # if handler:
    #     print "----search end---"
    #     #handler(track=track, local_uri=filename)

    # return filename


def download(tracks, update_func, finish_func):
    tasks = [(track, update_func) for track in tracks]
    tasks = [(Track(), update_func) for _ in range(0, 2)]
    thread_pool.map(__download, tasks)

    thread_pool.close()
    thread_pool.join()
    if finish_func:
        finish_func()


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


def __extract_stream_url(track):
    """
    get downloadable stream url from track
    :param track:
    :return: download url
    """
    resource = client.get(track.stream_url,
                          allow_redirects=False)
    return resource.location
