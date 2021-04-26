#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw


class MenuBar(qtw.QMenuBar):

    def addMenus(self, *menus):
        for menu in menus:
            self.addMenu(menu)