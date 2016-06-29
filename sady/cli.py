#!/usr/bin/python
# -*- coding: utf-8 -*-
import click
import cmd
import logging
import random
import asyncio
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
    intro = '{0}{1}{2}'.format('-' * 5, 'Relax', '-' * 5)

    def __init__(self, loop):
        cmd.Cmd.__init__(self)
        self.player = MPlayer(loop)

    def do_search(self, q):
        """search track by keywords"""
        self.player.search(q, False)

    def do_play(self, name):
        """search and play track by every thing input(ex: p let's it go)"""
        if not name:
            name = random.choice(TRACK_NAMES)
        self.player.search(name, True)

    def do_any(self, name):
        """search and play track by every thing input(ex: p let's it go)"""
        if not name:
            name = random.choice(TRACK_NAMES)
        self.player.search(name, True)

    def do_history(self, args):
        """show search history"""
        self.player.search_history()

    def do_select(self, index):
        """select one track in showing track list by index and play"""
        self.player.select(index)

    def do_top(self, args):
        """show top tracks in playlist"""
        self.player.show_top_tracks()

    def do_list(self, args):
        """show current page of track list"""
        self.player.show_curr_page()

    def do_next(self, what):
        """do next page | track"""
        if not what:
            self.player.next()

        if what in ('page', 'list'):
            self.player.show_next_page()
        else:
            pass

    def do_prev(self, what):
        """do prev page | track"""
        if not what:
            self.player.prev()
            return

        if what in ('page', 'list'):
            self.player.show_prev_page()
        else:
            pass


@click.command()
@click.option('--query', '-q',
              multiple=True,
              default=[],
              help='track keywords')
def start(query):
    if len(query):
        cmd = 'p {0}'.format(' '.join(query))
        event_loop = asyncio.get_event_loop()
        player = PlayerCMD(event_loop)
        player.onecmd(cmd)
        player.cmdloop()
        event_loop.run_forever()
    else:
        event_loop = asyncio.get_event_loop()
        PlayerCMD(event_loop).cmdloop()
        event_loop.run_forever()
