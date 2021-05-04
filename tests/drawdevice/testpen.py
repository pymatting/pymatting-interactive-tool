# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from PyQt5 import QtCore as qtc
from model.drawdevice import Pen
from model.misc import Image
from model.enum import Color
import numpy as np


class TestPen(unittest.TestCase):
    def testSetWidth(self):
        pen = Pen(qtc.Qt.SolidLine, qtc.Qt.RoundCap, qtc.Qt.RoundJoin)
        pen.setWidth(20)
        self.assertEqual(20, pen.width())
        self.assertEqual(10, pen.radius())
        self.assertEqual(10 + pen.previewWidth(), pen.previewRadius())

        pen.setWidth(19)
        self.assertEqual(19, pen.width())
        self.assertEqual(9.5, pen.radius())
        self.assertEqual(9.5 + pen.previewWidth(), pen.previewRadius())

        pen.setWidth(1)
        self.assertEqual(1, pen.width())
        self.assertEqual(0.5, pen.radius())
        self.assertEqual(0.5 + pen.previewWidth(), pen.previewRadius())

    def testDrawLine(self):
        image = Image.empty(qtc.QSize(10, 10))
        before = np.copy(image.byteView())
        pen = Pen(qtc.Qt.SolidLine, qtc.Qt.RoundCap, qtc.Qt.RoundJoin, 1)
        pen.setColor(Color.lightGreen)
        rect = pen.drawLine(image, qtc.QPointF(0, 0), qtc.QPointF(10, 10))
        after = np.copy(image.byteView())
        self.assertTrue(np.any(before != after))
        self.assertTrue(np.all(after.diagonal()[1, :] == 255))
        self.assertTrue(rect == qtc.QRect(-2, -2, 14, 14))

    def testDrawPoint(self):
        image = Image.empty(qtc.QSize(10, 10))
        before = np.copy(image.byteView())
        pen = Pen(qtc.Qt.SolidLine, qtc.Qt.RoundCap, qtc.Qt.RoundJoin, 1)
        pen.setColor(Color.lightGreen)
        rect = pen.drawPoint(image, qtc.QPointF(5, 5))
        after = np.copy(image.byteView())
        self.assertTrue(np.any(before != after))
        self.assertTrue(rect == qtc.QRect(3, 3, 4, 4))
