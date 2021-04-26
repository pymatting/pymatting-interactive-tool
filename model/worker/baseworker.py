#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc


class BaseWorker(qtc.QObject):

    error = qtc.pyqtSignal(str, Exception)