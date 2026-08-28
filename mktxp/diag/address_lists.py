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
    cmd_dest = "address_lists"
    cmd_help = "Address List metrics (comma-separated list names)"
    filter_group_title = "Address List Filters (-al)"
    help_prefixes = ["-al", "--addr"]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-al",
            "--address_lists",
            dest="address_lists",
            help="Address List metrics (comma-separated list names)",
            type=str,
            metavar="LISTS",
        )

    def execute(self, router_entry, args: dict) -> None:
        include = args.get("include") or []
        exclude = args.get("exclude") or []
        if isinstance(include, str):
            include = [include]
        if isinstance(exclude, str):
            exclude = [exclude]

        AddressListOutput.clients_summary(
            router_entry,
            args.get("address_lists"),
            include=include,
            exclude=exclude,
        )
