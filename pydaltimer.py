import threading
import time

class PydalTimer:
    def __init__(self, call_back):
        self.call_back = call_back
        self.factor = 10
        self.duration = 0
        self.remaining = 0
        self.active = False
        self.thread = threading.Thread(target=self._timer)
        self.thread.start()

    def _timer(self):
        while True:
            if self.active == True:
                if self.remaining < 0:
                    self.active = False
                    self.call_back()
                self.remaining -= 1
                time.sleep(1 / self.factor)

    def set(self, duration, start=False):
        self.duration = duration
        self.remaining = self.duration * self.factor
        if start:
            self.start()

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def get_progress(self):
        return int(( (self.duration - (self.remaining / self.factor)) / self.duration) * 100)

    def is_active(self):
        return self.active