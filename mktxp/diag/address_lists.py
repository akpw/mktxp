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
from mktxp.cli.output.address_list_out import AddressListOutput


class AddressListDiagHandler(BaseDiagHandler):
    """Diagnostic handler for firewall address lists."""

    name = "address_lists"
    cmd_flags = ["-al", "--address_lists"]
    cmd_prefixes = ["-al", "--addr"]
    cmd_dest = "address_lists"
    cmd_help = "Address List metrics (comma-separated list names)"
    filter_group_title = "Address List Filters (-al)"
    help_prefixes = ["-al", "--addr", "--dynamic-only", "--static-only"]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-al",
            "--address_lists",
            dest="address_lists",
            help="Address List metrics (comma-separated list names)",
            type=str,
            metavar="LISTS",
        )

    def register_filter_options(self, parser) -> None:
        group = parser.add_argument_group(self.filter_group_title)

        status_group = group.add_mutually_exclusive_group()
        if "--dynamic-only" in parser._option_string_actions:
            status_group._group_actions.append(parser._option_string_actions["--dynamic-only"])
        else:
            status_group.add_argument(
                "--dynamic-only",
                dest="dynamic_only",
                help="Show dynamic address list entries only (e.g. threat bans, scanners)",
                action="store_true",
                default=False,
            )

        if "--static-only" in parser._option_string_actions:
            status_group._group_actions.append(parser._option_string_actions["--static-only"])
        else:
            status_group.add_argument(
                "--static-only",
                dest="static_only",
                help="Show static address list entries only",
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

        dynamic_only = args.get("dynamic_only", False)
        static_only = args.get("static_only", False)

        AddressListOutput.clients_summary(
            router_entry,
            args.get("address_lists"),
            include=include,
            exclude=exclude,
            dynamic_only=dynamic_only,
            static_only=static_only,
        )
