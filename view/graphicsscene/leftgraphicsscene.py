#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from view.slider import HSlider
from view.spinbox import SpinBox
from view.contextmenu import PaintContextMenu
from view.groupbox import HGroupBox
from model.drawdevice import Brush, Paintbucket
from model.misc import Project, UndoStack, Screenshot, AdjustingRect, Image
from model.enum import Mode, DrawMode
from model.util import showWarning, makeQThread, calculateDiffRect
from model.worker import Cropper, Scaler
from strings import acceptCropText, cropTitle, brushWidthSliderToolTip, paintBucketToolTip
from .basescene import BaseScene
from math import ceil


class LeftGraphicsScene(BaseScene):
    drawn = qtc.pyqtSignal(qtc.QRect)
    colorChanged = qtc.pyqtSignal(qtg.QColor)
    requestStatusMessage = qtc.pyqtSignal(str)
    requestCropping = qtc.pyqtSignal(Project, qtc.QRect)
    requestScaling = qtc.pyqtSignal(Project, int, int, bool)

    def __init__(self, project: Project, parent=None):
        super(LeftGraphicsScene, self).__init__(project, parent)
        self.settings = dict(mode=Mode.brush, cursorPos=dict(last=None, current=None),
                             drawDevices=dict(brush=Brush(), paintbucket=Paintbucket()), screenshot=None,
                             cropArea=dict(start=None, end=None))

        self.painting = False
        self.updateOnMouseMove = False
        self.brushSliderStep = 1
        self.project = project
        self.undoStack = UndoStack()
        self.setupWorkers()
        self.setupWidgets()
        self.setupConnection()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETUP                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def setupWorkers(self):
        self.cropper, self.cropperThread = makeQThread(Cropper(), "Cropper")
        self.scaler, self.scalerThread = makeQThread(Scaler(), "Scaler")

    def setupConnection(self):
        self.paintbucket().filled.connect(self.onFloodFill)
        self.project.canvasChanged.connect(lambda: self.updateSceneRect(self.project.canvas()))
        self.project.canvasChanged.connect(self.resetUndoStack)
        self.project.trimapPreviewChanged.connect(self.invalidateForeground)
        self.project.trimapPreviewChanged.connect(self.resetUndoStack)
        self.cropper.error.connect(showWarning)
        self.requestCropping.connect(self.cropper.crop)
        self.requestScaling.connect(self.scaler.scale)
        self.brushWidthSlider.valueChanged.connect(self.brushWidthSpinBox.setValue)
        self.brushWidthSpinBox.valueChanged.connect(self.brushWidthSlider.setValue)
        self.brushWidthSlider.valueChanged.connect(self.setBrushWidth)
        self.project.canvasChanged.connect(self.adjustMaxBrushWidth)
        self.paintbucketSpinBox.valueChanged.connect(self.setPaintbucketThreshold)

    def setupWidgets(self):
        self.brushWidthSlider = HSlider(1, 100, 50, brushWidthSliderToolTip, tickInterval=4)
        self.brushWidthSlider.setFixedWidth(200)
        self.brushWidthSpinBox = SpinBox(1, 100, 50, wrapping=False)
        self.paintbucketSpinBox = SpinBox(0, 442, 20, paintBucketToolTip, wrapping=False)
        self.brushAction = qtw.QWidgetAction(self)
        self.brushGroupBox = HGroupBox("Brush Settings")
        self.brushGroupBox.addWidgets(qtw.QLabel("Width"), self.brushWidthSlider, self.brushWidthSpinBox)
        self.brushAction.setDefaultWidget(self.brushGroupBox)
        self.paintBucketAction = qtw.QWidgetAction(self)
        self.paintBucketGroupBox = HGroupBox("Paintbucket Settings")
        threshHoldLabel = qtw.QLabel("Threshold")
        threshHoldLabel.setSizePolicy(qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)
        self.paintBucketGroupBox.addWidgets(threshHoldLabel, self.paintbucketSpinBox)
        self.paintBucketAction.setDefaultWidget(self.paintBucketGroupBox)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                EVENTS                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def mousePressEvent(self, event: qtw.QGraphicsSceneMouseEvent) -> None:
        self.setCursorPos(event.lastScenePos(), event.scenePos())
        if self.leftButtonPressed(event):
            self.painting = True
            if self.mode().isBrush():
                self.makeScreenshot()
            elif self.mode().isCrop():
                self.makeScreenshot()
                self.setCropStart(event.scenePos())

    def mouseMoveEvent(self, event: qtw.QGraphicsSceneMouseEvent) -> None:
        self.setCursorPos(event.lastScenePos(), event.scenePos())
        if self.leftButtonMoved(event):
            if self.mode().isBrush():
                self.makeScreenshot()
                rect = self.brush().drawLine(self.project.trimapPreview(), event.lastScenePos(), event.scenePos())
                self.screenshot().addRect(rect)
                if self.updateOnMouseMove:
                    self.project.setEdited()
                    self.drawn.emit(rect)
            elif self.mode().isCrop() and self.cropStart():
                self.setCropEnd(event.scenePos())
                self.invalidateForeground()
        self.renderBrushPreview()

    def mouseReleaseEvent(self, event: qtw.QGraphicsSceneMouseEvent) -> None:
        self.setCursorPos(event.lastScenePos(), event.scenePos())
        if self.leftButtonReleased(event):
            self.painting = False
            if self.mode().isBrush():
                self.makeScreenshot()
                rect = self.brush().drawPoint(self.project.trimapPreview(), event.scenePos())
                self.screenshot().addRect(rect)
                self.project.setEdited()
                self.takeScreenshot(self.screenshot())
                self.setScreenshot(None)
                if self.updateOnMouseMove:
                    self.drawn.emit(rect)
                else:
                    self.drawn.emit(self.project.canvas().rect())
            elif self.mode().isCrop():
                self.setCropEnd(event.scenePos())
                cropRect = self.cropRect()
                if cropRect and self.project.canvasRect().intersects(cropRect):
                    self.crop(self.project.canvas().rect().intersected(cropRect))
            elif self.mode().isPaintbucket():
                if event.modifiers() == qtc.Qt.ControlModifier:
                    self.paintbucket().fill(self.project.trimapPreview(), self.project.trimapPreview(),
                                            event.scenePos(), tolerance=0)
                else:
                    self.paintbucket().fill(self.project.canvas(), self.project.trimapPreview(), event.scenePos())

        self.resetCropRect()
        self.invalidateForeground()

    def previewRect(self):
        return AdjustingRect().addPoints([self.lastPos(), self.pos()], self.brush().previewRadius()).toQRectF()

    def mouseDoubleClickEvent(self, event: qtw.QGraphicsSceneMouseEvent) -> None:
        self.mousePressEvent(event)

    def keyPressEvent(self, event: qtg.QKeyEvent) -> None:
        super(LeftGraphicsScene, self).keyPressEvent(event)
        if (event.key() == qtc.Qt.Key_1):
            self.setDrawMode(DrawMode.foreground)
        elif (event.key() == qtc.Qt.Key_2):
            self.setDrawMode(DrawMode.background)
        elif (event.key() == qtc.Qt.Key_3):
            self.setDrawMode(DrawMode.unknownColored)
        elif (event.key() == qtc.Qt.Key_4):
            self.setDrawMode(DrawMode.unknownTransparent)
        elif event.key() == qtc.Qt.Key_Plus:
            if self.mode().isBrush():
                self.increaseSliderValue()
            elif self.mode().isPaintbucket():
                self.increasePaintbucktThreshold()
        elif event.key() == qtc.Qt.Key_Minus:
            if self.mode().isBrush():
                self.decreaseSliderValue()
            elif self.mode().isPaintbucket():
                self.decreasePaintbucketThreshold()

    def wheelEvent(self, event: qtw.QGraphicsSceneWheelEvent) -> None:
        if event.modifiers() == qtc.Qt.ShiftModifier:
            event.accept()
            if event.delta() > 0:
                if self.mode().isBrush():
                    self.increaseSliderValue()
                elif self.mode().isPaintbucket():
                    self.increasePaintbucktThreshold()
            elif event.delta() < 0:
                if self.mode().isBrush():
                    self.decreaseSliderValue()
                elif self.mode().isPaintbucket():
                    self.decreasePaintbucketThreshold()
        else:
            event.ignore()

    def contextMenuEvent(self, event: qtw.QGraphicsSceneContextMenuEvent) -> None:
        if self.mode().isBrush() or self.mode().isPaintbucket():
            if not self.updateOnMouseMove:
                self.drawn.emit(self.project.canvas().rect())

            self.takeScreenshot(self.screenshot())
            ctxMenu = PaintContextMenu()
            ctxMenu.addActions([self.brushAction, self.paintBucketAction])
            ctxMenu.exec(event.screenPos())
            self.invalidate()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                GETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def drawDevice(self):
        if self.mode().isBrush():
            return self.brush()
        elif self.mode().isPaintbucket():
            return self.paintbucket()
        else:
            return None

    def brush(self):
        return self.settings["drawDevices"]["brush"]

    def paintbucket(self):
        return self.settings["drawDevices"]["paintbucket"]

    def lastPos(self):
        return self.settings["cursorPos"]["last"]

    def pos(self):
        return self.settings["cursorPos"]["current"]

    def mode(self):
        return self.settings["mode"]

    def screenshot(self):
        return self.settings["screenshot"]

    def cropRect(self):
        if self.cropStart() and self.cropEnd() and self.cropStart() != self.cropEnd():
            return qtc.QRectF(self.cropStart(), self.cropEnd()).toAlignedRect().normalized()
        else:
            return None

    def cropStart(self):
        return self.settings["cropArea"]["start"]

    def cropEnd(self):
        return self.settings["cropArea"]["end"]

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def setCursorPos(self, lastPos: qtc.QPointF, curPos: qtc.QPointF):
        self.settings["cursorPos"] = {"last": lastPos, "current": curPos}

    def setDrawMode(self, drawMode: DrawMode):
        if self.mode().isBrush() or self.mode().isPaintbucket():
            drawer = self.drawDevice()
            drawer.setDrawMode(drawMode)
            self.colorChanged.emit(drawer.previewColor())
            self.invalidateForeground()

    def setMode(self, mode: Mode):
        self.settings["mode"] = mode
        drawDevice = self.drawDevice()
        if drawDevice:
            self.setDrawMode(drawDevice.drawMode())
        self.invalidate()
        self.takeScreenshot(self.screenshot())

    def setScreenshot(self, screenshot: Screenshot):
        self.settings["screenshot"] = screenshot

    def setCropStart(self, point: qtc.QPointF):
        self.settings["cropArea"]["start"] = point

    def setBrushWidth(self, width):
        self.brush().setWidth(width)
        self.requestStatusMessage.emit(f"Width: {width}")
        self.invalidateForeground()

    def setCropEnd(self, point: qtc.QPointF):
        self.settings["cropArea"]["end"] = point

    def setPaintbucketThreshold(self, threshold: int):
        self.paintbucket().setTolerance(threshold)
        self.requestStatusMessage.emit(f"Threshold: {threshold}")

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SLOTS                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    @qtc.pyqtSlot()
    def undo(self):
        if not self.painting:
            value = self.undoStack.undo()
            if value:
                rectf = value.rectF()
                painter = qtg.QPainter(self.project.trimapPreview())
                painter.setCompositionMode(qtg.QPainter.CompositionMode_Source)
                painter.drawImage(rectf, value.before())
                self.invalidateForeground(rectf)
                self.project.setEdited()
                self.invalidate()
                self.drawn.emit(rectf.toAlignedRect())

    @qtc.pyqtSlot()
    def redo(self):
        if not self.painting:
            value = self.undoStack.redo()
            if value:
                rectf = value.rectF()
                painter = qtg.QPainter(self.project.trimapPreview())
                painter.setCompositionMode(qtg.QPainter.CompositionMode_Source)
                painter.drawImage(rectf, value.after())
                self.invalidateForeground(rectf)
                self.project.setEdited()
                self.invalidate()
                self.drawn.emit(rectf.toAlignedRect())

    @qtc.pyqtSlot()
    def toggleDrawMode(self):
        if self.mode().isBrush() or self.mode().isPaintbucket():
            drawer = self.drawDevice()
            if drawer.drawMode().isForeground():
                self.setDrawMode(DrawMode.background)
            elif drawer.drawMode().isBackground():
                self.setDrawMode(DrawMode.unknownColored)
            elif drawer.drawMode().isUnknownColored():
                self.setDrawMode(DrawMode.unknownTransparent)
            elif drawer.drawMode().isUnknownTransparent():
                self.setDrawMode(DrawMode.foreground)

    @qtc.pyqtSlot()
    def resetUndoStack(self):
        self.undoStack = UndoStack()

    @qtc.pyqtSlot(Image, qtc.QRectF)
    def onFloodFill(self, before: Image, rectf: qtc.QRectF):
        self.invalidateForeground(rectf)
        screenshot = Screenshot.fromImages(before, self.project.trimapPreview(), rectf)
        screenshot.take()
        self.undoStack.push(screenshot)
        self.drawn.emit(rectf.toAlignedRect())

    @qtc.pyqtSlot()
    def adjustMaxBrushWidth(self):
        maxPenWidth = ceil(max(self.project.canvasWidth(), self.project.canvasHeight()) * 0.2)
        self.brushWidthSpinBox.setMaximum(maxPenWidth)
        self.brushWidthSlider.setMaximum(maxPenWidth)
        self.brushWidthSlider.setTickInterval(ceil(maxPenWidth / 25))
        self.brushSliderStep = ceil(maxPenWidth/100)


    @qtc.pyqtSlot()
    def clearTrimapPreview(self):
        screenshot = Screenshot(self.project.trimapPreview())
        self.project.trimapPreview().clear()
        clearedRect = calculateDiffRect(screenshot.before(), screenshot.after())
        screenshot.addRect(clearedRect)
        self.takeScreenshot(screenshot)
        if clearedRect:
            self.drawn.emit(clearedRect.toAlignedRect())

    @qtc.pyqtSlot(bool)
    def disableUpdateOnMouseMove(self, disabled):
        self.enableUpdateOnMouseMove(not disabled)

    def enableUpdateOnMouseMove(self, enabled):
        self.updateOnMouseMove = enabled

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def drawBackground(self, painter: qtg.QPainter, rect: qtc.QRectF):
        painter.drawImage(0, 0, self.project.canvas())

    def drawForeground(self, painter: qtg.QPainter, rect: qtc.QRectF):
        painter.drawImage(0, 0, self.project.trimapPreview())
        self.drawBrushPreview(painter)
        if self.mode().isCrop():
            painter.setPen(qtc.Qt.NoPen)
            painter.setBrush(qtg.QBrush(qtg.QColor(160, 160, 160, 160)))
            painter.drawRect(self.project.canvas().rect())
            cropRect = self.cropRect()
            if cropRect:
                rect = self.project.canvasRect().intersected(cropRect)
                if rect:
                    painter.drawImage(rect, self.project.canvas().copy(rect))
                    painter.drawImage(rect, self.project.trimapPreview().copy(rect))
                    painter.setPen(qtc.Qt.green)
                    font = painter.font()
                    font.setPointSize(12)
                    painter.setFont(font)
                    transformed_rect = painter.transform().mapRect(rect)
                    painter.resetTransform()
                    painter.drawText(transformed_rect, qtc.Qt.AlignCenter | qtc.Qt.TextDontClip,
                                     f" [{rect.width()} x {rect.height()}]")

    def renderBrushPreview(self):
        if self.mode().isBrush() and self.lastPos() and self.pos():
            self.invalidateForeground(self.previewRect())

    def drawBrushPreview(self, painter: qtg.QPainter):
        if self.lastPos() and self.pos() and self.mode().isBrush():
            brush = self.brush()
            painter.setPen(qtg.QPen(qtc.Qt.black, brush.previewWidth()))
            painter.setBrush(qtg.QBrush(brush.previewColor(), qtc.Qt.SolidPattern))
            painter.drawEllipse(self.pos(), brush.radius(), brush.radius())

    def clearBrushPreview(self):
        self.setCursorPos(None, None)
        self.invalidateForeground()

    def increaseSliderValue(self):
        self.brushWidthSlider.setValue(self.brushWidthSlider.value() + self.brushSliderStep)

    def decreaseSliderValue(self):
        self.brushWidthSlider.setValue(self.brushWidthSlider.value() - self.brushSliderStep)

    def increasePaintbucktThreshold(self, step=1):
        self.paintbucketSpinBox.setValue(self.paintbucketSpinBox.value() + step)

    def decreasePaintbucketThreshold(self, step=1):
        self.paintbucketSpinBox.setValue(self.paintbucketSpinBox.value() - step)


    def makeScreenshot(self):
        if not self.screenshot():
            self.setScreenshot(Screenshot(self.project.trimapPreview()))

    def takeScreenshot(self, screenshot):
        if screenshot and screenshot.take():
            self.undoStack.push(screenshot)
        self.setScreenshot(None)

    def resetCropRect(self):
        self.setCropStart(None)
        self.setCropEnd(None)

    def close(self):
        self.cropper.error.disconnect()
        self.requestCropping.disconnect()
        self.cropperThread.quit()
        self.cropperThread.wait()
        self.paintbucket().close()

    def crop(self, rect: qtc.QRect):
        response = qtw.QMessageBox.question(None, cropTitle, acceptCropText)
        if response == qtw.QMessageBox.Yes:
            self.requestCropping.emit(self.project, rect)
