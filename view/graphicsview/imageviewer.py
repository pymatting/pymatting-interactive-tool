# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from model.misc import Image
from strings import imageViewerTitle
from .baseview import BaseView


class ImageScene(qtw.QGraphicsScene):
    def __init__(self, image: Image, parent=None):
        super(ImageScene, self).__init__(parent)
        dx = image.width() * 0.02
        self.setSceneRect(qtc.QRectF(image.rect()).adjusted(-dx, -dx, dx, dx))
        self.image = image

    def drawForeground(self, painter: qtg.QPainter, rect: qtc.QRectF) -> None:
        painter.drawImage(0, 0, self.image)


class ImageView(BaseView):
    def mousePressEvent(self, event: qtg.QMouseEvent) -> None:
        super(ImageView, self).mousePressEvent(event)
        if event.buttons() == qtc.Qt.MiddleButton:
            self.enableDrag(True)
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
        super(ImageView, self).mouseReleaseEvent(event)
        if event.button() == qtc.Qt.MiddleButton:
            self.enableDrag(False)

    def keyPressEvent(self, event: qtg.QKeyEvent) -> None:
        if event.key() == qtc.Qt.Key_Space and not event.isAutoRepeat():
            self.enableDrag(True)
        elif (
            event.modifiers() == qtc.Qt.ControlModifier
            and event.key() == qtc.Qt.Key_F
            and not event.isAutoRepeat()
        ):
            self.fitInView()

    def keyReleaseEvent(self, event: qtg.QKeyEvent) -> None:
        if event.key() == qtc.Qt.Key_Space and not event.isAutoRepeat():
            self.enableDrag(False)


class ImageViewer(qtw.QWidget):
    def __init__(self, paths, parent=None):
        super(ImageViewer, self).__init__(parent=parent)
        self.setWindowTitle(imageViewerTitle)
        # self.resize(500, 500)
        images = [Image(path) for path in paths]
        names = [
            f"{qtc.QFileInfo(path).fileName()} - [{image.width()}x{image.height()}]"
            for path, image in zip(paths, images)
        ]
        self.views = [
            ImageView(ImageScene(image), None) for image in images if not image.isNull()
        ]
        self.tabWidget = qtw.QTabWidget(self)
        [self.tabWidget.addTab(view, name) for view, name in zip(self.views, names)]
        # tabWidget.setTabsClosable(True)
        # tabWidget.tabCloseRequested.connect(tabWidget.removeTab)
        self.tabWidget.setMovable(True)
        layout = qtw.QVBoxLayout(self)
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)
        self.tabWidget.currentChanged.connect(self.fitInView)

    def fitInView(self, index):
        self.tabWidget.widget(index).fitInView()

    def fitCurrentInView(self):
        self.fitInView(self.tabWidget.currentIndex())

    def showEvent(self, event: qtg.QShowEvent) -> None:
        super(ImageViewer, self).showEvent(event)
        self.fitCurrentInView()

    def resizeEvent(self, event: qtg.QResizeEvent) -> None:
        super(ImageViewer, self).resizeEvent(event)
        self.fitCurrentInView()

    def show(self) -> None:
        if self.views:
            super(ImageViewer, self).show()
