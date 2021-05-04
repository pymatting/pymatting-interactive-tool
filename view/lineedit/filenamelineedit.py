# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw
from model.misc import FileNameValidator


class FileNameLineEdit(qtw.QLineEdit):
    def __init__(self, text, parent=None):
        super(FileNameLineEdit, self).__init__(text, parent)
        self.setText(text)
        self.setValidator(FileNameValidator())
