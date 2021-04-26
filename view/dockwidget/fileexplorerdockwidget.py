#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw
from view.treeview import FileExplorerTreeView


class FileExplorerDockWidget(qtw.QDockWidget):

    def __init__(self, treeView: FileExplorerTreeView, title="File Explorer", flags=None, parent=None):
        if flags and parent:
            super(FileExplorerDockWidget, self).__init__(title, flags=flags, parent=parent)
        elif flags:
            super(FileExplorerDockWidget, self).__init__(title, flags=flags)
        elif parent:
            super(FileExplorerDockWidget, self).__init__(title, parent=parent)
        else:
            super(FileExplorerDockWidget, self).__init__(title)
        self.setWidget(treeView)

