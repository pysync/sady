#!/usr/bin/python
# -*- coding: utf-8 -*-

from tabulate import tabulate

TRACK_HEADERS = ('#no', '#id', '#title', '#playback', '#genre', '#synced')
HEADER_RULER = '-' * 15

STORE_HEADERS = ('#id', '#path')


class UI(object):
    def show_files(self, files):
        data = [(track_id, path)
                for (track_id, path) in files.items()]
        print tabulate(data, headers=STORE_HEADERS)

    def show_tracks(self, tracks):
        data = [(index,
                 track.id,
                 track.title,
                 track.playback_count,
                 track.genre,
                 track.synced or 'False'
                 ) for (index, track) in enumerate(tracks)]
        print tabulate(data, headers=TRACK_HEADERS)

    def show_wait(self, message='loading..'):
        self.show_message(message)

    def show_message(self, msg):
        padding = (len(HEADER_RULER) - len(msg)) / 2 - 1
        formatted_msg = '%s %s %s' % ('-' * padding, msg, '-' * padding)
        print formatted_msg
