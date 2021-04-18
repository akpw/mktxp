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

import os, sys, shutil
from collections import namedtuple
from configobj import ConfigObj
from abc import ABCMeta, abstractmethod
from pkg_resources import Requirement, resource_filename
from mktxp.utils.utils import FSHelper


''' MKTXP conf file handling
'''

class MKTXPConfigKeys:
    ''' MKTXP config file keys
    '''
    # Section Keys
    ENABLED_KEY = 'enabled'
    HOST_KEY = 'hostname'
    PORT_KEY = 'port'
    USER_KEY = 'username'
    PASSWD_KEY = 'password'

    SSL_KEY = 'use_ssl'
    NO_SSL_CERTIFICATE = 'no_ssl_certificate'
    SSL_CERTIFICATE_VERIFY = 'ssl_certificate_verify'

    FE_DHCP_KEY = 'dhcp'
    FE_DHCP_LEASE_KEY = 'dhcp_lease'    
    FE_DHCP_POOL_KEY = 'pool'    
    FE_INTERFACE_KEY = 'interface'
    FE_FIREWALL_KEY = 'firewall'
    FE_MONITOR_KEY = 'monitor'
    FE_ROUTE_KEY = 'route'
    FE_WIRELESS_KEY = 'wireless'
    FE_WIRELESS_CLIENTS_KEY = 'wireless_clients'
    FE_CAPSMAN_KEY = 'capsman'
    FE_CAPSMAN_CLIENTS_KEY = 'capsman_clients'
    FE_POE_KEY = 'poe'
    FE_NETWATCH_KEY = 'netwatch'

    MKTXP_SOCKET_TIMEOUT = 'socket_timeout'    
    MKTXP_SOCKET_TIMEOUT = 'socket_timeout'   
    MKTXP_INITIAL_DELAY = 'initial_delay_on_failure'
    MKTXP_MAX_DELAY = 'max_delay_on_failure'
    MKTXP_INC_DIV = 'delay_inc_div'
    MKTXP_BANDWIDTH_KEY = 'bandwidth'
    MKTXP_BANDWIDTH_TEST_INTERVAL = 'bandwidth_test_interval'

    # UnRegistered entries placeholder
    NO_ENTRIES_REGISTERED = 'NoEntriesRegistered'

    MKTXP_USE_COMMENTS_OVER_NAMES = 'use_comments_over_names'


    # Base router id labels
    ROUTERBOARD_NAME = 'routerboard_name'
    ROUTERBOARD_ADDRESS = 'routerboard_address'

    # Default values
    DEFAULT_API_PORT = 8728
    DEFAULT_API_SSL_PORT = 8729
    DEFAULT_MKTXP_PORT = 49090
    DEFAULT_MKTXP_SOCKET_TIMEOUT = 2
    DEFAULT_MKTXP_INITIAL_DELAY = 120
    DEFAULT_MKTXP_MAX_DELAY = 900
    DEFAULT_MKTXP_INC_DIV = 5
    DEFAULT_MKTXP_BANDWIDTH_TEST_INTERVAL = 420

    BOOLEAN_KEYS_NO = {ENABLED_KEY, SSL_KEY, NO_SSL_CERTIFICATE, SSL_CERTIFICATE_VERIFY}
    
    # Feature keys enabled by default
    BOOLEAN_KEYS_YES = {FE_DHCP_KEY, FE_DHCP_LEASE_KEY, FE_DHCP_POOL_KEY, FE_INTERFACE_KEY, FE_FIREWALL_KEY,
                      FE_MONITOR_KEY, FE_ROUTE_KEY, MKTXP_USE_COMMENTS_OVER_NAMES, 
                      FE_WIRELESS_KEY, FE_WIRELESS_CLIENTS_KEY, FE_CAPSMAN_KEY, FE_CAPSMAN_CLIENTS_KEY, FE_POE_KEY, FE_NETWATCH_KEY}

    SYSTEM_BOOLEAN_KEYS_YES = (MKTXP_BANDWIDTH_KEY,)

    STR_KEYS = (HOST_KEY, USER_KEY, PASSWD_KEY)
    MKTXP_INT_KEYS = (PORT_KEY, MKTXP_SOCKET_TIMEOUT, MKTXP_INITIAL_DELAY, MKTXP_MAX_DELAY, MKTXP_INC_DIV, MKTXP_BANDWIDTH_TEST_INTERVAL)

    # MKTXP config entry nane
    MKTXP_CONFIG_ENTRY_NAME = 'MKTXP'


