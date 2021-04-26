#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw
from strings import newBackgroundOrAlphaText, newBackgroundText, alphaText, cancelText

class MessageBoxNewBackgroundOrAlpha(qtw.QMessageBox):
    NewBackground = qtw.QMessageBox.AcceptRole  # 0
    Alpha = qtw.QMessageBox.RejectRole  # 1
    Cancel = qtw.QMessageBox.DestructiveRole  # 2

    def __init__(self):
        super(MessageBoxNewBackgroundOrAlpha, self).__init__()
        newBackgroundButton = qtw.QPushButton(newBackgroundText)
        alphaButton = qtw.QPushButton(alphaText)
        cancelButton = qtw.QPushButton(cancelText)
        self.setText(newBackgroundOrAlphaText)
        self.addButton(newBackgroundButton, qtw.QMessageBox.YesRole)
        self.addButton(alphaButton, qtw.QMessageBox.NoRole)
        self.addButton(cancelButton, qtw.QMessageBox.RejectRole)
        self.setIcon(qtw.QMessageBox.Question)
        self.setWindowTitle("Drag & Drop")