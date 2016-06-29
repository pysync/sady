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
        print(tabulate(tabular_data=data, headers=STORE_HEADERS))

    def show_tracks(self, tracks, offset=0):
        data = [(index + offset,
                 track.id,
                 track.title,
                 track.playback_count,
                 track.genre,
                 track.synced or 'False'
                 ) for (index, track) in enumerate(tracks)]
        print(tabulate(data, headers=TRACK_HEADERS))

    def show_wait(self, message='loading..'):
        self.show_message(message)

    def show_message(self, msg):
        padding = int((len(HEADER_RULER) - len(msg)) / 2 - 1)
        formatted_msg = '{0} {1} {2}'.format('-' * padding, msg, '-' * padding)
        print(formatted_msg)
