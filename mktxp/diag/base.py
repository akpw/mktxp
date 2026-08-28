# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
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


class BaseDiagHandler(ABC):
    """Abstract base class for diagnostic domain handlers."""

    name: str = ""
    cmd_flags: List[str] = []
    cmd_dest: str = ""
    cmd_help: str = ""
    filter_group_title: Optional[str] = None
    help_prefixes: List[str] = []

    @abstractmethod
    def register_diag_cmd(self, parser_group) -> None:
        """Register the diagnostic command switch (e.g. -cc, -dc) into the Diagnostic Commands group."""
        pass

    def register_filter_options(self, parser) -> None:
        """Register specialized filter arguments (e.g. --low-signal, --unidentified) into their dedicated group."""
        pass

    def matches_help_target(self, argv: List[str]) -> bool:
        """Check if any argument in argv matches this handler for targeted context-aware help."""
        if not self.help_prefixes:
            return any(arg in self.cmd_flags for arg in argv)
        for arg in argv:
            if arg in self.cmd_flags:
                return True
            for prefix in self.help_prefixes:
                if arg.startswith(prefix):
                    return True
        return False

    @abstractmethod
    def execute(self, router_entry, args: dict) -> None:
        """Execute data collection, filtering, and table rendering for this diagnostic domain."""
        pass
