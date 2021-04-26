#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from threading import Event

class ContinueEvent(Event):
    def __init__(self):
        super(ContinueEvent, self).__init__()
        self.set()