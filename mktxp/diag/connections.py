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
from mktxp.cli.config import config_handler
from mktxp.cli.output.conn_stats_out import ConnectionsStatsOutput


class ConnectionDiagHandler(BaseDiagHandler):
    """Diagnostic handler for IP connection tracking."""

    name = "connections"
    cmd_flags = ["-cn", "--conn_stats"]
    cmd_prefixes = ["-cn", "--conn"]
    cmd_dest = "conn_stats"
    cmd_help = "IP connections stats"
    filter_group_title = "IP Connections Filters (-cn)"
    help_prefixes = ["-cn", "--conn", "--top", "--min-conns"]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-cn",
            "--conn_stats",
            dest="conn_stats",
            help="IP connections stats",
            action="store_true",
        )

    def register_filter_options(self, parser) -> None:
        diag_conf = (
            config_handler.diag_config()
            if hasattr(config_handler, "diag_config")
            else {}
        )
        top_def = diag_conf.get("top_connections_count", 10)

        group = parser.add_argument_group(self.filter_group_title)
        group.add_argument(
            "--top",
            dest="top",
            help=f"Show top N talkers (default: {top_def})",
            nargs="?",
            const=True,
            default=None,
            metavar="N",
        )
        group.add_argument(
            "--min-conns",
            dest="min_conns",
            help="Filter out hosts with fewer than N active connections",
            type=int,
            default=None,
            metavar="N",
        )

    def execute(self, router_entry, args: dict) -> None:
        include = args.get("include") or []
        exclude = args.get("exclude") or []
        if isinstance(include, str):
            include = [include]
        if isinstance(exclude, str):
            exclude = [exclude]

        top = args.get("top")
        min_conns = args.get("min_conns")

        ConnectionsStatsOutput.clients_summary(
            router_entry,
            include=include,
            exclude=exclude,
            top=top,
            min_conns=min_conns,
        )
