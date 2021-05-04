# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from enum import Enum


class Control(Enum):
    start = (0,)
    stop = (1,)
    pause = 2

    def isStart(self):
        return self == Control.start

    def isStop(self):
        return self == Control.stop

    def isPause(self):
        return self == Control.pause