class ConfigEntry:
    MKTXPConfigEntry = namedtuple('MKTXPConfigEntry', [MKTXPConfigKeys.ENABLED_KEY, MKTXPConfigKeys.HOST_KEY, MKTXPConfigKeys.PORT_KEY,
                                                 MKTXPConfigKeys.USER_KEY, MKTXPConfigKeys.PASSWD_KEY,
                                                 MKTXPConfigKeys.SSL_KEY, MKTXPConfigKeys.NO_SSL_CERTIFICATE, MKTXPConfigKeys.SSL_CERTIFICATE_VERIFY,

                                                 MKTXPConfigKeys.FE_DHCP_KEY, MKTXPConfigKeys.FE_DHCP_LEASE_KEY, MKTXPConfigKeys.FE_DHCP_POOL_KEY, MKTXPConfigKeys.FE_INTERFACE_KEY, MKTXPConfigKeys.FE_FIREWALL_KEY,
                                                 MKTXPConfigKeys.FE_MONITOR_KEY, MKTXPConfigKeys.FE_ROUTE_KEY, MKTXPConfigKeys.FE_WIRELESS_KEY, MKTXPConfigKeys.FE_WIRELESS_CLIENTS_KEY,
                                                 MKTXPConfigKeys.FE_CAPSMAN_KEY, MKTXPConfigKeys.FE_CAPSMAN_CLIENTS_KEY, MKTXPConfigKeys.FE_POE_KEY, MKTXPConfigKeys.FE_NETWATCH_KEY, MKTXPConfigKeys.MKTXP_USE_COMMENTS_OVER_NAMES
                                                 ])
    MKTXPSystemEntry = namedtuple('MKTXPSystemEntry', [MKTXPConfigKeys.PORT_KEY, MKTXPConfigKeys.MKTXP_SOCKET_TIMEOUT,
                                                  MKTXPConfigKeys.MKTXP_INITIAL_DELAY, MKTXPConfigKeys.MKTXP_MAX_DELAY,
                                                  MKTXPConfigKeys.MKTXP_INC_DIV, MKTXPConfigKeys.MKTXP_BANDWIDTH_KEY, MKTXPConfigKeys.MKTXP_BANDWIDTH_TEST_INTERVAL])


class OSConfig(metaclass = ABCMeta):
    ''' OS-related config
    '''
    @staticmethod
    def os_config(quiet = False):
        ''' Factory method
        '''
        if sys.platform == 'linux':
            return LinuxConfig()
        elif sys.platform == 'darwin':
            return OSXConfig()
        else:
            if not quiet:
                print(f'Non-supported platform: {sys.platform}')
            return None

    @property
    @abstractmethod
    def mktxp_user_dir_path(self):
        pass


class OSXConfig(OSConfig):
    ''' OSX-related config
    '''
    @property
    def mktxp_user_dir_path(self):
        return FSHelper.full_path('~/mktxp')


class LinuxConfig(OSConfig):
    ''' Linux-related config
    '''
    @property
    def mktxp_user_dir_path(self):
        return FSHelper.full_path('~/mktxp')
        #return FSHelper.full_path('/etc/mktxp')


