#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from view.icon import Icon


class ToolButton(qtw.QToolButton):
    pressed = qtc.pyqtSignal(object)

    def __init__(self, value, icon: Icon, toolTip: str, shortcut=None,
                 autoExclusive=True,
                 checkable=True, checked=False, enabled=True, autoRepeat=False, parent=None):
        super(ToolButton, self).__init__(parent)
        self.setAutoExclusive(autoExclusive)
        self.value = value
        if icon:
            self.setIcon(icon)
        self.setCheckable(checkable)
        self.setChecked(checked)
        self.setToolTip(toolTip)
        self.setEnabled(enabled)
        self.setAutoRepeat(autoRepeat)
        if shortcut:
            self.setShortcut(qtg.QKeySequence(shortcut))

        super(ToolButton, self).pressed.connect(self.emitValue)

    def emitValue(self):
        self.pressed.emit(self.value)
