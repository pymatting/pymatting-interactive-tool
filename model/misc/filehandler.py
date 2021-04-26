#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from model.misc import Project, Image
from model.util import showWarning, makeQThread
from model.worker import Saver, Opener
from model.enum import Status

from view.messagebox import MessageBoxOverwrite, SaveMessageBox
from view.dialog import NewProjectDialog
from strings import saveAsTitle, overwriteMessageText, saveErrorText, openTitle, settingsFileName


class FileHandler(qtc.QObject):
    """ Implements functionalities for saving, opening and creating a new project.

    """

    finished = qtc.pyqtSignal(str)
    error = qtc.pyqtSignal(str)

    # Signal(New path to save the project at, Project) and Signal(project). This signal has two different signals in one
    requestSaving = qtc.pyqtSignal([str, Project], [Project])
    # signal(Path to project, current project)
    requestOpening = qtc.pyqtSignal(str, Project)

    def __init__(self, project: Project, parent=None):
        super(FileHandler, self).__init__(parent=parent)
        self.project = project
        self.setupWorkers()
        self.setupConnections()
        self.reduceColorBleeding = False

    def setupWorkers(self):
        self.saver, self.saverThread = makeQThread(Saver(), "Saver")
        self.opener, self.openerThread = makeQThread(Opener(), "Opener")

    def setupConnections(self):
        self.requestSaving[Project].connect(self.saver.save)
        self.requestSaving[str, Project].connect(self.saver.saveAs)
        self.requestOpening.connect(self.opener.open)
        self.opener.finished.connect(self.onOpen)
        self.saver.finished.connect(self.onSave)

    def new(self, filePath=None):
        """ Creats a new project.

        :param filePath: Image path. If not specified, a FileDialog is shown to pick a file
        :return: None
        """
        maybeSaveStatus = self.maybeSave()
        if maybeSaveStatus.isSuccessful():
            if not filePath:
                filePath, _ = qtw.QFileDialog.getOpenFileName(caption="New Project",
                                                              filter='Image (*.png *.jpg *.jpeg) ;; All Files (*)',
                                                              initialFilter='Image (*.png *.jpg *.jpeg)')
            if filePath and qtc.QFileInfo(filePath).isFile():
                accepted, projectName = NewProjectDialog(qtc.QFileInfo(filePath).fileName().split(".")[0]).execute()
                if accepted:
                    canvas = Image(filePath)
                    if not canvas.isNull():
                        self.project.new(canvas, projectName)
                        self.finished.emit("New project created!")
                    else:
                        self.error.emit("Creating a new project failed!")
                else:
                    self.finished.emit("New project creation canceled!")
            else:
                self.finished.emit("Creating a new project has been canceled!")

    def open(self, path: str = None):
        """ Open a project.

        :param path: Open project at specified path. If path is None, show a FileDialog
        :return: None
        """
        status = self.maybeSave()
        if status.isSuccessful():
            if not path:
                path = qtw.QFileDialog.getExistingDirectory(caption=openTitle)
            if path:
                if qtc.QFileInfo(path).isDir() and qtc.QFileInfo(qtc.QDir(path).filePath(settingsFileName)).isFile():
                    self.requestOpening.emit(path, self.project)
                else:
                    self.error.emit("Opening failed!")
            else:
                self.finished.emit("Opening canceled!")

    def onOpen(self, status: Status):
        if status.isSuccessful():
            self.finished.emit("Project opened!")
            self.project.setUnedited()
        elif status.isAborted():
            self.finished.emit("Opening project canceled!")
        else:
            self.error.emit("Opening project failed!")

    def save(self, nowait=False):
        """ Save the Project. If the project has not been saved yet, execute saveAs instead.

        :param nowait: If nowait is true, block the GUI Thread, else execute in a Saver-Thread
        :return: None if save is execute, else status of saveAs
        """

        path = self.project.path()
        if path and qtc.QFileInfo(path).isDir() and qtc.QFileInfo(path).isWritable():
            if nowait:
                return self.saver.save(self.project)
            else:
                self.requestSaving[Project].emit(self.project)
        else:
            return self.saveAs(nowait)

    @qtc.pyqtSlot()
    def saveAs(self, nowait=False):
        """ Saves the project to a folder. Also shows a FileDialog

        :param nowait: Block GUI-Thread if nowait is true, else execute in Saver-Thread
        :return: Status of this action
        """
        path = qtw.QFileDialog.getExistingDirectory(caption=saveAsTitle)
        if path:
            if qtc.QFileInfo(path).isDir() and qtc.QFileInfo(path).isWritable():
                status, projectFolderPath = self.createProjectFolder(path)
                if status.isSuccessful():
                    if nowait:
                        return self.saver.saveAs(projectFolderPath, self.project)
                    else:
                        self.requestSaving[str, Project].emit(projectFolderPath, self.project)
                elif status.isAborted():
                    self.finished.emit("Saving canceled!")
                elif status.isFailed():
                    self.error.emit(saveErrorText)
                return status
            else:
                self.error.emit(saveErrorText)
                return Status.failed
        else:
            self.finished.emit("Saving canceled!")
            return Status.aborted

    def maybeSave(self):
        """ Prompts a dialog asking if the user wants to save before continuing their action if the current project
        is edited and has not been saved yet.

        :return: Status
        """

        if self.project.isEdited():
            response = SaveMessageBox().exec()
            if response == SaveMessageBox.Save:
                return self.save(nowait=True)
            elif response == SaveMessageBox.Cancel:
                self.finished.emit("Saving canceled!")
                return Status.aborted
        return Status.successful

    def onSave(self, status: Status):
        if status.isSuccessful():
            self.finished.emit("Saved!")
        elif status.isAborted():
            self.finished.emit("Saving canceled!")
        else:
            self.error.emit("Saving failed!")

    def createProjectFolder(self, path: str):
        """ Creates the project folder.
        If the folder already exists, prompts a dialog asking the user if he/she wants to overwrite it.

        :param path: Path where the folder should be created
        :return: Status
        """
        folderName = self.project.title()
        dir = qtc.QDir(path)
        if dir.mkdir(folderName) and dir.cd(folderName):
            return Status.successful, dir.absolutePath()
        elif dir.cd(folderName):
            response = MessageBoxOverwrite(overwriteMessageText.format(folderName, path)).exec()
            if response == MessageBoxOverwrite.Overwrite:
                return Status.successful, dir.absolutePath()
            return Status.aborted, None
        return Status.failed, None

    def updateSettingsFile(self):
        """ Updates the settings file

        :return: None
        """
        if self.project.path() and qtc.QFileInfo(self.project.path()).isDir():
            self.saver.saveSettings(self.project.path(), self.project)

    def close(self):
        self.requestSaving.disconnect()
        self.requestOpening.disconnect()
        self.saver.finished.disconnect()
        self.opener.finished.disconnect()
        self.saverThread.quit()
        self.saverThread.wait()
        self.openerThread.quit()
        self.openerThread.wait()
