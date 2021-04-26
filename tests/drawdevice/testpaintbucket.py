#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from PyQt5 import QtCore as qtc
from model.drawdevice import Paintbucket
from model.util import ndarrayToImage
from model.misc import Image
from model.enum import Color
import numpy as np


class TestPaintBucket(unittest.TestCase):

    def testFill(self):
        canvasArray = np.full((10, 10, 4), 255)
        canvasArray[:, 0:1] = [0, 0, 0, 255]
        canvasArray[4:6, :] = [0, 0, 0, 255]
        canvasArray[:, 9:11] = [0, 0, 0, 255]
        canvas = ndarrayToImage(canvasArray)
        trimapPreview = Image.empty(qtc.QSize(10, 10))
        paintbucket = Paintbucket()
        paintbucket.setColor(Color.lightGreen)
        before, rect = paintbucket.fill(canvas, trimapPreview, qtc.QPointF(0, 0), True)
        paintbucket.close()
        self.assertTrue(before != trimapPreview)
        self.assertTrue(np.all(trimapPreview.byteView()[:, 0:1] == Color.lightGreen.bgra()))
        self.assertTrue(np.all(trimapPreview.byteView()[4:6, :] == Color.lightGreen.bgra()))
        self.assertTrue(np.all(trimapPreview.byteView()[:, 9:11] == Color.lightGreen.bgra()))
        self.assertTrue(np.all(trimapPreview.byteView()[0:4, 2:9] == [0, 0, 0, 0]))
        self.assertTrue(np.all(trimapPreview.byteView()[6:11, 2:9] == [0, 0, 0, 0]))
