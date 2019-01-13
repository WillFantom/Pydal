from __future__ import print_function, unicode_literals
from PyInquirer import style_from_dict, Token, prompt, Separator
import getpass

from pydalui import PydalUI
from pydaltypes import Song

class PydalCli(PydalUI):
    def __init__(self, player):
        self.player = player
        self.title = "||  PYDAL  ||  a TIDAL player for linux"
        print(self.title)

    def alert(self, message):
        print("|> " + message + " <|")

    def error(self, message, exit=False):
        print("!> " + message + " <!")
        if exit:
            exit()

    def current(self):
        print("| -- Now Playing -- ")
        if self.player.get_now() != None:
            track = self.player.get_now().get_track()
            album = self.player.get_now().get_album()
            artist = self.player.get_now().get_artist()
            state = self.player.get_now().get_state()
            progress = self.player.get_now().get_progressbar()
            print("|> Track: " + track)
            print("|> Artist: " + artist)
            print("|> Album: " + album)
            print("|> State: " + state)
            print("|> Progress <" + progress + ">")
        else:
            print("|> NOTHING")
        print()

    def playing(self):
        self.current()

    def paused(self):
        self.current()

    def stopped(self):
        self.current()

    def view_queue(self, distace, history=False):
        raise NotImplementedError("Implement Me") #TODO

    def pass_input(self):
        return str(getpass.getpass("|>> Enter your TIDAL password >> "))

    def uname_input(self):
        return str(input("|>> Enter your TIDAL username >> "))

    def search_prompt(self, field, formatted_list):
        question = [
            {
                "type": "checkbox",
                "message": " >> Select " + str(field) + "s >>",
                "name": "results",
                "choices": formatted_list
            }
        ]
        return prompt(question)

    def yesno_prompt(self, message):
        question = [
            {
                "type": "confirm",
                "message": message,
                "name": "yn",
                "default": False,
            } 
        ]
        response = prompt(question)
        return response["yn"]

    def exit(self):
        print("||>  EXITING PYDAL")

    def help(self):
        print("|> -- HELP")
        print("|> play - plays the current track")
        print("|> pause - pauses the current track")
        print("|> next - skips to the next track in the queue")
        print("|> previous - skips to the previous track in the queue")
        print("|> current - shows what is currently playing")
        print("|> search [field] [term] - searches for term with a field")
        print("|> exit - quits Pydal")

    def run(self):
        while True:
            i = ""
            while i == "":
                i = input("|>> ")
            command = i.split()[0].lower()
            if command == "play":
                self.player.play_pause()
            elif command == "pause":
                self.player.play_pause()
            elif command == "next":
                self.player.next()
            elif command == "previous":
                self.player.previous()
            elif command == "current":
                self.current()
            elif command == "search":
                if len(i.split()) < 3:
                    self.help()
                else:
                    self.player.search(i.split()[1].lower(), i.split(' ', 2)[2])
            elif command == "help":
                self.help()
            elif command == "exit":
                self.player.exit()
            else:
                self.help()