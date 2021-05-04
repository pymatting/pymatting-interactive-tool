# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from enum import Enum


class Method(Enum):
    cgd = (0,)
    vcycle = 1

    def isCgd(self):
        return self == Method.cgd

    def isVcycle(self):
        return self == Method.vcycle
