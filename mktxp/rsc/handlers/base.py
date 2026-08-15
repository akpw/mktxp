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
from typing import List, Optional
from mktxp.rsc.ast import SectionNode


class BaseHandler(ABC):
    """
    Base handler in the Chain of Responsibility for claiming and organizing AST sections.
    """

    def __init__(self, name: str, patterns: List[str], index: int = 0):
        self.name = name
        self.patterns = [p.strip() for p in patterns if p.strip()]
        self.index = index
        self.claimed_sections: List[SectionNode] = []
        self.next_handler: Optional['BaseHandler'] = None

    def can_handle(self, path: str) -> bool:
        norm = path.strip()
        for p in self.patterns:
            if norm == p or norm.startswith(p + ' ') or norm.startswith(p + '/'):
                return True
        return False

    def handle(self, section: SectionNode):
        if self.can_handle(section.path):
            self.claimed_sections.append(section)
        elif self.next_handler:
            self.next_handler.handle(section)

    def get_output_filename(self, numbered: bool = True) -> str:
        if numbered and self.index > 0:
            return f"{self.index:02d}-{self.name}.rsc"
        return f"{self.name}.rsc"
