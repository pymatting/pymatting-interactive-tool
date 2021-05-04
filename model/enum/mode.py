# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from enum import Enum


class Mode(Enum):
    brush = (0,)
    paintBucket = (1,)
    crop = (2,)
    drag = (3,)
    clearTrimap = (4,)
    clearNewBackground = 5

    def isBrush(self):
        return self == Mode.brush

    def isPaintbucket(self):
        return self == Mode.paintBucket

    def isDrag(self):
        return self == Mode.drag

    def isCrop(self):
        return self == Mode.crop
