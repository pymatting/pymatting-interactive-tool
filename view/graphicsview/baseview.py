# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from model.misc import Project, Image


class BaseView(qtw.QGraphicsView):
    imageDropped = qtc.pyqtSignal()
    dragEnabled = qtc.pyqtSignal(bool)

    def __init__(self, scene: qtw.QGraphicsScene, project: Project, parent=None):
        super(BaseView, self).__init__(scene, parent=parent)
        self.project = project
        self.setBackgroundRole(qtg.QPalette.Shadow)
        self.setupConnections(scene)
        self.setupVariables()
        self.setMouseTracking(True)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETUP                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def setupConnections(self, scene: qtw.QGraphicsScene):
        scene.sceneRectChanged.connect(self.fitInView)

    def setupVariables(self):
        self.scaleFactor = 1.25
        self.cursorPos = self.sceneRect().center()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                EVENTS                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def mousePressEvent(self, event: qtg.QMouseEvent) -> None:
        super(BaseView, self).mousePressEvent(event)
        if event.buttons() == qtc.Qt.MiddleButton:
            self.dragEnabled.emit(True)
            self.mousePressEvent(
                qtg.QMouseEvent(
                    event.type(),
                    event.pos(),
                    qtc.Qt.LeftButton,
                    qtc.Qt.LeftButton,
                    event.modifiers(),
                )
            )

    def mouseReleaseEvent(self, event: qtg.QMouseEvent) -> None:
        super(BaseView, self).mouseReleaseEvent(event)
        if event.button() == qtc.Qt.MiddleButton:
            self.dragEnabled.emit(False)

    def keyPressEvent(self, event: qtg.QKeyEvent) -> None:
        super(BaseView, self).keyPressEvent(event)
        if event.key() == qtc.Qt.Key_Space and not event.isAutoRepeat():
            self.dragEnabled.emit(True)

    def keyReleaseEvent(self, event: qtg.QKeyEvent) -> None:
        super(BaseView, self).keyReleaseEvent(event)
        if event.key() == qtc.Qt.Key_Space and not event.isAutoRepeat():
            self.dragEnabled.emit(False)

    def wheelEvent(self, event: qtg.QWheelEvent) -> None:
        if event.modifiers() == qtc.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn()
            elif event.angleDelta().y() < 0:
                self.zoomOut()
        else:
            super(BaseView, self).wheelEvent(event)

    def enterEvent(self, event: qtc.QEvent) -> None:
        super(BaseView, self).enterEvent(event)
        self.setFocus(qtc.Qt.MouseFocusReason)

    def dragEnterEvent(self, event: qtg.QDragEnterEvent) -> None:
        super(BaseView, self).dragEnterEvent(event)
        mimeData = event.mimeData()
        if mimeData.hasUrls() and len(mimeData.urls()) == 1:
            urls = mimeData.urls()
            url = urls[0]
            localFile = url.toLocalFile()
            mimeDatabase = qtc.QMimeDatabase()
            mimeTypeForFile = mimeDatabase.mimeTypeForFile(localFile)
            mimeType = mimeTypeForFile.name()
            if mimeType in ["image/jpeg", "image/png"]:
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event: qtg.QDragMoveEvent) -> None:
        # dont remove this
        pass

    def dropEvent(self, event: qtg.QDropEvent) -> None:
        super(BaseView, self).dropEvent(event)
        mimeData = event.mimeData()
        urls = mimeData.urls()
        url = urls[0]
        localFile = url.toLocalFile()
        self.onDrop(localFile)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SLOTS                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    @qtc.pyqtSlot()
    def fitInView(self):
        super(BaseView, self).fitInView(self.sceneRect(), qtc.Qt.KeepAspectRatio)
        self.invalidateScene()

    @qtc.pyqtSlot(bool)
    def enableDrag(self, b):
        if b:
            self.setDragMode(qtw.QGraphicsView.ScrollHandDrag)
        else:
            self.setDragMode(qtw.QGraphicsView.NoDrag)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def zoomIn(self):
        self.setTransformationAnchor(qtw.QGraphicsView.AnchorUnderMouse)
        self.scale(self.scaleFactor, self.scaleFactor)
        self.setTransformationAnchor(qtw.QGraphicsView.AnchorViewCenter)

    def zoomOut(self):
        self.scale(1 / self.scaleFactor, 1 / self.scaleFactor)

    def onDrop(self, path: str):
        pass
