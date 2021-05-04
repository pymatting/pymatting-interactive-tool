# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5.QtCore import Qt
from model.drawdevice import Pen


class Brush(Pen):
    def __init__(self):
        super(Brush, self).__init__(Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
