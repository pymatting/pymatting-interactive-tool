#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5.QtCore import QPoint, QPointF, pyqtSignal, pyqtSlot, QRectF
from PyQt5.QtGui import QColor
from model.enum import DrawMode, Color
from model.worker import FloodFiller
from model.drawdevice import DrawDevice
from model.util import makeQThread
from model.misc import Image


class Paintbucket(DrawDevice):
    """
    Wrapper class that performs the Floodfill-Algorithm
    """

    """ Internal signal used to communicate with the FloodFill-Worker
    Signal(Reference Image, Image to be filled, NewColor, StartPos, Tolerance)
    """
    start = pyqtSignal(object, object, QColor, QPoint, int)

    """ Signal when FloodFill-Worker finished its work
    Signal(Copy of Image before it was filled, Area that changed)
    """
    filled = pyqtSignal(Image, QRectF)

    def __init__(self):
        super(Paintbucket, self).__init__()
        self.setTolerance(20)
        self.setupWorker()
        self.setupConnections()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETUP                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def setupConnections(self):
        self.floodFiller.finished.connect(self.filled.emit)
        self.start.connect(self.floodFiller.fill)

    def setupWorker(self):
        self.floodFiller, self.floodFillerThread = makeQThread(FloodFiller(), "Floodfiller")

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def setTolerance(self, tol: int):
        self.settings["tolerance"] = tol

    ####################################################################################################################
    #                                                                                                                  #
    #                                                GETTER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def tolerance(self):
        return self.settings["tolerance"]

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SLOTS                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def fill(self, canvas: Image, trimapPreview: Image, startPos: QPointF, nowait=False, tolerance=None):
        """ Fill trimapPreview based on pixels in canvas image

        :param canvas: Reference Image where the neighbouring pixels are searched
        :param trimapPreview: Image to be filled
        :param startPos: Start position for floodfill
        :param nowait: Execute in seperate thread if nowait is false, else block until finished
        :param tolerance: Floodfill tolerance
        :return: If nowait is True, returns a copy of the image before the change aswell as the area that was filled.
        If nowait is False, the result is emitted with the filled(..) signal. This function then returns None
        """
        param = (canvas, trimapPreview, self.color(), startPos.toPoint(), self.tolerance() if tolerance is None else tolerance)
        if nowait:
            return self.floodFiller.fill(*param)
        else:
            self.start.emit(*param)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def close(self):
        self.floodFiller.finished.disconnect()
        self.start.disconnect()
        self.floodFillerThread.quit()
        self.floodFillerThread.wait()
