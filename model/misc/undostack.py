# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc


class UndoStack(qtc.QObject):
    """Class that provides an undo stack"""

    def __init__(self, maxSize=100):
        super(UndoStack, self).__init__()
        self.stack = []
        self.currentIndex = -1
        self.maxSize = maxSize

    def push(self, item):
        self.currentIndex += 1
        if self.currentIndex < self.maxSize:
            self.stack.insert(self.currentIndex, item)
            if len(self.stack) - 1 > self.currentIndex:
                del self.stack[self.currentIndex + 1 :]
        else:
            del self.stack[0]
            self.currentIndex -= 1
            self.stack.insert(self.currentIndex, item)

    def undo(self):
        if self.currentIndex - 1 >= -1:
            item = self.stack[self.currentIndex]
            self.currentIndex -= 1
            return item
        return None

    def redo(self):
        if self.currentIndex + 1 < self.stack.__len__():
            self.currentIndex += 1
            item = self.stack[self.currentIndex]
            return item
        return None
