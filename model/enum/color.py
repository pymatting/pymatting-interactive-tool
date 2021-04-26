#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from enum import Enum
from PyQt5 import QtGui as qtg


class Color(Enum):
    transparent = qtg.QColor(0, 0, 0, 0)
    black = qtg.QColor(0, 0, 0, 255)
    green = qtg.QColor(0, 255, 0, 255)
    red = qtg.QColor(255, 0, 0, 255)
    gray = qtg.QColor(160,160,160,255)
    lightGreen = qtg.QColor(0, 255, 0, 100)
    lightRed = qtg.QColor(255, 0, 0, 101)
    lightBlue = qtg.QColor(0, 0, 255, 102)
    lightGray = qtg.QColor(160, 160, 160, 100)

    def rgba(self):
        color = self.value
        return color.red(), color.green(), color.blue(), color.alpha()

    def bgra(self):
        color = self.value
        return [color.blue(), color.green(), color.red(), color.alpha()]