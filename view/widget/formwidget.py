#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw
from view.spinbox import SpinBox, DoubleSpinBox


class FormWidget(qtw.QWidget):

    def __init__(self):
        super(FormWidget, self).__init__()
        self.setLayout(qtw.QFormLayout(self))

    def addSpinBox(self, string, min, max, value, toolTip=None, specialValueText=None, wrapping=True):
        spinBox = SpinBox(min, max, value, toolTip, specialValueText, wrapping)
        self.addRow(string, spinBox)
        return spinBox

    def addDoubleSpinBox(self, string, min, max, value, decimals, step, toolTip=None, wrapping=True):
        doubleSpinBox = DoubleSpinBox(min, max, value, decimals, step, toolTip, wrapping)
        self.addRow(string, doubleSpinBox)
        return doubleSpinBox

    def addCheckBox(self, string, checked=False):
        checkBox = qtw.QCheckBox("")
        checkBox.setChecked(checked)
        self.addRow(string,checkBox)
        return checkBox

    def addComboBox(self, string, texts, values, toolTip, currentIndex=0):
        comboBox = qtw.QComboBox()
        comboBox.setToolTip(toolTip)
        if len(texts) == len(values):
            for text, value in zip(texts, values):
                comboBox.addItem(text, value)
        comboBox.setCurrentIndex(currentIndex)
        self.addRow(string, comboBox)
        return comboBox

    def addRow(self, string, widget):
        self.layout().addRow(string, widget)