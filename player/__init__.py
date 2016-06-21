# player
import click
import soundcloud
import tempfile
import os
import requests
import subprocess
import random
import cmd


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

""" templ playlist file """
PLAYLIST_FILE = 'playlist.m3u'

""" client id """
CLIENT_ID = 'eca1790e16470735633dd7ee79dd6074'

class Player(cmd.Cmd):
    """
    Simple Player
    """
    def __init__(self):
        cmd.Cmd.__init__(self)

        # setup client
        self.client = soundcloud.Client(client_id=CLIENT_ID)

    """ search in sound clound and play """
    def do_p(self, name):
        if not name:
            name = self.random_track()

        tracks = self.client.get('/tracks', q=name, limit=1)
        if not len(tracks):
            print 'not found song name: %s' % name
            return

        track = tracks[0]
        track.stream_url
        resource = self.client.get(track.stream_url, allow_redirects=False)
        stream_url = resource.location

        file_name = self.download(stream_url)

        with open(PLAYLIST_FILE, 'w') as f:
            f.write(file_name)

        print 'starting mplayer'
        subprocess.call(['mplayer',
                        '-vo',
                        'null',
                        '-playlist',
                        PLAYLIST_FILE,
                        '-shuffle']
        )

        print 'ending.. mplayer'

    """ cleanup """
    def clean():
        with open(PLAYLIST_FILE, 'r') as f:
            track_names = f.readlines()
            for track_name in track_names:
                os.remove(track_name)
        os.remove(myplaylist)

    """
    download sound to random file
    """
    def download(self, stream_url):
        request = requests.get(stream_url)
        chunk_size = 512 * 1024
        (fd, filename) = tempfile.mkstemp()
        try:
            tfile = os.fdopen(fd, 'wb')
            for chunk in request.iter_content(chunk_size):
                if chunk:
                    tfile.write(chunk)
            tfile.close()
        finally:
            print 'write done: %s' % filename
        return filename

    def random_track(self):
        return random.choice(TRACK_NAMES)

@click.command()
def cli():
    Player().cmdloop()


# lib ref
# https://pymotw.com/2/cmd/
# https://developers.soundcloud.com/docs/api/reference
