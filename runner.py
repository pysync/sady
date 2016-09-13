from sady.gateway import Gateway
from sady.store import Track, TrackList
from sady import config
from sady.ui import UI

import asyncio

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    gw = Gateway(loop)
    ui = UI()
    tracks_list = TrackList(config.TRACK_DATA_FILE,
                            config.PLAYLIST_FILE)

    tracks = tracks_list.top_tracks(20)
    ui.show_tracks(tracks)


    def update_and_refresh(result):
        track, local_uri = result.result()
        if not local_uri:
            ui.show_message("cannot download: {0}".format(track.title))
        else:
            tracks_list.update(track.get_track_id(), local_uri=local_uri, synced=True)
            ui.show_message("{0} -> {1}".format(track.get_track_id(), local_uri))
            # ui.show_tracks(tracks)


    def try_download(index):
        ui.show_message("download one track")
        track, local_uri = loop.run_until_complete(gw.download(tracks[index]))
        ui.show_message("download to: -> {0}".format(local_uri))
        tracks_list.update(track.get_track_id, local_uri=local_uri, synced=True)
        ui.show_tracks(tracks)


    def download_finish(results):
        ui.show_message("download done")
        ui.show_tracks(tracks)


    def try_download_multi():
        ui.show_message("download all track")
        loop.run_until_complete(gw.downloads(tracks,
                                             update_and_refresh,
                                             download_finish))


    #
    def try_soundcloud():
        import soundcloud
        client = soundcloud.Client(client_id=config.CLIENT_ID)
        resources = client.get('/tracks', q='Westlife', limit=10)
        for r in resources:
            print('id: {0}'.format(r.id))
            print('downloadable: {0}'.format(r.downloadable))
            print('streamable: {0}'.format(r.streamable))
            print('title: -> {0}'.format(r.title))


    def try_search():
        __tracks = loop.run_until_complete(gw.search('westlife'))
        if __tracks:
            ui.show_tracks(__tracks)
            ui.show_message("saving...")
            tracks_list.clean()
            tracks_list.add_all(__tracks, flush=True)
            tracks = tracks_list.top_tracks(20)
            ui.show_tracks(tracks)
        else:
            ui.show_message("not found")


    # try_soundcloud()
    # try_download(0)
    #try_download_multi()
    # try_search()
    loop.run_forever()
