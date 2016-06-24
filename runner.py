import logging
import json
import random
import jsonpickle

logger = logging.getLogger(__name__)

logger.info('-- app starting...')


class Track:
    fields = ('id', 'title', 'playback_count', 'genre')

    def __init__(self, *argv, **kwargs):
        if argv and len(argv):
            obj = argv[0]
            if not isinstance(obj, Track):
                raise ValueError('cannot instance Track with: %s' % obj.__class__)

            for field in self.fields:
                if hasattr(obj, field):
                    val = getattr(obj, field)
                    setattr(self, field, val)
        else:
            if kwargs:
                for k, v in kwargs.items():
                    if k in self.fields:
                        setattr(self, k, v)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class TrackList(object):

    def __init__(self):
        self.tracks = []

tracks = []
for i in range(0, 10, 1):
    track = Track(
        id=str(i),
        title='track: %s' % i,
        playback_count=random.choice(range(100, 10000)),
        genre=random.choice(('POP', 'KPOP', 'VPOP'))
    )
    tracks.append(track)

print 'writing...'
with open('track.json', 'w') as f:
    f.write(jsonpickle.encode(tracks))

print 'reading...'
with open('track.json', 'r') as f:
    load_tracks = jsonpickle.decode(f.read())
    print load_tracks

    for t in load_tracks:
        print t.title