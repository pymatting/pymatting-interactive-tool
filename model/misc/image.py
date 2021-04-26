#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from qimage2ndarray import byte_view, rgb_view, raw_view, alpha_view


class Image(qtg.QImage):
    """ Wraps the QImage class providing functionalities to generate views into the memory if an instance

    """

    @classmethod
    def empty(cls, size: qtc.QSize, format=qtg.QImage.Format_ARGB32):
        return Image.full(size, qtc.Qt.transparent, format)

    @classmethod
    def full(cls, size:qtc.QSize, color, format=qtg.QImage.Format_ARGB32):
        image = qtg.QImage(size, format)
        image.fill(color)
        return Image(image)

    def clear(self):
        self.fill(qtc.Qt.transparent)

    def __view(self, func, key: str, normalized=False):
        try:
            return self.views_norm[key] if normalized else self.views[key]
        except:
            if not hasattr(self, "views") or not hasattr(self, "views_norm"):
                self.views = {}
                self.views_norm = {}
            view = func(self) / 255.0 if normalized else func(self)
            if normalized:
                self.views_norm[key] = view
            else:
                self.views[key] = view
            return view

    def rgbView(self, normalized=False):
        return self.__view(rgb_view, "rgb", normalized)

    def byteView(self, normalized=False):
        """ Creates a byte view of an image instance

        :param normalized: values are between 0 and 1 if normalized is true
        :return: Returns a byte view. Colors are in order Blue, Green, Red, Alpha for RGBA Images
        """
        return self.__view(byte_view, "byte", normalized)

    def alphaView(self, normalized=False):
        return self.__view(alpha_view, "alpha", normalized)

    def rawView(self, normalized=False):
        return self.__view(raw_view, "raw", normalized)

    def copy(self, rect: qtc.QRect = None) -> 'Image':
        if rect:
            cp = super(Image, self).copy(rect)
        else:
            cp = super(Image, self).copy()
        return Image(cp)

    def convertToFormat(self, format: qtg.QImage.Format, flags=None) -> 'Image':
        if flags:
            result = super(Image, self).convertToFormat(format, flags)
        else:
            result = super(Image, self).convertToFormat(format)
        return Image(result)

    def scaled(self, width: int, height: int, aspectRatioMode: qtc.Qt.AspectRatioMode = None,
               transformMode: qtc.Qt.TransformationMode = None) -> 'Image':
        if aspectRatioMode and transformMode:
            result = super(Image, self).scaled(width, height, aspectRatioMode, transformMode)
        elif aspectRatioMode:
            result = super(Image, self).scaled(width, height, aspectRatioMode)
        elif transformMode:
            result = super(Image, self).scaled(width, height, transformMode=transformMode)
        else:
            result = super(Image, self).scaled(width, height)
        return Image(result)

    def transformed(self, matrix: qtg.QTransform, mode: qtc.Qt.TransformationMode = None) -> 'Image':
        if mode:
            trans = super(Image, self).transformed(matrix, mode)
        else:
            trans = super(Image, self).transformed(matrix)
        return Image(trans)
