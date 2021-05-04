# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from PyQt5 import QtCore as qtc
from model.misc import AdjustingRect


class TestAdjustingRect(unittest.TestCase):
    def testAddPointstraight(self):
        adjustRect = AdjustingRect()
        adjustRect.addPoint(qtc.QPointF(0, 0), 1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-1, -1, 1, 1))
        adjustRect.addPoint(qtc.QPointF(0, 1), 1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-1, -1, 1, 2))
        adjustRect.addPoint(qtc.QPointF(1, 0), 1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-1, -1, 2, 2))
        adjustRect.addPoint(qtc.QPointF(0, -1), 1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-1, -2, 2, 2))
        adjustRect.addPoint(qtc.QPointF(-1, 0), 1)

    def testAddPointDiagonal(self):
        adjustRect = AdjustingRect()
        adjustRect.addPoint(qtc.QPointF(0, 0), 1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-1, -1, 1, 1))
        adjustRect.addPoint(qtc.QPointF(1, 1), 1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-1, -1, 2, 2))
        adjustRect.addPoint(qtc.QPointF(-1, -1), 1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-2, -2, 2, 2))
        adjustRect.addPoint(qtc.QPointF(-2, 2), 1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-3, -2, 2, 3))
        adjustRect.addPoint(qtc.QPointF(2, -2), 1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-3, -3, 3, 3))

    def testAddRect(self):
        adjustRect = AdjustingRect()
        adjustRect.addRect(qtc.QRectF(qtc.QPointF(-1, -1), qtc.QPointF(1, 1)))
        self.assertTrue(adjustRect.boundingCoordinates() == (-1, -1, 1, 1))
        adjustRect.addRect(qtc.QRectF(qtc.QPointF(-2, -2), qtc.QPointF(2, 2)))
        self.assertTrue(adjustRect.boundingCoordinates() == (-2, -2, 2, 2))
        adjustRect.addRect(qtc.QRectF(qtc.QPointF(-2, -2), qtc.QPointF(3, 4)))
        self.assertTrue(adjustRect.boundingCoordinates() == (-2, -2, 3, 4))
        adjustRect.addRect(qtc.QRectF(qtc.QPointF(-4, -1), qtc.QPointF(5, 4)))
        self.assertTrue(adjustRect.boundingCoordinates() == (-4, -2, 5, 4))
        adjustRect.addRect(qtc.QRectF(qtc.QPointF(100, 100), qtc.QPointF(100, 100)))
        self.assertTrue(adjustRect.boundingCoordinates() == (-4, -2, 5, 4))
        adjustRect.addRect(qtc.QRectF(qtc.QPointF(100, 100), qtc.QPointF(-100, -100)))
        self.assertTrue(adjustRect.boundingCoordinates() == (-100, -100, 100, 100))

    def testRadius(self):
        adjustRect = AdjustingRect()
        adjustRect.addPoint(qtc.QPointF(0, 1), 2)
        self.assertTrue(adjustRect.boundingCoordinates() == (-2, -1, 2, 3))
        adjustRect.addPoint(qtc.QPointF(100, 100), -1)
        self.assertTrue(adjustRect.boundingCoordinates() == (-2, -1, 2, 3))

    def testBorders(self):
        adjustRect = AdjustingRect((0, 0), 100, 100)
        adjustRect.addPoint(qtc.QPointF(0, 0), 5)
        self.assertTrue(adjustRect.boundingCoordinates() == (0, 0, 5, 5))
        adjustRect.addPoint(qtc.QPointF(100, 100), 5)
        self.assertTrue(adjustRect.boundingCoordinates() == (0, 0, 100, 100))
        adjustRect = AdjustingRect((0, 0), 100, 100)
        adjustRect.addRect(qtc.QRectF(qtc.QPointF(-100, -100), qtc.QPointF(101, 101)))
        self.assertTrue(adjustRect.boundingCoordinates() == (0, 0, 100, 100))

    def testNotChanged(self):
        adjustRect = AdjustingRect((0, 0), 100, 100)
        self.assertTrue(adjustRect.toQRectF() is None)
        adjustRect = AdjustingRect()
        self.assertTrue(adjustRect.toQRectF() is None)

    def testAddRectNone(self):
        adjustingRect = AdjustingRect()
        adjustingRect.addRect(None)
        self.assertIsNone(adjustingRect.toQRectF())
        self.assertIsNone(adjustingRect.toQRect())

    def testFromRect(self):
        rect = qtc.QRect(10, 20, 30, 40)
        adjustingRect = AdjustingRect.fromRect(rect)
        adjustingRect.addRect(rect)
        self.assertEqual(adjustingRect.toQRect(), rect)
