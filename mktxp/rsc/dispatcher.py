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
from mktxp.cli.config import config_handler
from mktxp.rsc.engine import RSCEngine
from mktxp.rsc.fetcher import SSHExportFetcher


class RSCDispatcher:
    """Handles options registration, argument validation, and execution for RouterOS RSC commands."""

    @staticmethod
    def register_cli_options(subparsers, add_entry_name_fn, help_formatter_cls) -> None:
        """Register the 'rsc' subcommand and its 'format' and 'split' actions."""
        rsc_parser = subparsers.add_parser(
            "rsc",
            description="RouterOS GitOps configuration formatter and splitter",
            formatter_class=help_formatter_cls,
        )
        rsc_subparsers = rsc_parser.add_subparsers(
            dest="rsc_cmd",
            title="RSC actions",
            metavar="{format, split}",
        )

        # rsc format
        format_parser = rsc_subparsers.add_parser(
            "format",
            description="Formats raw RouterOS export into a single clean .rsc file",
            formatter_class=help_formatter_cls,
        )
        format_parser.add_argument(
            "-i",
            "--input",
            dest="input",
            default=None,
            help="Input RouterOS export .rsc file path",
            type=str,
        )
        add_entry_name_fn(
            format_parser,
            registered_only=True,
            required=False,
            help="Router entry name from mktxp.conf for live export over SSH",
        )
        format_parser.add_argument(
            "-o",
            "--out",
            dest="out",
            default=None,
            help="Output file path (defaults to stdout)",
            type=str,
        )
        format_parser.add_argument(
            "--show-sensitive",
            dest="show_sensitive",
            action="store_true",
            default=False,
            help="Include passwords and sensitive keys in live export",
        )
        format_parser.add_argument(
            "--user",
            dest="user",
            type=str,
            default=None,
            help="Override SSH username for live export",
        )
        format_parser.add_argument(
            "--ssh-key",
            dest="ssh_key",
            type=str,
            default=None,
            help="Path to SSH private key for live export",
        )
        format_parser.add_argument(
            "--ssh-port",
            dest="ssh_port",
            type=int,
            default=None,
            help="Override SSH port (default: 22)",
        )
        format_parser.add_argument(
            "--wrap",
            dest="wrap_lines",
            action="store_true",
            default=False,
            help="Wrap long lines with backslashes",
        )
        format_parser.add_argument(
            "--wrap-col",
            dest="wrap_col",
            type=int,
            default=80,
            help="Line wrapping column width (default: 80)",
        )
        format_parser.add_argument(
            "--strip-macs",
            dest="strip_macs",
            action="store_true",
            default=False,
            help="Strip dynamic MAC addresses",
        )

        # rsc split
        split_parser = rsc_subparsers.add_parser(
            "split",
            description="Splits raw RouterOS export into modular GitOps directory structure",
            formatter_class=help_formatter_cls,
        )
        split_parser.add_argument(
            "-i",
            "--input",
            dest="input",
            default=None,
            help="Input RouterOS export .rsc file path",
            type=str,
        )
        add_entry_name_fn(
            split_parser,
            registered_only=True,
            required=False,
            help="Router entry name from mktxp.conf for live export over SSH",
        )
        split_parser.add_argument(
            "-d",
            "-o",
            "--out-dir",
            dest="out_dir",
            default=None,
            help="Output directory to emit .rsc files",
            type=str,
        )
        split_parser.add_argument(
            "--show-sensitive",
            dest="show_sensitive",
            action="store_true",
            default=False,
            help="Include passwords and sensitive keys in live export",
        )
        split_parser.add_argument(
            "--numbered",
            dest="numbered_files",
            action="store_true",
            default=None,
            help="Prefix split filenames with numeric indices",
        )
        split_parser.add_argument(
            "--no-numbered",
            dest="numbered_files",
            action="store_false",
            help="Do not prefix split filenames with numeric indices",
        )
        split_parser.add_argument(
            "--user",
            dest="user",
            type=str,
            default=None,
            help="Override SSH username for live export",
        )
        split_parser.add_argument(
            "--ssh-key",
            dest="ssh_key",
            type=str,
            default=None,
            help="Path to SSH private key for live export",
        )
        split_parser.add_argument(
            "--ssh-port",
            dest="ssh_port",
            type=int,
            default=None,
            help="Override SSH port (default: 22)",
        )
        split_parser.add_argument(
            "--wrap",
            dest="wrap_lines",
            action="store_true",
            default=False,
            help="Wrap long lines with backslashes",
        )
        split_parser.add_argument(
            "--wrap-col",
            dest="wrap_col",
            type=int,
            default=80,
            help="Line wrapping column width (default: 80)",
        )
        split_parser.add_argument(
            "--extract-scripts",
            dest="extract_scripts",
            action="store_true",
            default=False,
            help="Extract multi-line scripts into separate .rsc files",
        )
        split_parser.add_argument(
            "--strip-macs",
            dest="strip_macs",
            action="store_true",
            default=False,
            help="Strip dynamic MAC addresses",
        )

    @staticmethod
    def validate_cli_args(args: dict, parser) -> None:
        """Validate RSC command line arguments."""
        if not args.get("rsc_cmd"):
            print("Specify an action for 'rsc' (e.g. 'mktxp rsc format -h' or 'mktxp rsc split -h')")
            parser.exit()

        has_input = bool(args.get("input"))
        has_entry = bool(args.get("entry_name"))

        if not has_input and not has_entry:
            print("Specify either an input file with -i / --input or a router entry with -en / --entry-name")
            parser.exit()

        if has_input and has_entry:
            print("Specify either -i / --input or -en / --entry-name, not both")
            parser.exit()

        if has_input:
            if not os.path.isfile(args["input"]):
                print(f"Input file does not exist or is not readable: {args['input']}")
                parser.exit()

    @staticmethod
    def dispatch(args: dict) -> None:
        rsc_conf = config_handler.rsc_config()

        entry_name = args.get("entry_name")
        if entry_name:
            config_entry = config_handler.config_entry(entry_name)
            if not config_entry:
                print(f"Failed to load router entry '{entry_name}' from mktxp.conf")
                return

            print(
                f"Fetching live RouterOS export from '{entry_name}' ({config_entry.hostname})..."
            )
            fetcher = SSHExportFetcher.from_config_entry(
                entry_name=entry_name,
                config_entry=config_entry,
                rsc_conf=rsc_conf,
                cli_overrides=args,
            )
            try:
                raw_text = fetcher.fetch_export()
            except Exception as exc:
                print(f"Error fetching live export: {exc}")
                return
        else:
            input_path = args["input"]
            with open(input_path, "r", encoding="utf8") as f:
                raw_text = f.read()

        engine = RSCEngine(rsc_conf)

        extract_scripts_conf = rsc_conf.get("extract_scripts", False)
        if isinstance(extract_scripts_conf, str):
            extract_scripts_conf = extract_scripts_conf.lower() in ("true", "1", "yes")

        if args["rsc_cmd"] == "format":
            out_path = args.get("out")
            formatted_text, _ = engine.format(
                raw_text=raw_text,
                wrap_lines=args.get("wrap_lines", False),
                wrap_col=args.get("wrap_col", 80),
                extract_scripts=False,
                strip_dynamic_macs=args.get("strip_macs", False),
            )

            if out_path:
                with open(out_path, "w", encoding="utf8") as f:
                    f.write(formatted_text)
                print(f"Formatted RouterOS export written to {out_path}")
            else:
                print(formatted_text)

        elif args["rsc_cmd"] == "split":
            extract_scripts = args.get("extract_scripts", False) or extract_scripts_conf
            out_dir = args.get("out_dir")
            if not out_dir:
                base_dir = rsc_conf.get("base_dir", "./exports")
                if entry_name:
                    sub_name = entry_name
                else:
                    sub_name = os.path.splitext(os.path.basename(args["input"]))[0]
                out_dir = os.path.join(base_dir, sub_name)

            emitted_files = engine.split(
                raw_text=raw_text,
                output_dir=out_dir,
                numbered=args.get("numbered", True),
                wrap_lines=args.get("wrap_lines", False),
                wrap_col=args.get("wrap_col", 80),
                extract_scripts=extract_scripts,
                strip_dynamic_macs=args.get("strip_macs", False),
            )

            print(
                f"Successfully split RouterOS export into {len(emitted_files)} files in: {out_dir}"
            )
            for fname in sorted(emitted_files.keys()):
                print(f"  |- {fname}")
