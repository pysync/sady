import os

IS_DEBUG = True

USER_DIR = os.path.expanduser('~')
if not USER_DIR:
    USER_DIR = '/var/tmp'

DATA_DIR = os.path.join(USER_DIR, 'sady')
TRACK_DIR = os.path.join(DATA_DIR, 'tracks')

LOG_FILE = os.path.join(DATA_DIR, 'app.log')
TRACK_DATA_FILE = os.path.join(DATA_DIR, 'tracks.json')
PLAYLIST_FILE = os.path.join(DATA_DIR, 'playlist.m3u')

for dir_path in (DATA_DIR, TRACK_DIR):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

for file_path in (LOG_FILE, TRACK_DATA_FILE, PLAYLIST_FILE):
    if not os.path.exists(file_path):
        with open(file_path, 'a') as f:
            os.utime(file_path, None)
