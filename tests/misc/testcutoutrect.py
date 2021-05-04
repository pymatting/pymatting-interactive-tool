# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from PyQt5 import QtCore as qtc
from model.misc import CutoutRect


class TestCutoutRect(unittest.TestCase):
    def makeCutoutRect(self, width, height):
        return CutoutRect(qtc.QRectF(0, 0, width, height))

    def testSetWidth(self):
        cutoutRect = self.makeCutoutRect(100, 200)
        cutoutRect.setWidth(100, True)
        self.assertEqual(100, cutoutRect.width())
        self.assertEqual(200, cutoutRect.height())
        cutoutRect.setWidth(200, True)
        self.assertEqual(200, cutoutRect.width())
        self.assertEqual(400, cutoutRect.height())
        cutoutRect.setWidth(7, True)
        self.assertEqual(7, cutoutRect.width())
        self.assertEqual(14, cutoutRect.height())
        cutoutRect.setWidth(1, True)
        self.assertEqual(1, cutoutRect.width())
        self.assertEqual(2, cutoutRect.height())
        cutoutRect.setWidth(0, True)
        self.assertEqual(1, cutoutRect.width())
        self.assertEqual(2, cutoutRect.height())
        cutoutRect.setWidth(-1, True)
        self.assertEqual(1, cutoutRect.width())
        self.assertEqual(2, cutoutRect.height())

    def testSetHeight(self):
        cutoutRect = self.makeCutoutRect(100, 200)
        cutoutRect.setHeight(200, True)
        self.assertEqual(100, cutoutRect.width())
        self.assertEqual(200, cutoutRect.height())
        cutoutRect.setHeight(400, True)
        self.assertEqual(200, cutoutRect.width())
        self.assertEqual(400, cutoutRect.height())
        cutoutRect.setHeight(7, True)
        self.assertEqual(3, cutoutRect.width())
        self.assertEqual(7, cutoutRect.height())
        cutoutRect.setHeight(1, True)
        self.assertEqual(1, cutoutRect.width())
        self.assertEqual(1, cutoutRect.height())
        cutoutRect.setHeight(0, True)
        self.assertEqual(1, cutoutRect.width())
        self.assertEqual(1, cutoutRect.height())
        cutoutRect.setHeight(6, True)
        self.assertEqual(3, cutoutRect.width())
        self.assertEqual(6, cutoutRect.height())

    def testMirror(self):
        cutoutRect = self.makeCutoutRect(100, 200)
        cutoutRect.mirrorVertical()
        self.assertEqual(cutoutRect.scale(), (-1, 1))
        cutoutRect.mirrorVertical()
        self.assertEqual(cutoutRect.scale(), (1, 1))
        cutoutRect.mirrorHorizontal()
        self.assertEqual(cutoutRect.scale(), (1, -1))
        cutoutRect.mirrorHorizontal()
        self.assertEqual(cutoutRect.scale(), (1, 1))
        cutoutRect.mirrorHorizontal()
        cutoutRect.mirrorVertical()
        self.assertEqual(cutoutRect.scale(), (-1, -1))

    def testReset(self):
        cutoutRect = self.makeCutoutRect(200, 400)
        cutoutRect.setAngle(56)
        self.assertEqual(cutoutRect.angle(), 56)
        cutoutRect.setScale((-1, -2))
        self.assertEqual(cutoutRect.scale(), (-1, -2))
        self.assertEqual(cutoutRect.width(), 200)
        self.assertEqual(cutoutRect.height(), 800)
        cutoutRect.reset()
        self.assertEqual(cutoutRect.angle(), 0)
        self.assertEqual(cutoutRect.scale(), (1, 1))
        self.assertEqual(cutoutRect.width(), 200)
        self.assertEqual(cutoutRect.height(), 400)

    def testTranslate(self):
        cutoutRect = self.makeCutoutRect(200, 400)
        cutoutRect.translate(10, 20)
        self.assertEqual(cutoutRect.center(), qtc.QPointF(110, 220))
        cutoutRect.translate(-10, -20)
        self.assertEqual(cutoutRect.center(), qtc.QPointF(100, 200))
