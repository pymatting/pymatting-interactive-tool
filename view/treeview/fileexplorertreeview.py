# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from view.graphicsview import ImageViewer
from strings import settingsFileName


class FileExplorerTreeView(qtw.QTreeView):
    fileRenamed = qtc.pyqtSignal(str, str, str)  # path, oldName, newName
    requestOpenNewProject = qtc.pyqtSignal(str)

    def __init__(self, project, parent=None):
        super(FileExplorerTreeView, self).__init__(parent=parent)
        self.imageViews = []
        self.editing = False
        self.setSortingEnabled(True)
        self.project = project
        self.setSelectionMode(qtw.QAbstractItemView.ExtendedSelection)
        self.setupConnection()

    def keyPressEvent(self, event: qtg.QKeyEvent) -> None:
        if event.key() == qtc.Qt.Key_Return and not self.editing:
            indices = self.selectedIndexes()
            paths = {self.model().filePath(index) for index in indices}
            imageViewer = ImageViewer(paths)
            self.imageViews.append(imageViewer)
            imageViewer.show()

        elif event.key() == qtc.Qt.Key_Delete and not self.editing:
            indices = self.selectedIndexes()
            answer = qtw.QMessageBox.question(
                self, "Delete?", "Do you want to delete the selected files?"
            )
            if answer == qtw.QMessageBox.Yes:
                for index in indices:
                    try:
                        self.model().remove(index)
                    except:
                        pass

    def edit(
        self,
        index: qtc.QModelIndex,
        trigger: qtw.QAbstractItemView.EditTrigger,
        event: qtg.QMouseEvent,
    ) -> bool:
        self.editing = False
        if self.model():
            if self.model().data(index) == settingsFileName:
                if trigger == qtw.QAbstractItemView.DoubleClicked:
                    answer = qtw.QMessageBox.question(
                        self, "Open?", "Do you want to open a new project?"
                    )
                    if answer == qtw.QMessageBox.Yes:
                        path = (
                            qtc.QFileInfo(self.model().filePath(index))
                            .dir()
                            .absolutePath()
                        )
                        self.requestOpenNewProject.emit(path)
                return super(FileExplorerTreeView, self).edit(
                    index, qtw.QAbstractItemView.SelectedClicked, event
                )
            elif trigger == qtw.QAbstractItemView.DoubleClicked:
                imageViewer = ImageViewer([self.model().filePath(index)])
                imageViewer.show()
                self.imageViews.append(imageViewer)
                return super(FileExplorerTreeView, self).edit(
                    index, qtw.QAbstractItemView.SelectedClicked, event
                )
            elif trigger == qtw.QAbstractItemView.SelectedClicked:
                path = self.model().filePath(index)
                if qtc.QFileInfo(path).isFile():
                    path = qtc.QFileInfo(path).dir()

                if (
                    path == self.project.path()
                    or qtc.QDir(path).dirName() == self.project.title()
                ):
                    self.editing = True
                    return super(FileExplorerTreeView, self).edit(
                        index, qtw.QAbstractItemView.DoubleClicked, event
                    )
            else:
                return super(FileExplorerTreeView, self).edit(index, trigger, event)
        return super(FileExplorerTreeView, self).edit(index, trigger, event)

    def createModel(self, rootPath):
        fileSystemModel = qtw.QFileSystemModel()
        fileSystemModel.setFilter(
            qtc.QDir.NoDot | qtc.QDir.NoDotDot | qtc.QDir.Files | qtc.QDir.Dirs
        )
        fileSystemModel.setReadOnly(False)
        fileSystemModel.setRootPath(rootPath)
        fileSystemModel.fileRenamed.connect(self.fileRenamed.emit)
        return fileSystemModel

    def setupConnection(self):
        self.project.pathChanged.connect(self.setRootPath)

    def setRootPath(self, path: str):
        if path:
            self.setModel(self.createModel(path))
            dir = qtc.QDir(path)
            dir.cdUp()
            self.setRootIndex(self.model().index(dir.absolutePath()))
        else:
            self.setModel(None)

    def close(self) -> bool:
        for imageView in self.imageViews:
            imageView.deleteLater()
        return super(FileExplorerTreeView, self).close()
