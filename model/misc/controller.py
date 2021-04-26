#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from model.misc import Solver
from model.events import PauseEvent, StopEvent, ContinueEvent, QuitEvent, UpdateEvent, Event
from model.enum import Reason, Method, Kernel, Preconditioner
from queue import Queue


class Controller(qtc.QObject):
    """ This class controls the solver and servers as an agent between the solver and the view elements

    """

    stopped = qtc.pyqtSignal()
    started = qtc.pyqtSignal()
    paused = qtc.pyqtSignal()

    # Signal(Current Error, Minimum Error)
    calculated = qtc.pyqtSignal(object, object)
    # Signal(Minimum Error)
    toleranceChanged = qtc.pyqtSignal(object)
    toleranceReached = qtc.pyqtSignal()

    def __init__(self, project):
        super(Controller, self).__init__()
        self.project = project
        self.stopEvent = StopEvent()
        self.pauseEvent = PauseEvent()
        self.continueEvent = ContinueEvent()
        self.eventQueue = Queue()
        self.queueEvent(self.stopEvent)
        self.solver = Solver(self.project.canvas(), self.project.trimapPreview(), self.project.alphaMatte(),
                             self.eventQueue, self.continueEvent)
        self.solver.start()
        self.setupConnections()

    def setupConnections(self):
        self.project.canvasChanged.connect(self.changeCanvas)
        self.project.alphaMatteChanged.connect(self.changeAlphaMatte)
        self.project.trimapPreviewChanged.connect(self.changeTrimapPreview)
        self.solver.calculated.connect(self.project.setEdited)
        self.solver.calculated.connect(self.calculated.emit)
        self.solver.toleranceChanged.connect(self.toleranceChanged.emit)
        self.solver.toleranceReached.connect(self.toleranceReached.emit)

    def changeCanvas(self):
        self.queueUpdateEvent(Reason.canvasChanged, self.project.canvas())
        self.restart()

    def changeAlphaMatte(self):
        self.queueUpdateEvent(Reason.alphaMatteChanged, self.project.alphaMatte())
        self.restart()

    def changeTrimapPreview(self):
        self.queueUpdateEvent(Reason.trimapPreviewChanged, self.project.trimapPreview())
        self.restart()

    def changeMethod(self, method: Method):
        self.queueUpdateEvent(Reason.methodChanged, method)
        self.restart()

    def changeRadius(self, radius: int):
        self.queueUpdateEvent(Reason.radiusChanged, radius)
        self.restart()

    def changeEpsilon(self, epsilon: float):
        self.queueUpdateEvent(Reason.epsilonChanged, epsilon)
        self.restart()

    def changeTolerance(self, tolerance: int):
        self.queueUpdateEvent(Reason.rtolChanged, tolerance)
        self.restart()

    def changeLambda(self, lmd: int):
        self.queueUpdateEvent(Reason.lambdaChanged, lmd)
        self.restart()

    def changePreconditioner(self, preconditioner: Preconditioner):
        self.queueUpdateEvent(Reason.preconditionerChanged, preconditioner)
        self.restart()

    def changeKernel(self, kernel: Kernel):
        self.queueUpdateEvent(Reason.kernelChanged, kernel)
        self.restart()

    def changePostIter(self, postIter: int):
        self.queueUpdateEvent(Reason.postIterChanged, postIter)
        self.restart()

    def changePreIter(self, preIter: int):
        self.queueUpdateEvent(Reason.preIterChanged, preIter)
        self.restart()

    def changePrintError(self, printError:bool):
        self.queueUpdateEvent(Reason.printErrorChanged, printError)

    def start(self):
        self.unblockSolver()
        self.started.emit()

    def stop(self):
        if not self.isStopped():
            if self.isPaused():
                self.pauseEvent.set()
            self.queueEvent(self.stopEvent)
            self.stopped.emit()

    def pause(self):
        if not self.isPaused():
            self.queueEvent(self.pauseEvent)
            self.paused.emit()

    def restart(self):
        if self.isWaiting():
            self.continueEvent.set()

    def trimapUpdated(self, rect: qtc.QRect):
        self.queueUpdateEvent(Reason.trimapChanged, rect)
        self.restart()

    def queueUpdateEvent(self, reason: Reason, value=None):
        self.queueEvent(UpdateEvent(reason, value))

    def queueEvent(self, event: Event):
        event.clear()
        self.eventQueue.put_nowait(event)

    def unblockSolver(self):
        self.pauseEvent.set()
        self.stopEvent.set()
        self.continueEvent.set()

    def isPaused(self):
        return not self.pauseEvent.isSet()

    def isStopped(self):
        return not self.stopEvent.isSet()

    def isWaiting(self):
        return not self.continueEvent.isSet()

    def clearEventQueue(self):
        while not self.eventQueue.empty():
            self.eventQueue.get_nowait()

    def close(self):
        self.clearEventQueue()
        self.queueEvent(QuitEvent())
        self.unblockSolver()
        self.solver.join()
