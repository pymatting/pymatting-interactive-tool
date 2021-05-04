# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw


class Action(qtw.QAction):
    def __init__(
        self,
        text: str,
        icon=None,
        shortcut=None,
        slot=None,
        autoRepeat=False,
        parent=None,
    ):
        super(Action, self).__init__(text, parent=parent)
        self.setAutoRepeat(autoRepeat)
        if shortcut:
            self.setShortcut(shortcut)
        if icon:
            self.setIcon(icon)
        if slot:
            self.triggered.connect(slot)
