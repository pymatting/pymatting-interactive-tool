# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from model.misc import Project, Controller, Image
from model.enum import Reason, Method, Kernel, Preconditioner


class TestController(unittest.TestCase):
    def makeController(self):
        canvas = Image.empty(qtc.QSize(100, 100))
        trimapPreview = Image.empty(canvas.size())
        alphaMatte = Image.full(
            canvas.size(), qtc.Qt.black, qtg.QImage.Format_Grayscale8
        )
        project = Project(canvas, alphaMatte, trimapPreview)
        return Controller(project)

    def testStartStopPause(self):
        controller = self.makeController()
        self.assertTrue(controller.isStopped())
        self.assertFalse(controller.isPaused())
        self.assertFalse(controller.isWaiting())
        controller.start()
        self.assertFalse(controller.isPaused())
        self.assertFalse(controller.isStopped())
        self.assertFalse(controller.isWaiting())
        controller.stop()
        self.assertFalse(controller.isPaused())
        self.assertTrue(controller.isStopped())
        self.assertFalse(controller.isWaiting())
        controller.start()
        self.assertFalse(controller.isPaused())
        self.assertFalse(controller.isStopped())
        self.assertFalse(controller.isWaiting())
        controller.pause()
        self.assertTrue(controller.isPaused())
        self.assertFalse(controller.isStopped())
        self.assertFalse(controller.isWaiting())
        controller.start()
        self.assertFalse(controller.isPaused())
        self.assertFalse(controller.isStopped())
        self.assertFalse(controller.isWaiting())
        controller.pause()
        controller.stop()
        self.assertFalse(controller.isPaused())
        self.assertTrue(controller.isStopped())
        self.assertFalse(controller.isWaiting())
        controller.close()

    def testUnblockSolver(self):
        controller = self.makeController()
        controller.unblockSolver()
        self.assertFalse(controller.isPaused())
        self.assertFalse(controller.isStopped())
        self.assertFalse(controller.isWaiting())
        controller.close()

    def testClearEventQueue(self):
        controller = self.makeController()
        controller.stop()
        controller.eventQueue.put("a")
        controller.eventQueue.put("b")
        controller.eventQueue.put("c")
        controller.eventQueue.put("d")
        controller.clearEventQueue()
        self.assertTrue(controller.eventQueue.empty())
        controller.close()

    def testChange(self):
        controller = self.makeController()
        controller.stop()
        controller.changeMethod(Method.vcycle)
        controller.changeEpsilon(2)
        controller.changeKernel(Kernel.linear)
        controller.changeLambda(1024)
        controller.changePostIter(4)
        controller.changePreconditioner(Preconditioner.jacobi)
        controller.changePreIter(7)
        controller.changeRadius(9)
        controller.changeTolerance(24)
        method = controller.eventQueue.get_nowait().value
        self.assertEqual(method, Method.vcycle)
        epsilon = controller.eventQueue.get_nowait().value
        self.assertEqual(epsilon, 2)
        kernel = controller.eventQueue.get_nowait().value
        self.assertEqual(kernel, Kernel.linear)
        lmd = controller.eventQueue.get_nowait().value
        self.assertEqual(lmd, 1024)
        postIter = controller.eventQueue.get_nowait().value
        self.assertEqual(postIter, 4)
        preconditioner = controller.eventQueue.get_nowait().value
        self.assertEqual(preconditioner, Preconditioner.jacobi)
        preIter = controller.eventQueue.get_nowait().value
        self.assertEqual(preIter, 7)
        radius = controller.eventQueue.get_nowait().value
        self.assertEqual(radius, 9)
        tolerance = controller.eventQueue.get_nowait().value
        self.assertEqual(tolerance, 24)
        controller.continueEvent.clear()
        self.assertTrue(controller.isWaiting())
        controller.changeTolerance(5)
        self.assertFalse(controller.isWaiting())
        controller.close()

    def testTrimapUpdated(self):
        controller = self.makeController()
        rect = qtc.QRect(100, 100, 500, 700)
        controller.trimapUpdated(rect)
        self.assertEqual(rect, controller.eventQueue.get_nowait().value)
        controller.continueEvent.clear()
        self.assertTrue(controller.isWaiting())
        controller.trimapUpdated(rect)
        self.assertFalse(controller.isWaiting())
        controller.close()
