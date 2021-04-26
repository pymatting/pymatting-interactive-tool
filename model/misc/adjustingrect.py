#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from math import inf


class AdjustingRect:
    """ An AdjustingRect is a growing rectangle that surrounds the points added to this. This class is implemented as a
    Builder class, which means, most functions in this class return the object itself to chain multiple method calls
    e.g:
    x...points
    0...fill character
    1...adjusting rect bounding area

    0 0 0 0 0 0 0                           0 0 0 0 0 0 0
    0 0 1 1 1 0 0    add another point      0 0 1 1 1 1 1
    0 0 1 x 1 0 0    ------------------->   0 0 1 x 0 0 1
    0 0 1 1 1 0 0                           0 0 1 0 0 0 1
    0 0 0 0 0 0 0                           0 0 1 0 0 x 1
    0 0 0 0 0 0 0                           0 0 1 1 1 1 1
    """

    def __init__(self, topLeft=None, maxHeight=None, maxWidth=None):
        if topLeft and maxHeight and maxWidth:
            self.min_x, self.min_y = topLeft
            self.max_x = self.min_x + maxWidth
            self.max_y = self.min_y + maxHeight
        else:
            self.min_x = self.min_y = -inf
            self.max_x = self.max_y = inf
        self.reset()

    @classmethod
    def fromRect(cls, rect: qtc.QRect):
        return cls((rect.topLeft().x(), rect.topLeft().y()), rect.height(), rect.width())

    def adjust(self, x0, y0, xn, ym):
        if x0 == xn or y0 == ym:
            return
        if x0 < self.x0:
            self.x0 = x0 if x0 > self.min_x else self.min_x
        if y0 < self.y0:
            self.y0 = y0 if y0 > self.min_y else self.min_y
        if xn > self.xn:
            self.xn = xn if xn < self.max_x else self.max_x
        if ym > self.ym:
            self.ym = ym if ym < self.max_y else self.max_y

    def addRect(self, rect):
        """ Adjust this instance with another rectangle
        :param rect: Another rectangle
        :return: self
        """
        try:
            rect = rect.normalized()
            x0 = rect.topLeft().x()
            y0 = rect.topLeft().y()
            xn = x0 + rect.width()
            ym = y0 + rect.height()
            self.adjust(x0, y0, xn, ym)
        except:
            pass
        return self

    def addPoint(self, point: qtc.QPointF, penRadius: float = 1):
        """ Adjust this instance with a point

        :param point: A point
        :param penRadius: The current pen radius
        :return: self
        """

        if penRadius >= 1:
            rect = qtc.QRectF(point.x() - penRadius, point.y() - penRadius, penRadius * 2, penRadius * 2)
            self.addRect(rect)
        return self

    def addPoints(self, points, penRadius: float = 1):
        for point in points:
            self.addPoint(point, penRadius)
        return self

    def boundingCoordinates(self):
        """ Return the bounding corrdinates of this instance
        :return: (topLeftX, topLefty, bottomLeftX, bottomLeftY)
        """
        return self.x0, self.y0, self.xn, self.ym

    def toQRectF(self):
        width = self.xn - self.x0
        height = self.ym - self.y0
        if width >= 0 and height >= 0:
            return qtc.QRectF(self.x0, self.y0, width, height)
        else:
            return None

    def toQRect(self, normalized=False):
        rectf = self.toQRectF()
        if rectf:
            return rectf.toAlignedRect() if not normalized else rectf.toAlignedRect().normalized()
        else:
            return None

    def reset(self):
        self.x0 = self.max_x
        self.y0 = self.max_y
        self.xn = self.min_x
        self.ym = self.min_y
