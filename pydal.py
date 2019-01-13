import tidalapi as tdl
import threading
import time
import json
import getpass
import vlc

from pydalcli import PydalCli
from pydalweb import PydalWeb

class Pydal:
    def __init__(self):
        self.cli = PydalCli(self)
        self.web = PydalWeb()
        self.settings = Settings()
        self.session = None
        self.session = self.get_session()
        self.media_player = vlc.MediaPlayer()
        self.now_playing = NowPlaying(None, self.next)
        self.queue = Queue()
        self.current_radio = Queue()

        self.cli.run()

    def get_settings(self):
        ''' Returns the current settings object of the app '''
        if self.settings.is_valid() == True:
            return self.settings
        else:
            self.cli.error("Invalid Settings", exit=False)
            self.cli.error("Look at the GitHub repo for config example", exit=True)

    def get_session(self, retry=False):
        ''' Returns the current tidal session if a login check is successful '''
        if self.session == None or self.session.check_login() == False:
            if retry == True:
                self.cli.error("Invalid Session", exit=True)
            else:
                self.session = self.create_session()
                return self.get_session(retry=True)
        else:
            return self.session

    def get_now_playing(self, field):
        ''' Returns the str {field} of the current track '''
        fields = ["track", "artist", "album"]
        if field.lower() not in fields:
            self.cli.error("Invalid Field Requested from Now Playing", exit=True)
        if self.now_playing == None:
            return str("{null}")
        else:
            return str(self.now_playing.get(field.lower()))

    def get_queue(self, count):
        ''' Returns the next {count} items in the queue as str(track name) - str(track artist name) '''
        if count > self.queue.remaining():
            count = self.queue.remaining()
        tracks = self.queue.get_next(count)
        formatted = []
        for track in tracks:
            formatted.append(str(track.name) + " - " + str(track.artist.name))
        return formatted

    def create_session(self):
        ''' Creates a Session '''
        session_config = tdl.Config(self.settings.get("quality"))
        username = self.settings.get_username(self.cli)
        password = self.settings.get_password(self.cli)
        session = tdl.Session(session_config)
        session.login(username, password)
        return session

    def play_pause(self, retry=False):
        ''' Starts or resumes if not playing. Pauses a playing song '''
        if self.now_playing.status() == NowPlayingStatus.none or self.now_playing.status() == NowPlayingStatus.stopped:
            if retry == True:
                self.cli.print_message("No Track Avaliable to Play")
            else:
                self.next(retry=True)
        elif self.now_playing.status() == NowPlayingStatus.playing:
            self.media_player.pause()
            self.now_playing.set_paused()
            self.cli.print_message("Paused")
        elif self.now_playing.status() == NowPlayingStatus.paused:
            self.media_player.play()
            self.now_playing.set_playing()
            self.cli.print_message("Playing")
        else:
            self.cli.error("Invalid Now Playing Status Detected", exit=True)


    def next(self, retry=False):
        ''' Plays the next track in the queue or current radio '''
        self.media_player.stop()
        if self.queue.is_empty() == False:
            self.now_playing = NowPlaying(self.queue.get_next(), self.next)
        elif self.current_radio.is_empty() == False:
            self.now_playing = NowPlaying(self.current_radio.get_next(), self.next)
        else:
            self.now_playing = NowPlaying(None, self.next)

        if self.now_playing.status() != NowPlayingStatus.none:
            print(self.now_playing.get_id())
            self.media_player = vlc.MediaPlayer(str(str(self.settings.get("protocol")) + "://" + str(self.get_session().get_media_url(self.now_playing.get_id()))))
            self.now_playing.track_timer.start()

        self.play_pause(retry=retry)

    def previous(self):
        ''' Plays the previous track if avaiable '''
        if self.queue.has_previous():
            self.media_player.stop()
            self.now_playing = NowPlaying(self.queue.get_previous(), self.next)
            self.play_pause()
        else:
            self.cli.print_message("No Previous Track")

    def search(self, term):
        ''' Searches TIDAL for tracks, artists, albums and playlist of a given term '''
        tracks = self.get_session().search("track", term).tracks[0:int(self.settings.get("search_tracks"))]
        artists = self.get_session().search("artist", term).artists[0:int(self.settings.get("search_artists"))]
        albums = self.get_session().search("album", term).albums[0:int(self.settings.get("search_albums"))]
        playlists = self.get_session().search("playlist", term).playlists[0:int(self.settings.get("search_playlists"))]
        idx = 1
        formatted = []
        for track in tracks:
            formatted.append({"name" : str(idx) + " : track : " + str(track.name) + " : " + str(track.artist.name)})
            idx = idx + 1
        for artist in artists:
            formatted.append({"name" : str(idx) + " : artist : " + str(artist.name) + " : (will add top 5 tracks to queue)"})
            idx = idx + 1
        for album in albums:
            formatted.append({"name" : str(idx) + " : album : " + str(album.name) + " : " + str(album.artist.name)})
            idx = idx + 1
        for playlist in playlists:
            formatted.append({"name" : str(idx) + " : playlist : " + str(playlist.name)})
            idx = idx + 1
        choice = self.cli.search_menu(formatted)
        for result in choice['results']:
            i = int(result.split()[0]) - 1
            if i in range(0, int(self.settings.get("search_tracks"))):
                self.queue.add(tracks[i])
            elif i in range(int(self.settings.get("search_tracks")), int(self.settings.get("search_artists"))):
                top_tracks = self.session.get_artist_top_tracks(artists[i - int(self.settings.get("search_tracks"))].id)
                if len(top_tracks < 5):
                    self.queue.add(top_tracks)
                else:
                    self.queue.add(top_tracks[0:5])
            elif i in range(int(self.settings.get("search_artists")), int(self.settings.get("search_albums"))):
                album_tracks = self.session.get_album_tracks(albums[i - int(self.settings.get("search_tracks")) - int(self.settings.get("search_artists"))].id)
                self.queue.add(album_tracks)
            elif i in range(int(self.settings.get("search_albums")), int(self.settings.get("search_playlists"))):
                playlist_tracks = self.session.get_playlist_tracks(playlists[i - int(self.settings.get("search_tracks")) - int(self.settings.get("search_artists")) - int(self.settings.get("search_albums"))].id)
                self.queue.add(playlist_tracks)
        if self.now_playing.status() == NowPlayingStatus.none or self.now_playing.status() == NowPlayingStatus.stopped:
            self.play_pause()

    def logout(self):
        ''' Kills the current session '''
        self.session = None

    def exit(self):
        ''' Exits the app '''
        self.queue.write()
        self.logout()
        self.cli.exit()


