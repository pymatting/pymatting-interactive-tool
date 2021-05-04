# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from enum import Enum


class DrawMode(Enum):
    foreground = (1,)
    background = (2,)
    unknownTransparent = (3,)
    unknownColored = 4

    def isForeground(self):
        return self == DrawMode.foreground

    def isBackground(self):
        return self == DrawMode.background

    def isUnknown(self):
        return self in [DrawMode.unknownTransparent, DrawMode.unknownColored]

    def isUnknownTransparent(self):
        return self == DrawMode.unknownTransparent

    def isUnknownColored(self):
        return self == DrawMode.unknownColored
