#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw


class HSlider(qtw.QSlider):
    def __init__(self, min:int, max:int, value:int, toolTip=None, step=1, tickInterval=2, tickPosition:qtw.QSlider.TickPosition=qtw.QSlider.TicksBelow):
        super(HSlider, self).__init__(qtc.Qt.Horizontal)
        self.setMinimum(min)
        self.setMaximum(max)
        self.setSingleStep(step)
        self.setTickInterval(tickInterval)
        self.setValue(value)
        if tickPosition:
            self.setTickPosition(tickPosition)
        self.setToolTip(toolTip)
