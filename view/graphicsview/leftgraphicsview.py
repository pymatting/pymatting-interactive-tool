#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from .baseview import BaseView
from view.graphicsscene import LeftGraphicsScene
from view.messagebox import MessageBoxCanvasOrTrimap
from view.scrollbar import ScrollBar
from strings import fileIsCorruptedText
from model.misc import Project, Image, FileHandler
from model.enum import Mode
from model.util import showWarning


class LeftGraphicsView(BaseView):

    requestNewProject = qtc.pyqtSignal(str)

    def __init__(self, scene: LeftGraphicsScene, project: Project, parent=None):
        super(LeftGraphicsView, self).__init__(scene, project, parent)
        self.leftGraphicsScene = scene
        self.setupScrollbars()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETUP                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def setupScrollbars(self):
        hScrollBar = ScrollBar()
        hScrollBar.entered.connect(lambda: self.leaveEvent(None))
        hScrollBar.left.connect(lambda: self.enterEvent(None))
        vScrollBar = ScrollBar()
        vScrollBar.entered.connect(lambda: self.leaveEvent(None))
        vScrollBar.left.connect(lambda: self.enterEvent(None))
        self.setHorizontalScrollBar(hScrollBar)
        self.setVerticalScrollBar(vScrollBar)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def setMode(self, mode: Mode):
        self.leftGraphicsScene.setMode(mode)
        self.changeCursor(mode)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                Events                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def enterEvent(self, event: qtc.QEvent) -> None:
        if event:
            super(LeftGraphicsView, self).enterEvent(event)
        self.changeCursor(self.leftGraphicsScene.mode())

    def leaveEvent(self, event: qtc.QEvent) -> None:
        if event:
            super(LeftGraphicsView, self).leaveEvent(event)
        self.leftGraphicsScene.clearBrushPreview()
        self.leftGraphicsScene.painting = False
        self.setCursor(qtc.Qt.ArrowCursor)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                Helper                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def changeCursor(self, mode: Mode):
        if mode.isBrush():
            self.setCursor(qtc.Qt.BlankCursor)
        elif mode.isPaintbucket():
            self.setCursor(qtc.Qt.CrossCursor)
        elif mode.isCrop():
            self.setCursor(qtc.Qt.ArrowCursor)

    def onDrop(self, path:str):
        image = Image(path)
        if image.isNull():
            showWarning(fileIsCorruptedText, FileNotFoundError("Could not find file"))
        else:
            response = MessageBoxCanvasOrTrimap().exec()
            if response == MessageBoxCanvasOrTrimap.Canvas:
                self.requestNewProject.emit(path)
                self.imageDropped.emit()
            elif response == MessageBoxCanvasOrTrimap.Trimap:
                self.project.setTrimap(image)
                self.imageDropped.emit()
