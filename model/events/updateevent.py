#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from threading import Event
from model.enum import Reason

class UpdateEvent(Event):
    def __init__(self, reason:Reason, value=None):
        super(UpdateEvent, self).__init__()
        self.reason = reason
        self.value = value

