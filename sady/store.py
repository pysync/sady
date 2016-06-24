#!/usr/bin/python
# -*- coding: utf-8 -*-

import tempfile
import os
import requests
from sady import config


class History(object):
    """ data length """
    MAX_SIZE = 100

    def __init__(self):
        self.data = []

    def update(self, q, tracks):
        if len(self.data) >= self.MAX_SIZE:
            del self.data[-1]
        self.data.append((q, tracks))

    def get(self, index=-1):
        if not self.data:
            return None
        return self.data[index]

    def all_tracks(self):
        tracks = []
        for (q, t) in self.data:
            for track in t:
                tracks.append(track)
        return tracks

    def size(self):
        return len(self.data)


class PlayList(object):
    CHUNK_SIZE = 512 * 1024

    def __init__(self):
        self.track_data = {}
        self.load_track_data()

    def load_track_data(self):

        with open(config.TRACK_DATA_FILE, 'r') as f:
            for line in f:
                (track_id, file_path) = line.strip('\n\r').split('\t')
                self.track_data[track_id] = file_path

    def get(self, track_id):
        return self.track_data.get(str(track_id), None)

    def write(self, track_id, url):
        file_path = self.__download(url)
        with open(config.PLAYLIST_FILE, 'a') as f:
            f.write('%s\n' % file_path)

        with open(config.TRACK_DATA_FILE, 'a') as f:
            f.write('%s\t%s\n' % (track_id, file_path))

        self.track_data[str(track_id)] = file_path
        return file_path

    def __download(self, url):
        request = requests.get(url)

        (fd, filename) = tempfile.mkstemp(prefix='track_', dir=config.TRACK_DIR)
        try:
            tfile = os.fdopen(fd, 'wb')
            for chunk in request.iter_content(self.CHUNK_SIZE):
                if chunk:
                    tfile.write(chunk)
            tfile.close()
        finally:
            print 'write done: %s' % filename
        return filename

    def __clean(self):
        with open(config.PLAYLIST_FILE, 'r') as f:
            track_file_paths = f.readlines()
            for track_name in track_file_paths:
                os.remove(track_name)
        os.remove(config.PLAYLIST_FILE)
