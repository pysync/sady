import logging

from sady import config
from sady.store import TrackList, SearchResult
from sady.ui import UI
from sady.gateway import Gateway
from enum import Enum
import subprocess

logger = logging.getLogger(__name__)

logger.debug('-- app starting...')


class Action(Enum):
    search = 1
    history = 2
    playlist = 3
    play = 4


class MPlayer(object):
    TASK_SEARCH = 'QUERY'
    MAX_SEARCH_TASK = 1

    def __init__(self, loop):
        self.ui = UI()
        self.loop = loop
        self.gw = Gateway(loop)
        self.tracks_list = TrackList(config.PAGE_SIZE,
                                     config.TRACK_DATA_FILE,
                                     config.PLAYLIST_FILE)
        self.search_result = SearchResult(config.PAGE_SIZE, [])
        self.action = Action.playlist

    def search(self, q, start=False):
        """ search track online by query"""
        self.ui.show_wait("searching..")
        self.action = Action.search
        results = self.loop.run_until_complete(self.gw.search(query=q))
        if not results:
            self.ui.show_message("not found track with query=%s" % q)
        else:
            self.search_result.set(results)
            for result in self.search_result.tracks:
                track = self.tracks_list.track_by_id(result.get_track_id())
                if track:
                    result.update(synced=True, local_uri=track.local_uri)

        top_tracks = self.search_result.top_tracks()
        self.ui.show_tracks(top_tracks)
        if start:
            self.__select_one(top_tracks, 0)

    def search_history(self):
        self.action = Action.search
        if not self.search_result.tracks:
            self.ui.show_message("history empty")
        else:
            self.ui.show_tracks(self.search_result.top_tracks())

    def play(self, track):
        """ start play a track """
        self.ui.show_message("[start]mplayer..: %s" % track.title)
        subprocess.call(['mplayer',
                         '-vo',
                         'null',
                         track.local_uri]
                        )
        self.ui.show_message('[end]mplayer..')

    def show_top_tracks(self):
        top_tracks = self.tracks_list.top_tracks()
        self.action = Action.playlist

        if not top_tracks:
            self.ui.show_message("playlist empty")
        else:
            self.ui.show_tracks(top_tracks)

    def show_curr_page(self):
        if self.action == Action.playlist:
            source = self.tracks_list
        else:
            source = self.search_result

        offset, page = source.curr_page()

        if not page:
            offset = 0
            page = source.top_tracks()

        if not page:
            self.ui.show_message("playlist empty")
        else:
            self.ui.show_tracks(page, offset)

    def show_next_page(self):
        if self.action == Action.playlist:
            source = self.tracks_list
        else:
            source = self.search_result

        offset, next_tracks = source.next_page()

        if not next_tracks:
            self.ui.show_message("playlist empty")
        else:
            self.ui.show_tracks(next_tracks, offset)

    def show_prev_page(self):
        if self.action == Action.playlist:
            source = self.tracks_list
        else:
            source = self.search_result

        offset, prev_tracks = source.prev_page()

        if not prev_tracks:
            self.ui.show_message("playlist empty")
        else:
            self.ui.show_tracks(prev_tracks, offset)

    def start_playlist(self):
        """start a playlist by absolute file path"""
        self.ui.show_message('start playlist')
        subprocess.call(['mplayer',
                         '-vo',
                         'null',
                         '-playlist',
                         self.tracks_list.playlist_uri,
                         '-shuffle']
                        )
        self.ui.show_message('end playlist')

    def next(self):
        """show next page using current context"""
        if self.action in (Action.playlist, Action.search):
            self.show_next_page()
        else:
            pass

    def prev(self):
        """show prev page using current context"""
        if self.action in (Action.playlist, Action.search):
            self.show_prev_page()
        else:
            pass

    def select(self, index):
        """start a track by index"""

        try:
            index = int(index)
        except ValueError as e:
            self.ui.show_message("invalid index")
            return

        if self.action == Action.playlist:
            offset, page = self.tracks_list.curr_page()
        else:
            offset, page = self.search_result.curr_page()

        self.ui.show_message('index = {0} '.format(index - offset))
        self.__select_one(page, index - offset)

    def sync(self, indices=None):
        """sync result of search by indices
        """
        track_list = self.search_result.tracks
        if not track_list:
            self.ui.show_message('empty list')
            return

        if not indices:
            valid_indices = range(0, len(track_list))
        else:
            valid, err, valid_indices = self.__validate_indices(track_list, indices)
            if not valid:
                self.ui.show_message(err)
                return

        def __update_func(future):
            track, local_uri = future.result()
            if not local_uri:
                self.ui.show_message("sync [{0}]{1} failed.".format(track.id, track.title))
            else:
                self.tracks_list.update(track.get_track_id(), True, synced=True, local_uri=local_uri)
                track.update(local_uri=local_uri, synced=True)
                self.ui.show_message("synced [{0}]{1} -> {2}".format(track.id, track.title, local_uri))

        tracks = [self.search_result.tracks[i] for i in valid_indices]
        self.tracks_list.add_all(track_list, True)
        self.ui.show_message('syncing..')
        self.loop.run_until_complete(self.gw.downloads(tracks, __update_func, None))
        self.ui.show_tracks(track_list)
        self.ui.show_message('synced done.')

    def __select_one(self, current_list, index):
        """select one track in list by index and play
        if track not in track list - add track to track list
        if track not sync yet - sync track
        """
        if not self.__validate_select(current_list, index):
            return
        track = current_list[index]
        if not track.is_playable():
            self.ui.show_message("track: {0} cannot play, track required to purchase or credit".format(track.title))
            return

        self.tracks_list.add(track, True)

        if track.synced and track.local_uri:
            self.play(track)
        else:
            """ track not synced yet"""
            self.ui.show_wait('syncing..')
            _, local_uri = self.loop.run_until_complete(self.gw.download(track))
            if not local_uri:
                self.ui.show_message('cannot syncing track data - please select other track to play')
                return

            self.__synced_handler(track, local_uri, current_list, True)

    def __synced_handler(self, track, local_uri, current_list, start=False):
        """ update track after sync"""
        if not local_uri:
            self.ui.show_message('track {0} sync failed.'.format(track.title))
            return

        self.tracks_list.update(track.get_track_id(), True, synced=True, local_uri=local_uri)
        self.ui.show_tracks(current_list)
        self.ui.show_message('track {0} synced.'.format(track.title))
        if start:
            self.play(self.tracks_list.track_by_id(track.get_track_id()))

    def __validate_select(self, track_list, index):
        if not track_list:
            """ track list is empty """
            self.ui.show_message("track list is empty")
            return False
        if index < 0 or index >= len(track_list):
            """ invalid selection """
            self.ui.show_message("invalid, expect index in: [%s -> %s]" % (0, len(track_list)))
            return False
        return True

    @classmethod
    def __validate_indices(cls, track_list, indices):
        valid_indices = []
        length = len(track_list)
        error = None
        for i in indices:
            if not i.isdigit():
                error = "in valid select for index: {0}, index must be digit".format(i)
                return False, error, valid_indices
            else:

                index = int(i)
                if index < 0 or index >= length:
                    error = "invalid index {0}, expect index must in: [{0} -> {1}]".format(index, 0, length)
                    return False, error, valid_indices
                else:
                    valid_indices.append(index)
        return True, error, valid_indices
