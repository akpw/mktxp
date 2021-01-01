#!/usr/bin/env python
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

import sys
import pkg_resources
import mktxp.cli.checks.chk_pv
from mktxp.cli.options import MKTXPOptionsParser, MKTXPCommands
from mktxp.cli.config.config import config_handler, ConfigEntry
from mktxp.basep import MKTXPProcessor

class MKTXPDispatcher:
    ''' Base MKTXP Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = MKTXPOptionsParser()

    # Dispatcher
    def dispatch(self):
        args = self.option_parser.parse_options()

        if args['sub_cmd'] == MKTXPCommands.VERSION:
            self.print_version()

        elif args['sub_cmd'] == MKTXPCommands.INFO:
            self.print_info()

        elif args['sub_cmd'] == MKTXPCommands.SHOW:
            self.show_entries()

        elif args['sub_cmd'] == MKTXPCommands.ADD:
            self.add_entry(args)

        elif args['sub_cmd'] == MKTXPCommands.EDIT:
            self.edit_entry(args)

        elif args['sub_cmd'] == MKTXPCommands.DELETE:
            self.delete_entry(args)

        elif args['sub_cmd'] == MKTXPCommands.START:
            self.start_export(args)

        else:
            # nothing to dispatch
            return False

        return True

    # Dispatched methods
    def print_version(self):
        ''' Prints MKTXP version info
        '''
        version = pkg_resources.require("mktxp")[0].version
        print('Mikrotik RouterOS Prometheus Exporter version {}'.format(version))

    def print_info(self):
        ''' Prints MKTXP general info
        '''
        print('Mikrotik RouterOS Prometheus Exporter: {}'.format(self.option_parser.script_name))
        print(self.option_parser.description)


    def show_entries(self):
        for entryname in config_handler.registered_entries():
            entry = config_handler.entry(entryname)

            print('[{}]'.format(entryname))
            for field in entry._fields:
                print('    {}: {}'.format(field, getattr(entry, field)))
            print()

    def add_entry(self, args):
        args.pop('sub_cmd', None)
        entry_name = args['entry_name']
        args.pop('entry_name', None)

        entry_info = ConfigEntry.MKTXPEntry(**args)
        config_handler.register_entry(entry_name = entry_name, entry_info = entry_info)


    def edit_entry(self, args):
        pass

    def delete_entry(self, args):
        config_handler.unregister_entry(entry_name = args['entry_name'])
        

    def start_export(self, args):
        MKTXPProcessor.start()


def main():
    MKTXPDispatcher().dispatch()

if __name__ == '__main__':
    main()

