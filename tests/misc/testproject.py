#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
import sys
import numpy as np
from tests.utility import setupImages, makeProject, openCanvas, openRandomImage, openAlphaMatte, openTrimap, openTrimapPreview
from model.misc import CutoutRect
from model.enum.color import Color
from model.util import trimapToRgba, imageToTrimap
from PyQt5.QtCore import QRectF

class TestProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if not setupImages():
            sys.exit(1)

    def testSetCanvas(self):
        imageName = "GT01"
        project = makeProject(imageName)
        canvas = openRandomImage()
        project.setCanvas(canvas)
        self.assertTrue(np.all(canvas.byteView() == project.canvas().byteView()))
        self.assertEqual(canvas.width(),  project.alphaMatte().width())
        self.assertEqual(canvas.height(), project.alphaMatte().height())
        self.assertEqual(canvas.width(),  project.trimapPreview().width())
        self.assertEqual(canvas.height(), project.trimapPreview().height())

    def testSetAlphaMatte(self):
        project = makeProject("GT01")
        alphaMatte = openAlphaMatte("GT02")
        project.setAlphaMatte(alphaMatte)
        alphaMatte = alphaMatte.scaled(project.canvas().width(), project.canvas().height())
        self.assertTrue(np.all(alphaMatte.byteView() == project.alphaMatte().byteView()))


    def testSetTrimap(self):
        project = makeProject("GT01")
        trimap = openTrimap("GT02")
        project.setTrimap(trimap)
        trimap = trimap.scaled(project.canvas().width(), project.canvas().height())
        self.assertTrue(np.all(trimapToRgba(trimap).byteView() == project.trimapPreview().byteView()))

    def testSetTrimapPreview(self):
        project = makeProject("GT01")
        trimap = openTrimapPreview("GT02")
        project.setTrimapPreview(trimap)
        trimap = trimap.scaled(project.canvas().width(), project.canvas().height())
        self.assertTrue(np.all(trimap.byteView() == project.trimapPreview().byteView()))

    def testSetNewBackground1(self):
        project = makeProject("GT01")
        newBackground = openRandomImage()
        project.setNewBackground(newBackground)
        self.assertTrue(np.all(newBackground.byteView() == project.newBackground().byteView()))


    def testSetProjectTitle(self):
        project = makeProject("GT01", True)
        project.setTitle("new title")
        self.assertEqual("new title", project.title())

    def testEdited(self):
        project = makeProject("GT01", True)
        project.setEdited()
        self.assertTrue(project.isEdited())
        project.setUnedited()
        self.assertFalse(project.isEdited())


    def testNew(self):
        project = makeProject("GT01", True)
        canvas = openCanvas("GT02")
        newHeight , newWidth= canvas.height(), canvas.width()

        project.setPath(__file__)
        project.setCutoutRect(CutoutRect(QRectF(-200, -200, 200, 200), (2,3), 100))
        project.setEdited()
        project.setTitle("test")

        project.new(canvas, "name")

        self.assertTrue(np.all(canvas.byteView() == project.canvas().byteView()))
        self.assertTrue(np.all(np.full((newHeight, newWidth, 1), 0)   == project.alphaMatte().byteView()))
        self.assertTrue(np.all(np.full((newHeight, newWidth, 1), 160) == project.trimap().byteView()))
        self.assertTrue(np.all(np.full((newHeight, newWidth),0)       == project.trimapPreview().byteView()[:,:,3]))
        self.assertTrue(project.title() == "name")
        self.assertTrue(project.cutoutRect().width() == project.canvasWidth())
        self.assertTrue(project.cutoutRect().height() == project.canvasHeight())
        self.assertTrue(project.cutoutRect().scale() == (1, 1))
        self.assertTrue(project.cutoutRect().angle() == 0)
        self.assertIsNone(project.newBackground())
        self.assertIsNone(project.path())
        self.assertFalse(project.isEdited())