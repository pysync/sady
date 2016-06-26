#!/usr/bin/python
# -*- coding: utf-8 -*-
import click
from sady import PlayerCMD


@click.command()
@click.option('--query', '-q',
              multiple=True,
              default=[],
              help='track keywords')
def start(query):
    if len(query):
        cmd = 'p %s' % ' '.join(query)
        player = PlayerCMD()
        player.onecmd(cmd)
        player.cmdloop()
    else:
        PlayerCMD().cmdloop()
