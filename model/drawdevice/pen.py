# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from model.misc import AdjustingRect, Image
from model.drawdevice import DrawDevice


class Pen(DrawDevice):
    """
    Wrapper class that represents a Pen. It can draw lines and points. The look of the drawings depend on the width, style,
    capstyle aswell as the joinstyle of this pen
    """

    def __init__(
        self,
        style: qtc.Qt.PenStyle,
        capStyle: qtc.Qt.PenCapStyle,
        joinStyle: qtc.Qt.PenJoinStyle,
        width=50,
        previewWidth=1,
    ):
        super(Pen, self).__init__()
        self.setStyle(style)
        self.setCapStyle(capStyle)
        self.setJoinStyle(joinStyle)
        self.setPreviewWidth(previewWidth)
        self.setWidth(width)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def setRadius(self, radius: float):
        self.settings["radius"] = radius
        self.setPreviewRadius(radius + self.previewWidth())

    def setWidth(self, width: int):
        self.settings["width"] = width
        self.setRadius(width / 2)

    def setPreviewWidth(self, previewWidth: int):
        self.settings["previewWidth"] = previewWidth

    def setPreviewRadius(self, radius: int):
        self.settings["previewRadius"] = radius

    def setStyle(self, style: qtc.Qt.PenStyle):
        self.settings["style"] = style

    def setCapStyle(self, capStyle: qtc.Qt.PenCapStyle):
        self.settings["cap"] = capStyle

    def setJoinStyle(self, joinStyle: qtc.Qt.PenJoinStyle):
        self.settings["join"] = joinStyle

    ####################################################################################################################
    #                                                                                                                  #
    #                                                GETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def radius(self):
        return self.settings["radius"]

    def width(self):
        return self.settings["width"]

    def previewWidth(self):
        return self.settings["previewWidth"]

    def previewRadius(self):
        return self.settings["previewRadius"]

    def style(self):
        return self.settings["style"]

    def capStyle(self):
        return self.settings["cap"]

    def joinStyle(self):
        return self.settings["join"]

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def pen(self):
        return qtg.QPen(
            self.color(), self.width(), self.style(), self.capStyle(), self.joinStyle()
        )

    def drawLine(self, image: Image, start: qtc.QPointF, end: qtc.QPointF):
        """Draw a line in the given image between start and end

        :param image: Target image
        :param start: Start position of the line
        :param end: End position of the line
        :return: Rect surrounding the line with a minimal area
        """

        painter = qtg.QPainter(image)
        painter.setCompositionMode(self.compositionMode())
        painter.setPen(self.pen())
        painter.drawLine(start, end)
        return AdjustingRect().addPoints([start, end], self.previewRadius()).toQRect()

    def drawPoint(self, image: Image, pos: qtc.QPointF):
        """Draw a point in the given image at position pos

        :param image: Target image
        :param pos: Position of the point
        :return: Rect surrounding the point with a minimal area
        """
        painter = qtg.QPainter(image)
        painter.setCompositionMode(self.compositionMode())
        painter.setPen(self.pen())
        painter.drawPoint(pos)
        return AdjustingRect().addPoint(pos, self.previewRadius()).toQRect()
