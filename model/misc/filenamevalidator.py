#Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)

from PyQt5.QtGui import QValidator
from typing import Tuple
import re


class FileNameValidator(QValidator):

    def __init__(self):
        super(FileNameValidator, self).__init__()
        self.regex = re.compile(r"^[a-zA-Z0-9]+[a-zA-Z0-9-_]*$")

    def validate(self, string: str, index: int) -> Tuple[QValidator.State, str, int]:
        if not string:
            return (QValidator.Intermediate, string, index)
        if self.regex.match(string):
            return (QValidator.Acceptable, string, index)
        else:
            return (QValidator.Invalid, string, index)
