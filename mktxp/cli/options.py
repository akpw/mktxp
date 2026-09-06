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

import os
from argparse import ArgumentParser, HelpFormatter
from importlib.metadata import version as Version
from mktxp.cli.config import config_handler, CustomConfig
from mktxp.cli.config.actions import ConfigCLI
from mktxp.diag.registry import DiagRegistry
from mktxp.rsc.dispatcher import RSCDispatcher
from mktxp.utils.utils import FSHelper, UniquePartialMatchList


class MKTXPCommands:
    DIAG = "diag"
    PRINT = "print"
    RSC = "rsc"
    EXPORT = "export"
    EDIT = "edit"
    SHOW = "show"
    INFO = "info"

    @classmethod
    def commands_meta(cls):
        return "".join(
            (
                "{",
                f"{cls.DIAG}, ",
                f"{cls.RSC}, ",
                f"{cls.EXPORT}, ",
                f"{cls.EDIT}, ",
                f"{cls.SHOW}, ",
                f"{cls.INFO}, ",
                "}",
            )
        )


class MKTXPOptionsParser:
    """Base MKTXP Options Parser"""

    def __init__(self):
        self._script_name = f"MKTXP"
        version = Version("mktxp")
        self._description = f"""
MikroTik RouterOS CLI Diagnostic Tool, GitOps Configuration Manager, and Prometheus Exporter, version {version}
- Diagnostics: Live CLI network diagnostics, client registration monitoring, and targeted filtering ('mktxp diag -h')
- RSC: RouterOS GitOps configuration formatter and modular directory splitter ('mktxp rsc -h')
- Metrics: Multi-device Prometheus metric collection with dedicated Grafana dashboard (https://grafana.com/grafana/dashboards/13679)
For more information, run: 'mktxp -h'
"""

    @property
    def description(self):
        return self._description

    @property
    def script_name(self):
        return self._script_name

    # Options Parsing Workflow
    def parse_options(self, cli_args=None):
        global_options_parser = ArgumentParser(add_help=False)
        self.parse_global_options(global_options_parser)
        namespace, _ = global_options_parser.parse_known_args(cli_args)
        if namespace.cfg_dir:
            config_handler(CustomConfig(namespace.cfg_dir))
        else:
            config_handler()

        commands_parser = ArgumentParser(
            prog=self._script_name,
            description="MikroTik RouterOS CLI Diagnostic Tool, GitOps Configuration Manager, and Prometheus Exporter",
            formatter_class=MKTXPHelpFormatter,
            parents=[global_options_parser],
        )
        self.parse_commands(commands_parser)
        args = vars(commands_parser.parse_args(cli_args))

        self._check_args(args, commands_parser)
        return args

    def parse_global_options(self, parser):
        parser.add_argument(
            "--cfg-dir",
            dest="cfg_dir",
            type=lambda d: self._is_valid_dir_path(parser, d),
            help="MKTXP config files directory (optional)",
        )

    def parse_commands(self, parser):
        subparsers = parser.add_subparsers(
            dest="sub_cmd",
            title="MKTXP commands",
            metavar=MKTXPCommands.commands_meta(),
        )

        # 1. Diag command (with print as alias)
        diag_parser = subparsers.add_parser(
            MKTXPCommands.DIAG,
            aliases=[MKTXPCommands.PRINT],
            description="Displays selected metrics and diagnostics on the command line",
            usage="%(prog)s -en ENTRY [COMMAND] [FILTERS]",
            formatter_class=MKTXPHelpFormatter,
        )
        required_args_group = diag_parser.add_argument_group("Required Arguments")
        self._add_entry_name(
            required_args_group, registered_only=True, help="Name of config RouterOS entry"
        )

        diag_cmds_group = diag_parser.add_argument_group("Diagnostic Commands")
        for handler in DiagRegistry.get_handlers():
            handler.register_diag_cmd(diag_cmds_group)

        general_filters_group = diag_parser.add_argument_group("General Filters")
        general_filters_group.add_argument(
            "-in",
            "--include",
            dest="include",
            help="Include: patterns separated by ';'",
            type=str,
            default=None,
            metavar="PATTERNS",
        )
        general_filters_group.add_argument(
            "-ex",
            "--exclude",
            dest="exclude",
            help="Exclude: patterns separated by ';'",
            type=str,
            default=None,
            metavar="PATTERNS",
        )

        for handler in DiagRegistry.get_handlers():
            handler.register_filter_options(diag_parser)

        # 2. RSC command
        RSCDispatcher.register_cli_options(subparsers, self._add_entry_name, MKTXPHelpFormatter)

        # 3. Export command
        subparsers.add_parser(
            MKTXPCommands.EXPORT,
            description="Starts exporting Miktorik Router Metrics to Prometheus",
            formatter_class=MKTXPHelpFormatter,
        )

        # 4. Edit command
        ConfigCLI.register_edit_options(subparsers, MKTXPHelpFormatter)

        # 5. Show command
        ConfigCLI.register_show_options(subparsers, self._add_entry_name, MKTXPHelpFormatter)

        # 6. Info command
        subparsers.add_parser(
            MKTXPCommands.INFO,
            description="Displays MKTXP info",
            formatter_class=MKTXPHelpFormatter,
        )

    # Options checking
    def _check_args(self, args, parser):
        self._check_cmd_args(args, parser)

        if args["sub_cmd"] == MKTXPCommands.RSC:
            RSCDispatcher.validate_cli_args(args, parser)

        if args["sub_cmd"] in (
            MKTXPCommands.SHOW,
            MKTXPCommands.DIAG,
            MKTXPCommands.PRINT,
            MKTXPCommands.RSC,
        ):
            if args.get("entry_name"):
                args["entry_name"] = UniquePartialMatchList(
                    config_handler.registered_entries()
                ).find(args["entry_name"])

        if args["sub_cmd"] in (MKTXPCommands.DIAG, MKTXPCommands.PRINT):
            if not config_handler.config_entry(args["entry_name"]).enabled:
                print(
                    f"Can not run diagnostics for disabled RouterOS entry: {args['entry_name']}\nRun 'mktxp edit' to review and enable it in the configuration file first"
                )
                parser.exit()

    def _check_cmd_args(self, args, parser):
        if "sub_cmd" not in args or not args["sub_cmd"]:
            cmd = self._default_command
            if cmd:
                args["sub_cmd"] = cmd
            else:
                parser.print_help()
                parser.exit()

    @property
    def _default_command(self):
        return MKTXPCommands.INFO

    @staticmethod
    def _is_valid_dir_path(parser, path_arg):
        path_arg = FSHelper.full_path(path_arg)
        if not (os.path.exists(path_arg) and os.path.isdir(path_arg)):
            parser.error(f'"{path_arg}" does not seem to be an existing directory path')
        else:
            return path_arg

    @staticmethod
    def _is_valid_file_path(parser, path_arg):
        path_arg = FSHelper.full_path(path_arg)
        if not (os.path.exists(path_arg) and os.path.isfile(path_arg)):
            parser.error(f'"{path_arg}" does not seem to be an existing file path')
        else:
            return path_arg

    @staticmethod
    def _add_entry_name(parser, registered_only=False, required=True, help="MKTXP Entry name"):
        registered_entries = []
        if registered_only:
            try:
                registered_entries = list(config_handler.registered_entries())
                if registered_entries:
                    help = f"{help} (choose from: {', '.join(registered_entries)})"
            except Exception as exc:
                if config_handler.system_entry().verbose_mode:
                    print(f"Warning: unable to load registered router entries: {exc}")

        parser.add_argument(
            "-en",
            "--entry-name",
            dest="entry_name",
            type=str,
            metavar="ENTRY",
            required=required,
            choices=UniquePartialMatchList(registered_entries) if registered_only else None,
            help=help,
        )

    @staticmethod
    def _system_editor():
        return ConfigCLI.system_editor()


