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


import subprocess
from routeros_exporter.cli.config.config import config_handler
from routeros_exporter.cli.options import RouterOSExporterOptionsParser, RouterOSExporterCommands
from routeros_exporter.flow.processor.base_proc import ExportProcessor, OutputProcessor


class RouterOSExporterDispatcher:
    ''' Base RouterOS_Exporter Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = RouterOSExporterOptionsParser()

    # Dispatcher
    def dispatch(self):
        args = self.option_parser.parse_options()

        if args['sub_cmd'] == RouterOSExporterCommands.INFO:
            self.print_info()

        elif args['sub_cmd'] == RouterOSExporterCommands.SHOW:
            self.show_entries(args)

        elif args['sub_cmd'] == RouterOSExporterCommands.ENTRY:
            self.create_entry(args)

        elif args['sub_cmd'] == RouterOSExporterCommands.EXPORT:
            self.start_export(args)

        elif args['sub_cmd'] == RouterOSExporterCommands.PRINT:
            self.print(args)

        elif args['sub_cmd'] == RouterOSExporterCommands.EDIT:
            self.edit_entry(args)

        else:
            # nothing to dispatch
            return False

        return True

    # Dispatched methods
    def print_info(self):
        ''' Prints RouterOS_Exporter general info
        '''
        print(f'{self.option_parser.script_name}: {self.option_parser.description}')

    def show_entries(self, args):
        if args['config']:
            print(f'RouterOS_Exporter data config: {config_handler.usr_conf_data_path}')
            print(f'RouterOS_Exporter internal config: {config_handler.routeros_exporter_conf_path}')
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
            subprocess.check_call([editor, config_handler.routeros_exporter_conf_path])
        else:
            subprocess.check_call([editor, config_handler.usr_conf_data_path])

    def create_entry(self, args):
        ''' 创建新的 RouterOS 配置条目 '''
        entry_name = args['entry_name']

        # 检查条目是否已存在
        if config_handler.registered_entry(entry_name):
            print(f'错误: 配置条目 [{entry_name}] 已存在')
            print(f'使用 "routeros_exporter edit" 命令编辑现有条目')
            return

        # 创建新条目
        config_handler.config[entry_name] = {}

        # 添加用户提供的参数
        if args.get('hostname'):
            config_handler.config[entry_name]['hostname'] = args['hostname']
        if args.get('port'):
            config_handler.config[entry_name]['port'] = args['port']
        if args.get('username'):
            config_handler.config[entry_name]['username'] = args['username']
        if args.get('password'):
            config_handler.config[entry_name]['password'] = args['password']

        # 添加注释
        config_handler.config.comments[entry_name] = [
            '',
            f'# RouterOS device configuration for {entry_name}',
            '# Customize settings below or inherit from [default] section'
        ]

        # 保存配置文件
        try:
            config_handler.config.write()
            print(f'成功创建配置条目 [{entry_name}]')
            print(f'配置文件位置: {config_handler.usr_conf_data_path}')
            print(f'\n使用以下命令编辑完整配置:')
            print(f'  routeros_exporter edit')
        except Exception as exc:
            print(f'错误: 无法保存配置文件: {exc}')

    def start_export(self, args):
        ExportProcessor.start()

    def print(self, args):
        if args['wifi_clients']:
            OutputProcessor.wifi_clients(args['entry_name'])

        elif args['capsman_clients']:
            OutputProcessor.capsman_clients(args['entry_name'])

        elif args['dhcp_clients']:
            OutputProcessor.dhcp_clients(args['entry_name'])

        elif args['conn_stats']:
            OutputProcessor.conn_stats(args['entry_name'])

        elif args['kid_control']:
            OutputProcessor.kid_control(args['entry_name'])

        elif args['address_lists']:
            OutputProcessor.address_lists(args['entry_name'], args['address_lists'])

        elif args['netwatch']:
            OutputProcessor.netwatch(args['entry_name'])

        else:
            print("Select metric option(s) to print out, or run 'routeros_exporter print -h' to find out more")

def main():
    RouterOSExporterDispatcher().dispatch()

if __name__ == '__main__':
    main()
