# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from .baseview import BaseView
from view.messagebox import MessageBoxNewBackgroundOrAlpha
from model.util import showWarning
from model.misc import Image

from strings import fileIsCorruptedText


class RightGraphicsView(BaseView):
    def onDrop(self, path: str):
        image = Image(path)
        if image.isNull():
            showWarning(fileIsCorruptedText, FileNotFoundError("File not found."))
        else:
            response = MessageBoxNewBackgroundOrAlpha().exec()
            if response == MessageBoxNewBackgroundOrAlpha.Alpha:
                self.project.setAlphaMatte(image)
                self.imageDropped.emit()
            elif response == MessageBoxNewBackgroundOrAlpha.NewBackground:
                self.project.setNewBackground(image)
                self.project.resetCutoutRect()
                self.imageDropped.emit()
