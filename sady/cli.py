#!/usr/bin/python
# -*- coding: utf-8 -*-
import click
import cmd
import logging
import random

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

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.player = MPlayer()

    def do_search(self, q):
        """search track by keywords"""
        self.player.search(q, False)

    def do_p(self, name):
        """search and play track by every thing input(ex: p let's it go)"""
        if not name:
            name = random.choice(TRACK_NAMES)
        self.player.search(name, True)


@click.command()
@click.option('--query', '-q',
              multiple=True,
              default=[],
              help='track keywords')
def start(query):
    if len(query):
        cmd = 'p {0}'.format(' '.join(query))
        player = PlayerCMD()
        player.onecmd(cmd)
        player.cmdloop()
    else:
        PlayerCMD().cmdloop()
