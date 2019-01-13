from __future__ import print_function, unicode_literals
from PyInquirer import style_from_dict, Token, prompt, Separator
import getpass

class PydalCli:
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
        return response["yn"]