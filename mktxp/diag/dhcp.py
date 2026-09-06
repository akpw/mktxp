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
from mktxp.cli.output.dhcp_out import DHCPOutput


class DHCPDiagHandler(BaseDiagHandler):
    """Diagnostic handler for DHCP leases."""

    name = "dhcp"
    cmd_flags = ["-dc", "--dhcp_clients"]
    cmd_prefixes = ["-dc", "--dhcp"]
    cmd_dest = "dhcp_clients"
    cmd_help = "DHCP clients metrics"
    filter_group_title = "DHCP Server Filters (-dc)"
    help_prefixes = ["-dc", "-d", "--dhcp", "--unidentified", "--static", "--dynamic", "--active-only", "--inactive-only"]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-dc",
            "--dhcp_clients",
            dest="dhcp_clients",
            help="DHCP clients metrics",
            action="store_true",
        )

    def register_filter_options(self, parser) -> None:
        group = parser.add_argument_group(self.filter_group_title)
        group.add_argument(
            "--unidentified",
            dest="unidentified",
            help="Show unidentified devices with no hostname and no comment",
            action="store_true",
            default=False,
        )
        lease_type_group = group.add_mutually_exclusive_group()
        lease_type_group.add_argument(
            "--static",
            dest="static_only",
            help="Show static leases only",
            action="store_true",
            default=False,
        )
        lease_type_group.add_argument(
            "--dynamic",
            dest="dynamic_only",
            help="Show dynamic leases only",
            action="store_true",
            default=False,
        )
        active_status_group = group.add_mutually_exclusive_group()
        active_status_group.add_argument(
            "--active-only",
            dest="active_only",
            help="Show actively bound leases only (hide stale/waiting)",
            action="store_true",
            default=False,
        )
        active_status_group.add_argument(
            "--inactive-only",
            dest="inactive_only",
            help="Show inactive/waiting leases only (offline devices)",
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

        unidentified = args.get("unidentified", False)
        static_only = args.get("static_only", False)
        dynamic_only = args.get("dynamic_only", False)
        active_only = args.get("active_only", False)
        inactive_only = args.get("inactive_only", False)

        DHCPOutput.clients_summary(
            router_entry,
            include=include,
            exclude=exclude,
            unidentified=unidentified,
            static_only=static_only,
            dynamic_only=dynamic_only,
            active_only=active_only,
            inactive_only=inactive_only,
        )
