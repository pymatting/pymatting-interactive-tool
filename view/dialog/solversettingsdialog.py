#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from view.widget import FormWidget
from view.groupbox import VGroupBox
from model.enum import Method, Preconditioner, Kernel
from strings import *


class SolverSettingsDialog(qtw.QDialog):
    methodChanged = qtc.pyqtSignal(Method)
    radiusChanged = qtc.pyqtSignal(int)
    epsilonChanged = qtc.pyqtSignal(float)
    toleranceChanged = qtc.pyqtSignal(int)
    lambdaChanged = qtc.pyqtSignal(int)
    preconditionerChanged = qtc.pyqtSignal(Preconditioner)
    kernelChanged = qtc.pyqtSignal(Kernel)
    postIterChanged = qtc.pyqtSignal(int)
    preIterChanged = qtc.pyqtSignal(int)
    printErrorChanged = qtc.pyqtSignal(bool)
    hasVcycle = qtc.pyqtSignal(bool)

    def __init__(self):
        super(SolverSettingsDialog, self).__init__()
        self.setMinimumWidth(400)
        self.setWindowTitle(solverSettingsTitle)
        self.setLayout(qtw.QVBoxLayout())
        self.setupWidgets()
        self.setupButtons()
        self.setupConnections()

    def setupWidgets(self):
        self.tabWidget = qtw.QTabWidget(self)
        self.setupGeneralTab()
        self.setupMethodTab()
        self.layout().addWidget(self.tabWidget)

    def setupGeneralTab(self):
        formWidget = FormWidget()
        self.laplacianNameComboBox = formWidget.addComboBox("Laplacian", ["Closed-Form-Laplacian"], [None],
                                                            laplacianToolTip)
        self.methodComboBox = formWidget.addComboBox("Method", ["cgd", "vcycle"],
                                                     [Method.cgd, Method.vcycle], methodToolTip, 0)
        self.radiusSpinBox = formWidget.addSpinBox("Radius", 1, 5, 1, radiusToolTip, wrapping=False)
        self.epsilonSpinBox = formWidget.addDoubleSpinBox("Epsilon", 0.0000001, 1, 0.0000001 , 7, 0.0000001, epsilonToolTip, wrapping=False)
        self.toleranceSpinBox = formWidget.addSpinBox("Tolerance", 0, 99, 7, toleranceToolTip, "disabled",
                                                      wrapping=False)
        self.lambdaSpinBox = formWidget.addSpinBox("Lambda", 1, 100000, 100, lambdaToolTip, wrapping=False)
        self.printErrorCheckBox = formWidget.addCheckBox("Print Error", checked=False)
        self.tabWidget.addTab(formWidget, "General")

    def setupMethodTab(self):
        cgdFormWidget = FormWidget()
        container = qtw.QWidget()
        container.setLayout(qtw.QVBoxLayout(container))
        cgdGroupBox = VGroupBox("CGD")
        cgdGroupBox.addWidget(cgdFormWidget)
        self.preconditionerComboBox = cgdFormWidget.addComboBox("Preconditioner", ["none", "jacobi", "vcycle"],
                                                                [Preconditioner.none, Preconditioner.jacobi,
                                                                 Preconditioner.vcycle], preconditionerToolTip, 2)
        vcycleFormWidget = FormWidget()
        vcycleGroupBox = VGroupBox("V-Cycle")
        self.kernelComboBox = vcycleFormWidget.addComboBox("Kernel", ["linear", "gaussian"],
                                                           [Kernel.linear, Kernel.gaussian], kernelToolTip, 1)
        self.preIterSpinBox = vcycleFormWidget.addSpinBox("Pre-Iterations", 1, 1000, 1, preIterToolTip, wrapping=False)
        self.postIterSpinBox = vcycleFormWidget.addSpinBox("Post-Iterations", 1, 1000, 1, postIterToolTip,
                                                           wrapping=False)
        vcycleGroupBox.addWidget(vcycleFormWidget)
        container.layout().addWidget(cgdGroupBox)
        container.layout().addWidget(vcycleGroupBox)
        self.tabWidget.addTab(container, "Solver")

    def setupConnections(self):
        self.buttonBox.button(qtw.QDialogButtonBox.Ok).pressed.connect(self.accept)
        self.buttonBox.button(qtw.QDialogButtonBox.RestoreDefaults).pressed.connect(self.restoreDefaults)
        self.methodComboBox.currentIndexChanged.connect(
            lambda i: self.methodChanged.emit(self.methodComboBox.itemData(i)))
        self.methodChanged.connect(self.emitHasVcycle)
        self.radiusSpinBox.valueChanged.connect(self.radiusChanged.emit)
        self.epsilonSpinBox.valueChanged.connect(self.epsilonChanged.emit)
        self.toleranceSpinBox.valueChanged.connect(self.toleranceChanged.emit)
        self.lambdaSpinBox.valueChanged.connect(self.lambdaChanged.emit)
        self.preconditionerComboBox.currentIndexChanged.connect(
            lambda i: self.preconditionerChanged.emit(self.preconditionerComboBox.itemData(i)))
        self.preconditionerChanged.connect(self.emitHasVcycle)
        self.kernelComboBox.currentIndexChanged.connect(
            lambda i: self.kernelChanged.emit(self.kernelComboBox.itemData(i)))
        self.postIterSpinBox.valueChanged.connect(self.postIterChanged.emit)
        self.preIterSpinBox.valueChanged.connect(self.preIterChanged.emit)
        self.printErrorCheckBox.clicked.connect(self.printErrorChanged.emit)

    def emitHasVcycle(self):
        preconditioner = self.preconditionerComboBox.itemData(self.preconditionerComboBox.currentIndex())
        method = self.methodComboBox.itemData(self.methodComboBox.currentIndex())
        hasVcycle =  method == Method.vcycle or method == Method.cgd and preconditioner==Preconditioner.vcycle
        self.hasVcycle.emit(hasVcycle)

    def setupButtons(self):
        self.buttonBox = qtw.QDialogButtonBox(qtw.QDialogButtonBox.RestoreDefaults | qtw.QDialogButtonBox.Ok,
                                              qtc.Qt.Horizontal)
        self.layout().addWidget(self.buttonBox)

    def restoreDefaults(self):
        self.laplacianNameComboBox.setCurrentIndex(0)
        self.methodComboBox.setCurrentIndex(0)
        self.radiusSpinBox.setValue(1)
        self.epsilonSpinBox.setValue(0.0000001)
        self.toleranceSpinBox.setValue(7)
        self.lambdaSpinBox.setValue(100)
        self.preconditionerComboBox.setCurrentIndex(2)
        self.kernelComboBox.setCurrentIndex(1)
        self.preIterSpinBox.setValue(1)
        self.postIterSpinBox.setValue(1)


    def logIncreaseEpsilon(self):
        self.epsilonSpinBox.setValue(self.epsilonSpinBox.value() * 10.0)

    def logDecreaseEpsilon(self):
        self.epsilonSpinBox.setValue(self.epsilonSpinBox.value() / 10.0)

