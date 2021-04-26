#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw


class ToolBar(qtw.QToolBar):

    def __init__(self, title, parent=None):
        super(ToolBar, self).__init__(parent=parent)
        self.setMovable(True)
        self.setFloatable(True)
        self.setWindowTitle(title)


    def addWidgets(self, *widgets):
        for widget in widgets:
            self.addWidget(widget)
