#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw


class PushButton(qtw.QPushButton):
    pressed = qtc.pyqtSignal(object)

    def __init__(self, text: str, toolTip=None, value=None, parent=None):
        super(PushButton, self).__init__(text, parent=parent)
        self.setToolTip(toolTip)
        self.value = value
        super(PushButton, self).pressed.connect(self.emitValue)

    def emitValue(self):
        self.pressed.emit(self.value)
