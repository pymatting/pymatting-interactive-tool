# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw


class SpinBox(qtw.QSpinBox):
    def __init__(
        self,
        min: int,
        max: int,
        value: int,
        toolTip=None,
        specialValueText: str = None,
        wrapping=True,
        parent=None,
    ):
        super(SpinBox, self).__init__(parent=parent)
        self.setMinimum(min)
        self.setMaximum(max)
        self.setValue(value)
        self.setToolTip(toolTip)
        if specialValueText:
            self.setSpecialValueText(specialValueText)
        self.setWrapping(wrapping)
        self.setAccelerated(True)


class DoubleSpinBox(qtw.QDoubleSpinBox):
    def __init__(
        self, min, max, value, decimals, step, toolTip=None, wrapping=True, parent=None
    ):
        super(DoubleSpinBox, self).__init__(parent=parent)
        self.setMinimum(min)
        self.setMaximum(max)
        self.setValue(value)
        self.setDecimals(decimals)
        # self.setSingleStep(step)
        self.setToolTip(toolTip)
        self.setWrapping(wrapping)
        self.setAccelerated(True)
        # self.setStepType(qtw.QAbstractSpinBox.AdaptiveDecimalStepType)
