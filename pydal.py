import tidalapi as tdl
import threading
import time
import json
import getpass
import vlc

class TrackTimer:
    def __init__(self, duration, call):
        self.timeout = duration
        self.call = call
        self.start_time = 0
        self.pause_time = 0
        self.timer = None

    def start(self):
        if self.pause_time == None:
            self.timer = threading.Timer(self.timeout, self.call)
            self.start_time = time.time()
        else:
            self.timer = threading.Timer(self.timeout - (self.pause_time - self.start_time), self.call)
        self.timer.start()

    def pause(self):
        self.pause_time = time.time()
        self.timer.cancel()


class NowPlaying:
    ''' Details about the currently playing track '''
    
    def __init__(self, tidal_player, track):
        self.tidal_player = tidal_player
        self.track_id = track.id
        self.track = track
        self.artist = self.track.artist
        self.album = self.track.album
        self.track_timer = TrackTimer(self.track.duration, self.tidal_player.next)
        self.tidal_player.set_media("rtmp://" + self.tidal_player.get_url(self.track_id))

    def get_track(self):
        name = self.track.name
        if name == None:
            return "{Name Not Found}"
        else:
            return str(name)

    def get_artist(self):
        artists = []
        artists.append(self.track.artist)
        if len(artists) < 1:
            return "{Artist Not Found}"
        else:
            return str(artists[0])

    def get_album(self):
        name = self.track.name
        if name == None:
            return "{Name Not Found}"
        else:
            return str(name)

    def play(self):
        self.tidal_player.play_media()
        self.track_timer.start()
        print("|| >> Playing <<")

    def pause(self):
        self.tidal_player.pause_media()
        self.track_timer.pause()
        print("|| >> Paused <<")

    def add_track_to_favourites(self):
        self.tidal_player.get_favoutites().add_track(self.track.id)

    def add_artist_to_favourites(self):
        self.tidal_player.get_favoutites().add_artist(self.track.artist.id)

    def add_album_to_favourites(self):
        self.tidal_player.get_favoutites().add_album(self.track.album.id)


class PlayQueue:
    def __init__(self, init):
        self.current_index = 0
        self.tracks = init

    def save(self):
        exit()

class PlayerConfig:
    def __init__(self, file_name):
        self.file_name = str(file_name + '.json')
        self.data = None
        self.update_settings()

    def update_settings(self):
        try:
            with open(self.file_name) as config_file:
                self.data = json.load(config_file)
        except:
            exit("ERROR: No Config File Found")

    def get(self, field):
        data = self.data[field]
        if data == "":
            return None
        else:
            return data
    

class TidalPlayer:
    def __init__(self):
        self.config = PlayerConfig('config')
        self.session = self.create_session()
        self.now_playing = None
        self.queue = PlayQueue(self.read('data', 'queue'))
        self.history = PlayQueue(self.read('data', 'history'))

    def create_session(self):
        session_config = tdl.Config(self.config.get('quality'))
        session = tdl.Session(session_config)
        username = self.config.get('username')
        password = self.config.get('password')
        if username == None:
            username = str(input("|| Enter your username >  "))
        if password == None:
            password = str(getpass.getpass("|| Enter your password >  "))
        session.login(username, password)
        if session.check_login() == False:
            exit("Invalid Login Credentials")
        return session

    def read(self, file_name, field):
        try:
            with open(file_name + '.json') as file:
                return json.load(file)[field]
        except:
            return {}

class Player:
    def __init__(self):
        print("||---------||")
        print("||  TIDAL  ||    cli player")
        print("||---------||")
        self.tidal_player = TidalPlayer()
        self.run_loop()

    def run_loop(self):
        exit()

player = Player()
    


    
