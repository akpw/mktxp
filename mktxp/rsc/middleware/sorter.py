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

from typing import Set
from mktxp.rsc.ast import RSCConfig, CommandNode
from .base import BaseMiddleware


ORDERED_PATHS: Set[str] = {
    '/ip firewall filter',
    '/ipv6 firewall filter',
    '/ip firewall nat',
    '/ipv6 firewall nat',
    '/ip firewall mangle',
    '/ipv6 firewall mangle',
    '/ip firewall raw',
    '/ipv6 firewall raw',
    '/ip route',
    '/ipv6 route',
    '/routing rule',
    '/interface bridge port',
    '/interface bridge vlan',
    '/ip dhcp-server lease'
}


class DeterminismSorter(BaseMiddleware):
    """
    Alphabetically sorts commands in Unordered paths to guarantee deterministic,
    zero-diff Git outputs, while strictly preserving top-down order in stateful/ordered paths.
    """

    def process(self, config: RSCConfig) -> RSCConfig:
        for section in config.sections:
            if self._is_ordered_path(section.path):
                # Never sort ordered/stateful paths
                continue

            # Sort unordered commands
            section.commands.sort(key=self._get_sort_key)

        return config

    def _is_ordered_path(self, path: str) -> bool:
        norm_path = path.strip()
        return any(norm_path == op or norm_path.startswith(op + ' ') or norm_path.startswith(op + '/') for op in ORDERED_PATHS)

    def _get_sort_key(self, cmd: CommandNode) -> tuple:
        # Sort by specific known parameters
        if cmd.command != 'add':
            return (0, cmd.target or '', cmd.find_expr or '')

        if 'list' in cmd.params and 'interface' in cmd.params:
            return (1, cmd.params.get('list', ''), cmd.params.get('interface', ''))

        if 'name' in cmd.params:
            # Strip quotes if present for clean alphabetic sorting
            raw_name = cmd.params['name'].strip('"\'')
            return (2, raw_name.lower())

        if 'interface' in cmd.params:
            return (3, cmd.params['interface'].strip('"\'').lower())

        if 'address' in cmd.params:
            return (4, cmd.params['address'].strip('"\'').lower())

        # Fallback to key-value string representation
        return (5, " ".join(f"{k}={v}" for k, v in cmd.params.items()))
