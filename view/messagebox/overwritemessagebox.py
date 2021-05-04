# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw


class MessageBoxOverwrite(qtw.QMessageBox):
    Overwrite = qtw.QMessageBox.AcceptRole  # 0
    Cancel = qtw.QMessageBox.DestructiveRole  # 2

    def __init__(self, message):
        super(MessageBoxOverwrite, self).__init__()
        overwriteButton = qtw.QPushButton("Overwrite")
        cancelButton = qtw.QPushButton("Cancel")
        self.setText(message)
        self.setWindowTitle("Overwrite?")
        self.addButton(overwriteButton, qtw.QMessageBox.YesRole)
        self.addButton(cancelButton, qtw.QMessageBox.RejectRole)
        self.setIcon(qtw.QMessageBox.Question)
