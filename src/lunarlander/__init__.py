# SPDX-License-Identifier: BSD-3-Clause

from .config import Config

config = Config()

from .engine import Engine
from . import helpers


def start(*args, **kwargs):
    eng = Engine(*args, **kwargs)
    eng.finalize()
    return eng
