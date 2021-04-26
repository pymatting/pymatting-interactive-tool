#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw
from strings import canvasOrTrimapText, cancelText, trimapText, canvasText

class MessageBoxCanvasOrTrimap(qtw.QMessageBox):
    Canvas = qtw.QMessageBox.AcceptRole  # 0
    Trimap = qtw.QMessageBox.RejectRole  # 1
    Cancel = qtw.QMessageBox.DestructiveRole  # 2

    def __init__(self):
        super(MessageBoxCanvasOrTrimap, self).__init__()
        canvasButton = qtw.QPushButton(canvasText)
        trimapButton = qtw.QPushButton(trimapText)
        cancelButton = qtw.QPushButton(cancelText)
        self.setText(canvasOrTrimapText)
        self.addButton(canvasButton, qtw.QMessageBox.YesRole)
        self.addButton(trimapButton, qtw.QMessageBox.NoRole)
        self.addButton(cancelButton, qtw.QMessageBox.RejectRole)
        self.setIcon(qtw.QMessageBox.Question)
        self.setWindowTitle("Drag & Drop")
