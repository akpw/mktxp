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


import subprocess
from mktxp.cli.config.config import config_handler
from mktxp.cli.options import MKTXPOptionsParser, MKTXPCommands
from mktxp.flow.processor.base_proc import ExportProcessor, OutputProcessor


class MKTXPDispatcher:
    ''' Base MKTXP Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = MKTXPOptionsParser()

    # Dispatcher
    def dispatch(self):
        args = self.option_parser.parse_options()

        if args['sub_cmd'] == MKTXPCommands.INFO:
            self.print_info()

        elif args['sub_cmd'] == MKTXPCommands.SHOW:
            self.show_entries(args)

        elif args['sub_cmd'] == MKTXPCommands.EXPORT:
            self.start_export(args)

        elif args['sub_cmd'] == MKTXPCommands.PRINT:
            self.print(args)

        elif args['sub_cmd'] == MKTXPCommands.EDIT:
            self.edit_entry(args)

        else:
            # nothing to dispatch
            return False

        return True

    # Dispatched methods
    def print_info(self):
        ''' Prints MKTXP general info
        '''
        print(f'{self.option_parser.script_name}: {self.option_parser.description}')

    def show_entries(self, args):
        if args['config']:
            print(f'MKTXP data config: {config_handler.usr_conf_data_path}')
            print(f'MKTXP internal config: {config_handler.mktxp_conf_path}')
        else:
            for entryname in config_handler.registered_entries():
                if args['entry_name'] and entryname != args['entry_name']:
                    continue
                entry = config_handler.config_entry(entryname)
                print(f'[{entryname}]')
                divider_fields = set(['username', 'use_ssl', 'dhcp'])
                for field in entry._fields:
                    if field == 'password':
                        print(f'    {field}: {"*" * len(entry.password)}')
                    else:
                        if field in divider_fields:
                            print()
                        print(f'    {field}: {getattr(entry, field)}')
                print('\n')

    def edit_entry(self, args):        
        editor = args['editor']
        if not editor:
            print(f'No editor to edit the following file with: {config_handler.usr_conf_data_path}')
        if args['internal']:
            subprocess.check_call([editor, config_handler.mktxp_conf_path])
        else:
            subprocess.check_call([editor, config_handler.usr_conf_data_path])
       
    def start_export(self, args):
        ExportProcessor.start()

    def print(self, args):
        if not (args['wifi_clients'] or args['capsman_clients']):
            print("Select metric option(s) to print out, or run 'mktxp print -h' to find out more")

        if args['wifi_clients']:
            OutputProcessor.wifi_clients(args['entry_name'])

        if args['capsman_clients']:
            OutputProcessor.capsman_clients(args['entry_name'])

        if args['dhcp_clients']:
            OutputProcessor.dhcp_clients(args['entry_name'])
            

def main():
    MKTXPDispatcher().dispatch()

if __name__ == '__main__':
    main()

