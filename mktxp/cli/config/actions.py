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
import shutil
import shlex
import subprocess
from mktxp.cli.config.loader import config_handler


class ConfigCLI:
    """Handles CLI options registration and actions related to configuration inspection and editing (show, edit)."""

    @staticmethod
    def register_show_options(subparsers, add_entry_name_fn, help_formatter_cls) -> None:
        """Register the 'show' subcommand."""
        show_parser = subparsers.add_parser(
            "show",
            description="Displays MKTXP config router entries",
            formatter_class=help_formatter_cls,
        )
        add_entry_name_fn(show_parser, registered_only=True, required=False, help="Config entry name")
        show_parser.add_argument(
            "-cfg",
            "--config",
            dest="config",
            help="Shows MKTXP config files paths",
            action="store_true",
        )

    @staticmethod
    def register_edit_options(subparsers, help_formatter_cls) -> None:
        """Register the 'edit' subcommand."""
        edit_parser = subparsers.add_parser(
            "edit",
            description="Edits an existing MKTXP router entry",
            formatter_class=help_formatter_cls,
        )
        optional_args_group = edit_parser.add_argument_group("Optional Arguments")
        optional_args_group.add_argument(
            "-ed",
            "--editor",
            dest="editor",
            help="Command line editor to use (auto-detected by default)",
            default=None,
            type=str,
        )
        optional_args_group.add_argument(
            "-i",
            "--internal",
            dest="internal",
            help="Edit MKTXP internal configuration (advanced)",
            action="store_true",
        )

    @staticmethod
    def system_editor():
        """Detect system editor. Returns None if no editor can be found."""
        editor = os.environ.get("EDITOR")
        if editor:
            return editor
        for name in ("nano", "vi", "vim"):
            path = shutil.which(name)
            if path:
                return path
        return None

    @staticmethod
    def show(args: dict) -> None:
        """Display configuration paths or formatted router entries."""
        if args.get("config"):
            print(f"MKTXP data config: {config_handler.usr_conf_data_path}")
            print(f"MKTXP internal config: {config_handler.mktxp_conf_path}")
        else:
            for entryname in config_handler.registered_entries():
                if args.get("entry_name") and entryname != args["entry_name"]:
                    continue
                entry = config_handler.config_entry(entryname)
                print(f"[{entryname}]")
                divider_fields = set(["username", "use_ssl", "dhcp"])
                for field in entry._fields:
                    if field == "password":
                        print(f'    {field}: {"*" * len(entry.password)}')
                    else:
                        if field in divider_fields:
                            print()
                        print(f"    {field}: {getattr(entry, field)}")
                print("\n")

    @staticmethod
    def edit(args: dict, fallback_editor_detector=None) -> None:
        """Launch the system editor to edit user or internal configuration files."""
        detector = fallback_editor_detector or ConfigCLI.system_editor
        editor = args.get("editor") or detector()

        if not editor:
            print("No editor found to edit configuration files.")
            print(
                "Please set the EDITOR environment variable or specify an editor with --editor"
            )
            return

        editor_cmd = shlex.split(editor)

        if args.get("internal"):
            subprocess.check_call(editor_cmd + [config_handler.mktxp_conf_path])
        else:
            subprocess.check_call(editor_cmd + [config_handler.usr_conf_data_path])
