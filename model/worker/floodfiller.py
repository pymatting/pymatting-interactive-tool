#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from model.util import findBoundingRect
from model.misc import Image
from model.worker import BaseWorker
from strings import floodFillErrorText
from numba import njit
from numba.core.types import b1, i8, f8, UniTuple, u1
from numba.typed import List
import numpy as np
import config.config


class FloodFiller(BaseWorker):
    finished = qtc.pyqtSignal(Image, qtc.QRectF)

    @qtc.pyqtSlot(Image, Image, qtg.QColor, qtc.QPoint, int)
    def fill(self, canvas: Image, trimapPreview: Image, new_color: qtg.QColor, startPos: qtc.QPoint,
             tol: int):
        """ Performs floodfill algorithm in trimapPreview based on pixels in canvas starting at startPos and sets the
        colors to new_color

        :param canvas: Reference Image
        :param trimapPreview: Image that will be filled
        :param new_color: Fillcolor
        :param startPos: Starting position for floodfill algorithm
        :param tol: Tolerance for floodfill algorithm
        :return: Copy of image before it was changed aswell as the bounding rect of the area that was filled. Also emits
        signal finished with the return value described before.
        """
        try:
            before = trimapPreview.copy()
            x_start, y_start = startPos.x(), startPos.y()
            canvasView = canvas.byteView()
            trimapPreviewView = trimapPreview.byteView()
            rect = canvas.rect()
            height, width, depth = canvasView.shape
            if rect.contains(qtc.QPoint(x_start, y_start)):
                # colors needs to be in bgra form not argb
                new_color = np.array([new_color.blue(), new_color.green(), new_color.red(), new_color.alpha()])
                mask = fill_(canvasView, (x_start, y_start), (width, height, depth), tol).astype(bool)
                trimapPreviewView[mask] = new_color
                rect = findBoundingRect(mask)
                self.finished.emit(before, rect)
                return before, rect
        except Exception as e:
            self.error.emit(floodFillErrorText, e)
            return None, None


@njit(b1(i8, i8, i8, i8, f8[:, :]), nogil=config.config.nogil, cache=config.config.cache)
def isValid_(y, x, maxWidth, maxHeight, visited):
    return x >= 0 and x < maxWidth and y >= 0 and y < maxHeight and visited[y, x] == 0


@njit(f8[:, :](u1[:, :, :], UniTuple(i8, 2), UniTuple(i8, 3), i8), nogil=config.config.nogil, cache=config.config.cache)
def fill_(canvasView, startPos, shape, tolerance):
    """ Performs the actual algorithm

    :param canvasView: Memory view of canvas
    :param startPos: starting position
    :param shape: shape of canvasView
    :param tolerance: Tolerance value for floodfill algorithm
    :return: boolean mask of pixels that need to be filled
    """
    width, height, depth = shape
    x_start, y_start = startPos

    coloringMask = np.zeros((height, width))
    visited = np.zeros((height, width), dtype=np.float64)
    visited[y_start, x_start] = 1
    stack = List()
    stack.append((y_start, x_start))

    # Pixel colors are in BGRA order because PyQt5 likes that format for whatever reason
    start_r = canvasView[y_start, x_start, 2]
    start_g = canvasView[y_start, x_start, 1]
    start_b = canvasView[y_start, x_start, 0]
    # Maximum distance would be around 442, but since squared distances are calculated for efficiency, tolerance
    # needs to be squared
    squaredTolerance = tolerance ** 2
    while stack:
        y, x = stack.pop()
        # calculate difference vector
        r = canvasView[y, x, 2] - start_r
        g = canvasView[y, x, 1] - start_g
        b = canvasView[y, x, 0] - start_b
        # calculate squared distance
        squaredDistance = r * r + g * g + b * b

        if squaredDistance <= squaredTolerance:
            coloringMask[y, x] = True
            down = (y + 1, x)
            if isValid_(*down, width, height, visited):
                stack.append(down)
                visited[y + 1, x] = 1
            right = (y, x + 1)
            if isValid_(*right, width, height, visited):
                stack.append(right)
                visited[y, x + 1] = 1
            up = (y - 1, x)
            if isValid_(*up, width, height, visited):
                stack.append(up)
                visited[y - 1, x] = 1
            left = (y, x - 1)
            if isValid_(*left, width, height, visited):
                stack.append(left)
                visited[y, x - 1] = 1
    return coloringMask
