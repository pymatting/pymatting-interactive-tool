#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from model.util import trimapToRgba, matchScale, imageToTrimap, cutout, ndarrayToImage
from model.misc import CutoutRect, Image
from model.enum import Color
from pymatting import estimate_foreground_ml


class Project(qtc.QObject):
    # Signal(Has been edited?, Project path, Project Title)
    edited = qtc.pyqtSignal(bool, str, str)
    # Signal(new path)
    pathChanged = qtc.pyqtSignal(str)
    fileRenamed = qtc.pyqtSignal()
    aspectRatioChanged = qtc.pyqtSignal()

    trimapPreviewChanged = qtc.pyqtSignal()
    alphaMatteChanged = qtc.pyqtSignal()
    canvasChanged = qtc.pyqtSignal()
    # Signal(Is the new background none?)
    newBackgroundChanged = qtc.pyqtSignal(bool)

    def __init__(self, canvas, alphaMatte, trimapPreview, newBackground=None, parent=None):
        super(Project, self).__init__(parent)
        self.images = dict(canvas=canvas,
                           trimapPreview=trimapPreview,
                           alphaMatte=alphaMatte,
                           newBackground=newBackground)

        self.__settings = dict(strings=dict(project=dict(title=self.defaultProjectTitle())))
        self.resetFileNames()
        self.resetCutoutRect()
        self._edited = False
        self.__path = None
        self.__reduceColorBleeding = True

    @classmethod
    def empty(cls, width=500, height=500):
        canvas = Image(width, height, Image.Format_ARGB32)
        canvas.fill(qtc.Qt.white)
        trimapPreview = Image(width, height, Image.Format_ARGB32)
        trimapPreview.fill(qtc.Qt.transparent)
        alphaMatte = Image(width, height, Image.Format_Grayscale8)
        alphaMatte.fill(qtc.Qt.black)
        return cls(canvas, alphaMatte, trimapPreview)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def resetFileNames(self):
        self.__settings["strings"]["fileName"] = dict(canvas="canvas.png",
                                                      alphaMatte="alpha.png",
                                                      newBackground=None,
                                                      cutout="cutout.png",
                                                      trimap="trimap.png")

    def setReduceColorBleeding(self, b):
        self.__reduceColorBleeding = b

    def resetCutoutRect(self):
        self.setCutoutRect(CutoutRect(self.canvasRectF()))

    def setCanvas(self, canvas: Image):
        if canvas and not canvas.isNull():
            if canvas.format() != Image.Format_ARGB32:
                canvas = canvas.convertToFormat(Image.Format_ARGB32)
            self.images["canvas"] = canvas
            self.matchScale()
            self.canvasChanged.emit()

    def setAlphaMatte(self, alphaMatte):
        if alphaMatte and not alphaMatte.isNull():
            if alphaMatte.format() != Image.Format_Grayscale8:
                alphaMatte = alphaMatte.convertToFormat(Image.Format_Grayscale8)
            alphaMatte = matchScale(alphaMatte, self.canvas())
            self.images["alphaMatte"] = alphaMatte
            self.alphaMatteChanged.emit()
        elif alphaMatte and alphaMatte.isNull():
            alphaMatte = Image.full(self.canvas().size(), Color.black.value, Image.Format_Grayscale8)
            self.images["alphaMatte"] = alphaMatte
            self.alphaMatteChanged.emit()

    def setTrimapPreview(self, trimapPreview: Image):
        if trimapPreview and not trimapPreview.isNull():
            if trimapPreview.format() != Image.Format_ARGB32:
                trimapPreview = trimapPreview.convertToFormat(Image.Format_ARGB32)
            trimapPreview = matchScale(trimapPreview, self.canvas())
            self.images["trimapPreview"] = trimapPreview
            self.trimapPreviewChanged.emit()

    def setTrimap(self, trimap: Image):
        if not trimap.isNull():
            trimapPreview = trimapToRgba(trimap)
            self.setTrimapPreview(trimapPreview)
        else:
            self.setTrimapPreview(Image.empty(self.canvas().size()))


    def setNewBackground(self, newBackground: Image, delete=True):
        if newBackground and newBackground.isNull():
            self.__settings["strings"]["fileName"]["newBackground"] = None
            self.images["newBackground"] = None
        elif newBackground:
            if newBackground.format() != Image.Format_ARGB32:
                newBackground = newBackground.convertToFormat(Image.Format_ARGB32)
            if not self.newBackgroundName():
                self.__settings["strings"]["fileName"]["newBackground"] = "newBackground.png"
            self.images["newBackground"] = newBackground
        else:
            dir = qtc.QDir(self.path())
            filePath = dir.filePath(self.newBackgroundName())
            if delete and qtc.QFileInfo(dir.absolutePath()).isDir() and qtc.QFileInfo(filePath).isFile():
                dir.remove(self.newBackgroundName())
            self.__settings["strings"]["fileName"]["newBackground"] = None
            self.images["newBackground"] = newBackground
        self.newBackgroundChanged.emit(not self.newBackground() is None)
        self.fileRenamed.emit()

    def setPath(self, path: str):
        # if path != self.path():
        self.__path = path
        self.pathChanged.emit(self.path())

    def setTitle(self, title: str):
        self.__settings["strings"]["project"]["title"] = title

    def setEdited(self):
        self._edited = True
        self.edited.emit(self._edited, self.path(), self.title())

    def setUnedited(self):
        self._edited = False
        self.edited.emit(self._edited, self.path(), self.title())

    def setCutoutRect(self, rect: CutoutRect):
        self.__cutoutRect = rect
        self.cutoutRect().changed.connect(self.setEdited)

    def setSettings(self, settings: dict):
        self.__settings = settings
        rect = settings["cutout"]["rect"]
        angle = settings["cutout"]["angle"]
        scale = settings["cutout"]["scale"]
        self.setCutoutRect(CutoutRect(rect, scale, angle))

    def setImages(self, images: dict):
        self.images = images

    def changeImages(self, canvas, alphaMatte, trimapPreview=None, trimap=None, newBackground=-1, resetCutout=False, edited=False, aspectRatioChanged=True):
        self.setCanvas(canvas)
        self.setAlphaMatte(alphaMatte)
        if trimapPreview:
            self.setTrimapPreview(trimapPreview)
        if trimap:
            self.setTrimap(trimap)
        if newBackground != -1:
            self.setNewBackground(newBackground)
        if resetCutout:
            self.resetCutoutRect()
        if edited:
            self.setEdited()
        if aspectRatioChanged:
            self.aspectRatioChanged.emit()

    def new(self, canvas: Image, projectName: str):
        self.setCanvas(canvas)
        self.clearAlphaMatte()
        self.clearTrimapPreview()
        self.setNewBackground(None, False)
        self.setTitle(projectName)
        self.setPath(None)
        self.setUnedited()
        self.resetCutoutRect()
        self.resetFileNames()
        self.aspectRatioChanged.emit()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                GETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################
    def reduceColorBleeding(self):
        return self.__reduceColorBleeding

    def names(self):
        return [self.canvasName(), self.alphaMatteName(), self.trimapName(), self.cutoutName(),
                self.newBackgroundName()]

    def canvas(self) -> Image:
        return self.images["canvas"]

    def alphaMatte(self) -> Image:
        return self.images["alphaMatte"]

    def trimapPreview(self) -> Image:
        return self.images["trimapPreview"]

    def trimap(self):
        return imageToTrimap(self.trimapPreview())

    def newBackground(self) -> Image:
        return self.images["newBackground"]

    def path(self):
        return self.__path

    def title(self):
        return self.__settings["strings"]["project"]["title"]

    def isEdited(self):
        return self._edited

    def canvasWidth(self):
        return self.canvas().width()

    def canvasHeight(self):
        return self.canvas().height()

    def canvasRect(self):
        return self.canvas().rect()

    def canvasRectF(self):
        return qtc.QRectF(self.canvas().rect())

    def clearTrimapPreview(self):
        trimapPreview = Image.empty(self.canvas().size())
        self.setTrimapPreview(trimapPreview)

    def clearAlphaMatte(self):
        alphaMatte = Image.full(self.canvas().size(), Color.black.value, qtg.QImage.Format_Grayscale8)
        self.setAlphaMatte(alphaMatte)

    def removeNewBackground(self):
        self.setNewBackground(None)
        self.resetCutoutRect()

    def cutoutRect(self):
        return self.__cutoutRect

    def fileName(self, key: str):
        return self.__settings["strings"]["fileName"].get(key, None)

    def canvasName(self):
        return self.fileName("canvas")

    def alphaMatteName(self):
        return self.fileName("alphaMatte")

    def trimapName(self):
        return self.fileName("trimap")

    def cutoutName(self):
        return self.fileName("cutout")

    def newBackgroundName(self):
        return self.fileName("newBackground")

    def settings(self):
        settings = self.__settings.copy()
        settings["cutout"] = self.cutoutRect().settings()
        return settings

    def parentPath(self):
        dir = qtc.QDir(self.path())
        if dir.cdUp():
            return dir.absolutePath()
        else:
            return None

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SLOTS                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    @qtc.pyqtSlot(str, str, str)
    def renameFile(self, path: str, oldName: str, newName: str):
        if path == self.path():
            for key, value in self.__settings["strings"]["fileName"].items():
                if value == oldName:
                    self.__settings["strings"]["fileName"][key] = newName
        elif path == self.parentPath() and oldName == self.title():
            self.setTitle(newName)
            path = qtc.QDir(path)
            path.cd(newName)
            self.setPath(path.absolutePath())
        self.setUnedited()
        self.fileRenamed.emit()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def matchScale(self):
        self.setAlphaMatte(matchScale(self.alphaMatte(), self.canvas()))
        self.setTrimapPreview(matchScale(self.trimapPreview(), self.canvas()))

    def close(self):
        self.edited.disconnect()
        self.pathChanged.disconnect()
        self.trimapPreviewChanged.disconnect()
        self.alphaMatteChanged.disconnect()
        self.canvasChanged.disconnect()
        self.newBackgroundChanged.disconnect()

    def defaultProjectTitle(self):
        return "untitled"

    def cutout(self):
        if self.reduceColorBleeding():
            foregroundEstimate = ndarrayToImage(
                estimate_foreground_ml(self.canvas().rgbView(True), self.alphaMatte().rawView(True)), True)
            cut = cutout(foregroundEstimate, self.alphaMatte())
        else:
            cut = cutout(self.canvas(), self.alphaMatte())
        if self.newBackground():
            newBackground = self.newBackground().copy()
            painter = qtg.QPainter(newBackground)
            painter.setTransform(self.cutoutRect().transform())
            painter.drawImage(self.cutoutRect().rect(), cut)
            cut = newBackground
        else:
            cut = cut.transformed(self.cutoutRect().transform())
        return cut
