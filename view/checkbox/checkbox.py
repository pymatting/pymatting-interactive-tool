#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw


class CheckBox(qtw.QCheckBox):


    def __init__(self, text, toolTip:str, checked=False, parent=None):
        super(CheckBox, self).__init__(text, parent)
        self.setChecked(checked)
        self.setToolTip(toolTip)