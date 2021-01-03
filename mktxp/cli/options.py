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
from mktxp.cli.config.config import config_handler, MKTXPConfigKeys
from mktxp.utils.utils import FSHelper, UniquePartialMatchList, run_cmd


class MKTXPCommands:
    INFO = 'info'
    VERSION = 'version'
    SHOW = 'show'
    ADD = 'add'
    EDIT = 'edit'
    DELETE = 'delete' 
    START = 'start'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        f'{cls.INFO}, ',
                        f'{cls.VERSION}, ',
                        f'{cls.SHOW}, ',
                        f'{cls.ADD}, ',
                        f'{cls.EDIT}, ',
                        f'{cls.DELETE}, ',
                        f'{cls.START}',                        
                        '}'))

class MKTXPOptionsParser:
    ''' Base MKTXP Options Parser
    '''
    def __init__(self):
        self._script_name = 'MKTXP'
        self._description = \
    '''
    Prometheus Exporter for Mikrotik RouterOS Devices.

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
                                description = self._description,
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
        # Version command
        subparsers.add_parser(MKTXPCommands.VERSION,
                                        description = 'Displays MKTXP version info',
                                        formatter_class=MKTXPHelpFormatter)

        # Show command
        show_parser = subparsers.add_parser(MKTXPCommands.SHOW,
                                        description = 'Displays MKTXP config router entries',
                                        formatter_class=MKTXPHelpFormatter)
        self._add_entry_name(show_parser, registered_only = True, required = False, help = "Config entry name")
        show_parser.add_argument('-cp', '--configpath', dest='configpath',
                                        help = "Shows MKTXP config file path",
                                        action = 'store_true')

        # Add command
        add_parser = subparsers.add_parser(MKTXPCommands.ADD,
                                        description = 'Adds a new MKTXP router entry',
                                        formatter_class=MKTXPHelpFormatter)
        required_args_group = add_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = False, help = "Config entry name")
        required_args_group.add_argument('-host', '--hostname', dest='hostname',
                help = "IP address of RouterOS device to export metrics from",
                type = str,
                required=True)
        required_args_group.add_argument('-usr', '--username', dest='username',
                help = "username",
                type = str,
                required=True)
        required_args_group.add_argument('-pwd', '--password', dest='password',
                help = "password",
                type = str,
                required=True)

        optional_args_group = add_parser.add_argument_group('Optional Arguments')
        optional_args_group.add_argument('-e', dest='enabled',
                help = "Enables entry for metrics processing",
                action = 'store_false')

        optional_args_group.add_argument('-port', dest='port',
                help = "port",
                default = MKTXPConfigKeys.DEFAULT_API_PORT,
                type = int)

        optional_args_group.add_argument('-ssl', '--use-ssl', dest='use_ssl',
                help = "Connect via RouterOS api-ssl service",
                action = 'store_true')
        optional_args_group.add_argument('-ssl-cert', '--use-ssl-certificate', dest='ssl_certificate',
                help = "Connect with configured RouterOS SSL ceritficate",
                action = 'store_true')

        optional_args_group.add_argument('-dhcp', '--export_dhcp', dest='dhcp',
                help = "Export DHCP metrics",
                action = 'store_true')
        optional_args_group.add_argument('-dhcp_lease', '--export_dhcp_lease', dest='dhcp_lease',
                help = "Export DHCP Lease metrics",
                action = 'store_true')
        optional_args_group.add_argument('-pool', '--export_pool', dest='pool',
                help = "Export IP Pool metrics",
                action = 'store_true')
        optional_args_group.add_argument('-interface', '--export_interface', dest='interface',
                help = "Export Interface metrics",
                action = 'store_true')
        optional_args_group.add_argument('-monitor', '--export_monitor', dest='monitor',
                help = "Export Interface Monitor metrics",
                action = 'store_true')
        optional_args_group.add_argument('-route', '--export_route', dest='route',
                help = "Export IP Route metrics",
                action = 'store_true')
        optional_args_group.add_argument('-wireless', '--export_wireless', dest='wireless',
                help = "Export Wireless metrics",
                action = 'store_true')
        optional_args_group.add_argument('-capsman', '--export_capsman', dest='capsman',
                help = "Export CAPsMAN metrics",
                action = 'store_true')

        # Edit command
        edit_parser = subparsers.add_parser(MKTXPCommands.EDIT,
                                        description = 'Edits an existing MKTXP router entry',
                                        formatter_class=MKTXPHelpFormatter)
        edit_parser.add_argument('-ed', '--editor', dest='editor',
                help = f"command line editor to use ({self._system_editor()} by default)",
                default = self._system_editor(),
                type = str)        

        # Delete command
        delete_parser = subparsers.add_parser(MKTXPCommands.DELETE,
                                        description = 'Deletes an existing MKTXP router entry',
                                        formatter_class=MKTXPHelpFormatter)
        required_args_group = delete_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = True, help = "Name of entry to delete")

        # Start command
        start_parser = subparsers.add_parser(MKTXPCommands.START,
                                        description = 'Starts exporting Miktorik Router Metrics',
                                        formatter_class=MKTXPHelpFormatter)

    # Options checking
    def _check_args(self, args, parser):
        ''' Validation of supplied CLI arguments
        '''
        # check if there is a cmd to execute
        self._check_cmd_args(args, parser)

        if args['sub_cmd'] == MKTXPCommands.DELETE:
            # Registered Entry name could be a partial match, need to expand
            args['entry_name'] = UniquePartialMatchList(config_handler.registered_entries()).find(args['entry_name'])

        elif args['sub_cmd'] == MKTXPCommands.ADD:
            if args['entry_name'] in (config_handler.registered_entries()):
                print(f"{args['entry_name']}: entry name already exists")
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
        return MKTXPCommands.START


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

