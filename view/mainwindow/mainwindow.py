# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from strings import *
from math import log10
from model.enum import Control, Color, Mode, Status
from model.misc import Project, FileHandler, Controller
from model.util import showWarning
from view.icon import Icon
from view.toolbutton import ToolButton, ColorToolButton
from view.splitter import HSplitter
from view.graphicsview import LeftGraphicsView, RightGraphicsView
from view.graphicsscene import LeftGraphicsScene, RightGraphicsScene
from view.toolbar import ToolBar
from view.action import Action
from view.menubar import MenuBar
from view.treeview import FileExplorerTreeView
from view.dockwidget import FileExplorerDockWidget
from view.dialog import SolverSettingsDialog, ScaleProjectDialog

APPLICATION_NAME = "PyMatting Interactive Tool"


class MainWindow(qtw.QMainWindow):
    def __init__(self, primaryScreenSize: qtc.QSize, parent=None):
        super(MainWindow, self).__init__(parent)
        self.project = Project.empty()
        self.resize(primaryScreenSize * 0.7)
        self.setupCentralWidget(self.project)
        self.setupWidgets()
        self.setupWindowTitle()
        self.setupDialogs()
        self.setupConnections()
        self.show()
        self.fitInViewAction.trigger()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SETUP                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    def setupWidgets(self):
        self.setupToolBar()
        self.setupFileExplorer()
        self.setupMenubar()
        self.setupStatusBar()
        self.setupSolver()
        self.fileHandler = FileHandler(self.project, self)

    def setupDialogs(self):
        self.solverSettingsDialog = SolverSettingsDialog()
        self.scaleDialog = ScaleProjectDialog(self.project)

    def setupSolver(self):
        self.controller = Controller(self.project)

    def setupConnections(self):
        """Toolbuttons"""
        self.startToolButton.pressed.connect(self.controller.start)
        self.pauseToolButton.pressed.connect(self.controller.pause)
        self.stopToolButton.pressed.connect(self.controller.stop)
        self.stopToolButton.pressed.connect(self.project.clearAlphaMatte)
        self.brushToolButton.pressed.connect(self.leftGraphicsView.setMode)
        self.paintbucketToolButton.pressed.connect(self.leftGraphicsView.setMode)
        self.cropToolButton.pressed.connect(self.leftGraphicsView.setMode)
        self.dragToolButton.pressed.connect(self.leftGraphicsView.setMode)
        self.dragToolButton.toggled.connect(self.leftGraphicsView.enableDrag)
        self.dragToolButton.toggled.connect(self.rightGraphicsView.enableDrag)
        self.previewToolButton.pressed.connect(
            self.rightGraphicsScene.toggleCutoutPreview
        )
        self.previewToolButton.pressed.connect(self.changePreviewToolButtonIcon)
        self.clearTrimapToolButton.pressed.connect(
            self.leftGraphicsScene.clearTrimapPreview
        )
        self.clearTrimapToolButton.pressed.connect(self.project.setEdited)
        self.clearTrimapToolButton.pressed.connect(
            self.leftGraphicsScene.invalidateForeground
        )
        self.removeNewBackgroundToolButton.pressed.connect(
            self.project.removeNewBackground
        )
        self.removeNewBackgroundToolButton.pressed.connect(
            self.rightGraphicsScene.invalidateForeground
        )
        self.fileExplorerToolButton.clicked.connect(
            self.fileExplorerDockWidget.setVisible
        )
        self.colorBleedToolButton.clicked.connect(self.project.setReduceColorBleeding)
        self.increaseSmoothnessToolButton.clicked.connect(
            self.solverSettingsDialog.logIncreaseEpsilon
        )
        self.increaseSmoothnessToolButton.clicked.connect(self.showEpsilonChanges)
        self.decreaseSmoothnessToolButton.clicked.connect(
            self.solverSettingsDialog.logDecreaseEpsilon
        )
        self.decreaseSmoothnessToolButton.clicked.connect(self.showEpsilonChanges)
        self.scaleToolButton.pressed.connect(self.scaleDialog.show)
        """ Actions """
        self.undoAction.triggered.connect(self.leftGraphicsScene.undo)
        self.redoAction.triggered.connect(self.leftGraphicsScene.redo)
        self.fitInViewAction.triggered.connect(self.leftGraphicsView.fitInView)
        self.fitInViewAction.triggered.connect(self.rightGraphicsView.fitInView)
        self.saveAsAction.triggered.connect(self.fileHandler.saveAs)
        self.saveAction.triggered.connect(self.fileHandler.save)
        self.openAction.triggered.connect(self.fileHandler.open)
        self.newAction.triggered.connect(self.fileHandler.new)
        self.quitAction.triggered.connect(self.close)
        self.zoomInAction.triggered.connect(self.leftGraphicsView.zoomIn)
        self.zoomInAction.triggered.connect(self.rightGraphicsView.zoomIn)
        self.zoomOutAction.triggered.connect(self.leftGraphicsView.zoomOut)
        self.zoomOutAction.triggered.connect(self.rightGraphicsView.zoomOut)
        self.solverSettingsAction.triggered.connect(self.solverSettingsDialog.show)
        """ project """
        self.project.edited.connect(self.updatedWindowTitle)
        self.project.newBackgroundChanged.connect(self.enablePreview)
        # self.project.fileRenamed.connect(self.fileExplorerTreeView.updateModel)
        # self.project.canvasChanged.connect(self.pauseToolButton.click)
        """ pushbutton """
        self.colorToolButton.pressed.connect(self.leftGraphicsScene.toggleDrawMode)
        """ graphicscenes """
        # self.project.canvasChanged.connect(self.updatedWindowTitle)
        self.leftGraphicsScene.colorChanged.connect(
            self.colorToolButton.setBackgroundColor
        )
        self.leftGraphicsScene.drawn.connect(self.controller.trimapUpdated)
        self.leftGraphicsScene.requestStatusMessage.connect(self.showStatusMessage)
        self.scaleDialog.requestScale.connect(
            self.leftGraphicsScene.requestScaling.emit
        )
        """ graphicsview """
        self.leftGraphicsView.requestNewProject.connect(self.fileHandler.new)
        self.leftGraphicsView.dragEnabled.connect(self.onDragEnabled)
        self.rightGraphicsView.dragEnabled.connect(self.onDragEnabled)
        """ splitter """
        self.splitter.splitterMoved.connect(self.fitInViewAction.trigger)
        self.splitter.collapsedRight.connect(self.rightGraphicsScene.setDisabled)
        """ File Explorer """
        self.fileExplorerDockWidget.visibilityChanged.connect(
            self.fitInViewAction.trigger
        )
        self.fileExplorerTreeView.fileRenamed.connect(self.project.renameFile)
        self.fileExplorerTreeView.fileRenamed.connect(
            self.fileHandler.updateSettingsFile
        )
        self.fileExplorerTreeView.requestOpenNewProject.connect(self.fileHandler.open)
        """ Controller """
        self.controller.started.connect(lambda: self.pauseToolButton.setEnabled(True))
        self.controller.started.connect(lambda: self.stopToolButton.setEnabled(True))
        self.controller.started.connect(lambda: self.startToolButton.setEnabled(False))

        self.controller.paused.connect(lambda: self.pauseToolButton.setEnabled(False))
        self.controller.paused.connect(lambda: self.stopToolButton.setEnabled(True))
        self.controller.paused.connect(lambda: self.startToolButton.setEnabled(True))

        self.controller.stopped.connect(lambda: self.pauseToolButton.setEnabled(False))
        self.controller.stopped.connect(lambda: self.stopToolButton.setEnabled(False))
        self.controller.stopped.connect(lambda: self.startToolButton.setEnabled(True))

        self.controller.calculated.connect(self.setProgressBarValue)
        self.controller.toleranceReached.connect(self.setMaximumProgressBarValue)
        self.controller.toleranceChanged.connect(self.calculationProgressBar.reset)

        """ Dialog """
        self.solverSettingsDialog.methodChanged.connect(self.controller.changeMethod)
        self.solverSettingsDialog.radiusChanged.connect(self.controller.changeRadius)
        self.solverSettingsDialog.epsilonChanged.connect(self.controller.changeEpsilon)
        self.solverSettingsDialog.toleranceChanged.connect(
            self.controller.changeTolerance
        )
        self.solverSettingsDialog.lambdaChanged.connect(self.controller.changeLambda)
        self.solverSettingsDialog.preconditionerChanged.connect(
            self.controller.changePreconditioner
        )
        self.solverSettingsDialog.kernelChanged.connect(self.controller.changeKernel)
        self.solverSettingsDialog.postIterChanged.connect(
            self.controller.changePostIter
        )
        self.solverSettingsDialog.preIterChanged.connect(self.controller.changePreIter)
        self.solverSettingsDialog.hasVcycle.connect(
            self.leftGraphicsScene.disableUpdateOnMouseMove
        )
        self.solverSettingsDialog.printErrorChanged.connect(
            self.controller.changePrintError
        )
        """ Filehandler """
        self.fileHandler.finished.connect(self.showStatusMessage)
        self.fileHandler.error.connect(showWarning)

    def setupCentralWidget(self, project):
        self.splitter = HSplitter(self)
        self.leftGraphicsScene = LeftGraphicsScene(project)
        self.leftGraphicsView = LeftGraphicsView(
            self.leftGraphicsScene, project, self.splitter
        )
        self.rightGraphicsScene = RightGraphicsScene(project)
        self.rightGraphicsView = RightGraphicsView(
            self.rightGraphicsScene, project, self.splitter
        )
        self.splitter.addWidget(self.leftGraphicsView)
        self.splitter.addWidget(self.rightGraphicsView)
        self.setCentralWidget(self.splitter)

    def setupFileExplorer(self):
        self.fileExplorerTreeView = FileExplorerTreeView(self.project)
        self.fileExplorerDockWidget = FileExplorerDockWidget(self.fileExplorerTreeView)
        self.addDockWidget(
            qtc.Qt.LeftDockWidgetArea, self.fileExplorerDockWidget, qtc.Qt.Vertical
        )
        self.fileExplorerDockWidget.hide()

    def setupToolBar(self):
        self.toolBar = ToolBar(toolBarTitle, self)
        self.startToolButton = ToolButton(
            Control.start,
            Icon(playIconName),
            startToolTip,
            autoExclusive=False,
            checkable=False,
        )
        self.pauseToolButton = ToolButton(
            Control.start,
            Icon(pauseIconName),
            pauseToolTip,
            autoExclusive=False,
            checkable=False,
            enabled=False,
        )
        self.stopToolButton = ToolButton(
            Control.start,
            Icon(stopIconName),
            stopToolTip,
            autoExclusive=False,
            checkable=False,
            enabled=False,
        )
        self.brushToolButton = ToolButton(
            Mode.brush,
            Icon(brushIconName),
            brushToolTip,
            checked=True,
            shortcut=qtc.Qt.Key_B,
        )
        self.paintbucketToolButton = ToolButton(
            Mode.paintBucket,
            Icon(paintbucketIconName),
            paintBucketToolTip,
            shortcut=qtc.Qt.Key_P,
        )
        self.cropToolButton = ToolButton(
            Mode.crop, Icon(cropIconName), cropToolTip, shortcut=qtc.Qt.Key_C
        )
        self.scaleToolButton = ToolButton(
            None,
            Icon(scaleIconName),
            scaleToolTip,
            shortcut=qtc.Qt.Key_S,
            checkable=False,
            checked=False,
            autoExclusive=False,
        )
        self.dragToolButton = ToolButton(
            Mode.drag, Icon(handIconName), dragToolTip, shortcut=qtc.Qt.Key_D
        )
        self.clearTrimapToolButton = ToolButton(
            None,
            Icon(clearTrimapIconName),
            clearTrimapToolTip,
            autoExclusive=False,
            checkable=False,
        )
        self.removeNewBackgroundToolButton = ToolButton(
            None,
            Icon(removeNewBackgroundIconName),
            clearNewBackgroundToolTip,
            autoExclusive=False,
            checkable=False,
        )
        self.previewToolButton = ToolButton(
            None,
            Icon(hideIconName),
            cutoutPreviewToolTip,
            shortcut=qtc.Qt.Key_R,
            autoExclusive=False,
            checkable=False,
        )
        self.colorToolButton = ColorToolButton(
            colorPushButtonToolTip, Color.lightGreen.value
        )

        self.increaseSmoothnessToolButton = ToolButton(
            None,
            Icon(increaseIconName),
            increaseSmoothnessToolTip,
            autoExclusive=False,
            checkable=False,
        )
        self.decreaseSmoothnessToolButton = ToolButton(
            None,
            Icon(decreaseIconName),
            decreaseSmoothnessToolTip,
            autoExclusive=False,
            checkable=False,
        )
        self.fileExplorerToolButton = ToolButton(
            None,
            Icon(fileTreeIconName),
            fileTreeToolTip,
            autoExclusive=False,
            checkable=True,
        )

        self.colorBleedToolButton = ToolButton(
            None,
            Icon(colorBleedingIconName),
            colorBleedToolTip,
            autoExclusive=False,
            checked=True,
        )
        self.toolBar.addWidgets(
            self.pauseToolButton, self.startToolButton, self.stopToolButton
        )
        self.toolBar.addSeparator()
        self.toolBar.addWidgets(
            self.brushToolButton,
            self.paintbucketToolButton,
            self.cropToolButton,
            self.scaleToolButton,
            self.dragToolButton,
            self.colorToolButton,
        )
        self.toolBar.addSeparator()
        self.toolBar.addWidgets(
            self.clearTrimapToolButton,
            self.removeNewBackgroundToolButton,
            self.colorBleedToolButton,
            self.previewToolButton,
        )
        self.toolBar.addSeparator()
        self.toolBar.addWidgets(
            self.increaseSmoothnessToolButton, self.decreaseSmoothnessToolButton
        )
        self.toolBar.addSeparator()
        self.toolBar.addWidgets(self.fileExplorerToolButton)
        self.addToolBar(qtc.Qt.TopToolBarArea, self.toolBar)

    def setupMenubar(self):
        self.setupFileMenu()
        self.setupEditMenu()
        self.setupViewMenu()
        self.setupSettingsMenu()
        self.setupHelpMenu()
        self.setMenuBar(MenuBar())
        self.menuBar().addMenus(
            self.menuFile,
            self.menuEdit,
            self.menuView,
            self.menuSettings,
            self.menuHelp,
        )

    def setupFileMenu(self):
        self.menuFile = qtw.QMenu(fileMenuName)
        self.newAction = Action(
            newActionName,
            self.standardIcon(qtw.QStyle.SP_FileIcon),
            qtg.QKeySequence.New,
        )
        self.openAction = Action(
            openActionName,
            self.standardIcon(qtw.QStyle.SP_DirOpenIcon),
            qtg.QKeySequence.Open,
        )
        self.saveAction = Action(
            saveActionName,
            self.standardIcon(qtw.QStyle.SP_DialogSaveButton),
            qtg.QKeySequence.Save,
        )
        self.saveAsAction = Action(saveAsActionName, shortcut=qtg.QKeySequence.SaveAs)
        self.quitAction = Action(quitActionName, shortcut=qtg.QKeySequence.Quit)
        self.menuFile.addActions(
            [
                self.newAction,
                self.openAction,
                self.saveAction,
                self.saveAsAction,
                self.quitAction,
            ]
        )

    def setupEditMenu(self):
        self.menuEdit = qtw.QMenu(editMenuName)
        self.undoAction = Action(
            undoActionName, Icon(undoIconName), qtg.QKeySequence.Undo, autoRepeat=True
        )
        self.redoAction = Action(
            redoActionName, Icon(redoIconName), qtg.QKeySequence.Redo, autoRepeat=True
        )
        self.menuEdit.addActions([self.undoAction, self.redoAction])

    def setupViewMenu(self):
        self.menuView = qtw.QMenu(viewMenuName)
        self.zoomInAction = Action(
            zoomInActionName,
            Icon(zoomInIconName),
            qtg.QKeySequence.ZoomIn,
            autoRepeat=True,
        )
        self.zoomOutAction = Action(
            zoomOutActionName,
            Icon(zoomOutIconName),
            qtg.QKeySequence.ZoomOut,
            autoRepeat=True,
        )
        self.fitInViewAction = Action(
            fitToViewActionName,
            Icon(fitInViewIconName),
            qtg.QKeySequence("ctrl+F"),
            autoRepeat=True,
        )
        self.menuView.addActions(
            [self.zoomInAction, self.zoomOutAction, self.fitInViewAction]
        )

    def setupSettingsMenu(self):
        self.menuSettings = qtw.QMenu("Settings")
        self.solverSettingsAction = Action(
            solverSettingsActionName,
            Icon(settingsIconName),
            shortcut=qtg.QKeySequence("ctrl+c"),
        )
        self.menuSettings.addActions([self.solverSettingsAction])

    def setupHelpMenu(self):
        self.menuHelp = qtw.QMenu("Help")
        self.showAuthorAction = Action("Author..", slot=self.showAuthorText)
        self.showLicenseAction = Action("License..", slot=self.showLicenseText)
        self.showCreditsAction = Action("Credits..", slot=self.showCreditsText)
        self.menuHelp.addActions(
            [self.showCreditsAction, self.showAuthorAction, self.showLicenseAction]
        )

    def showLicenseText(self):
        licensePath = qtc.QFileInfo(__file__).dir()
        licensePath.cdUp()
        licensePath.cdUp()
        with open(licensePath.filePath("COPYING"), "r") as file:
            license = file.read()
        self.showReadOnlyText("License", license)

    def showAuthorText(self):
        licensePath = qtc.QFileInfo(__file__).dir()
        licensePath.cdUp()
        licensePath.cdUp()
        with open(licensePath.filePath("AUTHOR"), "r") as file:
            author = file.read()
        self.showReadOnlyText("Author", author)

    def showCreditsText(self):
        creditsText = qtc.QFileInfo(__file__).dir()
        creditsText.cdUp()
        creditsText.cdUp()
        with open(creditsText.filePath("CREDITS"), "r") as file:
            credits = file.read()
        self.showReadOnlyText("Credits", credits)

    def showReadOnlyText(self, title, text):
        dialog = qtw.QDialog(self)
        dialog.setLayout(qtw.QVBoxLayout())
        dialog.setMinimumWidth(420)
        dialog.setMinimumHeight(400)
        dialog.setWindowTitle(title)
        textEdit = qtw.QTextBrowser()
        textEdit.setOpenExternalLinks(True)
        textEdit.setAcceptRichText(True)
        textEdit.setText(text)
        dialog.layout().addWidget(textEdit)
        dialog.show()

    def setupStatusBar(self):
        # self.canvasSizeLabel = qtw.QLabel(f"[{self.project.canvasWidth()}x{self.project.canvasHeight()}]")
        # self.statusBar().addPermanentWidget(self.canvasSizeLabel)
        self.calculationProgressBar = qtw.QProgressBar(
            alignment=qtc.Qt.AlignCenter, minimum=0, maximum=100
        )
        self.calculationProgressBar.setFixedWidth(100)
        self.calculationProgressBar.setFixedHeight(15)
        self.calculationProgressBar.setStyleSheet("color:black")
        self.statusBar().addPermanentWidget(self.calculationProgressBar)

    def setupWindowTitle(self):
        self.updatedWindowTitle(
            self.project.isEdited(), self.project.path(), self.project.title()
        )

    ####################################################################################################################
    #                                                                                                                  #
    #                                                HELPER                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def getCheckedToolButton(self):
        if self.dragToolButton.isChecked():
            return self.dragToolButton
        elif self.paintbucketToolButton.isChecked():
            return self.paintbucketToolButton
        elif self.cropToolButton.isChecked():
            return self.cropToolButton
        else:
            return self.brushToolButton

    def standardIcon(self, pixmap):
        return self.style().standardIcon(pixmap)

    ####################################################################################################################
    #                                                                                                                  #
    #                                                EVENTS                                                            #
    #                                                                                                                  #
    ####################################################################################################################

    def closeEvent(self, event: qtg.QCloseEvent) -> None:
        status = self.fileHandler.maybeSave()
        if status == Status.aborted or status == Status.failed:
            event.ignore()
        else:
            self.prepareClose(event)

    def prepareClose(self, event):
        self.stopToolButton.click()
        self.rightGraphicsScene.close()
        self.leftGraphicsScene.close()
        self.fileHandler.close()
        self.project.close()
        self.fileExplorerTreeView.close()
        self.controller.close()
        event.accept()

    def onDragEnabled(self, enabled):
        if enabled:
            self.lastButton = self.getCheckedToolButton()
            self.dragToolButton.click()
        else:
            try:
                self.lastButton.click()
            except:
                self.lastButton = None

    def resizeEvent(self, event: qtg.QResizeEvent) -> None:
        super(MainWindow, self).resizeEvent(event)
        self.fitInViewAction.trigger()

    ####################################################################################################################
    #                                                                                                                  #
    #                                                SLOTS                                                             #
    #                                                                                                                  #
    ####################################################################################################################

    @qtc.pyqtSlot(object, object)
    def setProgressBarValue(self, value, minimum):
        if value:
            minimum = -1 * log10(minimum)
            value = -1 * log10(value)
            percentage = int((value / minimum) * 100)
            self.calculationProgressBar.setValue(percentage)

    @qtc.pyqtSlot()
    def setMaximumProgressBarValue(self):
        self.calculationProgressBar.setValue(self.calculationProgressBar.maximum())

    @qtc.pyqtSlot()
    def enablePreview(self):
        if self.project.newBackground() and not self.rightGraphicsScene.showCutout():
            self.previewToolButton.click()

    @qtc.pyqtSlot(bool, str, str)
    def updatedWindowTitle(self, edited: bool, projectPath: str, projectName: str):
        if projectPath:
            title = f"{APPLICATION_NAME} - [{projectPath}] - [{self.project.canvasWidth()}x{self.project.canvasHeight()}] - {projectName} "
        else:
            title = f"{APPLICATION_NAME} - [{self.project.canvasWidth()}x{self.project.canvasHeight()}] - {projectName}"
        if edited:
            self.setWindowTitle(f"{title}*")
        else:
            self.setWindowTitle(f"{title}")

    # @qtc.pyqtSlot()
    # def updateSizeLabel(self):
    #     rect = self.project.canvas().rect()
    #     self.canvasSizeLabel.setText(f"[{rect.width()}x{rect.height()}]")

    @qtc.pyqtSlot()
    def changePreviewToolButtonIcon(self):
        if self.rightGraphicsScene.showCutout():
            self.previewToolButton.setIcon(Icon(showIconName))
        else:
            self.previewToolButton.setIcon(Icon(hideIconName))

    def showEpsilonChanges(self):
        self.showStatusMessage(
            f"Epsilon: {self.solverSettingsDialog.epsilonSpinBox.value()}"
        )

    def showStatusMessage(self, text, duration=3000):
        self.statusBar().showMessage(text, duration)