class MKTXPHelpFormatter(HelpFormatter):
    """Custom formatter for ArgumentParser
    Disables double metavar display, showing only for long-named options,
    and dynamically filters specialized filter groups when a specific diagnostic command is in argv.
    """

    def format_help(self):
        import sys

        help_text = super().format_help()
        argv = sys.argv
        matching_handlers = DiagRegistry.get_matching_help_handlers(argv)

        if matching_handlers:
            sections = help_text.split("\n\n")
            filtered_sections = []
            for sec in sections:
                skip = False
                for handler in DiagRegistry.get_handlers():
                    if handler.filter_group_title and handler.filter_group_title in sec:
                        if handler not in matching_handlers:
                            skip = True
                            break
                if skip:
                    continue

                if sec.startswith("Diagnostic Commands:"):
                    lines = sec.split("\n")
                    header = lines[0]
                    filtered_lines = [header]
                    i = 1
                    while i < len(lines):
                        line = lines[i]
                        if line.startswith("  -"):
                            belongs = any(
                                any(flag in line for flag in h.cmd_flags)
                                for h in matching_handlers
                            )
                            if belongs:
                                filtered_lines.append(line)
                                i += 1
                                while (
                                    i < len(lines)
                                    and lines[i].startswith(" ")
                                    and not lines[i].startswith("  -")
                                ):
                                    filtered_lines.append(lines[i])
                                    i += 1
                                continue
                        i += 1
                    sec = "\n".join(filtered_lines)

                filtered_sections.append(sec)
            return "\n\n".join(filtered_sections)
        return help_text

    def _format_action_invocation(self, action):
        if not action.option_strings:
            (metavar,) = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            if action.nargs == 0:
                parts.extend(action.option_strings)
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append("%s" % option_string)
                parts[-1] += " %s" % args_string
            return ", ".join(parts)
