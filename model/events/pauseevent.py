#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from threading import Event

class PauseEvent(Event):
    def __init__(self):
        super(PauseEvent, self).__init__()
        self.set()