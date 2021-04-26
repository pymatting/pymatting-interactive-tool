#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from model.worker import BaseWorker
from model.misc import Project
from strings import scalingFailed


class Scaler(BaseWorker):

    def scale(self, project, newWidth, newHeight, keepAspectRatio):
        try:
            transformationMode = qtc.Qt.SmoothTransformation
            aspectRatioMode = qtc.Qt.KeepAspectRatio if keepAspectRatio else qtc.Qt.IgnoreAspectRatio
            if newWidth >= 1 and newHeight >= 1:
                canvas = project.canvas().scaled(newWidth, newHeight, aspectRatioMode, transformationMode)
                alphaMatte = project.alphaMatte().scaled(newWidth, newHeight, aspectRatioMode, transformationMode)
                trimapPreview = project.trimapPreview().scaled(newWidth, newHeight, aspectRatioMode, transformationMode)
                project.changeImages(canvas, alphaMatte, trimapPreview=trimapPreview, resetCutout=True, edited=True, aspectRatioChanged=False)
        except Exception as e:
            self.error.emit(scalingFailed, e)
