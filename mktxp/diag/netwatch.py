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
    cmd_prefixes = ["-nw", "--net"]
    cmd_dest = "netwatch"
    cmd_help = "Netwatch metrics"
    filter_group_title = "Netwatch Filters (-nw)"
    help_prefixes = ["-nw", "--net", "--down-only", "--up-only"]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-nw",
            "--netwatch",
            dest="netwatch",
            help="Netwatch metrics",
            action="store_true",
        )

    def register_filter_options(self, parser) -> None:
        group = parser.add_argument_group(self.filter_group_title)
        status_group = group.add_mutually_exclusive_group()
        status_group.add_argument(
            "--down-only",
            dest="down_only",
            help="Show unreachable/down targets only",
            action="store_true",
            default=False,
        )
        status_group.add_argument(
            "--up-only",
            dest="up_only",
            help="Show reachable/up targets only",
            action="store_true",
            default=False,
        )

    def execute(self, router_entry, args: dict) -> None:
        include = args.get("include") or []
        exclude = args.get("exclude") or []
        if isinstance(include, str):
            include = [include]
        if isinstance(exclude, str):
            exclude = [exclude]

        down_only = args.get("down_only", False)
        up_only = args.get("up_only", False)

        NetwatchOutput.clients_summary(
            router_entry,
            include=include,
            exclude=exclude,
            down_only=down_only,
            up_only=up_only,
        )
