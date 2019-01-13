class PydalUI():
    def alert(self, message):
        raise NotImplementedError("Implement Me")

    def error(self, message, exit=False):
        raise NotImplementedError("Implement Me")

    def current(self):
        raise NotImplementedError("Implement Me")

    def playing(self):
        raise NotImplementedError("Implement Me")

    def paused(self):
        raise NotImplementedError("Implement Me")

    def stopped(self):
        raise NotImplementedError("Implement Me")

    def view_queue(self, distace, history=False):
        raise NotImplementedError("Implement Me")

    def pass_input(self):
        raise NotImplementedError("Implement Me")

    def uname_input(self):
        raise NotImplementedError("Implement Me")

    def search_prompt(self, field, formatted_list):
        raise NotImplementedError("Implement Me")

    def yesno_prompt(self, message):
        raise NotImplementedError("Implement Me")

    def exit(self):
        raise NotImplementedError("Implement Me")

    def help(self):
        raise NotImplementedError("Implement Me")

    def run(self):
        raise NotImplementedError("Implement Me")