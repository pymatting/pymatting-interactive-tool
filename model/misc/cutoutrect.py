# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from numpy import sign


class CutoutRect(qtc.QObject):
    """This is a class which wraps some functionalities for displaying the foreground object.
    This rect can also transform itself for display purposes. It can rotate, scale, translate and mirror itself. Its
    transform() function then is used to transform a QPainters coordinate system.
    """

    changed = qtc.pyqtSignal()

    def __init__(self, rect: qtc.QRectF, scale=(1, 1), angle=0):
        super(CutoutRect, self).__init__()
        self.__rect = rect
        self.__scale = scale
        self.__angle = angle
        self.__aspectRatio = rect.height() / rect.width()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def setRect(self, rect: qtc.QRect):
        self.__rect = rect
        self.changed.emit()

    def setScale(self, scale: tuple):
        self.__scale = scale
        self.changed.emit()

    def setAngle(self, angle: int):
        self.__angle = angle
        self.changed.emit()

    def setWidth(self, width: float, keepAspectRatio: bool = True):
        width = 1 if width <= 0 else width
        x, y = self.scale()
        sx = sign(x)
        x = sx * (width / self.rect().width())
        self.setScale((x, y))
        if keepAspectRatio:
            newHeight = int(self.aspectRatio() * width)
            newHeight = 1 if newHeight <= 0 else newHeight
            self.setHeight(newHeight, False)
        self.changed.emit()

    def setHeight(self, height: float, keepAspectRatio: bool = True):
        height = 1 if height <= 0 else height
        x, y = self.scale()
        sy = sign(y)
        y = sy * (height / self.rect().height())
        self.setScale((x, y))
        if keepAspectRatio:
            newWidth = int((1 / self.aspectRatio()) * height)
            newWidth = 1 if newWidth <= 0 else newWidth
            self.setWidth(newWidth, False)
        self.changed.emit()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                GETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def settings(self):
        return dict(rect=self.rect(), angle=self.angle(), scale=self.scale())

    def rect(self):
        return self.__rect

    def polygonF(self):
        return qtg.QPolygonF(self.rect())

    def scale(self):
        return self.__scale

    def angle(self):
        return self.__angle

    def aspectRatio(self):
        return self.__aspectRatio

    def height(self):
        return round(abs(self.scale()[1] * self.rect().height()))

    def width(self):
        return round(abs(self.scale()[0] * self.rect().width()))

    def center(self):
        return self.rect().center()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def translate(self, dx, dy):
        self.rect().translate(dx, dy)
        self.changed.emit()

    def moveCenter(self, center: qtc.QPointF):
        self.rect().moveCenter(center)
        self.changed.emit()

    def transform(self):
        """Builds a QTransform() with the given scale, transformation, rotation and mirroring. This
        can be used to transform a QPainters coordinate system.
        :return: QTransform() object which has been scaled, rotated, transformed and mirror
        """
        transform = qtg.QTransform()
        center = self.rect().center()
        transform.translate(center.x(), center.y())
        transform.scale(*self.scale())
        transform.rotate(self.angle())
        transform.translate(-center.x(), -center.y())
        return transform

    def reset(self):
        self.setAngle(0)
        self.setScale((1, 1))
        self.resetCenter()

    def resetCenter(self):
        self.moveCenter(
            qtc.QPointF(self.rect().width() // 2, self.rect().height() // 2)
        )

    def mirror(self, orientation: qtc.Qt.Orientation):
        if orientation == qtc.Qt.Vertical:
            x, y = self.scale()
            x *= -1
        elif orientation == qtc.Qt.Horizontal:
            x, y = self.scale()
            y *= -1
        else:
            x, y = self.scale()
        self.setScale((x, y))

    def mirrorVertical(self):
        self.mirror(qtc.Qt.Vertical)

    def mirrorHorizontal(self):
        self.mirror(qtc.Qt.Horizontal)

    def contains(self, point: qtc.QPointF):
        return (
            self.transform()
            .map(self.polygonF())
            .containsPoint(point, qtc.Qt.OddEvenFill)
        )
