#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import random
import cmd
from sady import config
from sady.player import MPlayer

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


class PlayerCMD(cmd.Cmd):
    """
    Simple Player
    """
    prompt = 'mbox>'
    intro = '%s%s%s' % ('-' * 5, 'Relax', '-' * 5)

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.player = MPlayer()

    def do_search(self, q):
        """search track by keywords"""
        self.player.search(q, False)

    def do_history(self, p):
        """show cached last tracks"""
        self.player.show_history()

    def do_p(self, name):
        """search and play track by every thing input(ex: p let's it go)"""
        if not name:
            name = random.choice(TRACK_NAMES)
        self.player.search(name, True)

    def do_select(self, index):
        """select one track to play by index"""
        self.player.select_track(index)

    def do_local(self, arg):
        """show local data"""
        self.player.show_synced()

    def do_sync(self, arg):
        """show local data"""
        self.player.sync_all()

# lib ref
# https://pymotw.com/2/cmd/
# https://developers.soundcloud.com/docs/api/reference
