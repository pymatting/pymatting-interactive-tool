# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw


class HSplitter(qtw.QSplitter):
    collapsedRight = qtc.pyqtSignal(bool)

    def __init__(self, parent=None):
        super(HSplitter, self).__init__(qtc.Qt.Horizontal, parent=parent)
        self.splitterMoved.connect(self.check)

    def check(self, pos, index):
        min, max = self.getRange(index)
        if pos == max:
            self.collapsedRight.emit(True)
        else:
            self.collapsedRight.emit(False)
