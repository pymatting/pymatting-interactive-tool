# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)
import sys
import unittest
import numpy as np
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from tests.utility import setupImages
from model.misc import Solver, Image, AdjustingRect
from model.misc.solver import getUpdatedADiag_
from model.enum import Reason, Method, Preconditioner, Kernel, Color
from model.events import UpdateEvent
from model.util import trimapToRgba
from threading import Event
from queue import Queue
from scipy.sparse import csr_matrix
from skimage.metrics import structural_similarity as ssim
import scipy.sparse
from typing import Optional


class MockEvent(Event):
    def wait(self, timeout: Optional[float] = ...) -> bool:
        return False


class TestSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not setupImages():
            sys.exit(1)

    def makeImages(self):
        imagesPath = qtc.QFileInfo(__file__).dir()
        imagesPath.cdUp()
        imagesPath.cd("test_images")
        imageName = "GT15"
        canvas = Image(qtc.QDir(imagesPath.filePath("canvas")).filePath(imageName))
        trimapPreview = trimapToRgba(
            Image(qtc.QDir(imagesPath.filePath("Trimap1")).filePath(imageName))
        )
        alphaMatte = Image.full(
            canvas.size(), qtc.Qt.black, qtg.QImage.Format_Grayscale8
        )
        return canvas, trimapPreview, alphaMatte

    def makeSolver(self):
        canvas, trimapPreview, alphaMatte = self.makeImages()
        eventQueue = Queue()
        continueEvent = MockEvent()
        return (
            canvas,
            trimapPreview,
            alphaMatte,
            continueEvent,
            eventQueue,
            Solver(canvas, trimapPreview, alphaMatte, eventQueue, continueEvent),
        )

    def testFlatten2D(self):
        _, _, _, _, _, solver = self.makeSolver()
        for i in range(100):
            array2D = np.random.rand(100, 100)
            truth = array2D.flatten(order="C")
            self.assertTrue(np.all(truth == solver.flatten2D(array2D)))

    def testNorm2(self):
        _, _, _, _, _, solver = self.makeSolver()
        for i in range(100):
            array1D = np.random.rand(100)
            truth = np.linalg.norm(array1D)
            self.assertTrue(np.allclose(truth, solver.vecNorm2(array1D)))

    def testSpDiag(self):
        _, _, _, _, _, solver = self.makeSolver()
        for i in range(100):
            mat1 = csr_matrix(np.random.rand(100, 100))
            mat2 = csr_matrix(np.random.rand(100, 200))
            mat3 = csr_matrix(np.random.rand(200, 100))
            truth1 = mat1.diagonal()
            truth2 = mat2.diagonal()
            truth3 = mat3.diagonal()
            self.assertTrue(np.allclose(truth1, solver.spDiag(mat1)))
            self.assertTrue(np.allclose(truth2, solver.spDiag(mat2)))
            self.assertTrue(np.allclose(truth3, solver.spDiag(mat3)))

    def testAddTile(self):
        _, _, _, _, _, solver = self.makeSolver()
        a = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.int64)
        tile = np.tile([1, 2, 3], 3)
        truth = a + tile
        self.assertTrue(np.all(truth == solver.addTile(a, np.array([1, 2, 3]), 3)))

    def testGetUpdatedADiag(self):
        for i in range(100):
            L = np.random.rand(100, 100)
            w = 10
            L_diag = L.diagonal().copy()
            x0, y0, xn, yn = 3, 2, 7, 4
            c = np.full((10, 10), 1, dtype=np.float64)
            C = np.diagflat(c)
            A = L + C
            c[y0:yn, x0:xn] = np.random.rand(yn - y0, xn - x0)
            C = np.diagflat(c)
            ind, A_diag = getUpdatedADiag_((x0, y0, xn, yn), w, L_diag, c.flatten())
            truth = L + C
            A[ind, ind] = A_diag
            self.assertTrue(np.allclose(truth, A))
            self.assertTrue(np.allclose(truth.diagonal()[ind], A_diag))

    def testSpDot(self):
        _, _, _, _, _, solver = self.makeSolver()
        for i in range(100):
            A = csr_matrix(np.random.rand(100, 100))
            b = np.random.rand(100)
            truth = A.dot(b)
            self.assertTrue(np.allclose(truth, solver.spDot(A, b)))

    def testEvents(self):
        _, _, alphaMatte, _, eventQueue, solver = self.makeSolver()
        eventQueue.put_nowait(UpdateEvent(Reason.rtolChanged, 4))
        eventQueue.put_nowait(UpdateEvent(Reason.preIterChanged, 3))
        eventQueue.put_nowait(UpdateEvent(Reason.postIterChanged, 5))
        eventQueue.put_nowait(UpdateEvent(Reason.radiusChanged, 8))
        eventQueue.put_nowait(UpdateEvent(Reason.lambdaChanged, 321))
        eventQueue.put_nowait(UpdateEvent(Reason.epsilonChanged, 22))
        eventQueue.put_nowait(UpdateEvent(Reason.methodChanged, Method.vcycle))
        eventQueue.put_nowait(
            UpdateEvent(Reason.preconditionerChanged, Preconditioner.jacobi)
        )
        eventQueue.put_nowait(UpdateEvent(Reason.kernelChanged, Kernel.linear))
        solver.processEvents(eventQueue)
        self.assertEqual(1e-4, solver.get_rtol())
        self.assertEqual(3, solver.get_pre_iter())
        self.assertEqual(5, solver.get_post_iter())
        self.assertEqual(8, solver.get_radius())
        self.assertEqual(321, solver.get_lambda())
        self.assertEqual(22, solver.get_epsilon())
        self.assertEqual(Method.vcycle, solver.get_method())
        self.assertEqual(Preconditioner.jacobi, solver.get_preconditioner())
        self.assertEqual(Kernel.linear, solver.get_kernel()[0])

    def test_solvers(self):
        imagesPath = qtc.QFileInfo(__file__).dir()
        imagesPath.cdUp()
        imagesPath.cd("test_images")
        imageName = "GT15"
        gt_alpha = (
            Image(qtc.QDir(imagesPath.filePath("alpha")).filePath(imageName))
            .convertToFormat(qtg.QImage.Format_Grayscale8)
            .rawView()
        )
        alpha_cgd_no_preconditioner = self.doCgd(Preconditioner.none, 967)
        alpha_cgd_jacobi = self.doCgd(Preconditioner.jacobi, 567)
        alpha_cgd_vcycle = self.doCgd(Preconditioner.vcycle, 72)
        alpha_vcycle = self.doVcycle(649)

        ssim1 = ssim(alpha_cgd_no_preconditioner, gt_alpha)
        ssim2 = ssim(alpha_cgd_jacobi, gt_alpha)
        ssim3 = ssim(alpha_cgd_vcycle, gt_alpha)
        ssim4 = ssim(alpha_vcycle, gt_alpha)

        self.assertTrue(ssim1 >= 0.95)
        self.assertTrue(ssim2 >= 0.95)
        self.assertTrue(ssim3 >= 0.95)
        self.assertTrue(ssim4 >= 0.95)

    def doCgd(self, preconditioner, iterations):
        _, _, alphaMatte, _, eventQueue, solver = self.makeSolver()
        solver.setRtol(7)
        solver.setMethod(Method.cgd)
        solver.setPreconditioner(preconditioner)
        for i in range(iterations):
            solver.solve()
        self.assertTrue(solver.error < 1e-7)
        return alphaMatte.rawView()

    def doVcycle(self, iterations):
        _, _, alphaMatte, _, eventQueue, solver = self.makeSolver()
        solver.setRtol(7)
        solver.setMethod(Method.vcycle)
        for i in range(iterations):
            solver.solve()
        self.assertTrue(solver.error < 1e-7)
        return alphaMatte.rawView()

    # numbers from https://en.wikipedia.org/wiki/Conjugate_gradient_method#Numerical_example
    def testCgd(self):
        _, _, _, _, _, solver = self.makeSolver()
        A = csr_matrix(np.array([[1, 0, 0], [1, 2, 0], [1, 2, 3]], dtype=np.float64))

        b = np.array([1, 2, 3], dtype=np.float64)
        alpha = np.array([0, 0, 0], dtype=np.float64)
        r = b - A.dot(alpha)
        p = r.copy()
        alpha, r, p = solver.cgd(A, alpha, r, p)
        alpha = np.round(alpha, 2)
        r = np.round(r, 2)
        p = np.round(p, 2)
        self.assertTrue(np.all(np.allclose([0.26, 0.53, 0.79], alpha, 1e-2)))
        self.assertTrue(np.all(np.allclose([0.74, 0.68, -0.7], r, 1e-2)))
        self.assertTrue(np.all(np.allclose([0.84, 0.89, -0.38], p, 1e-2)))

        alpha, r, p = solver.cgd(A, alpha, r, p)
        alpha = np.round(alpha, 2)
        r = np.round(r, 2)
        p = np.round(p, 2)
        self.assertTrue(np.all(np.allclose([0.77, 1.07, 0.57], alpha, 1e-1)))
        self.assertTrue(np.all(np.allclose([0.23, -0.89, -1.59], r, 1e-1)))
        self.assertTrue(np.all(np.allclose([2.14, 1.13, -2.45], p, 1e-1)))

    def testResetL(self):
        _, _, _, _, _, solver = self.makeSolver()
        solver.L = 1
        solver.L_diag = 2
        solver.A = 3
        solver.r = 4
        solver.z = 5
        solver.b = 6
        solver.c = 7
        solver.norm_b = 8
        solver.M = 9
        solver.p = 10
        solver.A_diag = 11
        solver.m_diag = 12
        solver.cache = {}

        solver.reset_L()
        self.assertIsNotNone(solver.b)
        self.assertIsNotNone(solver.norm_b)
        self.assertIsNotNone(solver.c)

        self.assertIsNone(solver.L)
        self.assertIsNone(solver.L_diag)
        self.assertIsNone(solver.A)
        self.assertIsNone(solver.A_diag)
        self.assertIsNone(solver.r)
        self.assertIsNone(solver.z)
        self.assertIsNone(solver.p)
        self.assertIsNone(solver.m_diag)
        self.assertIsNone(solver.cache)
        self.assertIsNone(solver.M)

    def testResetA(self):
        _, _, _, _, _, solver = self.makeSolver()
        solver.L = 1
        solver.L_diag = 2
        solver.A = 3
        solver.r = 4
        solver.z = 5
        solver.b = 6
        solver.c = 7
        solver.norm_b = 8
        solver.M = 9
        solver.p = 10
        solver.A_diag = 11
        solver.m_diag = 12
        solver.cache = {}

        solver.reset_A()
        self.assertIsNotNone(solver.L)
        self.assertIsNotNone(solver.L_diag)
        self.assertIsNotNone(solver.b)
        self.assertIsNotNone(solver.norm_b)
        self.assertIsNotNone(solver.c)

        self.assertIsNone(solver.A)
        self.assertIsNone(solver.A_diag)
        self.assertIsNone(solver.r)
        self.assertIsNone(solver.z)
        self.assertIsNone(solver.p)
        self.assertIsNone(solver.m_diag)
        self.assertIsNone(solver.cache)
        self.assertIsNone(solver.M)

    def testResetADiag(self):
        def testResetA(self):
            _, _, _, _, _, solver = self.makeSolver()
            solver.L = 1
            solver.L_diag = 2
            solver.A = 3
            solver.r = 4
            solver.z = 5
            solver.b = 6
            solver.c = 7
            solver.norm_b = 8
            solver.M = 9
            solver.p = 10
            solver.A_diag = 11
            solver.m_diag = 12
            solver.cache = {}

            solver.reset_A_Diag()
            self.assertIsNotNone(solver.L)
            self.assertIsNotNone(solver.L_diag)
            self.assertIsNotNone(solver.b)
            self.assertIsNotNone(solver.norm_b)
            self.assertIsNotNone(solver.c)
            self.assertIsNotNone(solver.A)

            self.assertIsNone(solver.A_diag)
            self.assertIsNone(solver.r)
            self.assertIsNone(solver.z)
            self.assertIsNone(solver.p)
            self.assertIsNone(solver.m_diag)
            self.assertIsNone(solver.cache)
            self.assertIsNone(solver.M)

    def testResetR(self):
        _, _, _, _, _, solver = self.makeSolver()
        solver.L = 1
        solver.L_diag = 2
        solver.A = 3
        solver.r = 4
        solver.z = 5
        solver.b = 6
        solver.c = 7
        solver.norm_b = 8
        solver.M = 9
        solver.p = 10
        solver.A_diag = 11
        solver.m_diag = 12
        solver.cache = {}

        solver.reset_r()
        self.assertIsNotNone(solver.L)
        self.assertIsNotNone(solver.L_diag)
        self.assertIsNotNone(solver.b)
        self.assertIsNotNone(solver.norm_b)
        self.assertIsNotNone(solver.c)
        self.assertIsNotNone(solver.A)
        self.assertIsNotNone(solver.A_diag)
        self.assertIsNotNone(solver.m_diag)
        self.assertIsNotNone(solver.cache)
        self.assertIsNotNone(solver.M)

        self.assertIsNone(solver.r)
        self.assertIsNone(solver.z)
        self.assertIsNone(solver.p)

    def testResetZ(self):
        _, _, _, _, _, solver = self.makeSolver()
        solver.L = 1
        solver.L_diag = 2
        solver.A = 3
        solver.r = 4
        solver.z = 5
        solver.b = 6
        solver.c = 7
        solver.norm_b = 8
        solver.M = 9
        solver.p = 10
        solver.A_diag = 11
        solver.m_diag = 12
        solver.cache = {}

        solver.reset_z()
        self.assertIsNotNone(solver.L)
        self.assertIsNotNone(solver.L_diag)
        self.assertIsNotNone(solver.b)
        self.assertIsNotNone(solver.norm_b)
        self.assertIsNotNone(solver.c)
        self.assertIsNotNone(solver.A)
        self.assertIsNotNone(solver.A_diag)
        self.assertIsNotNone(solver.m_diag)
        self.assertIsNotNone(solver.cache)
        self.assertIsNotNone(solver.M)
        self.assertIsNotNone(solver.r)
        self.assertIsNone(solver.z)
        self.assertIsNone(solver.p)

    def testResetM(self):
        _, _, _, _, _, solver = self.makeSolver()
        solver.L = 1
        solver.L_diag = 2
        solver.A = 3
        solver.r = 4
        solver.z = 5
        solver.b = 6
        solver.c = 7
        solver.norm_b = 8
        solver.M = 9
        solver.p = 10
        solver.A_diag = 11
        solver.m_diag = 12
        solver.cache = {}

        solver.reset_M()
        self.assertIsNotNone(solver.L)
        self.assertIsNotNone(solver.L_diag)
        self.assertIsNotNone(solver.b)
        self.assertIsNotNone(solver.norm_b)
        self.assertIsNotNone(solver.c)
        self.assertIsNotNone(solver.A)
        self.assertIsNotNone(solver.A_diag)
        self.assertIsNotNone(solver.m_diag)
        self.assertIsNotNone(solver.r)

        self.assertIsNone(solver.cache)
        self.assertIsNone(solver.M)
        self.assertIsNone(solver.z)
        self.assertIsNone(solver.p)

    def testResetMDiag(self):
        _, _, _, _, _, solver = self.makeSolver()
        solver.L = 1
        solver.L_diag = 2
        solver.A = 3
        solver.r = 4
        solver.z = 5
        solver.b = 6
        solver.c = 7
        solver.norm_b = 8
        solver.M = 9
        solver.p = 10
        solver.A_diag = 11
        solver.m_diag = 12
        solver.cache = {}

        solver.reset_M()
        self.assertIsNotNone(solver.L)
        self.assertIsNotNone(solver.L_diag)
        self.assertIsNotNone(solver.b)
        self.assertIsNotNone(solver.norm_b)
        self.assertIsNotNone(solver.c)
        self.assertIsNotNone(solver.A)
        self.assertIsNotNone(solver.A_diag)
        self.assertIsNotNone(solver.m_diag)
        self.assertIsNotNone(solver.r)

        self.assertIsNone(solver.cache)
        self.assertIsNone(solver.M)
        self.assertIsNone(solver.z)
        self.assertIsNone(solver.p)

    def testUpdateSystem(self):
        _, trimapPreview, _, _, _, solver = self.makeSolver()
        shape = trimapPreview.rawView().shape
        trimapPreview.clear()
        solver.changeTrimapPreview(trimapPreview)
        solver.solve()
        self.assertTrue(np.all(solver.b == 0))
        trimapPreview.byteView()[100:200, 300:400] = Color.lightGreen.bgra()
        trimapPreview.byteView()[0:100, :] = Color.lightRed.bgra()
        solver.updateSystem(
            AdjustingRect((0, 0), *shape).addRect(qtc.QRect(300, 100, 200, 200))
        )
        self.assertTrue(
            np.all(solver.b.reshape(shape)[100:200, 300:400] == solver.get_lambda())
        )
        self.assertTrue(
            np.all(solver.c.reshape(shape)[100:200, 300:400] == solver.get_lambda())
        )
        self.assertTrue(np.all(solver.c.reshape(shape)[0:100, :] == 0))

        self.assertNotEqual(0, solver.A.nnz)
        self.assertEqual(
            0, (solver.A - (solver.get_L() + scipy.sparse.diags(solver.c))).nnz
        )
        self.assertTrue(
            np.all(
                solver.A.diagonal()
                == (solver.get_L() + scipy.sparse.diags(solver.c)).diagonal()
            )
        )
        self.assertTrue(
            np.all(
                solver.r
                == solver.get_b() - solver.spDot(solver.get_A(), solver.get_alpha())
            )
        )
        self.assertTrue(
            np.all(
                solver.get_m_diag()
                == solver.flatten2D(
                    solver.get_A_diag() / solver.A.multiply(solver.A).sum(axis=0)
                )
            )
        )

        solver.updateSystem(
            AdjustingRect((0, 0), *shape).addRect(qtc.QRect(0, 0, shape[1], 100))
        )
        self.assertTrue(
            np.all(solver.c.reshape(shape)[0:100, :] == solver.get_lambda())
        )
        self.assertNotEqual(0, solver.A.nnz)
        self.assertEqual(
            0, (solver.A - (solver.get_L() + scipy.sparse.diags(solver.c))).nnz
        )
        self.assertTrue(
            np.all(
                solver.A.diagonal()
                == (solver.get_L() + scipy.sparse.diags(solver.c)).diagonal()
            )
        )
        self.assertTrue(
            np.all(
                solver.r
                == solver.get_b() - solver.spDot(solver.get_A(), solver.get_alpha())
            )
        )
        self.assertTrue(
            np.all(
                solver.get_m_diag()
                == solver.flatten2D(
                    solver.get_A_diag() / solver.A.multiply(solver.A).sum(axis=0)
                )
            )
        )
