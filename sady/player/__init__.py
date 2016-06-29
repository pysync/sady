import logging

from sady import config
from sady.store import TrackList
from sady.ui import UI
from sady.gateway import Gateway
from enum import Enum
import subprocess

logger = logging.getLogger(__name__)

logger.info('-- app starting...')


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
        self.search_result = []
        self.action = Action.playlist

    def search(self, q, start=False):
        """ search track online by query"""
        self.ui.show_wait("searching..")
        self.action = Action.search
        result = self.loop.run_until_complete(self.gw.search(query=q))
        if not result:
            self.ui.show_message("not found track with query=%s" % q)
        else:
            self.search_result = result
            for result in self.search_result:
                track = self.tracks_list.track_by_id(result.get_track_id())
                if track:
                    result.update(synced=True, local_uri=track.local_uri)
        self.ui.show_tracks(self.search_result)
        if start:
            self.__select_one(self.search_result, 0)

    def search_history(self):
        if not self.search_result:
            self.ui.show_message("history empty")
        else:
            self.ui.show_tracks(self.search_result)

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
        offset, page = self.tracks_list.curr_page()
        self.action = Action.playlist

        if not page:
            offset = 0
            page = self.tracks_list.top_tracks()

        if not page:
            self.ui.show_message("playlist empty")
        else:
            self.ui.show_tracks(page, offset)

    def show_next_page(self):
        offset, next_tracks = self.tracks_list.next_page()
        self.action = Action.playlist

        if not next_tracks:
            self.ui.show_message("playlist empty")
        else:
            self.ui.show_tracks(next_tracks, offset)

    def show_prev_page(self):
        offset, prev_tracks = self.tracks_list.prev_page()
        self.action = Action.playlist

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
        if self.action == Action.playlist:
            self.show_next_page()
        else:
            pass

    def prev(self):
        """show prev page using current context"""
        if self.action == Action.playlist:
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
            self.ui.show_message('index = {0} '.format(index - offset))
            for t in page:
                print(t.title)
            self.__select_one(page, index - offset)
        else:
            self.__select_one(self.search_result, index)

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
