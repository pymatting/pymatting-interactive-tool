#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from enum import Enum


class Status(Enum):
    successful = 0,
    failed = 1,
    aborted = 2

    def isSuccessful(self):
        return self == Status.successful

    def isFailed(self):
        return self == Status.failed

    def isAborted(self):
        return self == Status.aborted
