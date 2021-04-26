#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from model.misc import Project, Image
from model.worker import Cutter
from model.util import makeQThread
from view.contextmenu import TransformationContextMenu

from .basescene import BaseScene
from math import ceil


class RightGraphicsScene(BaseScene):
    requestCutout = qtc.pyqtSignal(Project, bool)

    def __init__(self, project: Project, parent=None):
        super(RightGraphicsScene, self).__init__(project, parent)
        self.settings = dict(showCutout=False, timer=qtc.QTimer(), enabled=True, FPS=60, cutout=None, hovered=False,
                             moving=False)
        self.setupWorker()
        self.setupConnections()
        self.restartTimer()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETUP                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def setupWorker(self):
        self.cutter, self.cutterThread = makeQThread(Cutter(), "Cutter")

    def setupConnections(self):
        self.project.alphaMatteChanged.connect(self.__updateSceneRect)
        self.project.newBackgroundChanged.connect(self.__updateSceneRect)
        self.requestCutout.connect(self.cutter.cut)
        self.cutter.finished.connect(self.setCutout)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                EVENTS                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def mousePressEvent(self, event: qtw.QGraphicsSceneMouseEvent) -> None:
        if self.leftButtonPressed(event) and self.project.cutoutRect().contains(event.scenePos()) \
                and self.showCutout() and self.project.newBackground():
            self.setMoving(True)
            self.project.setEdited()

    def mouseMoveEvent(self, event: qtw.QGraphicsSceneMouseEvent) -> None:
        if self.showCutout():
            self.setHovered(self.project.cutoutRect().contains(event.scenePos()))
            if self.moving():
                diff = event.scenePos() - event.lastScenePos()
                self.project.cutoutRect().translate(diff.x(), diff.y())

    def mouseReleaseEvent(self, event: qtw.QGraphicsSceneMouseEvent) -> None:
        if self.moving() and self.leftButtonReleased(event) and self.project.newBackground():
            self.setMoving(False)
            self.project.setEdited()

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.showCutout():
            self.cutter.toggleCutoutMode()

    def contextMenuEvent(self, event: qtw.QGraphicsSceneContextMenuEvent) -> None:
        super(RightGraphicsScene, self).contextMenuEvent(event)
        if self.showCutout():
            ctxMenu = TransformationContextMenu(self.project.cutoutRect())
            ctxMenu.exec(event.screenPos())

    ####################################################################################################################
    #                                                                                                                  #
    #                                                GETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def cutout(self):
        return self.settings["cutout"]

    def enabled(self):
        return self.settings["enabled"]

    def hovered(self):
        return self.settings["hovered"]

    def moving(self):
        return self.settings["moving"]

    def FPS(self):
        return self.settings["FPS"]

    def timer(self):
        return self.settings["timer"]

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def setCutout(self, image: Image):
        self.settings["cutout"] = image

    def setEnabled(self, enabled):
        if not enabled and self.enabled():
            self.settings["enabled"] = enabled
            self.stopTimer()
        elif enabled and not self.enabled():
            self.settings["enabled"] = enabled
            self.restartTimer()

    def setDisabled(self, disabled):
        self.setEnabled(not disabled)

    def setHovered(self, hovered: bool):
        self.settings["hovered"] = hovered

    def setMoving(self, moving: bool):
        self.settings["moving"] = moving

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SLOTS                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def invalidateForeground(self, rect: qtc.QRectF = None):
        super(RightGraphicsScene, self).invalidateForeground(rect)
        if self.showCutout():
            self.requestCutout.emit(self.project, False)

    @qtc.pyqtSlot()
    def toggleCutoutPreview(self):
        self.settings["showCutout"] = not self.settings["showCutout"]
        if self.showCutout():
            self.cutter.start()
        else:
            self.cutter.stop()
        self.__updateSceneRect()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def __updateSceneRect(self):
        if self.project.newBackground() and self.showCutout():
            image = self.project.newBackground()
        else:
            image = self.project.alphaMatte()
        super(RightGraphicsScene, self).updateSceneRect(image)

    def showCutout(self):
        return self.settings["showCutout"]

    def drawBackground(self, painter: qtg.QPainter, rect: qtc.QRectF) -> None:
        if self.project.newBackground() and self.showCutout():
            painter.drawImage(0, 0, self.project.newBackground())

    def drawForeground(self, painter: qtg.QPainter, rect: qtc.QRectF):
        if self.showCutout() and self.cutout():
            painter.setTransform(self.project.cutoutRect().transform(), True)
            painter.drawImage(self.project.cutoutRect().rect(), self.cutout())
            if self.hovered():
                painter.drawPolygon(self.project.cutoutRect().polygonF())
        else:
            painter.drawImage(0, 0, self.project.alphaMatte())

    def restartTimer(self):
        timer = self.timer()
        self.stopTimer()
        if self.enabled():
            self.cutter.start()
            interval = ceil(1000 / self.FPS()) if self.FPS() > 0 else 0
            timer.setInterval(interval)
            timer.timeout.connect(self.invalidateForeground)
            timer.start()

    def stopTimer(self):
        timer = self.timer()
        if timer.isActive():
            self.cutter.stop()
            timer.timeout.disconnect()
            timer.stop()

    def close(self):
        self.stopTimer()
        self.cutter.finished.disconnect()
        self.cutter.stop()
        self.requestCutout.disconnect()
        self.cutterThread.quit()
        self.cutterThread.wait()
