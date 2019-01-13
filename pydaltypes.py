import tidalapi as tdl
import vlc
import threading
import time

class SongState:
    playing = "PLAYING"
    paused = "PAUSED"
    stopped = "STOPPED"

class Song:
    def __init__(self, quality, url, end_call, error_print, crossfade, track):
        self.track = track
        self.album = track.album
        self.artist = track.artist
        self.state = SongState.stopped

        self.error_print = error_print

        self.media_protocol_ext = ""
        if quality != "LOSSLESS":
            self.media_protocol_ext = "rtmp://"
        self.media = vlc.MediaPlayer(self.media_protocol_ext + url)

        self.time_remaining = (track.duration * 10) - crossfade
        self.end_call = end_call
        self.timer = threading.Thread(target=self._timer)
        self.timing = False
        self.timer_active = False

    def play(self):
        try:
            self.media.play()
            if self.timer.isAlive() == False:
                self.timer_active = True
                self.timing = True
                self.timer.start()
            self.state = SongState.playing
        except:
            self.error_print("Song " + self.track.name + " could not be played", exit=False)
            self.end_call()

    def pause(self):
        try:
            self.media.pause()
            self.timing = False
            self.state = SongState.paused
        except:
            self.error_print("Song " + self.track.name + " could not be paused", exit=True)

    def stop(self):
        if self.state == SongState.playing or self.state == SongState.paused:
            self.media.stop()
        self.timer_active = False
        self.timing = False
        self.state = SongState.stopped

    def _timer(self):
        while self.timer_active == True:
            while self.time_remaining > 0:
                if self.timing == True:
                    time.sleep(0.1)
                    self.time_remaining -= 1
            self.end_call()
        print(self.track.name + ": TIMER ENDED")

    def get_track(self):
        return str(self.track.name)

    def get_album(self):
        return str(self.album.name)

    def get_artist(self):
        return str(self.artist.name)

    def get_state(self):
        return self.state

    def get_progressbar(self):
        percent = int(((self.track.duration - (self.time_remaining/10)) / self.track.duration) * 100)
        return "|" + ("-" * int((percent/5))) + (" " * int((20-(percent/5)))) + "|"


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
            self.now_playing.stop()
            self.previous.append(self.now_playing)
        if self.has_next():
            self.now_playing = self.next.pop(0)

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
            if self.now_playing.get_state() == SongState.stopped:
                self.now_playing.play()
            else:
                self.now_playing.stop()
                self.next = [self.now_playing] + self.next
            if self.has_previous():
                self.now_playing = self.previous.pop()

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
