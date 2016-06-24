#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import soundcloud
import subprocess
import random
import cmd
from ui import show_tracks, show_files
from ui import show_msg
from store import History
from store import PlayList
from sady import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


"""
sample track keywords
"""
TRACK_NAMES = [
    'neu vang anh',
    'buc tranh tu nuoc mat',
    'what make you beautyful',
    'Beautiful Japanese Song',
    'japanese beautiful piano & violin music',
    'My Love - Lee Seung Chul',
    'Casablanca - Bertie Higgins'
]

""" search result limit """
SEARCH_RESULT_LIMIT = 20

""" client id """
CLIENT_ID = 'eca1790e16470735633dd7ee79dd6074'


class Player(cmd.Cmd):
    """
    Simple Player
    """
    prompt = 'mbox>'
    intro = '%s%s%s' % ('-' * 5, 'Relax', '-' * 5)

    def __init__(self):
        cmd.Cmd.__init__(self)

        self.client = soundcloud.Client(client_id=CLIENT_ID)
        self.tracks = []
        self.playlist = PlayList()
        self.history = History()
        self.track_id = None
        self.q = None

    def show_track(self, track):
        formatted_track = '%s' % track.title
        print formatted_track

    def do_search(self, q):
        """search track by keywords"""
        tracks = self.client.get('/tracks', q=q, limit=SEARCH_RESULT_LIMIT)
        if tracks:
            self.history.update(q, tracks)
            self.tracks = tracks
            show_tracks(self.tracks)
        else:
            show_msg('NotFound')

    def do_history(self, p):
        """show cached last tracks"""
        if self.history.size():
            self.tracks = self.history.all_tracks()
            show_tracks(self.tracks)
        else:
            show_msg('Empty')

    def do_p(self, name):
        """search and play track by every thing input(ex: p let's it go)"""
        if not name:
            name = self.random_track()

        show_msg('searching..: %s' % name)
        tracks = self.client.get('/tracks', q=name, limit=1)
        if not len(tracks):
            show_msg('NotFound')
            return

        track = tracks[0]
        show_msg('loading..: %s' % track.title)

        track_file_path = self.playlist.get(track.id)
        if not track_file_path:
            resource = self.client.get(track.stream_url,
                                       allow_redirects=False)
            track_file_path = self.playlist.write(track.id,
                                                  resource.location)
        self.play_track(track_file_path)
        self.start_playlist()

    def do_select(self, index):
        """select one track to play by index"""

        if not self.tracks:
            show_msg('Empty List')
        else:
            index = int(index)
            if index != -1 and index not in range(0, len(self.tracks)):
                show_msg('index in: [%s -> %s]' % (0, len(self.tracks)))
            else:

                track = self.tracks[index]
                show_msg('loading..: %s' % track.title)
                track_file_path = self.playlist.get(track.id)
                if not track_file_path:
                    resource = self.client.get(track.stream_url,
                                               allow_redirects=False)
                    track_file_path = self.playlist.write(track.id,
                                                          resource.location)

                self.play_track(track_file_path)
                self.start_playlist()

    def do_inspect(self, arg):
        """show local data"""
        show_files(self.playlist.track_data)

    def play_track(self, track_file_path):
        """start track by absolute file path"""
        show_msg('starting player')
        subprocess.call(['mplayer',
                         '-vo',
                         'null',
                         track_file_path]
                        )
        show_msg('ending player')

    def start_playlist(self):
        """start a playlist by absolute file path"""
        show_msg('start playlist')
        subprocess.call(['mplayer',
                         '-vo',
                         'null',
                         '-playlist',
                         self.playlist.playlist_path,
                         '-shuffle']
                        )
        show_msg('end playlist')

    def random_track(self):
        """select random keyword"""
        return random.choice(TRACK_NAMES)

# lib ref
# https://pymotw.com/2/cmd/
# https://developers.soundcloud.com/docs/api/reference
