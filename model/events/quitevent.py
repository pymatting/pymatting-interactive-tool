#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from threading import Event

class QuitEvent(Event):
    pass