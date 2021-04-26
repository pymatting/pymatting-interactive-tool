#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from model.worker import BaseWorker
from model.misc import Project
from strings import croppingFailed


class Cropper(BaseWorker):

    @qtc.pyqtSlot(Project, qtc.QRect)
    def crop(self, project, rect):
        """ Crops the images of a project

        :param project: Project
        :param rect: Crop Rectangle
        :return: None
        """
        try:
            oldCanvas = project.canvas()
            oldAlphaMatte = project.alphaMatte()
            oldTrimapPreview = project.trimapPreview()
            try:
                canvas = project.canvas().copy(rect)
                alphaMatte = project.alphaMatte().copy(rect)
                trimapPreview = project.trimapPreview().copy(rect)
                project.changeImages(canvas, alphaMatte, trimapPreview=trimapPreview, resetCutout=True, edited=True)
            except Exception as e:
                project.changeImages(oldCanvas, oldAlphaMatte, trimapPreview=oldTrimapPreview, resetCutout=False, edited=False)
                self.error.emit(croppingFailed, e)
        except Exception as e:
            self.error.emit(croppingFailed, e)
