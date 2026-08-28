#!.usr/bin/env python
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


import mktxp.cli.checks.chk_pv  # Force version check before other imports
from mktxp.cli.config.actions import ConfigCLI
from mktxp.cli.options import MKTXPCommands, MKTXPOptionsParser
from mktxp.exporter import ExportProcessor
from mktxp.flow.router_entries_handler import RouterEntriesHandler
from mktxp.diag.registry import DiagRegistry


class MKTXPDispatcher:
    """Base MKTXP Commands Dispatcher"""

    def __init__(self):
        self.option_parser = MKTXPOptionsParser()

    # Dispatcher
    def dispatch(self):
        args = self.option_parser.parse_options()

        if args["sub_cmd"] in (MKTXPCommands.DIAG, MKTXPCommands.PRINT):
            self.diag(args)

        elif args["sub_cmd"] == MKTXPCommands.RSC:
            self.dispatch_rsc(args)

        elif args["sub_cmd"] == MKTXPCommands.EXPORT:
            self.start_export(args)

        elif args["sub_cmd"] == MKTXPCommands.EDIT:
            self.edit_entry(args)

        elif args["sub_cmd"] == MKTXPCommands.SHOW:
            self.show_entries(args)

        elif args["sub_cmd"] == MKTXPCommands.INFO:
            self.print_info()

        else:
            # nothing to dispatch
            return False

        return True

    # Dispatched methods
    def print_info(self):
        """Prints MKTXP general info"""
        print(f"{self.option_parser.script_name}: {self.option_parser.description}")

    def show_entries(self, args):
        ConfigCLI.show(args)

    def edit_entry(self, args):
        ConfigCLI.edit(args, fallback_editor_detector=self.option_parser._system_editor)

    def start_export(self, args):
        ExportProcessor.start()

    def diag(self, args):
        handler = DiagRegistry.get_active_handler(args)
        if handler:
            router_entry = RouterEntriesHandler.router_entry(args["entry_name"])
            if router_entry:
                handler.execute(router_entry, args)
        else:
            print(
                "Select diagnostic option(s) to run, or run 'mktxp diag -h' to find out more"
            )

    def print(self, args):
        return self.diag(args)

    def dispatch_rsc(self, args):
        """Dispatches RouterOS RSC configuration processing (format or split)"""
        from mktxp.rsc import RSCDispatcher
        RSCDispatcher.dispatch(args)


def main():
    MKTXPDispatcher().dispatch()


if __name__ == "__main__":
    main()