class Settings:
    def __init__(self):
        self.file_name = "config.json"
        self.file_data = self.read_settings()
        self.username = None
        self.password = None

    def read_settings(self):
        try:
            with open(self.file_name) as config_file:
                return json.load(config_file)
        except:
            return None
            f = open(self.file_name, "r+")
            f.close()


    def is_valid(self):
        valid = True

        #Verify Quality
        qualaties = ["LOW", "HIGH", "LOSSLESS"]
        if "quality" not in self.file_data:
            valid = False
        if self.file_data["quality"].upper() not in qualaties:
            valid = False

        #Verify Protocol
        protocols = ["rtmp"]
        if "protocol" not in self.file_data:
            valid = False
        if self.file_data["protocol"].upper() not in protocols:
            valid = False

        #Verify Search Max
        if "search_tracks" not in self.file_data:
            valid = False
        if "search_artists" not in self.file_data:
            valid = False
        if "search_albums" not in self.file_data:
            valid = False
        if "search_playlists" not in self.file_data:
            valid = False

        return valid
        
    def get_username(self, cli):
        if "username" not in self.file_data:
            username = cli.get_username()
            store = cli.yes_no("Store Username")
            if store == True:
                self.write("username", username)
            return username
        else:
            return self.get("username")

    def get_password(self, cli):
        if "password" not in self.file_data:
            password = cli.get_password()
            store = cli.yes_no("Store Password (in plaintext!)")
            if store == True:
                self.write("password", password)
            return password
        else:
            return self.get("password")

    def get(self, field):
        if field not in self.file_data:
            return None
        else:
            return self.file_data[field]

    def write(self, field, data):
        if field not in self.file_data:
            with open(self.file_name, "a") as f:
                data = {str(field) : str(data)}
                f.write(json.dumps(data))
                f.close()
        else: 
            a = 1
            # Implement Me


class NowPlayingStatus:
    none = "NONE"
    playing = "PLAYING"
    paused = "PAUSED"
    stopped = "STOPPED"


class TrackTimer:
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.timer = threading.Timer(timeout, callback)
        self.startTime = time.time()
        self.pauseTime = 0

    def start(self):
        self.timer.start()

    def pause(self):
        self.timer.cancel()
        self.pauseTime = time.time()

    def resume(self):
        self.timer = threading.Timer(
            self.timeout - (self.pauseTime - self.startTime),
            self.callback)


class NowPlaying:  
    def __init__(self, track, player_next):
        self.play_status = NowPlayingStatus.none
        self.track = track
        self.track_timer = None
        self.stop_call = player_next

        if self.track != None:
            self.set_data()

    def set_data(self):
        self.play_status = NowPlayingStatus.paused
        self.track_timer = TrackTimer(self.track.duration, self.stop)

    def stop(self):
        self.play_status = NowPlayingStatus.stopped
        self.stop_call()

    def set_playing(self):
        self.play_status = NowPlayingStatus.playing
        self.track_timer.resume()

    def set_paused(self):
        self.play_status = NowPlayingStatus.paused
        self.track_timer.pause()

    def status(self):
        return self.play_status

    def get(self, field):
        if field.lower() == "track":
            return str(self.track.name)
        elif field.lower() == "artist":
            return str(self.track.artist.name)
        elif field.lower() == "album":
            return str(self.track.album.name)
        else:
            exit("Sorry, I don't have a nice error message for this one :'(")

    def get_id(self):
        return self.track.id


class Queue:
    def __init__(self):
        self.current_length = -1
        self.current_position = -1
        self.tracks = []

    def get_next(self, count=0):
        self.current_position = self.current_position + 1
        return self.tracks[self.current_position]

    def get_previous(self):
        self.current_position = self.current_position - 1
        return self.tracks[self.current_position]

    def is_empty(self):
        if self.current_position >= self.current_length - 1:
            return True
        return False

    def remaining(self):
        return self.current_length - self.current_position - 1

    def add(self, tracks):
        self.tracks.append(tracks)
        self.current_length = len(self.tracks)

    def write(self):
        a=1
        #Implement Me


pydal = Pydal()