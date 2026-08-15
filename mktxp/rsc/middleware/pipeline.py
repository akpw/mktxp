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

from typing import List, Optional
from mktxp.rsc.ast import RSCConfig
from .base import BaseMiddleware
from .sorter import DeterminismSorter
from .scripts import ScriptExtractor
from .sanitizer import Sanitizer


class MiddlewarePipeline:
    """
    Orchestrates the sequential execution of AST middlewares.
    """

    def __init__(self, middlewares: Optional[List[BaseMiddleware]] = None):
        self.middlewares: List[BaseMiddleware] = middlewares if middlewares is not None else [
            DeterminismSorter(),
            ScriptExtractor(),
            Sanitizer()
        ]

    def add_middleware(self, middleware: BaseMiddleware) -> 'MiddlewarePipeline':
        self.middlewares.append(middleware)
        return self

    def execute(self, config: RSCConfig) -> RSCConfig:
        current_config = config
        for middleware in self.middlewares:
            current_config = middleware.process(current_config)
        return current_config
