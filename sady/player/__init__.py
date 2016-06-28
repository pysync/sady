import logging

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
        self.ui = UI()
        self.tracks_list = store.TrackList(config.TRACK_DATA_FILE, config.PLAYLIST_FILE)
        self.playlist_uri = self.tracks_list.playlist_uri
        self.search_result = []

    def search(self, q, start=False):
        """ search track online by query"""
        self.ui.show_wait("searching..")
        result = gateway.search(query=q)
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
                         self.tracks_list.playlist_uri,
                         '-shuffle']
                        )
        self.ui.show_message('end playlist')

    def __select_one(self, current_list, index):
        """select one track in list by index and play
        if track not in track list - add track to track list
        if track not sync yet - sync track
        """

        try:
            index = int(index)
        except ValueError as e:
            self.ui.show_message("invalid index")
            return
        if not self.__validate_select(current_list, index):
            return
        track = current_list[index]
        self.tracks_list.add(track, True)

        if track.synced and track.local_uri:
            self.play(track)
        else:
            """ track not synced yet"""
            self.ui.show_wait('syncing..')
            gateway.download([track],
                             lambda t, u: self.__synced_handler(t, u, current_list, True), None)

    def __synced_handler(self, track, url, current_list, start=False):
        """ update track after sync"""
        self.tracks_list.update(track.get_track_id(), True, synced=True, local_uri=url)
        self.ui.show_tracks(current_list)
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
