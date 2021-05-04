# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from model.worker import Cropper, Project
from PyQt5 import QtCore as qtc


class TestCropper(unittest.TestCase):
    def testCropping(self):
        project = Project.empty()
        cropper = Cropper()
        self.assertTrue(project.canvas().size() == qtc.QSize(500, 500))
        self.assertTrue(project.alphaMatte().size() == qtc.QSize(500, 500))
        self.assertTrue(project.trimapPreview().size() == qtc.QSize(500, 500))

        cropper.crop(project, qtc.QRect(300, 300, 100, 100))
        self.assertTrue(project.canvas().size() == qtc.QSize(100, 100))
        self.assertTrue(project.alphaMatte().size() == qtc.QSize(100, 100))
        self.assertTrue(project.trimapPreview().size() == qtc.QSize(100, 100))

        cropper.crop(project, "vfds")
        self.assertTrue(project.canvas().size() == qtc.QSize(100, 100))
        self.assertTrue(project.alphaMatte().size() == qtc.QSize(100, 100))
        self.assertTrue(project.trimapPreview().size() == qtc.QSize(100, 100))
