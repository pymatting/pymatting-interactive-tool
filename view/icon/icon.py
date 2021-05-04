# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg


class Icon(qtg.QIcon):
    def __init__(self, name, end="png"):
        super(Icon, self).__init__()
        iconPath = qtc.QFileInfo(__file__).dir()
        iconPath.cd("icons")
        iconPath = iconPath.filePath(f"{name}.{end}")
        self.addFile(iconPath)
