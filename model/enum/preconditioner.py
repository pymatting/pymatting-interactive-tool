#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from enum import Enum

class Preconditioner(Enum):
    none = 0,
    jacobi = 1,
    vcycle = 2

    def isNone(self):
        return self == Preconditioner.none

    def isJacobi(self):
        return self == Preconditioner.jacobi

    def isVcycle(self):
        return self == Preconditioner.vcycle