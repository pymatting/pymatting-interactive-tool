# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from threading import Event


class StopEvent(Event):
    def __init__(self):
        super(StopEvent, self).__init__()
        self.clear()
