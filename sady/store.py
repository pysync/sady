#!/usr/bin/python
# -*- coding: utf-8 -*-

import tempfile
import os
import requests

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

    PLAYLIST_SIZE = 100
    CHUNK_SIZE = 512 * 1024
    PLAYLIST_FILE = 'playlist.m3u'
    TRACK_URL_FILE = 'urls.txt'
    DATA_DIR_PREX = 'sady'

    def __init__(self):
        self.__init_store()
        self.load_track_data()


    def load_track_data(self):
        self.track_data = {}
        with open(self.trackurls_path, 'r') as f:
            for line in f:
                (track_id, filepath) = line.strip('\n\r').split('\t')
                self.track_data[track_id] = filepath

    def get(self, track_id):
        return self.track_data.get(str(track_id), None)

    def write(self, track_id, url):
        filepath = self.__download(url)
        with open(self.playlist_path, 'a') as f:
            f.write('%s\n' % filepath)

        with open(self.trackurls_path, 'a') as f:
            f.write('%s\t%s\n' % (track_id, filepath))

        self.track_data[str(track_id)] = filepath
        return filepath

    def __init_store(self):
        user_dir = os.path.expanduser('~')
        if not user_dir:
            user_dir = '/var/tmp'
        self.data_path = os.path.join(user_dir, self.DATA_DIR_PREX)

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        self.playlist_path = os.path.join(self.data_path, self.PLAYLIST_FILE)
        self.trackurls_path = os.path.join(self.data_path, self.TRACK_URL_FILE)

        if not os.path.exists(self.playlist_path):
            with open(self.playlist_path, 'a') as f:
                os.utime(self.playlist_path, None)

        if not os.path.exists(self.trackurls_path):
            with open(self.trackurls_path, 'a') as f:
                os.utime(self.trackurls_path, None)

    def __download(self, url):
        request = requests.get(url)

        (fd, filename) = tempfile.mkstemp(prefix='track', dir=self.data_path)
        try:
            tfile = os.fdopen(fd, 'wb')
            for chunk in request.iter_content(self.CHUNK_SIZE):
                if chunk:
                    tfile.write(chunk)
            tfile.close()
        finally:
            print 'write done: %s' % filename
        return filename

    def __clean():
        with open(self.playlist_path, 'r') as f:
            track_names = f.readlines()
            for track_name in track_names:
                os.remove(track_name)
        os.remove(self.playlist_path)


