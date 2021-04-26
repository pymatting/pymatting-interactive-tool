#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw


class GroupBox(qtw.QGroupBox):

    def __init__(self, title:str, orientation, parent=None):
        super(GroupBox, self).__init__(title, parent=parent)
        if orientation == qtc.Qt.Horizontal:
            self.setLayout(qtw.QHBoxLayout(self))
        else:
            self.setLayout(qtw.QVBoxLayout(self))


    def addWidget(self, widget:qtw.QWidget):
        self.layout().addWidget(widget)

    def addWidgets(self, *widgets):
        for widget in widgets:
            self.addWidget(widget)


