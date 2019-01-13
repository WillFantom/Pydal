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
        print(" -- Now Playing -- ")
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
            print("|> Progress:")
            print("   " + progress)
        else:
            print("|> NOTHING")

    def playing(self):
        self.current()

    def paused(self):
        self.current()

    def stopped(self):
        self.current()

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



















'''class PydalCli(PydalUI):
    def __init__(self, player):
        self.player = player
        a = 1

    def run(self):
        while True:
            command = str(input("|| >> "))
            if command.split()[0].lower() == "search":
                self.search(command)
            else:   
                action = {
                    "play": self.player.play_pause,
                    "pause": self.player.play_pause,
                    "next": self.player.next,
                    "exit": self.player.exit
                }.get(str(command.split()[0]).lower(), self.print_help)
                action()

    def print_message(self, message):
        print("|| >>  " + message + "  <<")

    def error(self, message, exit=False):
        print("|| !>  " + message)
        if exit == True:
            exit()

    def get_password(self):
        return str(getpass.getpass("|| Enter your TIDAL password >>  "))

    def search(self, command):
        if len(command.split()) <= 1:
            self.error("Must have a search term")
        else:
            self.player.search(command.split(' ', 1)[1])

    def search_menu(self, list):
        question = [
            {
                "type": "checkbox",
                "message": "Slect what to add to the queue",
                "name": "results",
                "choices": list
            }
        ]
        return prompt(question)

    def print_help(self):
        a=1

    def exit(self):
        print("||---------------||")
        print("|| !> Exiting <! ||")
        print("||---------------||")
        exit()

    def yes_no(self, message):
        question = [
        {
            "type": "confirm",
            "message": message,
            "name": "yn",
            "default": True,
        } ]
        response = prompt(question)
        return response["yn"]'''