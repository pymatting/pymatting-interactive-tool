#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw


class PaintContextMenu(qtw.QMenu):


    def __init__(self, parent=None, title="Draw Settings"):
        super(PaintContextMenu, self).__init__(title, parent)


