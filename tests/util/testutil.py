#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from model.util import *
import numpy as np


class TestUtil(unittest.TestCase):

    def testCalculateDiffRect1(self):
        A = ndarrayToImage(np.array([
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 0, 0]
        ]))

        B = ndarrayToImage(np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]))

        rect = calculateDiffRect(A, B)
        self.assertEqual(rect, qtc.QRectF(1, 0, 3, 3))

    def testCalculateDiffRect2(self):
        A = ndarrayToImage(np.array([
            [0, 1, 1, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0]
        ]))

        B = ndarrayToImage(np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0]
        ]))

        rect = calculateDiffRect(A, B)
        self.assertEqual(rect, qtc.QRectF(1, 0, 3, 3))

    def testCalculateDiffRect3(self):
        A = ndarrayToImage(np.array([
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]))

        B = ndarrayToImage(np.array([
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]))

        rect = calculateDiffRect(A, B)
        self.assertIsNone(rect)

    def testCalculateDiffRect4(self):
        A = ndarrayToImage(np.array([
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]))

        B = ndarrayToImage(np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]))

        rect = calculateDiffRect(A, B)
        self.assertEqual(rect, qtc.QRectF(2, 0, 1, 1))

    def testMatchScale(self):
        a = Image.empty(qtc.QSize(100, 100))
        b = Image.empty(qtc.QSize(50, 50))
        a = matchScale(a, b)
        self.assertEqual(a.size(), b.size())

    def testImageToTrimap(self):
        image = Image.empty(qtc.QSize(100, 100))
        byteView = image.byteView()
        byteView[10:20, 5:10] = Color.lightGreen.bgra()
        byteView[10:20, 10:15] = Color.lightRed.bgra()
        trimap = imageToTrimap(image)
        self.assertTrue(np.all(trimap.byteView()[10:20, 5:10] == 255))
        self.assertTrue(np.all(trimap.byteView()[10:20, 10:15] == 0))
        self.assertTrue(np.all(trimap.byteView()[10:20, 0:5] == 160))
        self.assertTrue(np.all(trimap.byteView()[10:20, 15:] == 160))
        self.assertTrue(np.all(trimap.byteView()[0:10, :] == 160))
        self.assertTrue(np.all(trimap.byteView()[20:, :] == 160))

    def testTrimapToRgba(self):
        trimap = ndarrayToImage(np.array([
            [160, 160, 160, 160, 160, 160],
            [160, 255, 255, 255, 160, 160],
            [160, 255, 255, 255, 160, 160],
            [160, 160, 160,   0,   0,   0],
            [160, 160, 160,   0,   0,   0]
        ]))

        rgba = trimapToRgba(trimap)

        self.assertTrue(np.all(rgba.byteView()[1:3, 1:4] == Color.lightGreen.bgra()))
        self.assertTrue(np.all(rgba.byteView()[3:, 3:] == Color.lightRed.bgra()))
        self.assertTrue(np.all(rgba.byteView()[0,   :] == Color.transparent.bgra()))
        self.assertTrue(np.all(rgba.byteView()[:,   0] == Color.transparent.bgra()))
        self.assertTrue(np.all(rgba.byteView()[3:, :3] == Color.transparent.bgra()))
        self.assertTrue(np.all(rgba.byteView()[3:, :3] == Color.transparent.bgra()))
        self.assertTrue(np.all(rgba.byteView()[:3, 4:] == Color.transparent.bgra()))


    def testCutoutForeground(self):
        image = ndarrayToImage(np.full((250,250,4), 7))
        alphaMatte = grayToImage(np.zeros((250,250)))
        alphaMatte.byteView()[100:200, 50:100] = [255]

        cut = cutoutForeground(image, alphaMatte)
        truth = np.zeros((250,250,4))
        truth[:,:] = [7,7,7,0]
        truth[100:200, 50:100] = [7,7,7,255]
        self.assertTrue(np.all(cut.byteView() == truth))

    def testCutoutBackground(self):
        image = ndarrayToImage(np.full((250,250,4), 7))
        alphaMatte = grayToImage(np.zeros((250,250)))
        alphaMatte.byteView()[100:200, 50:100] = [255]

        cut = cutoutBackground(image, alphaMatte)
        truth = np.zeros((250,250,4))
        truth[:,:] = [7,7,7,255]
        truth[100:200, 50:100] = [7,7,7,0]
        self.assertTrue(np.all(cut.byteView() == truth))











