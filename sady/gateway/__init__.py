import logging
import soundcloud
import requests
import tempfile
import os
from sady.store import Track
from sady import config
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 512 * 1024


class Gateway(object):
    def __init__(self, loop):
        self.client = soundcloud.Client(client_id=config.CLIENT_ID)
        self.loop = loop

    async def search(self, query, callback=None):
        """
        search by query string via sound cloud service
        :param query:
        :param callback:
        :return: list of track
        """

        def sync_search(q):
            resources = self.client.get('/tracks', q=q, limit=config.SEARCH_RESULT_LIMIT)
            return self.__to_tracks(resources)

        future = self.loop.run_in_executor(None, sync_search, query)
        if callback:
            future.add_done_callback(callback)
        return await future

    async def download(self, track, callback=None):
        """
        download content from track stream uri or track download url and write to file
        :param track:
        :param callback: (track, local_uri)
        :return: saved local uri
        """

        def sync_write(content):
            (fd, filename) = tempfile.mkstemp(prefix='track_', dir=config.TRACK_DIR)
            try:
                fh = os.fdopen(fd, 'wb')
                for chunk in content.iter_content(CHUNK_SIZE):
                    if chunk:
                        fh.write(chunk)
                fh.close()
            except IOError as e:
                logger.error('failed for download {0}'.format(e))
            return filename

        def sync_download():
            if not track.is_downloadable() and not track.is_streamable():
                logger.warn('track: {0} cannot download or stream'.format(track.get_track_id()))
                return track, None

            if track.download_url:
                url = track.download_url
            else:
                resource = self.client.get(track.stream_url, allow_redirects=False)
                url = resource.location
            logger.debug('download {0} by url {1}'.format(track.id, url))
            return track, sync_write(requests.get(url))

        future = self.loop.run_in_executor(None, sync_download)
        if callback:
            future.add_done_callback(callback)
        return await future

    async def downloads(self, tracks, update_func=None, finish_func=None):
        tasks = [self.download(track, callback=update_func) for track in tracks]
        results = await asyncio.gather(*tasks)
        if finish_func:
            finish_func(results)
        return results

    @classmethod
    def __to_tracks(cls, resources):
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
                      downloadable=resource.downloadable,
                      streamable=resource.streamable,
                      ) for resource in resources if hasattr(resource, 'id')]
