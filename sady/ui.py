#!/usr/bin/python
# -*- coding: utf-8 -*-

from tabulate import tabulate

TRACK_HEADERS = ('#no', '#id', '#title', '#playback', '#genre')
HEADER_RULER = '-' * 15

STORE_HEADERS = ('#id', '#path')

def show_tracks(tracks):
    data = [(index,
             track.id,
             track.title,
             track.playback_count,
             track.genre) for (index, track) in enumerate(tracks)]
    print tabulate(data, headers=TRACK_HEADERS)


def show_files(files):
    data = [(track_id, path)
            for (track_id, path) in files.items()]
    print tabulate(data, headers=STORE_HEADERS)

def show_msg(msg):
    padding = (len(HEADER_RULER) - len(msg)) / 2 - 1
    formatted_msg = '%s %s %s' % ('-' * padding, msg, '-' * padding)
    print formatted_msg
