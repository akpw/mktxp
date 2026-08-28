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

from mktxp.diag.base import BaseDiagHandler
from mktxp.cli.output.netwatch_out import NetwatchOutput


class NetwatchDiagHandler(BaseDiagHandler):
    """Diagnostic handler for Netwatch monitoring."""

    name = "netwatch"
    cmd_flags = ["-nw", "--netwatch"]
    cmd_dest = "netwatch"
    cmd_help = "Netwatch metrics"
    filter_group_title = "Netwatch Filters (-nw)"
    help_prefixes = ["-nw", "--net"]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-nw",
            "--netwatch",
            dest="netwatch",
            help="Netwatch metrics",
            action="store_true",
        )

    def execute(self, router_entry, args: dict) -> None:
        include = args.get("include") or []
        exclude = args.get("exclude") or []
        if isinstance(include, str):
            include = [include]
        if isinstance(exclude, str):
            exclude = [exclude]

        NetwatchOutput.clients_summary(router_entry, include=include, exclude=exclude)
