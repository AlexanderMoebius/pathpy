#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py -- pathpy init file
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2019-09-23 14:55 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
__version__ = '3.0.0'

from .utils.config import config
from .utils.logger import logger

from .classes import *
from .algorithms import *
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
