# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from PyQt5.QtGui import QPainter

from model.drawdevice import DrawDevice
from model.enum import DrawMode, Color


class TestDrawDevice(unittest.TestCase):
    def testSetDrawModeForeground(self):
        drawDevice = DrawDevice()
        drawDevice.setDrawMode(DrawMode.foreground)
        assert drawDevice.drawMode() == DrawMode.foreground
        assert drawDevice.compositionMode() == QPainter.CompositionMode_Source
        assert drawDevice.color() == Color.lightGreen.value
        assert drawDevice.previewColor() == Color.lightGreen.value

    def testSetDrawModeBackground(self):
        drawDevice = DrawDevice()
        drawDevice.setDrawMode(DrawMode.background)
        assert drawDevice.drawMode() == DrawMode.background
        assert drawDevice.compositionMode() == QPainter.CompositionMode_Source
        assert drawDevice.color() == Color.lightRed.value
        assert drawDevice.previewColor() == Color.lightRed.value

    def testSetDrawModeUnknown(self):
        drawDevice = DrawDevice()
        drawDevice.setDrawMode(DrawMode.unknownTransparent)
        assert drawDevice.drawMode() == DrawMode.unknownTransparent
        assert drawDevice.compositionMode() == QPainter.CompositionMode_Clear
        assert drawDevice.color() == Color.transparent.value
        assert drawDevice.previewColor() == Color.transparent.value
