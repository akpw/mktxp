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
from mktxp.cli.output.conn_stats_out import ConnectionsStatsOutput


class ConnectionDiagHandler(BaseDiagHandler):
    """Diagnostic handler for IP connection tracking."""

    name = "connections"
    cmd_flags = ["-cn", "--conn_stats"]
    cmd_dest = "conn_stats"
    cmd_help = "IP connections stats"
    filter_group_title = "IP Connections Filters (-cn)"
    help_prefixes = ["-cn", "--conn"]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-cn",
            "--conn_stats",
            dest="conn_stats",
            help="IP connections stats",
            action="store_true",
        )

    def execute(self, router_entry, args: dict) -> None:
        include = args.get("include") or []
        exclude = args.get("exclude") or []
        if isinstance(include, str):
            include = [include]
        if isinstance(exclude, str):
            exclude = [exclude]

        ConnectionsStatsOutput.clients_summary(router_entry, include=include, exclude=exclude)
