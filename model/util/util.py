#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from model.misc import AdjustingRect, Image
from model.enum import Color
from numba import njit
from numba.core.types import b1, i8, f8, UniTuple, u1
import numpy as np
import config.config
import qimage2ndarray


def showWarning(text: str, exception: Exception = None, title="Warning", parent=None):
    message = f"{text}\nException: {exception}" if exception else text
    qtw.QMessageBox.warning(parent, title, message)


def matchScale(target: Image, source: Image):
    if target and source and target.size() != source.size():
        target = target.scaled(source.width(), source.height())
    return target


def makeQThread(worker, threadName):
    """ Moves the worker object inside a QThread with the given threadName

    :param worker: Object that should be moved inside another thread
    :param threadName: name of the thread
    :return: object and its thread
    """
    thread = qtc.QThread()
    thread.setObjectName(f"Thread: {threadName}")
    worker.moveToThread(thread)
    thread.start()
    return worker, thread


def cutout(image: Image, alphaMatte: Image, foreground: bool = True):
    """ Cuts out the area inside the image defined by the alphaMatte

    :param image: Target image
    :param alphaMatte: Alpha-Matte
    :param foreground: Inverts the Alpha-Matte if foreground is false, i.e. cuts out the background
    :return:
    """
    if foreground:
        return __cutout(image.rgbView(), alphaMatte.byteView())
    else:
        return __cutout(image.rgbView(), 255 - alphaMatte.byteView())


def cutoutForeground(image: Image, alphaMatte: Image):
    return cutout(image, alphaMatte, True)


def cutoutBackground(image: Image, alphaMatte: Image):
    return cutout(image, alphaMatte, False)


def __cutout(image: np.ndarray, alphaMatte: np.ndarray) -> Image:
    try:
        return ndarrayToImage(np.concatenate([image, alphaMatte], axis=2))
    except:
        pass


def grayToImage(array: np.ndarray) -> Image:
    return Image(qimage2ndarray.gray2qimage(array))


def ndarrayToImage(array: np.ndarray, normalized=False) -> Image:
    return Image(qimage2ndarray.array2qimage(array * 255) if normalized else qimage2ndarray.array2qimage(array))


def imageToTrimap(image: Image) -> Image:
    try:
        rgb = image.rgbView()
        is_bg = rgb[:, :, 0] == 255
        is_fg = rgb[:, :, 1] == 255
        trimap_np = np.full((image.height(), image.width()), 160, dtype=np.uint8)
        trimap_np[is_fg] = 255
        trimap_np[is_bg] = 0
        return Image(grayToImage(trimap_np))
    except Exception as e:
        print(e)


def trimapToRgba(trimap: Image) -> Image:
    if trimap.Format != Image.Format_Grayscale8:
        trimap = trimap.convertToFormat(Image.Format_Grayscale8)
    trimap_np = trimap.rawView()
    rgba = np.full((trimap_np.shape[0], trimap_np.shape[1], 4), 0)
    rgba[trimap_np == 255] = [*Color.lightGreen.rgba()]
    rgba[trimap_np == 0] = [*Color.lightRed.rgba()]
    return ndarrayToImage(rgba)


def calculateDiffRect(img1: Image, img2: Image = None):
    """ Calculates the coordinates of the rectangle that surrounds the difference of two images with a minimal area

    :param img1: Image 1
    :param img2: Image 2
    :return: (Top left X, Top Left Y, Bottom Right X, Bottom Right Y)
    """
    img1ByteView = img1.byteView()
    if img2:
        img2ByteView = img2.byteView()
    else:
        img2ByteView = np.zeros_like(img1ByteView)
    boolArray = np.any(img1ByteView != img2ByteView, axis=2)
    return findBoundingRect(boolArray)


def findBoundingRect(boolArray):
    """ Calculates coordinates of rectangle that surrounds true values inside boolArray with a minimal area

    :param boolArray: Boolean array with True and False
    :return: (Top left X, Top Left Y, Bottom Right X, Bottom Right Y)
    """
    x0, y0, xn, yn = find_bounding_rect_(boolArray)
    if x0 >= 0 and y0 >= 0 and xn >= 0 and yn >= 0:
        rect = AdjustingRect((0, 0), *boolArray.shape)
        rect.adjust(x0, y0, xn, yn)
        return rect.toQRectF()
    return None


@njit(UniTuple(i8, 4)(b1[:, :]), nogil=config.config.nogil, cache=config.config.cache)
def find_bounding_rect_(boolArray):
    indexedArray = np.where(boolArray)
    if indexedArray[0].size and indexedArray[1].size:
        return np.min(indexedArray[1]), np.min(indexedArray[0]), np.max(indexedArray[1]) + 1, np.max(
            indexedArray[0]) + 1
    return -1, -1, -1, -1
