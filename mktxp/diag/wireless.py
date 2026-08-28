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
from mktxp.cli.output.capsman_out import CapsmanOutput
from mktxp.cli.output.wifi_out import WirelessOutput


class WirelessDiagHandler(BaseDiagHandler):
    """Diagnostic handler for wireless and CAPsMAN client metrics."""

    name = "wireless"
    cmd_flags = ["-cc", "--capsman_clients", "-wc", "--wifi_clients"]
    filter_group_title = "Wireless & CAPsMAN Filters (-cc, -wc)"
    help_prefixes = ["-cc", "--caps", "-wc", "--wifi"]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-cc",
            "--capsman_clients",
            dest="capsman_clients",
            help="CAPsMAN clients metrics",
            action="store_true",
        )
        parser_group.add_argument(
            "-wc",
            "--wifi_clients",
            dest="wifi_clients",
            help="WiFi clients metrics",
            action="store_true",
        )

    def register_filter_options(self, parser) -> None:
        group = parser.add_argument_group(self.filter_group_title)
        group.add_argument(
            "--low-signal",
            dest="low_signal",
            help="Show devices with weak signal (default: from [DIAG] low_signal_threshold)",
            nargs="?",
            const=True,
            default=None,
            metavar="DBM",
        )
        group.add_argument(
            "--min-signal",
            dest="min_signal",
            help="Show devices with strong signal (default: from [DIAG] min_signal_threshold)",
            nargs="?",
            const=True,
            default=None,
            metavar="DBM",
        )
        group.add_argument(
            "--low-rate",
            dest="low_rate",
            help="Show devices with low negotiated rate (default: from [DIAG] low_rate_threshold)",
            nargs="?",
            const=True,
            default=None,
            metavar="RATE",
        )
        group.add_argument(
            "--recent",
            dest="recent",
            help="Show newly connected devices (default: from [DIAG] recent_duration)",
            nargs="?",
            const=True,
            default=None,
            metavar="TIME",
        )
        group.add_argument(
            "--band",
            dest="band",
            help="Filter by frequency band (e.g. 2g, 5g, 6g)",
            type=str,
            default=None,
            metavar="BAND",
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
        low_signal = args.get("low_signal")
        min_signal = args.get("min_signal")
        low_rate = args.get("low_rate")
        recent = args.get("recent")
        band = args.get("band")

        if args.get("wifi_clients"):
            WirelessOutput.clients_summary(
                router_entry,
                include=include,
                exclude=exclude,
                diag_conf=diag_conf,
                low_signal=low_signal,
                min_signal=min_signal,
                low_rate=low_rate,
                recent=recent,
                band=band,
            )
        elif args.get("capsman_clients"):
            CapsmanOutput.clients_summary(
                router_entry,
                include=include,
                exclude=exclude,
                diag_conf=diag_conf,
                low_signal=low_signal,
                min_signal=min_signal,
                low_rate=low_rate,
                recent=recent,
                band=band,
            )
