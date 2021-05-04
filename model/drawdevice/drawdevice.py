# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPainter
from model.enum import Color, DrawMode


class DrawDevice(QObject):
    def __init__(self, drawMode: DrawMode = DrawMode.foreground):
        super(DrawDevice, self).__init__()
        self.settings = dict()
        self.setDrawMode(drawMode)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def setColor(self, color: Color):
        self.settings["color"] = color

    def setPreviewColor(self, color: Color):
        self.settings["previewColor"] = color

    def setCompositionMode(self, compMode: QPainter.CompositionMode):
        self.settings["compMode"] = compMode

    def setDrawMode(self, drawMode: DrawMode):
        self.settings["drawMode"] = drawMode
        if drawMode.isForeground():
            self.setColor(Color.lightGreen)
            self.setPreviewColor(Color.lightGreen)
            self.setCompositionMode(QPainter.CompositionMode_Source)
        elif drawMode.isBackground():
            self.setColor(Color.lightRed)
            self.setPreviewColor(Color.lightRed)
            self.setCompositionMode(QPainter.CompositionMode_Source)
        elif drawMode.isUnknownTransparent():
            self.setColor(Color.transparent)
            self.setPreviewColor(Color.transparent)
            self.setCompositionMode(QPainter.CompositionMode_Clear)
        elif drawMode.isUnknownColored():
            self.setColor(Color.lightBlue)
            self.setPreviewColor(Color.lightBlue)
            self.setCompositionMode(QPainter.CompositionMode_Source)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                GETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def color(self):
        return self.settings["color"].value

    def previewColor(self):
        return self.settings["previewColor"].value

    def compositionMode(self):
        return self.settings["compMode"]

    def drawMode(self):
        return self.settings["drawMode"]
