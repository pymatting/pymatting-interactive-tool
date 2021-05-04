# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from .groupbox import *


class HGroupBox(GroupBox):
    def __init__(self, title: str, parent=None):
        super(HGroupBox, self).__init__(title, qtc.Qt.Horizontal, parent=parent)
