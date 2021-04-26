#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from model.misc import AdjustingRect, Image


class Screenshot(qtc.QObject):
    """ This class is used for Undo-Redo.

    """

    def __init__(self, image: Image):
        super(Screenshot, self).__init__()
        self.images = dict(before=image.copy(), after=image)
        self.adjustingRect = AdjustingRect(image.rect())

    @classmethod
    def fromImages(cls, before: Image, after: Image, rectf: qtc.QRectF = None):
        screenshot = cls(before)
        screenshot.setAfter(after)
        if rectf:
            screenshot.addRect(rectf)
        return screenshot

    ####################################################################################################################
    #                                                                                                                  #
    #                                                GETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def rectF(self):
        return self.adjustingRect.toQRectF()

    def rect(self):
        return self.adjustingRect.toQRect()

    def before(self):
        return self.images["before"]

    def after(self):
        return self.images["after"]

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def setBefore(self, image: Image):
        self.images["before"] = image

    def setAfter(self, image: Image):
        self.images["after"] = image

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def addRect(self, rect: qtc.QRectF):
        self.adjustingRect.addRect(rect)

    def take(self):
        rect = self.adjustingRect.toQRect()
        if rect:
            self.setBefore(self.before().copy(rect))
            self.setAfter(self.after().copy(rect))
            return True
        return False
