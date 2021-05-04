# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw
from view.lineedit import FileNameLineEdit
from strings import createText, cancelText


class NewProjectDialog(qtw.QDialog):
    Create = qtw.QMessageBox.AcceptRole  # 0
    Cancel = qtw.QMessageBox.DestructiveRole  # 2

    def __init__(self, default, parent=None):
        super(NewProjectDialog, self).__init__(parent=parent)
        self.defaultName = default
        self.setLayout(qtw.QVBoxLayout(self))
        self.setupWidgets()
        self.setupButtons()
        self.setupConnections()
        self.disableCreateButton(self.defaultName)
        self.setWindowTitle("New Project")

    def setupWidgets(self):
        widget = qtw.QWidget()
        widget.setLayout(qtw.QFormLayout())
        self.lineEdit = FileNameLineEdit(self.defaultName)
        widget.layout().addRow("Project name:", self.lineEdit)
        self.layout().addWidget(widget)

    def setupButtons(self):
        self.buttonBox = qtw.QDialogButtonBox()
        self.createButton = qtw.QPushButton(createText)
        self.cancelButton = qtw.QPushButton(cancelText)
        self.buttonBox.addButton(self.createButton, 1)
        self.buttonBox.addButton(self.cancelButton, 1)
        self.layout().addWidget(self.buttonBox)

    def setupConnections(self):
        self.createButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.lineEdit.textChanged.connect(self.disableCreateButton)

    def disableCreateButton(self, currentText: str):
        if currentText:
            self.createButton.setEnabled(True)
        else:
            self.createButton.setEnabled(False)

    def execute(self):
        accepted = super(NewProjectDialog, self).exec()
        return accepted, self.lineEdit.text()
