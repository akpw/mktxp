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
from mktxp.cli.output.interface_out import InterfaceOutput


class InterfaceDiagHandler(BaseDiagHandler):
    """Diagnostic handler for Ethernet & SFP interface link status and PHY rate monitoring."""

    name = "interfaces"
    cmd_flags = ["-im", "--interface-monitor"]
    cmd_prefixes = ["-im", "--interface-monitor", "--interface"]
    cmd_dest = "interface_monitor"
    cmd_help = "Ethernet & SFP interface link status & PHY rates"
    filter_group_title = "Interface Monitor Filters (-im)"
    help_prefixes = [
        "-im",
        "--interface",
        "--plugged",
        "--unplugged",
        "--degraded",
        "--rate",
        "--rate-below",
        "--sfp-only",
    ]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-im",
            "--interface-monitor",
            dest="interface_monitor",
            help="Ethernet & SFP interface link status & PHY rates",
            action="store_true",
        )

    def register_filter_options(self, parser) -> None:
        diag_conf = (
            config_handler.diag_config()
            if hasattr(config_handler, "diag_config")
            else {}
        )
        degraded_def = diag_conf.get("degraded_threshold", "100M")

        group = parser.add_argument_group(self.filter_group_title)

        status_group = group.add_mutually_exclusive_group()
        status_group.add_argument(
            "--plugged",
            dest="plugged_only",
            help="Show plugged/linked interfaces only",
            action="store_true",
            default=False,
        )
        status_group.add_argument(
            "--unplugged",
            dest="unplugged_only",
            help="Show unplugged interfaces only",
            action="store_true",
            default=False,
        )

        group.add_argument(
            "--degraded",
            dest="degraded",
            help=f"Show degraded links below sub-rate (default: {degraded_def}) or half-duplex",
            nargs="?",
            const=True,
            default=None,
            metavar="RATE",
        )
        group.add_argument(
            "--rate",
            dest="rate",
            help="Filter by exact negotiated rate (e.g. 100M, 1G, 10G)",
            type=str,
            default=None,
            metavar="RATE",
        )
        group.add_argument(
            "--rate-below",
            dest="rate_below",
            help="Filter interfaces with rate below threshold (e.g. 1G)",
            type=str,
            default=None,
            metavar="RATE",
        )
        group.add_argument(
            "--sfp-only",
            dest="sfp_only",
            help="Show SFP interfaces only with optical DOM diagnostics",
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

        diag_conf = (
            config_handler.diag_config()
            if hasattr(config_handler, "diag_config")
            else {}
        )
        degraded = args.get("degraded")
        plugged_only = args.get("plugged_only", False)
        unplugged_only = args.get("unplugged_only", False)
        rate = args.get("rate")
        rate_below = args.get("rate_below")
        sfp_only = args.get("sfp_only", False)

        InterfaceOutput.interfaces_summary(
            router_entry,
            include=include,
            exclude=exclude,
            diag_conf=diag_conf,
            plugged_only=plugged_only,
            unplugged_only=unplugged_only,
            degraded=degraded,
            rate=rate,
            rate_below=rate_below,
            sfp_only=sfp_only,
        )
