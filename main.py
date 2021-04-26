#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from view.mainwindow import MainWindow
from view.icon import Icon
from PyQt5 import QtWidgets as qtw

try:
    # On windows
    import PyQt5.QtWinExtras as qte
except:
    # Not on windows
    pass

if __name__ == '__main__':
    import sys
    app = qtw.QApplication(sys.argv)
    app.setWindowIcon(Icon("lemur"))
    try:
        # Fixes issue where application icon does not show in the taskbar in a windows system. Tested on windows 10
        # Try catch needed, because import of QtWinExtras fails on linux system
        qte.QtWin.setCurrentProcessExplicitAppUserModelID("PyMatting Interactive Tool")
    except:
        pass
    mainWindow = MainWindow(app.primaryScreen().size())
    sys.exit(app.exec_())
