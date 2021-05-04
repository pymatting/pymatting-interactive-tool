# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from model.misc import Image


class BaseScene(qtw.QGraphicsScene):
    def __init__(self, project, parent=None):
        super(BaseScene, self).__init__(parent=parent)
        if project:
            self.project = project
            self.updateSceneRect(self.project.canvas())

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def updateSceneRect(self, image: Image):
        """Updates the scene rect to have a small margin on each side

        :param image: Image that needs to be displayed
        :return: None
        """
        dx = image.width() * 0.02
        self.setSceneRect(qtc.QRectF(image.rect()).adjusted(-dx, -dx, dx, dx))
        self.invalidate()

    def invalidateForeground(self, rect: qtc.QRectF = None):
        if rect:
            self.invalidate(rect=rect, layers=qtw.QGraphicsScene.ForegroundLayer)
        else:
            self.invalidate(layers=qtw.QGraphicsScene.ForegroundLayer)

    def leftButtonPressed(self, event: qtw.QGraphicsSceneMouseEvent):
        return event.button() == qtc.Qt.LeftButton

    def leftButtonMoved(self, event: qtw.QGraphicsSceneMouseEvent):
        return event.buttons() & qtc.Qt.LeftButton

    def leftButtonReleased(self, event: qtw.QGraphicsSceneMouseEvent):
        return event.button() == qtc.Qt.LeftButton
