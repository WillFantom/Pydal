import tidalapi as tdl
import json

from pydalcli import PydalCli
from pydalweb import PydalWeb
from pydaltypes import Song, Queue, SongState
from pydalsearch import Search

class Pydal:
    def __init__(self):
        #Create UIs
        self.cli = PydalCli(self)
        self.web = PydalWeb(self)

        #Set Default UI
        self.ui = self.cli

        #Get Settings from "config.json"
        self.settings = Settings("config", self.ui.error)

        #Create a Tidal Session
        self.session = self.create_session()

        #Create song list
        self.queue = Queue()

        #Run Pydal UI loop
        self.ui.run()

    def play_pause(self):
        if self.queue.get_now() == None:
            self.next()
        else:
            if self.queue.get_now().get_state() == SongState.playing:
                self.queue.get_now().pause()
                self.ui.paused()
            elif self.queue.get_now().get_state() == SongState.paused or self.queue.get_now().get_state() == SongState.stopped:
                self.queue.get_now().play()
                self.ui.playing()

    def stop(self):
        if self.queue.get_now() != None:
            self.queue.get_now().stop()
            self.ui.stopped()

    def next(self):
        if self.queue.has_next():
            self.queue.set_next()
            self.queue.get_now().play()
            self.ui.playing()
        else:
            self.ui.alert("Queue Empty")
            if self.queue.get_now() != None:
                self.queue.get_now().stop()

    def previous(self):
        if self.queue.has_previous():
            self.queue.set_previous()
            self.queue.get_now().play()
            self.ui.playing()
        else:
            self.ui.alert("History Empty")

    def search(self, field, term):
        search = Search(self.ui, self.session, self.settings.get("max_results"), term, field)
        selection = search.get_selection()
        to_add = []
        for item in selection:
            to_add.append(Song(self.settings.get("quality"), self.session.get_media_url(item.id), self.next, self.ui.error, self.settings.get("crossfade"), item))
        self.queue.add(to_add)
        self.ui.alert("Added " + str(len(to_add)) + " Items to the Queue")
        if self.queue.get_now() == None:
            self.next()

    def create_session(self):
        self.settings.validate()
        session_config = tdl.Config(self.settings.get("quality"))
        session = tdl.Session(session_config)
        try:
            session.login(self.settings.get_username(self.ui.uname_input, self.ui.yesno_prompt), self.settings.get_password(self.ui.pass_input, self.ui.yesno_prompt))
        except:
            self.ui.error("Error Creating Login Session", exit=True)
        if session.check_login() == False:
            self.ui.error("Invalid Login Credentials", exit=True)
        return session

    def get_now(self):
        return self.queue.get_now()

    def get_queue(self):
        return self.queue.get_next(self.settings.get("queue_lookahead"))

    def get_history(self):
        return self.queue.get_previous(self.settings.get("queue_lookahead"))

    def exit(self):
        self.queue.dump("data")
        self.session = None
        self.ui.exit()
        exit()


class Settings:
    def __init__(self, file_name, error_print):
        self.file_name = file_name+".json"
        self.error_print = error_print
        self.file_data = self.read()

    def read(self, retry=False):
        try:
            with open(self.file_name, "r") as config_file:
                return json.load(config_file)
        except:
            if retry == True:
                self.error_print("Settings Not Readable", exit=True)
            with open(self.file_name, "w+") as config_file:
                data = {}
                data["max_results"] = 7
                data["queue_lookahead"] = 7
                data["quality"] = "HIGH"
            return self.read(retry=True)

    def validate(self):
        #Quality
        qualaties = ["LOW", "HIGH", "LOSSLESS"]
        if "quality" not in self.file_data:
            self.error_print("Config does not specify quality", exit=True)
        if self.file_data["quality"] not in qualaties:
            self.error_print("Quality " + self.file_data["quality"] + " is not valid", exit=True)

        #Queue Lookahead
        if "queue_lookahead" not in self.file_data:
            self.error_print("Config does not specify queue_lookahead", exit=True)
        try:
            qlah = int(self.file_data["queue_lookahead"])
            if qlah < 1 or qlah > 50:
                raise Exception("Queue Lookahead not in Range")
        except:
            self.error_print("Queue Lookahead " + str(self.file_data["queue_lookahead"]) + " is not valid", exit=True)

        #Max Search
        if "max_results" not in self.file_data:
            self.error_print("Config does not specify max_results", exit=True)
        try:
            qlah = int(self.file_data["max_results"])
            if qlah < 1 or qlah > 50:
                raise Exception("Max Search Results not in Range")
        except:
            self.error_print("Max Search Results " + str(self.file_data["max_results"]) + " is not valid", exit=True)

        #Crossfade
        if "crossfade" not in self.file_data:
            self.error_print("Config does not specify crossfade", exit=True)
        try:
            qlah = int(self.file_data["crossfade"])
            if qlah < 0 or qlah > 5:
                raise Exception("crossfade Results not in Range")
        except:
            self.error_print("crossfade Results " + str(self.file_data["crossfade"]) + " is not valid", exit=True)
        
    def get_username(self, uname_input, yes_no):
        if "username" not in self.file_data:
            username = uname_input()
            return username
        else:
            return self.get("username")

    def get_password(self, pass_input, yes_no):
        if "password" not in self.file_data:
            password = pass_input()
            return password
        else:
            return self.get("password")

    def get(self, field):
        if field not in self.file_data:
            return None
        else:
            return self.file_data[field]

pydal = Pydal()