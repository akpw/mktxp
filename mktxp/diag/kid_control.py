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
from mktxp.cli.output.kid_control_out import KidControlOutput


class KidControlDiagHandler(BaseDiagHandler):
    """Diagnostic handler for Kid Control devices."""

    name = "kid_control"
    cmd_flags = ["-kc", "--kid_control"]
    cmd_prefixes = ["-kc", "--kid"]
    cmd_dest = "kid_control"
    cmd_help = "Kid Control device metrics"
    filter_group_title = "Kid Control Filters (-kc)"
    help_prefixes = [
        "-kc",
        "--kid",
        "--rate-above",
        "--active",
        "--unassigned",
        "--top",
        "--dynamic-only",
        "--static-only",
    ]

    def register_diag_cmd(self, parser_group) -> None:
        parser_group.add_argument(
            "-kc",
            "--kid_control",
            dest="kid_control",
            help="Kid Control device metrics",
            action="store_true",
        )

    def register_filter_options(self, parser) -> None:
        diag_conf = (
            config_handler.diag_config()
            if hasattr(config_handler, "diag_config")
            else {}
        )
        top_def = diag_conf.get("top_connections_count", 10)
        rate_def = diag_conf.get("rate_above_threshold", "1M")

        group = parser.add_argument_group(self.filter_group_title)

        if "--top" in parser._option_string_actions:
            group._group_actions.append(parser._option_string_actions["--top"])
        else:
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
            "--rate-above",
            dest="rate_above",
            help=f"Show devices with rate above threshold (default: {rate_def})",
            type=str,
            default=None,
            metavar="RATE",
        )
        group.add_argument(
            "--active",
            dest="active_only",
            help="Show active devices with non-zero traffic only",
            action="store_true",
            default=False,
        )
        group.add_argument(
            "--unassigned",
            dest="unassigned",
            help="Show unassigned devices with no user profile",
            action="store_true",
            default=False,
        )

        status_group = group.add_mutually_exclusive_group()
        if "--dynamic-only" in parser._option_string_actions:
            status_group._group_actions.append(parser._option_string_actions["--dynamic-only"])
        else:
            status_group.add_argument(
                "--dynamic-only",
                dest="dynamic_only",
                help="Show dynamic entries only",
                action="store_true",
                default=False,
            )

        if "--static-only" in parser._option_string_actions:
            status_group._group_actions.append(parser._option_string_actions["--static-only"])
        else:
            status_group.add_argument(
                "--static-only",
                dest="static_only",
                help="Show static entries only",
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

        active_only = args.get("active_only", False)
        rate_above = args.get("rate_above")
        unassigned = args.get("unassigned", False)
        dynamic_only = args.get("dynamic_only", False)
        static_only = args.get("static_only", False)
        top = args.get("top")

        KidControlOutput.clients_summary(
            router_entry,
            include=include,
            exclude=exclude,
            active_only=active_only,
            rate_above=rate_above,
            unassigned=unassigned,
            dynamic_only=dynamic_only,
            static_only=static_only,
            top=top,
        )
