import tidalapi as tdl
import vlc
import threading
import time

class SongState:
    playing = "PLAYING"
    paused = "PAUSED"
    stopped = "STOPPED"

class Song:
    def __init__(self, quality, url, end_call, error_print, track):
        self.track = track
        self.album = track.album
        self.artist = track.artist
        self.state = SongState.stopped

        self.error_print = error_print

        self.media_protocol_ext = ""
        if quality != "LOSSLESS":
            self.media_protocol_ext = "rtmp://"
        self.media = vlc.MediaPlayer(self.media_protocol_ext + url)

    def play(self):
        self.media.play()
        self.state = SongState.playing

    def pause(self):
        self.media.pause()
        self.state = SongState.paused

    def stop(self):
        self.media.stop()
        self.state = SongState.stopped

    def get_track(self):
        return str(self.track.name)

    def get_album(self):
        return str(self.album.name)

    def get_artist(self):
        return str(self.artist.name)

    def get_duration(self):
        return int(self.track.duration)

    def get_state(self):
        return self.state


class Queue:
    def __init__(self):
        self.now_playing = None
        self.previous = []
        self.next = []

    def has_next(self):
        if len(self.next) > 0:
            return True
        return False

    def get_next(self, count=-1):
        if count > len(self.next) or count == -1:
            count = len(self.next)
        return self.next[0:count]

    def set_next(self):
        if self.now_playing != None:
            self.previous.append(self.now_playing)
        if self.has_next():
            self.now_playing = self.next.pop(0)
        else:
            self.now_playing = None

    def has_previous(self):
        if len(self.previous) > 0:
            return True
        return False

    def get_previous(self, count=-1):
        if count > len(self.previous) or count == -1:
            count = len(self.previous)
        return self.next[-count]

    def set_previous(self):
        if self.now_playing != None:
            self.next = [self.now_playing] + self.next
        if self.has_previous():
            self.now_playing = self.previous.pop()
        else:
            self.now_playing = None

    def add(self, list):
        self.next += list

    def has_now(self):
        if self.now_playing != None:
            return True
        return False

    def get_now(self):
        if self.has_now() == True:
            return self.now_playing
        else:
            return None

    def play_now(self):
        self.now_playing.play()
    
    def pause_now(self):
        self.now_playing.pause()

    def stop_now(self):
        self.now_playing.stop()

    def dump(self, json_file):
        try:
            with open(json_file+".json", "w+") as file:
                data = {}
                data["history"] = self.previous
                data["current"] = self.now_playing
                data["queue"] = self.next
                file.write(data)
        except:
            pass
