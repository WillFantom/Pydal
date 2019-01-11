import tidalapi as tdl
import threading
import timer
import json
import vlc

class TrackTimer:
    def __init__(self):

class NowPlaying:
    ''' Details about the currently playing track '''
    
    def __init__(self, player, track):
        self.player = player
        self.track_id = track.id
        self.track = track
        self.artist = self.track.artist
        self.album = self.track.album
        self.track_timer = TrackTimer(self.track.duration, self.player.next())

    def get_track_info(self):
        ''' Get the information relating to the given tracks id '''


    def get_track_url(self):
        try:
            url = self.player.get_session().get_media_url(self.track_id)
        else:
            print("Could not get track from tidal (track id: %s)", self.track_id)
            self.player.next()
        return url

class PlayQueue:
    def __init__(self):

class PlayerUI:
    def __init__(self):

class TidalPlayer:
    def __init__(self):




    
