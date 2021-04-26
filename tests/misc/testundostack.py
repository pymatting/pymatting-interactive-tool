#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from model.misc import UndoStack


class TestUndoStack(unittest.TestCase):

    def test(self):
        maxSize = 100
        undoStack = UndoStack(maxSize)
        for i in range(maxSize):
            undoStack.push(i)
        undos = []
        for i in range(maxSize):
            undos.append(undoStack.undo())
        self.assertEqual(list(reversed(range(maxSize))), undos)
        redos = []
        for i in range(maxSize):
            redos.append(undoStack.redo())
        self.assertEqual(list(range(maxSize)), redos)

        for i in range(maxSize, maxSize * 2):
            undoStack.push(i)

        undos = []
        for i in range(maxSize):
            undos.append(undoStack.undo())
        self.assertEqual(list(reversed(range(maxSize, maxSize * 2))), undos)

        redos = []
        for i in range(maxSize):
            redos.append(undoStack.redo())
        self.assertEqual(list(range(maxSize, maxSize * 2)), redos)

        redos = []
        for i in range(maxSize):
            redos.append(undoStack.redo())
        self.assertEqual([None for _ in range(maxSize)], redos)

        for i in range(maxSize):
            undos.append(undoStack.undo())

        undos = []
        for i in range(maxSize):
            undos.append(undoStack.undo())

        self.assertEqual([None for _ in range(maxSize)], undos)
