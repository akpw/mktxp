# coding=utf8
## Copyright (c) 2026 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

from typing import List
from .base import BaseHandler


class ConfiguredHandler(BaseHandler):
    """
    Handler dynamically instantiated based on path subscriptions defined in configuration.
    """

    def __init__(self, name: str, patterns: List[str], index: int = 0):
        super().__init__(name=name, patterns=patterns, index=index)
