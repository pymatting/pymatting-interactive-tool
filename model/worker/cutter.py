#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from model.worker import BaseWorker
from model.util import cutout
from model.misc import Project, Image
from strings import cutoutErrorText


class Cutter(BaseWorker):
    finished = qtc.pyqtSignal(Image)

    def __init__(self):
        super(Cutter, self).__init__()
        self.cutoutForeground = True

    def toggleCutoutMode(self):
        self.cutoutForeground = not self.cutoutForeground
        return self.cutoutForeground

    @qtc.pyqtSlot(Project, bool)
    def cut(self, project: Project, nowait: bool):
        if self.running:
            try:
                cut = cutout(project.canvas(), project.alphaMatte(), self.cutoutForeground)
                if cut:
                    self.finished.emit(cut)
                    if nowait:
                        return cut
                return None
            except Exception as e:
                self.error.emit(cutoutErrorText, e)

    def moveToThread(self, thread: 'QThread') -> None:
        super(Cutter, self).moveToThread(thread)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False
