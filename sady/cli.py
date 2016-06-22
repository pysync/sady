#!/usr/bin/python
# -*- coding: utf-8 -*-
import click
from sady import Player

@click.command()
@click.option('--query', '-q',
              multiple=True,
              default=[],
              help='track keywords')
def start(query):
    if len(query):
        cmd = 'p %s' % ' '.join(query)
        Player().onecmd(cmd)
        Player().cmdloop()
    else:
        Player().cmdloop()
