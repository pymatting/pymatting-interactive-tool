#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw


class SaveMessageBox(qtw.QMessageBox):
    Save = qtw.QMessageBox.AcceptRole  # 0
    DontSave = qtw.QMessageBox.RejectRole  # 1
    Cancel = qtw.QMessageBox.DestructiveRole  # 2

    def __init__(self):
        super(SaveMessageBox, self).__init__()
        saveButton = qtw.QPushButton("Save")
        dontSaveButton = qtw.QPushButton("Don't Save")
        cancelButton = qtw.QPushButton("Cancel")
        self.setText("Do you want to save the project?")
        self.setWindowTitle("Save?")
        self.addButton(saveButton, qtw.QMessageBox.YesRole)
        self.addButton(dontSaveButton, qtw.QMessageBox.NoRole)
        self.addButton(cancelButton, qtw.QMessageBox.RejectRole)
        self.setIcon(qtw.QMessageBox.Question)
