#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw


class ScrollBar(qtw.QScrollBar):
    entered = qtc.pyqtSignal()
    left = qtc.pyqtSignal()

    def enterEvent(self, event: qtc.QEvent) -> None:
        super(ScrollBar, self).enterEvent(event)
        self.entered.emit()

    def leaveEvent(self, event: qtc.QEvent) -> None:
        super(ScrollBar, self).leaveEvent(event)
        self.left.emit()