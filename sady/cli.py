#!/usr/bin/python
# -*- coding: utf-8 -*-
import click
from sady import Player

@click.command()
def start():
    Player().cmdloop()
