# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw
from model.misc import CutoutRect
from view.spinbox import SpinBox
from view.slider import HSlider
from view.pushbutton import PushButton


class TransformationContextMenu(qtw.QMenu):
    def __init__(self, cutoutRect: CutoutRect, parent=None, title="Transform"):
        super(TransformationContextMenu, self).__init__(title, parent)
        self.cutoutRect = cutoutRect
        self.setupWidgets()
        self.updateValues()
        self.cutoutRect.changed.connect(self.updateValues)

    def setupWidgets(self):
        action = qtw.QWidgetAction(self)
        containerWidget = qtw.QGroupBox("Transform")
        containerLayout = qtw.QGridLayout(self)
        containerWidget.setLayout(containerLayout)
        action.setDefaultWidget(containerWidget)
        self.createRotationSlider(containerLayout)
        self.createScalingWidgets(containerLayout)
        self.setupMirroringButtons(containerLayout)
        self.setupResetButton(containerLayout)
        self.addAction(action)

    def createScalingWidgets(self, layout: qtw.QGridLayout):
        """Create Widgets to scale the cutout preview"""
        width, height = self.cutoutRect.width(), self.cutoutRect.height()
        self.widthSpinBox = SpinBox(1, 10000, width, wrapping=False)
        self.heightSpinBox = SpinBox(1, 10000, height, wrapping=False)
        desc = qtw.QLabel("Scale")
        xLabel = qtw.QLabel("x")
        """ Setup connections """
        self.widthSpinBox.valueChanged.connect(self.cutoutRect.setWidth)
        self.heightSpinBox.valueChanged.connect(self.cutoutRect.setHeight)
        """ Add widgets to the given GridLayout """
        layout.addWidget(desc, 1, 0)
        layout.addWidget(self.widthSpinBox, 1, 1)
        layout.addWidget(xLabel, 1, 2)
        layout.addWidget(self.heightSpinBox, 1, 3)

    def createRotationSlider(self, layout: qtw.QGridLayout):
        """Create Widgets used to rotate the cutout preview label"""
        angle = self.cutoutRect.angle()
        self.rotationSlider = HSlider(0, 360, angle, tickInterval=30)
        self.rotationSpinBox = SpinBox(0, 360, angle)
        desc = qtw.QLabel("Rotate")
        """ Setup connection """
        self.rotationSlider.valueChanged.connect(self.cutoutRect.setAngle)
        self.rotationSpinBox.valueChanged.connect(self.cutoutRect.setAngle)
        """ Add widgets to the given GridLayout """
        layout.addWidget(desc, 0, 0)
        layout.addWidget(self.rotationSlider, 0, 1)
        layout.addWidget(self.rotationSpinBox, 0, 3)

    def setupMirroringButtons(self, layout: qtw.QGridLayout):
        """Create Widgets to mirror the cutout preview"""
        mirrorVertical = PushButton("Vertical")
        mirrorHorizontal = PushButton("Horizontal")
        desc = qtw.QLabel("Mirror")
        """ Setup connections """
        mirrorVertical.pressed.connect(self.cutoutRect.mirrorVertical)
        mirrorHorizontal.pressed.connect(self.cutoutRect.mirrorHorizontal)
        """ Add widgets to the given GridLayout """
        layout.addWidget(desc, 3, 0)
        layout.addWidget(mirrorVertical, 3, 1)
        layout.addWidget(mirrorHorizontal, 3, 3)

    def setupResetButton(self, layout: qtw.QGridLayout):
        resetButton = PushButton("Reset")
        layout.addWidget(resetButton, 4, 0, 1, 4)
        resetButton.pressed.connect(self.cutoutRect.reset)

    def updateValues(self):
        self.widthSpinBox.blockSignals(True)
        self.heightSpinBox.blockSignals(True)
        self.rotationSlider.blockSignals(True)
        self.rotationSpinBox.blockSignals(True)

        self.widthSpinBox.setValue(self.cutoutRect.width())
        self.heightSpinBox.setValue(self.cutoutRect.height())
        self.rotationSlider.setValue(self.cutoutRect.angle())
        self.rotationSpinBox.setValue(self.cutoutRect.angle())

        self.rotationSpinBox.blockSignals(False)
        self.rotationSlider.blockSignals(False)
        self.widthSpinBox.blockSignals(False)
        self.heightSpinBox.blockSignals(False)
