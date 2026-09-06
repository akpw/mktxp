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

from typing import List, Optional
from mktxp.diag.base import BaseDiagHandler
from mktxp.diag.wireless import WirelessDiagHandler
from mktxp.diag.dhcp import DHCPDiagHandler
from mktxp.diag.connections import ConnectionDiagHandler
from mktxp.diag.kid_control import KidControlDiagHandler
from mktxp.diag.address_lists import AddressListDiagHandler
from mktxp.diag.netwatch import NetwatchDiagHandler


class DiagRegistry:
    """Registry of all available diagnostic domain handlers."""

    _handlers: List[BaseDiagHandler] = [
        WirelessDiagHandler(),
        DHCPDiagHandler(),
        ConnectionDiagHandler(),
        KidControlDiagHandler(),
        AddressListDiagHandler(),
        NetwatchDiagHandler(),
    ]

    @classmethod
    def get_handlers(cls) -> List[BaseDiagHandler]:
        return cls._handlers

    @classmethod
    def get_active_handler(cls, args: dict) -> Optional[BaseDiagHandler]:
        """Find the diagnostic handler matching the active CLI command switch."""
        for handler in cls._handlers:
            if handler.name == "wireless":
                if args.get("capsman_clients") or args.get("wifi_clients"):
                    return handler
            elif handler.cmd_dest and args.get(handler.cmd_dest):
                return handler
        return None

    @classmethod
    def get_matching_help_handlers(cls, argv: List[str]) -> List[BaseDiagHandler]:
        """Find handlers that match command switches in argv for targeted help formatting."""
        # 1. Prioritize primary command switches (e.g. -kc, -cn, --wifi)
        cmd_matches = [h for h in cls._handlers if h.matches_cmd(argv)]
        if cmd_matches:
            return cmd_matches

        # 2. If no primary command switch was provided, match by filter prefixes (e.g. --top, --rate-above)
        return [h for h in cls._handlers if h.matches_help_target(argv)]
