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

from abc import ABC, abstractmethod
from mktxp.rsc.ast import RSCConfig


class BaseMiddleware(ABC):
    """
    Abstract base class for AST mutation middlewares.
    """

    @abstractmethod
    def process(self, config: RSCConfig) -> RSCConfig:
        """
        Mutates or transforms the AST config and returns the result.
        """
        pass
