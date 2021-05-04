# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from enum import Enum


class Reason(Enum):
    trimapChanged = (0,)
    methodChanged = (3,)
    lambdaChanged = (4,)
    preconditionerChanged = (5,)
    epsilonChanged = (6,)
    radiusChanged = (7,)
    kernelChanged = (8,)
    preIterChanged = (9,)
    postIterChanged = (10,)
    rtolChanged = (11,)
    alphaMatteChanged = (12,)
    canvasChanged = (13,)
    trimapPreviewChanged = (14,)
    trimapPreviewUpdated = (15,)
    imagesChanged = (16,)
    printErrorChanged = 17
