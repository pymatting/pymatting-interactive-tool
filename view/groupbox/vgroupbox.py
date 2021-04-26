#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from .groupbox import *

class VGroupBox(GroupBox):
    def __init__(self, title:str, parent=None):
        super(VGroupBox, self).__init__(title, qtc.Qt.Vertical, parent=parent)