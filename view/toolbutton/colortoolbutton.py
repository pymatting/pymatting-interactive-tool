# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw


class ColorToolButton(qtw.QToolButton):
    def __init__(self, toolTip, color):
        super(ColorToolButton, self).__init__()
        self.setAutoExclusive(False)
        self.setCheckable(False)
        self.setToolTip(toolTip)
        self.setBackgroundColor(color)

    def setBackgroundColor(self, color: qtg.QColor):
        if color:
            styleSheet = f"""
                    QToolButton{{
                        background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()});
                        width: 20px;
                        height: 20px;
                        border-radius: 10px;
                        border-width: 1px;
                        border-color: gray;
                        border-style: solid;
                    }}
            """
            self.setStyleSheet(styleSheet)
