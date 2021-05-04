# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from strings import settingsFileName
from model.misc import Project
from model.worker import BaseWorker
from model.enum import Status
import pickle


class Saver(BaseWorker):
    finished = qtc.pyqtSignal(Status)

    def save(self, project):
        try:
            path = project.path()
            self.saveImages(path, project)
            self.saveSettings(path, project)
            project.setUnedited()
            self.finished.emit(Status.successful)
            return Status.successful
        except:
            self.finished.emit(Status.failed)
            return Status.failed

    def saveAs(self, path: str, project: Project):
        try:
            self.saveImages(path, project)
            self.saveSettings(path, project)
            project.setPath(path)
            project.setUnedited()
            self.finished.emit(Status.successful)
            return Status.successful
        except:
            self.finished.emit(Status.failed)
            return Status.failed

    def saveImages(self, path: str, project: Project):
        dir = qtc.QDir(path)
        quality = 100
        project.canvas().save(dir.filePath(project.canvasName()), quality=quality)
        project.alphaMatte().save(
            dir.filePath(project.alphaMatteName()), quality=quality
        )
        project.trimap().save(dir.filePath(project.trimapName()), quality=quality)
        project.cutout().save(dir.filePath(project.cutoutName()), quality=quality)
        if project.newBackground() and project.newBackgroundName():
            project.newBackground().save(
                dir.filePath(project.newBackgroundName()), quality=quality
            )

    def saveSettings(self, path: str, project: Project):
        dir = qtc.QDir(path)
        with open(dir.filePath(settingsFileName), "wb") as file:
            pickle.dump(project.settings(), file)
