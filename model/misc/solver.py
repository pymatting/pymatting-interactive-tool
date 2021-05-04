# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from model.misc import AdjustingRect, Image
from model.enum import Method, Preconditioner, Reason, Kernel
from model.events import UpdateEvent, QuitEvent, StopEvent, PauseEvent, ContinueEvent
from pymatting import cf_laplacian  # ADDED NOGIL=TRUE
from threading import Thread, Event
from queue import Queue
from numba import njit, prange
from numba.core.types import f8, i8, i4, u1, b1, UniTuple, Tuple, void
from time import perf_counter as time
from datetime import timedelta
import scipy.sparse, scipy.sparse.linalg
import numpy as np
import config.config
from PyQt5 import QtCore as qtc


class Solver(qtc.QObject, Thread):
    # Signal(Error, Tolerance)
    calculated = qtc.pyqtSignal(object, object)
    # Signal(New Tolerance)
    toleranceChanged = qtc.pyqtSignal(object)
    toleranceReached = qtc.pyqtSignal()

    def __init__(
        self, canvas, trimapPreview, alphaMatte, eventQueue: Queue, continueEvent: Event
    ):
        super(Solver, self).__init__()
        self.setName("Thread: Solver")
        self.changeImages(canvas, alphaMatte, trimapPreview)
        self.eventQueue = eventQueue
        self.continueEvent = continueEvent
        self.adjustingRect = None
        self.initTweakableVariables()
        self.initCalculationVariables()

    def run(self) -> None:
        """Event Loop

        :return: None
        """
        while self.processEvents(self.eventQueue):
            self.solve()

    def processEvents(self, queue):
        """Processes the events inside the queue

        :param queue: Queue
        :return:
        """
        while not queue.empty():
            event = queue.get_nowait()
            if isinstance(event, UpdateEvent):
                if event.reason == Reason.trimapChanged:
                    if not self.adjustingRect:
                        self.adjustingRect = AdjustingRect(
                            (0, 0), *self.alphaView.shape
                        )
                    self.adjustingRect.addRect(event.value)
                else:
                    self.adjustSystem()
                    if event.reason == Reason.canvasChanged:
                        self.changeCanvas(event.value)
                        self.calculationStart = time()
                    elif event.reason == Reason.trimapPreviewChanged:
                        self.changeTrimapPreview(event.value)
                    elif event.reason == Reason.alphaMatteChanged:
                        self.changeAlphaMatte(event.value)
                    elif event.reason == Reason.methodChanged:
                        self.setMethod(event.value)
                    elif event.reason == Reason.lambdaChanged:
                        self.setLambda(event.value)
                    elif event.reason == Reason.preconditionerChanged:
                        self.setPreconditioner(event.value)
                    elif event.reason == Reason.epsilonChanged:
                        self.setEpsilon(event.value)
                    elif event.reason == Reason.radiusChanged:
                        self.setRadius(event.value)
                    elif event.reason == Reason.kernelChanged:
                        self.setKernel(event.value)
                    elif event.reason == Reason.postIterChanged:
                        self.setPostIter(event.value)
                    elif event.reason == Reason.preIterChanged:
                        self.setPreIter(event.value)
                    elif event.reason == Reason.rtolChanged:
                        self.setRtol(event.value)
                    elif event.reason == Reason.printErrorChanged:
                        self.setPrintError(event.value)
            elif isinstance(event, QuitEvent):
                return False
            elif isinstance(event, StopEvent):
                event.wait()
                self.calculationStart = time()
            elif isinstance(event, PauseEvent):
                event.wait()
            else:
                event.wait()
        self.adjustSystem()
        return True

    def changeImages(self, canvas, alphaMatte, trimapPreview):
        self.changeCanvas(canvas)
        self.changeAlphaMatte(alphaMatte)
        self.changeTrimapPreview(trimapPreview)

    def changeCanvas(self, canvas: Image):
        self.canvas = canvas.rgbView(True)
        self.h = canvas.height()
        self.w = canvas.width()
        self.reset_L()
        self.reset_c()
        self.reset_b()

    def changeTrimapPreview(self, trimapPreview: Image):
        self.trimapPreviewView = trimapPreview.byteView()
        self.initCalculationVariables()
        self.reset_c()
        self.reset_b()

    def changeAlphaMatte(self, alphaMatte: Image):
        self.alphaView = alphaMatte.rawView()
        self.alpha = self.flatten2D(self.alphaView / 255.0)
        self.reset_c()
        self.reset_b()

    def initCalculationVariables(self):
        self.L = None
        self.L_diag = None
        self.A = None
        self.r = None
        self.z = None
        self.b = None
        self.c = None
        self.norm_b = None
        self.M = None
        self.p = None
        self.A_diag = None
        self.m_diag = None
        self.cache = {}
        self.error = 1

    def initTweakableVariables(self):
        self.lmd = 100.0
        self.rtol = 10 ** (-7)
        self.epsilon = 1e-7
        self.radius = 1
        self.preconditioner = Preconditioner.vcycle
        self.method = Method.cgd
        self.kernel = (
            Kernel.gaussian,
            (1 / 16) * np.array([1, 2, 1, 2, 4, 2, 1, 2, 1]),
        )
        self.preiter = 1
        self.postiter = 1
        self.printError = False

    def adjustSystem(self):
        if self.adjustingRect:
            self.updateSystem(self.adjustingRect)
            self.adjustingRect = None

    def updateSystem(self, rect: AdjustingRect):
        rect = rect.boundingCoordinates()
        isForeground = get_updated_foreground_area_(rect, self.trimapPreviewView)
        isKnown = get_updated_known_area_(rect, self.trimapPreviewView, isForeground)
        self.update_b(rect, isForeground)
        self.update_c(rect, isKnown)
        self.reset_M()
        self.reset_z()
        self.reset_p()

    def calculate_error(self):
        """Calculates the normalized residual |r|/ |b|

        :return: (|r|/|b|, has the tolerance been reached?)
        """
        rtol = self.get_rtol()
        norm_b = self.get_norm_b()
        if rtol and norm_b != 0:
            norm_r = self.vecNorm2(self.get_r())
            relativeError = norm_r / norm_b
            if self.printError:
                print(f"Error: {relativeError}")
            if relativeError <= rtol:
                return relativeError, True
            return relativeError, False
        return None, None

    def solve(self):
        """Performs an iteration of the specified method if the tolerance has not been reached yet

        :return: Error
        """
        try:
            self.error, toleranceReached = self.calculate_error()
            method = self.get_method()
            if toleranceReached is True:
                self.calculationEnd = time()
                print(
                    f"Time: {timedelta(seconds=self.calculationEnd - self.calculationStart)}"
                )
                self.toleranceReached.emit()
                self.continueEvent.clear()
                self.continueEvent.wait()
            elif method.isCgd():
                M = self.get_M()
                if M:
                    self.alpha, self.r, self.z = self.cgd_preconditioned(
                        self.get_A(), self.get_alpha(), self.get_r(), self.get_z(), M
                    )
                else:
                    self.alpha, self.r, self.p = self.cgd(
                        self.get_A(), self.get_alpha(), self.get_r(), self.get_p()
                    )
            elif method.isVcycle():
                self.r = self.get_b() - self.spDot(self.get_A(), self.get_alpha())
                self.alpha += self.vcycle(
                    self.get_A(),
                    self.get_r(),
                    self.get_shape(),
                    self.get_kernel()[1],
                    self.get_cache(),
                    self.get_pre_iter(),
                    self.get_post_iter(),
                )
            self.alphaView[...] = np.clip(
                self.get_alpha().reshape(self.alphaView.shape) * 255.0, 0, 255
            )
            self.calculated.emit(self.error, self.rtol)
            return self.error
        except:
            pass

    # ================================================= GETTERS =======================================================#
    def get_b(self):
        if self.b is None:
            self.b = make_b_(self.trimapPreviewView, self.get_lambda())
        return self.b

    def get_c(self):
        if self.c is None:
            self.c = make_c_(self.trimapPreviewView, self.get_lambda())
        return self.c

    def get_L(self):
        if self.L is None:
            self.L = cf_laplacian(self.canvas, self.get_epsilon(), self.get_radius())
        return self.L

    def get_L_diag(self):
        if self.L_diag is None:
            self.L_diag = self.spDiag(self.get_L())
        return self.L_diag

    def get_A(self):
        if self.A is None:
            self.A = self.get_L() + scipy.sparse.diags(self.get_c())
        return self.A

    def get_alpha(self):
        return self.alpha

    def get_r(self):
        if self.r is None:
            self.r = self.get_b() - self.spDot(self.get_A(), self.get_alpha())
        return self.r

    def get_norm_b(self):
        if self.norm_b is None:
            self.norm_b = self.vecNorm2(self.get_b())
        return self.norm_b

    def get_M(self):
        if self.M is None:
            preconditioner = self.get_preconditioner()
            if preconditioner.isNone():
                self.M = None
            elif preconditioner.isVcycle():
                self.M = lambda r: self.vcycle(
                    self.get_A(),
                    r,
                    self.get_shape(),
                    self.get_kernel()[1],
                    self.get_cache(),
                    self.get_pre_iter(),
                    self.get_post_iter(),
                )
            elif preconditioner.isJacobi():
                A_diag_inv = scipy.sparse.diags(1 / self.spDiag(self.get_A()))
                self.M = lambda r: A_diag_inv.dot(r)
        return self.M

    def get_height(self):
        return self.h

    def get_width(self):
        return self.w

    def get_shape(self):
        return (self.get_height(), self.get_width())

    def get_kernel(self):
        return self.kernel

    def get_radius(self):
        return self.radius

    def get_epsilon(self):
        return self.epsilon

    def get_lambda(self):
        return self.lmd

    def get_method(self):
        return self.method

    def get_preconditioner(self):
        return self.preconditioner

    def get_cache(self):
        if self.cache is None:
            self.cache = {}
        return self.cache

    def get_pre_iter(self):
        return self.preiter

    def get_post_iter(self):
        return self.postiter

    def get_p(self):
        if self.p is None:
            preconditioner = self.get_preconditioner()
            if preconditioner.isNone():
                self.p = self.get_r().copy()
            elif preconditioner.isVcycle() or preconditioner.isJacobi():
                self.p = self.get_z().copy()
        return self.p

    def get_z(self):
        if self.z is None:
            M = self.get_M()
            if M:
                self.z = M(self.get_r())
            else:
                self.z = self.get_r()
        return self.z

    def get_A_diag(self):
        if self.A_diag is None:
            self.A_diag = self.spDiag(self.get_A())
        return self.A_diag

    def get_m_diag(self):
        if self.m_diag is None:
            A = self.get_A()
            self.m_diag = self.flatten2D(self.get_A_diag() / A.multiply(A).sum(axis=0))
        return self.m_diag

    def get_rtol(self):
        return self.rtol

    # ================================================== SETTERS ======================================================#

    def setMethod(self, method: Method):
        self.method = method

    def setLambda(self, lmd: int):
        self.lmd = float(lmd)
        self.reset_b()
        self.reset_c()

    def setPreconditioner(self, preconditioner: Preconditioner):
        self.preconditioner = preconditioner
        self.reset_M()

    def setRadius(self, radius: int):
        self.radius = radius
        self.reset_L()

    def setEpsilon(self, epsilon: float):
        self.epsilon = epsilon
        self.reset_L()

    def setKernel(self, kernel: Kernel):
        if kernel == Kernel.gaussian:
            self.kernel = (kernel, (1 / 16) * np.array([1, 2, 1, 2, 4, 2, 1, 2, 1]))
        elif kernel == Kernel.linear:
            self.kernel = (kernel, (1 / 9) * np.array([1, 1, 1, 1, 1, 1, 1, 1, 1]))
        self.reset_M()

    def setPreIter(self, preiter):
        self.preiter = preiter

    def setPostIter(self, postiter):
        self.postiter = postiter

    def setRtol(self, rtol: int):
        if rtol == 0:
            self.rtol = 0
        else:
            self.rtol = 10 ** (-rtol)

        self.toleranceChanged.emit(self.rtol)

    def setPrintError(self, printError):
        self.printError = printError

    # ================================================= UPDATERS ===========================================================#
    def update_b(self, rect, isForeground):
        update_flattend_2D_array_(
            rect, self.get_lambda(), isForeground, self.get_b(), self.get_shape()
        )
        self.reset_norm_b()

    def update_c(self, rect, isKnown):
        update_flattend_2D_array_(
            rect, self.get_lambda(), isKnown, self.get_c(), self.get_shape()
        )
        self.update_A(rect, self.get_width(), self.get_L_diag(), self.get_c())

    def update_A(self, rect, w, L_diag, c):
        ind, A_diag = getUpdatedADiag_(rect, w, L_diag, c)
        self.get_A()[ind, ind] = A_diag
        self.update_r(ind)
        self.reset_A_Diag()

    def update_m_diag(self, ind, A_diag):
        A = self.get_A()[:, ind]
        self.get_m_diag()[ind] = self.flatten2D(A_diag / A.multiply(A).sum(axis=0))

    def update_r(self, ind):
        update_vec_(
            ind,
            self.get_b()[ind]
            - (
                self.spDot(
                    self.get_A()[ind, 0 : self.get_A().shape[1]], self.get_alpha()
                )
            ),
            self.get_r(),
        )

    # ================================================= RESETERS ======================================================#

    def reset_L(self):
        self.L = None
        self.reset_L_diag()
        self.reset_A()

    def reset_norm_b(self):
        self.norm_b = None

    def reset_L_diag(self):
        self.L_diag = None

    def reset_A(self):
        self.A = None
        self.reset_r()
        self.reset_A_Diag()
        self.reset_M()
        self.reset_m_diag()

    def reset_r(self):
        self.r = None
        self.reset_p()
        self.reset_z()

    def reset_p(self):
        self.p = None

    def reset_z(self):
        self.z = None
        self.reset_p()

    def reset_M(self):
        self.M = None
        self.reset_z()
        self.reset_cache()

    def reset_cache(self):
        self.cache = None

    def reset_A_Diag(self):
        self.A_diag = None
        self.reset_m_diag()

    def reset_m_diag(self):
        self.m_diag = None

    def reset_b(self):
        self.b = None
        self.reset_norm_b()
        self.reset_r()

    def reset_c(self):
        self.c = None
        self.reset_A()

    # ============================================= NUMBA WRAPPERS =========================================================#

    def addTile(self, dest: np.ndarray, a: np.ndarray, reps: int):
        """Calculate dest += np.tile(a, reps)

        :param dest: Where the tile should be added onto
        :param a: array
        :param reps: how often 'a' should be tiled
        :return:
        """
        return addTile_(dest.astype(np.int64), a.astype(np.int64), reps)

    def cgd(self, A, alpha, r, p):
        """Performs an parallel iteration of the cg-Method by:

        Magnus R. Hestenes and Eduard Stiefel (1952). „Methods of Conjugate Gradients for
        Solving Linear Systems“. In: Journal of Research of the National Bureau of Standards 49.6, S. 409–436.

        DOI: 10.6028/jres.049.044

        :param A: Matrix A
        :param alpha: Current Alpha-Matte
        :param r: Residuum
        :param p: Direction
        :return: (alpha_new, r_new, p_new)
        """
        return cgd_((A.data, A.indices, A.indptr, A.shape), alpha, r, p)

    def spDot(self, A, b):
        """Performs the dot-product of a sparse Matrix A and a dense vector b

        :param A: Sparse matrix
        :param b: Dense Vector
        :return: A@b
        """
        return sp_dot_((A.data, A.indices, A.indptr, A.shape), b)

    def spDiag(self, mat):
        """Returns the Diagonal of a sparse matrix

        :param mat: Sparse Matrix
        :return: diag(mat)
        """
        return sp_diag_((mat.data, mat.indices, mat.indptr, mat.shape))

    def flatten2D(self, arr):
        """Flattens a 2D array

        :param arr: 2D array
        :return: flattened array
        """
        return flatten_2D_(arr.astype(np.float64))

    def vcycle(
        self, A, b, shape, kernel, cache, preiter=1, postiter=1, instantSolveSize=64
    ):
        """Performs the V-Cycle Algorithm as suggested by:

        Philip G. Lee und Ying Wu (2014). Scalable Matting: A Sub-linear Approach. arXiv: 1404.3933 [cs.CV].
        Link: https://arxiv.org/abs/1404.3933

        :param A: Sparse matrix A
        :param b: Dense Vektor b
        :param shape: shape of image
        :param kernel: kernel for scaling
        :param cache: cache dictionary
        :param preiter: how many smoothing iterations at the beginning
        :param postiter: how many smoothing iterations at the end
        :param instantSolveSize: at which size should the system be solved immediately
        :return: A approximation of x in Ax = b
        """

        h, w = shape
        n = h * w
        if n < instantSolveSize:
            return scipy.sparse.linalg.spsolve(A, b)
        if shape in cache:
            P, PT, A_diag, A_small, m_diag = cache[shape]
        else:
            P, PT = self.make_P(shape, kernel)
            A_small = P.dot(A).dot(PT)
            A_diag = self.spDiag(A)
            m_diag = A_diag / A.multiply(A).sum(axis=0)  # sparse approx inv0
            m_diag = self.flatten2D(np.array(m_diag))
            cache[shape] = (P, PT, A_diag, A_small, m_diag)
        x = self.spai0_step(A, b, None, m_diag, preiter)
        r = b - self.spDot(A, x)
        r_small = self.spDot(P, r)
        x_small = self.vcycle(
            A_small,
            r_small,
            (h // 2, w // 2),
            kernel,
            cache,
            preiter,
            postiter,
            instantSolveSize,
        )
        x += PT.dot(x_small)
        x = self.spai0_step(A, b, x, m_diag, postiter)
        return x

    def spai0_step(self, A, b, x, m_diag, num_iter):
        """Uses the SPAI-0-Algorithm as described by:

        Oliver Bröker, Marcus J. Grote, Carsten Mayer and Arnold Reusken (2001). „Robust Parallel
        Smoothing for Multigrid Via Sparse Approximate Inverses“. In: SIAM Journal on
        Scientific Computing 23.4, S. 1396–1417.

        DOI: 10.1137/S1064827500380623

        Also see:

        Marcus J. Grote and Thomas Huckle (1997). „Parallel Preconditioning with Sparse Approximate
        Inverses“. In: SIAM Journal on Scientific Computing 18.3, S. 838–853.

        DOI: 10.1137/S1064827594276552

        Because SPAI-0 is based on the original algorithm in this paper.

        :param A: Sparse Matrix A
        :param b: Dense Vector b
        :param x: current solution for Ax=b
        :param m_diag: as described in the paper
        :param num_iter: how often x should be smoothed
        :return: smoothed x
        """

        return spai0_step_(A.data, A.indices, A.indptr, A.shape, b, x, m_diag, num_iter)

    def cgd_preconditioned(self, A, alpha, r, z, M):
        """Performs an iteration of the preconditioned Method of Conjugate Gradients. I adopted the
        implementation for this from:

        Jonathan Richard Shewchuk (1994). An Introduction to the Conjugate Gradient Method Without
        the Agonizing Pain.

        Link: https://dl.acm.org/doi/10.5555/865018

        Which extends the cg-Method of:

        Magnus R. Hestenes and Eduard Stiefel (1952). „Methods of Conjugate Gradients for
        Solving Linear Systems“. In: Journal of Research of the National Bureau of Standards 49.6, S. 409–436.

        DOI: 10.6028/jres.049.044

        Such that preconditioners can be used.
        I changed the variable names to match the variable names of the cg-Method. I also changed the structure a bit
        to prevent calculating values multiple times.

        :param A: Matrix A
        :param alpha: Current Alpha-Matte
        :param r: Residuum
        :param z: M(r)
        :param M: Preconditioner
        :return: (alpha_new, r_new, z_new)
        """
        Az = A.dot(z)
        rz = np.inner(r, z)
        zAz = np.inner(z, Az)
        if rz != 0 and zAz != 0:
            a = rz / zAz
            r_new = r - a * Az
            s = M(r_new)
            return alpha + a * z, r_new, s + (np.inner(r_new, s) / rz) * z
        return alpha, r, z

    def make_P(self, shape, kernel):
        """Constructs a down- and upsampling matrices P and P.T based on the given Kernel

        :param shape: shape of the original images
        :param kernel: flattened 3x3 matrix
        :return: P, P.T
        """
        h, w = shape
        n = h * w
        h2 = h // 2
        w2 = w // 2
        n2 = w2 * h2
        x2 = np.repeat(np.tile(np.arange(w2), h2), 9).astype(np.int64)
        y2 = np.repeat(np.repeat(np.arange(h2), w2), 9).astype(np.int64)
        x = self.addTile(
            x2 * 2, np.array([-1, 0, 1, -1, 0, 1, -1, 0, 1], dtype=np.int64), n2
        )
        y = self.addTile(
            y2 * 2, np.array([-1, -1, -1, 0, 0, 0, 1, 1, 1], dtype=np.int64), n2
        )
        mask = (0 <= x) & (x < w) & (0 <= y) & (y <= h)
        i_inds = (x2 + y2 * w2)[mask]
        j_inds = (x + y * w)[mask]
        values = np.tile(kernel, n2)[mask]
        downsample = scipy.sparse.csr_matrix((values, (i_inds, j_inds)), (n2, n))
        upsample = downsample.T
        return downsample, upsample

    def vecNorm2(self, a: np.ndarray):
        return vecNorm2_(a.astype(np.float64))


@njit(
    f8[:](f8[:, :]),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def flatten_2D_(arr):
    h, w = arr.shape
    result = np.empty((h * w,))
    for y in prange(h):
        for x in prange(w):
            result[y * w + x] = arr[y, x]
    return result


@njit(
    f8(f8[:]),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def vecNorm2_(a):
    length = a.shape[0]
    result = 0
    for i in prange(length):
        result += a[i] ** 2
    return np.sqrt(result)


@njit(nogil=config.config.nogil, cache=config.config.cache)
def update_flattend_2D_array_(rect, lmd, values, vec, shape):
    x0, y0, xn, ym = rect
    vec.reshape(shape)[y0:ym, x0:xn] = lmd * values


@njit(void(i8[:], f8[:], f8[:]), nogil=config.config.nogil, cache=config.config.cache)
def update_vec_(ind, values, vec):
    vec[ind] = values


@njit(
    f8[:](Tuple((f8[:], i4[:], i4[:], UniTuple(i8, 2)))),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def sp_diag_(mat):
    data, indices, indptr, shape = mat
    length = min(shape[0], shape[1])
    result = np.zeros((length,), dtype=data.dtype)
    for row in prange(length):
        for i in range(indptr[row], indptr[row + 1]):
            if indices[i] == row and data[i] != 0:
                result[row] += data[i]
                break
    return result


@njit(
    b1[:, :](u1[:, :, :]),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def get_foreground_area_(trimapPreviewView):
    return trimapPreviewView[:, :, 1] == 255


@njit(
    b1[:, :](u1[:, :, :]),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def get_background_area_(trimapPreviewView):
    return trimapPreviewView[:, :, 2] == 255


@njit(
    b1[:, :](u1[:, :, :]),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def get_known_area_(trimapPreviewView):
    isForeground = get_foreground_area_(trimapPreviewView)
    isBackground = get_background_area_(trimapPreviewView)
    isKnown = np.logical_or(isForeground, isBackground)
    return isKnown


@njit(
    b1[:, :](UniTuple(i8, 4), u1[:, :, :]),
    nogil=config.config.nogil,
    cache=config.config.cache,
)
def get_updated_foreground_area_(rect, trimapPreviewView):
    x0, y0, xn, yn = rect
    return trimapPreviewView[:, :, 1][y0:yn, x0:xn] == 255


@njit(
    b1[:, :](UniTuple(i8, 4), u1[:, :, :], b1[:, :]),
    nogil=config.config.nogil,
    cache=config.config.cache,
)
def get_updated_known_area_(rect, trimapPreviewView, isForeground):
    x0, y0, xn, yn = rect
    isBackground = trimapPreviewView[:, :, 2][y0:yn, x0:xn] == 255
    isKnown = np.logical_or(isForeground, isBackground)
    return isKnown


@njit(
    f8[:](u1[:, :, :], f8),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def make_b_(trimapPreviewView, lmd):
    isForeground = get_foreground_area_(trimapPreviewView)
    return flatten_2D_(lmd * isForeground)


@njit(
    f8[:](u1[:, :, :], f8),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def make_c_(trimapPreviewView, lmd):
    isKnown = get_known_area_(trimapPreviewView)
    return flatten_2D_(lmd * isKnown)


@njit(
    i8[:](i8[:], i8[:], i8), cache=config.config.cache, parallel=config.config.parallel
)
def addTile_(dest, a, reps):
    n = len(a)
    for i in prange(reps):
        for j in prange(n):
            dest[i * n + j] += a[j]
    return dest


@njit(
    Tuple((i8[:], f8[:]))(UniTuple(i8, 4), i8, f8[:], f8[:]),
    nogil=config.config.nogil,
    cache=config.config.cache,
)
def getUpdatedADiag_(rect, w, L_diag, c):
    x0, y0, xn, yn = rect
    starts = np.arange(y0, yn) * w + x0
    width = xn - x0
    ind = addTile_(np.repeat(starts, width), np.arange(xn - x0), yn - y0)
    A_diag = L_diag[ind] + c[ind]
    return ind, A_diag


@njit(
    f8[:](Tuple((f8[:], i4[:], i4[:], UniTuple(i8, 2))), f8[:]),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def sp_dot_(mat, b):
    """Calculates the sparse matrix vector product between a scipy.sparse.csr_matrix and a numpy.ndarray
    :param mat: tuple
    tuple containing the sparse matrix data, indices, indptr and shape
    :param b: numpy.ndarray
    vector to multiplie the matrix with
    :return:
    returns the dot product between mat and b (mat@b or mat.dot(b) if mat was of type scipy.sprase.csr_matrix)
    """
    data, indices, indptr, height = mat[0], mat[1], mat[2], mat[3][0]
    result = np.zeros((height,), dtype=np.float64)
    for row in prange(height):
        start = indptr[row]
        end = indptr[row + 1]
        res = 0
        for i in range(start, end):
            res += data[i] * b[indices[i]]
        result[row] = res
    return result


@njit(
    UniTuple(f8[:], 3)(
        Tuple((f8[:], i4[:], i4[:], UniTuple(i8, 2))), f8[:], f8[:], f8[:]
    ),
    nogil=config.config.nogil,
    parallel=config.config.parallel,
    cache=config.config.cache,
)
def cgd_(A, alpha, r, p):
    Ap = sp_dot_(A, p)
    length = alpha.shape[0]
    rr = 0
    pAp = 0
    for i in prange(length):
        rr += r[i] * r[i]
        pAp += p[i] * Ap[i]
    if rr != 0 and pAp != 0:
        a = rr / pAp
        alpha_new = np.empty(length)
        r_new = np.empty(length)
        p_new = np.empty(length)
        beta = 0
        for j in prange(length):
            alpha_new[j] = alpha[j] + a * p[j]
            r_new[j] = r[j] - a * Ap[j]
            p_new[j] = r_new[j] + p[j]
            beta += (r_new[j] ** 2) / rr
        beta_1 = beta - 1
        for k in prange(length):
            p_new[k] += beta_1 * p[k]
        return alpha_new, r_new, p_new
    return alpha, r, p


@njit(cache=config.config.cache)
def spai0_step_(A_data, A_indices, A_indptr, A_shape, b, x, m_diag, iterations):
    if x is None:
        if iterations > 0:
            x = m_diag * b
            iterations -= 1
        else:
            x = np.zeros_like(b)
    for iteration in range(iterations):
        x = x - m_diag * (sp_dot_((A_data, A_indices, A_indptr, A_shape), x) - b)
    return x
