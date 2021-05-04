# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from model.enum import Status
from model.worker import BaseWorker
from model.misc import Project, Image
from strings import settingsFileName
import pickle


class Opener(BaseWorker):

    finished = qtc.pyqtSignal(Status)

    def open(self, path: str, project: Project):
        oldSettings = project.settings().copy()
        oldImages = project.images.copy()
        try:
            newSettings = self.openSettings(path)
            project.setSettings(newSettings)
            self.updateProjectImages(project, path, newSettings)
            project.setPath(path)
            self.finished.emit(Status.successful)
        except:
            project.setSettings(oldSettings)
            project.setImages(oldImages)
            self.finished.emit(Status.failed)

    def openSettings(self, path: str):
        settingsPath = qtc.QDir(path).filePath(settingsFileName)
        with open(settingsPath, "rb") as file:
            return pickle.load(file)

    def updateProjectImages(self, project, projectPath, newSettings):
        fileNames = newSettings["strings"]["fileName"]
        dir = qtc.QDir(projectPath)
        canvas = Image(dir.filePath(fileNames["canvas"]))
        if not canvas.isNull():
            newBackground = Image(
                dir.filePath(fileNames["newBackground"])
                if fileNames["newBackground"]
                else ""
            )
            alphaMatte = Image(dir.filePath(fileNames["alphaMatte"]))
            trimap = Image(dir.filePath(fileNames["trimap"]))
            project.changeImages(
                canvas, alphaMatte, trimap=trimap, newBackground=newBackground
            )
            if newBackground.isNull():
                project.cutoutRect().resetCenter()

        else:
            raise Exception()
