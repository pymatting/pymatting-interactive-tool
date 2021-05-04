# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

import unittest
from PyQt5.QtGui import QValidator
from model.misc import FileNameValidator


class TestFileNameValidator(unittest.TestCase):
    def testFileNamesAcceptable(self):
        validator = FileNameValidator()
        self.assertEqual(QValidator.Acceptable, validator.validate("a", 0)[0])
        self.assertEqual(QValidator.Acceptable, validator.validate("1", 0)[0])
        self.assertEqual(QValidator.Acceptable, validator.validate("9", 0)[0])
        self.assertEqual(
            QValidator.Acceptable,
            validator.validate("023aaBc_Dwewq-qecsadWd23asfdse", 0)[0],
        )

    def testFileNamesInvalid(self):
        validator = FileNameValidator()
        self.assertEqual(QValidator.Invalid, validator.validate("_", 0)[0])
        self.assertEqual(QValidator.Invalid, validator.validate("-", 0)[0])
        self.assertEqual(
            QValidator.Invalid, validator.validate("023aaBc.Dwewq-qecsadWd23", 0)[0]
        )
        self.assertEqual(QValidator.Invalid, validator.validate(".", 0)[0])
        self.assertEqual(QValidator.Invalid, validator.validate("?", 0)[0])

    def testFileNamesIntermediate(self):
        validator = FileNameValidator()
        self.assertEqual(QValidator.Intermediate, validator.validate("", 0)[0])
