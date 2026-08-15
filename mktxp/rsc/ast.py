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

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CommandNode:
    command: str
    target: Optional[str] = None
    find_expr: Optional[str] = None
    params: OrderedDict = field(default_factory=OrderedDict)
    flags: List[str] = field(default_factory=list)
    leading_comments: List[str] = field(default_factory=list)
    trailing_comment: Optional[str] = None
    note_comment: Optional[str] = None
    raw_line: Optional[str] = None

    def clone(self) -> 'CommandNode':
        return CommandNode(
            command=self.command,
            target=self.target,
            find_expr=self.find_expr,
            params=OrderedDict(self.params),
            flags=list(self.flags),
            leading_comments=list(self.leading_comments),
            trailing_comment=self.trailing_comment,
            note_comment=self.note_comment,
            raw_line=self.raw_line
        )


@dataclass
class SectionNode:
    path: str
    commands: List[CommandNode] = field(default_factory=list)
    leading_comments: List[str] = field(default_factory=list)

    def clone(self) -> 'SectionNode':
        return SectionNode(
            path=self.path,
            commands=[cmd.clone() for cmd in self.commands],
            leading_comments=list(self.leading_comments)
        )


@dataclass
class ScriptNode:
    name: str
    source_code: str
    original_command: CommandNode


@dataclass
class RSCConfig:
    sections: List[SectionNode] = field(default_factory=list)
    header_comments: List[str] = field(default_factory=list)
    extracted_scripts: List[ScriptNode] = field(default_factory=list)

    def clone(self) -> 'RSCConfig':
        return RSCConfig(
            sections=[sec.clone() for sec in self.sections],
            header_comments=list(self.header_comments),
            extracted_scripts=list(self.extracted_scripts)
        )
