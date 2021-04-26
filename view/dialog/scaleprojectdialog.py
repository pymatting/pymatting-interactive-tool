#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from strings import scaleSettingsTitle
from view.widget import FormWidget
from model.misc import Project


class ScaleProjectDialog(qtw.QDialog):

    requestScale = qtc.pyqtSignal(Project, int, int, bool)
    

    def __init__(self, project: Project, parent=None):
        super(ScaleProjectDialog, self).__init__(parent=parent)
        self.project = project
        self.originalWidth = project.canvasWidth()
        self.originalHeight = project.canvasHeight()
        self.aspectRatio = self.originalHeight / self.originalWidth
        self.lastChanged = "width"
        self.setLayout(qtw.QVBoxLayout(self))
        self.setWindowTitle(scaleSettingsTitle)
        self.setupWidgets()
        self.setupButtons()
        self.setupConnections()

    def setupWidgets(self):
        self.formWidget = FormWidget()
        self.widthSpinBox = self.formWidget.addSpinBox("Width", 1, 10000, self.originalWidth, wrapping=False)
        self.heightSpinBox = self.formWidget.addSpinBox("Height", 1, 10000, self.originalHeight, wrapping=False)
        self.keepAspectRatioCheckBox = self.formWidget.addCheckBox("Keep Aspect Ratio", checked=True)
        self.layout().addWidget(self.formWidget)

    def setupConnections(self):
        self.widthSpinBox.valueChanged.connect(self.onWidthChanged)
        self.heightSpinBox.valueChanged.connect(self.onHeightChanged)
        self.keepAspectRatioCheckBox.clicked.connect(self.onKeepAspectRatioChecked)
        self.buttonBox.button(qtw.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.buttonBox.button(qtw.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.project.aspectRatioChanged.connect(self.updateAspectRatio)

    def onWidthChanged(self, newWidth):
        self.lastChanged = "width"
        if self.keepAspectRatioCheckBox.isChecked():
            newWidth = int(self.aspectRatio * newWidth)
            newWidth = 1 if newWidth <= 0 else newWidth
            self.heightSpinBox.blockSignals(True)
            self.heightSpinBox.setValue(newWidth)
            self.heightSpinBox.blockSignals(False)


    def onHeightChanged(self, newHeight):
        self.lastChanged = "height"
        if self.keepAspectRatioCheckBox.isChecked():
            newHeight = int((1 / self.aspectRatio) * newHeight)
            newHeight = 1 if newHeight <= 0 else newHeight
            self.widthSpinBox.blockSignals(True)
            self.widthSpinBox.setValue(newHeight)
            self.widthSpinBox.blockSignals(False)


    def onKeepAspectRatioChecked(self, checked):
        if checked:
            if self.lastChanged == "width":
                self.onWidthChanged(self.widthSpinBox.value())
            else:
                self.onHeightChanged(self.heightSpinBox.value())


    def setupButtons(self):
        self.buttonBox = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Cancel | qtw.QDialogButtonBox.Ok, qtc.Qt.Horizontal)
        self.layout().addWidget(self.buttonBox)

    def updateAspectRatio(self):
        self.aspectRatio = self.project.canvasHeight() / self.project.canvasWidth()

    def updateValues(self):
        self.originalWidth = self.project.canvasWidth()
        self.originalHeight = self.project.canvasHeight()
        self.widthSpinBox.setValue(self.originalWidth)
        self.heightSpinBox.setValue(self.originalHeight)
        
    def show(self) -> None:
        self.updateValues()
        super(ScaleProjectDialog, self).show()

    def accept(self) -> None:
        self.requestScale.emit(self.project, self.widthSpinBox.value(), self.heightSpinBox.value(), False)
        super(ScaleProjectDialog, self).accept()
