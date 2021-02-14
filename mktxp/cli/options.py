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
import pkg_resources
from argparse import ArgumentParser, HelpFormatter
from mktxp.cli.config.config import config_handler, MKTXPConfigKeys
from mktxp.utils.utils import FSHelper, UniquePartialMatchList, run_cmd


class MKTXPCommands:
    INFO = 'info'
    EDIT = 'edit'
    EXPORT = 'export'
    PRINT = 'print'
    SHOW = 'show'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        f'{cls.INFO}, ',
                        f'{cls.EDIT}, ',
                        f'{cls.EXPORT}, ',
                        f'{cls.PRINT}, ',
                        f'{cls.SHOW}, ',
                        '}'))

class MKTXPOptionsParser:
    ''' Base MKTXP Options Parser
    '''
    def __init__(self):
        self._script_name = f'MKTXP'
        version = pkg_resources.require("mktxp")[0].version
        self._description =  \
f'''
Prometheus Exporter for Mikrotik RouterOS, version {version}
Supports gathering metrics across multiple RouterOS devices, all easily configurable via built-in CLI interface.
Comes along with a dedicated Grafana dashboard (https://grafana.com/grafana/dashboards/13679)
Selected metrics info can be printed on the command line. For more information, run: 'mktxp -h'
'''

    @property
    def description(self):
        return self._description

    @property
    def script_name(self):
        return self._script_name

    # Options Parsing Workflow
    def parse_options(self):
        ''' General Options parsing workflow
        '''
        parser = ArgumentParser(prog = self._script_name,
                                description = 'Prometheus Exporter for Mikrotik RouterOS',
                                formatter_class=MKTXPHelpFormatter)

        self.parse_global_options(parser)
        self.parse_commands(parser)
        args = vars(parser.parse_args())

        self._check_args(args, parser)

        return args

    def parse_global_options(self, parser):
        ''' Parses global options
        '''
        pass

    def parse_commands(self, parser):
        ''' Commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd',
                                           title = 'MKTXP commands',
                                           metavar = MKTXPCommands.commands_meta())
        
        # Info command
        subparsers.add_parser(MKTXPCommands.INFO,
                                        description = 'Displays MKTXP info',
                                        formatter_class=MKTXPHelpFormatter)
        # Show command
        show_parser = subparsers.add_parser(MKTXPCommands.SHOW,
                                        description = 'Displays MKTXP config router entries',
                                        formatter_class=MKTXPHelpFormatter)
        self._add_entry_name(show_parser, registered_only = True, required = False, help = "Config entry name")
        show_parser.add_argument('-cfg', '--config', dest='config',
                                        help = "Shows MKTXP config files paths",
                                        action = 'store_true')

        # Edit command
        edit_parser = subparsers.add_parser(MKTXPCommands.EDIT,
                                        description = 'Edits an existing MKTXP router entry',
                                        formatter_class=MKTXPHelpFormatter)
        optional_args_group = edit_parser.add_argument_group('Optional Arguments')
        optional_args_group.add_argument('-ed', '--editor', dest='editor',
                help = f"Command line editor to use ({self._system_editor()} by default)",
                default = self._system_editor(),
                type = str)        
        optional_args_group.add_argument('-i', '--internal', dest='internal',
                help = f"Edit MKTXP internal configuration (advanced)",
                action = 'store_true')        

        # Export command
        export_parser = subparsers.add_parser(MKTXPCommands.EXPORT,
                                        description = 'Starts exporting Miktorik Router Metrics to Prometheus',
                                        formatter_class=MKTXPHelpFormatter)

        # Print command
        print_parser = subparsers.add_parser(MKTXPCommands.PRINT,
                                        description = 'Displays selected metrics on the command line',
                                        formatter_class=MKTXPHelpFormatter)
        required_args_group = print_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = True, help = "Name of config RouterOS entry")

        optional_args_group = print_parser.add_argument_group('Optional Arguments')
        optional_args_group.add_argument('-cc', '--capsman_clients', dest='capsman_clients',
                help = "CAPsMAN clients metrics",
                action = 'store_true')

        optional_args_group.add_argument('-wc', '--wifi_clients', dest='wifi_clients',
                help = "WiFi clients metrics",
                action = 'store_true')

        optional_args_group.add_argument('-dc', '--dhcp_clients', dest='dhcp_clients',
                help = "DHCP clients metrics",
                action = 'store_true')

    # Options checking
    def _check_args(self, args, parser):
        ''' Validation of supplied CLI arguments
        '''
        # check if there is a cmd to execute
        self._check_cmd_args(args, parser)

        if args['sub_cmd'] in (MKTXPCommands.SHOW, MKTXPCommands.PRINT):
            # Registered Entry name could be a partial match, need to expand
            if args['entry_name']:
                args['entry_name'] = UniquePartialMatchList(config_handler.registered_entries()).find(args['entry_name'])

        if args['sub_cmd'] == MKTXPCommands.PRINT:
            if not config_handler.config_entry(args['entry_name']).enabled:
                print(f"Can not print metrics for disabled RouterOS entry: {args['entry_name']}\nRun 'mktxp edit' to review and enable it in the configuration file first")
                parser.exit()

    def _check_cmd_args(self, args, parser):
        ''' Validation of supplied CLI commands
        '''
        # base command check
        if 'sub_cmd' not in args or not args['sub_cmd']:
            # If no command was specified, check for the default one
            cmd = self._default_command
            if cmd:
                args['sub_cmd'] = cmd
            else:
                # no appropriate default either
                parser.print_help()
                parser.exit()


    @property
    def _default_command(self):
        ''' If no command was specified, print INFO by default
        '''
        return MKTXPCommands.INFO


    # Internal helpers
    @staticmethod
    def _is_valid_dir_path(parser, path_arg):
        ''' Checks if path_arg is a valid dir path
        '''
        path_arg = FSHelper.full_path(path_arg)
        if not (os.path.exists(path_arg) and os.path.isdir(path_arg)):
            parser.error(f'"{path_arg}" does not seem to be an existing directory path')
        else:
            return path_arg

    @staticmethod
    def _is_valid_file_path(parser, path_arg):
        ''' Checks if path_arg is a valid file path
        '''
        path_arg = FSHelper.full_path(path_arg)
        if not (os.path.exists(path_arg) and os.path.isfile(path_arg)):
            parser.error('"{path_arg}" does not seem to be an existing file path')
        else:
            return path_arg

    @staticmethod
    def _add_entry_name(parser, registered_only = False, required = True, help = 'MKTXP Entry name'):
        parser.add_argument('-en', '--entry-name', dest = 'entry_name',
            type = str,
            metavar = config_handler.registered_entries() if registered_only else None,
            required = required,
            choices = UniquePartialMatchList(config_handler.registered_entries())if registered_only else None,
            help = help)

    @staticmethod
    def _add_entry_groups(parser):
        required_args_group = parser.add_argument_group('Required Arguments')
        MKTXPOptionsParser._add_entry_name(required_args_group)

    @staticmethod
    def _system_editor():
        editor = os.environ.get('EDITOR')
        if editor:
            return editor

        commands = ['which nano', 'which vi', 'which vim']
        for command in commands:
            editor = run_cmd(command, quiet = True).rstrip()
            if editor:
                break                                  
        return editor


class MKTXPHelpFormatter(HelpFormatter):
    ''' Custom formatter for ArgumentParser
        Disables double metavar display, showing only for long-named options
    '''
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    #parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)

