import logging

import time
from sady import store
from sady.ui import UI
from sady import gateway
from sady import config
import subprocess

logger = logging.getLogger(__name__)

logger.info('-- app starting...')


class MPlayer(object):
    TASK_SEARCH = 'QUERY'
    MAX_SEARCH_TASK = 1

    def __init__(self):
        self.workers = []
        self.ui = UI()
        self.downloader = gateway.Downloader(self.__all_track_synced_handler)
        self.tracks_list = store.TrackList(config.TRACK_DATA_FILE, config.PLAYLIST_FILE)
        self.history_list = store.TrackList(config.SEARCH_HISTORY_FILE, config.HISTORY_PLAYLIST_FILE)
        self.__tracks__ = []
        self.playlist_uri = self.tracks_list.playlist_uri

    def _next_worker_id(self):
        return len(self.workers)

    def _wait_workers(self, group):
        return [worker for worker in self.workers if worker.thread_group == group]

    def _worker_finish_handler(self, worker_id, group_name):
        self.workers = [worker for worker in self.workers if worker.thread_id != worker_id
                        and worker.thread_group != group_name]

    def search_handler(self, worker_id, group_name, result):
        self._worker_finish_handler(worker_id, group_name)
        self.__tracks__ = result
        if self.__tracks__:
            for track in self.__tracks__:
                if self.tracks_list.exists(track.get_track_id):
                    track.update(synced=True)
            self.history_list.add_all(self.__tracks__)

    def show_search_result(self):
        logger.info("tracks: %s" % self.history_list.tracks)
        self.ui.show_tracks(self.__tracks__)

    def show_history(self):
        self.__tracks__ = self.history_list.top_tracks(50)
        self.playlist_uri = self.history_list.playlist_uri
        self.ui.show_tracks(self.__tracks__)

    def show_synced(self):
        self.__tracks__ = self.tracks_list.top_tracks(50)
        self.playlist_uri = self.tracks_list.playlist_uri
        self.ui.show_tracks(self.__tracks__)

    def search(self, q, start=False):
        self.ui.show_wait()

        """wait other finish"""
        while len(self._wait_workers('search')) > self.MAX_SEARCH_TASK:
            time.sleep(1)

        worker = gateway.Worker(self._next_worker_id(),
                                self.TASK_SEARCH,
                                gateway.search,
                                self.search_handler,
                                q)

        self.workers.append(worker)
        worker.start()

        """wait for search"""
        self.ui.show_wait("searching..")
        while worker.isAlive():
            time.sleep(1)
        self.show_search_result()

        if self.__tracks__ and start:
            self.start_playlist()

    def __track_synced_handler(self, track):
        """ handle on synced event"""
        self.show_search_result()
        self.play(track)

    def __all_track_synced_handler(self):
        """ handle on all track synced event """
        self.ui.show_message("all track synced -- refresh ui")
        self.history_list.flush()
        self.tracks_list.flush()

    def play(self, track):
        """ start play a track """
        self.ui.show_message("playing..: %s" % track.title)
        logger.info(track.to_json())
        subprocess.call(['mplayer',
                         '-vo',
                         'null',
                         track.local_uri]
                        )
        self.ui.show_message('ending player')

    def start_playlist(self):
        """start a playlist by absolute file path"""
        self.ui.show_message('start playlist')
        subprocess.call(['mplayer',
                         '-vo',
                         'null',
                         '-playlist',
                         self.playlist_uri,
                         '-shuffle']
                        )
        self.ui.show_message('end playlist')

    def select_track(self, index):
        try:
            index = int(index)
        except Exception as e:
            self.ui.show_message("invalid select")
            return

        if not self.__validate_select(index):
            return

        track = self.__tracks__[index]

        if not track.synced:
            """ track not synced yet"""
            self.ui.show_wait('syncing..')
            tasks = [gateway.DownloadTask(track, self.__track_synced_handler)]
            self.downloader.add_tasks(tasks)
        else:
            self.play(track)

    def sync_all(self):
        self.ui.show_message("syncing..")
        tasks = [gateway.DownloadTask(track, None) for track in self.__tracks__]
        self.downloader.add_tasks(tasks)

    def sync(self, index):
        if not self.__validate_select(index):
            return

        track = self.__tracks__[index]

        if not track.synced:
            """ track not synced yet"""
            self.ui.show_wait('syncing..')
            tasks = [gateway.DownloadTask(track, self.__track_synced_handler)]
            self.downloader.add_tasks(tasks)
        else:
            """ track already synced"""
            self.ui.show_message("track synced")

    def __validate_select(self, index):
        if not self.__tracks__:
            """ track list is empty """
            self.ui.show_message("track list is empty")
            return False
        if index < 0 or index >= len(self.__tracks__):
            """ invalid selection """
            self.ui.show_message("invalid, expect index in: [%s -> %s]" % (0, len(self.__tracks__)))
            return False
        return True


if __name__ == '__main__':
    player = MPlayer()

    # for q in ('goi mua', 'westlife', 'tuan hung'):
    #     player.search(q)

    player.show_history()
    player.sync_all()
    player.sync(1)
    logger.info('MAIN END')
