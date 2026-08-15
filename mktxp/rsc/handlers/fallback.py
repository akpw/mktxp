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

from .base import BaseHandler


class DefaultHandler(BaseHandler):
    """
    Fallback handler at the end of the chain that claims all unhandled AST sections,
    guaranteeing zero configuration loss.
    """

    def __init__(self, name: str = 'other', index: int = 99):
        super().__init__(name=name, patterns=['/'], index=index)

    def can_handle(self, path: str) -> bool:
        return True