class MKTXPConfigHandler:
    def __init__(self):
        self.os_config = OSConfig.os_config()
        if not self.os_config:
            sys.exit(1)

        # mktxp user config folder
        if not os.path.exists(self.os_config.mktxp_user_dir_path):
            os.makedirs(self.os_config.mktxp_user_dir_path)

        # if needed, stage the user config data
        self.usr_conf_data_path = os.path.join(self.os_config.mktxp_user_dir_path, 'mktxp.conf')
        self.mktxp_conf_path = os.path.join(self.os_config.mktxp_user_dir_path, '_mktxp.conf')

        self._create_os_path(self.usr_conf_data_path, 'mktxp/cli/config/mktxp.conf')
        self._create_os_path(self.mktxp_conf_path, 'mktxp/cli/config/_mktxp.conf')

        self.re_compiled = {}

        self._read_from_disk()

    # MKTXP entries
    def registered_entries(self):
        ''' All MKTXP registered entries
        '''
        registered_entries = [entry_name for entry_name in self.config.keys()]
        if not registered_entries:
            registered_entries = [MKTXPConfigKeys.NO_ENTRIES_REGISTERED]

        return registered_entries

    def config_entry(self, entry_name):
        ''' Given an entry name, reads and returns the entry info
        '''
        entry_reader = self._config_entry_reader(entry_name)
        return ConfigEntry.MKTXPConfigEntry(**entry_reader)

    def system_entry(self):
        ''' MKTXP internal config entry
        '''
        _entry_reader = self._system_entry_reader()
        return ConfigEntry.MKTXPSystemEntry(**_entry_reader)

    # Helpers
    def _read_from_disk(self):
        ''' (Force-)Read conf data from disk
        '''
        self.config = ConfigObj(self.usr_conf_data_path)
        self._config = ConfigObj(self.mktxp_conf_path)

    def _create_os_path(self, os_path, resource_path):
        if not os.path.exists(os_path):
            # stage from the conf templates
            lookup_path = resource_filename(Requirement.parse("mktxp"), resource_path)
            shutil.copy(lookup_path, os_path)

    def _config_entry_reader(self, entry_name):
        config_entry_reader = {}
        write_needed = False
        for key in MKTXPConfigKeys.BOOLEAN_KEYS_NO.union(MKTXPConfigKeys.BOOLEAN_KEYS_YES):
            if self.config[entry_name].get(key):
                config_entry_reader[key] = self.config[entry_name].as_bool(key)
            else:
                config_entry_reader[key] = True if key in MKTXPConfigKeys.BOOLEAN_KEYS_YES else False
                write_needed = True # read from disk next time                

        for key in MKTXPConfigKeys.STR_KEYS:
            config_entry_reader[key] = self.config[entry_name][key]

        # port
        if self.config[entry_name].get(MKTXPConfigKeys.PORT_KEY):
            config_entry_reader[MKTXPConfigKeys.PORT_KEY] = self.config[entry_name].as_int(MKTXPConfigKeys.PORT_KEY)
        else:
            config_entry_reader[MKTXPConfigKeys.PORT_KEY] = self._default_value_for_key(MKTXPConfigKeys.SSL_KEY, config_entry_reader[MKTXPConfigKeys.SSL_KEY])
            write_needed = True # read from disk next time                

        if write_needed:
            self.config[entry_name] = config_entry_reader
            self.config.write()

        return config_entry_reader

    def _system_entry_reader(self):
        system_entry_reader = {}
        entry_name = MKTXPConfigKeys.MKTXP_CONFIG_ENTRY_NAME
        write_needed = False

        for key in MKTXPConfigKeys.MKTXP_INT_KEYS:
            if self._config[entry_name].get(key):
                system_entry_reader[key] = self._config[entry_name].as_int(key)
            else:
                system_entry_reader[key] = self._default_value_for_key(key)
                write_needed = True # read from disk next time                

        for key in MKTXPConfigKeys.SYSTEM_BOOLEAN_KEYS_YES:
            if self._config[entry_name].get(key):
                system_entry_reader[key] = self._config[entry_name].as_bool(key)
            else:
                system_entry_reader[key] = True
                write_needed = True # read from disk next time                
            
        if write_needed:
            self._config[entry_name] = system_entry_reader
            self._config.write()
            
        return system_entry_reader

    def _default_value_for_key(self, key, value = None):
        return {
                MKTXPConfigKeys.SSL_KEY: lambda value: MKTXPConfigKeys.DEFAULT_API_SSL_PORT if value else MKTXPConfigKeys.DEFAULT_API_PORT,
                MKTXPConfigKeys.PORT_KEY: lambda value: MKTXPConfigKeys.DEFAULT_MKTXP_PORT,
                MKTXPConfigKeys.MKTXP_SOCKET_TIMEOUT: lambda value: MKTXPConfigKeys.DEFAULT_MKTXP_SOCKET_TIMEOUT,
                MKTXPConfigKeys.MKTXP_INITIAL_DELAY: lambda value: MKTXPConfigKeys.DEFAULT_MKTXP_INITIAL_DELAY,
                MKTXPConfigKeys.MKTXP_MAX_DELAY: lambda value: MKTXPConfigKeys.DEFAULT_MKTXP_MAX_DELAY,
                MKTXPConfigKeys.MKTXP_INC_DIV: lambda value: MKTXPConfigKeys.DEFAULT_MKTXP_INC_DIV,
                MKTXPConfigKeys.MKTXP_BANDWIDTH_TEST_INTERVAL: lambda value: MKTXPConfigKeys.DEFAULT_MKTXP_BANDWIDTH_TEST_INTERVAL
                }[key](value)

# Simplest possible Singleton impl
config_handler = MKTXPConfigHandler()

