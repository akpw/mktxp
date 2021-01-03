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
    SSL_CERTIFICATE = 'ssl_certificate'

    FE_DHCP_KEY = 'dhcp'
    FE_DHCP_LEASE_KEY = 'dhcp_lease'    
    FE_DHCP_POOL_KEY = 'pool'    
    FE_INTERFACE_KEY = 'interface'
    FE_MONITOR_KEY = 'monitor'
    FE_ROUTE_KEY = 'route'
    FE_WIRELESS_KEY = 'wireless'
    FE_CAPSMAN_KEY = 'capsman'


    # UnRegistered entries placeholder
    NO_ENTRIES_REGISTERED = 'NoEntriesRegistered'

    # Base router id labels
    ROUTERBOARD_NAME = 'routerboard_name'
    ROUTERBOARD_ADDRESS = 'routerboard_address'

    # Default ports
    DEFAULT_API_PORT = 8728
    DEFAULT_API_SSL_PORT = 8729

    BOOLEAN_KEYS = [ENABLED_KEY, SSL_KEY, SSL_CERTIFICATE,  
                      FE_DHCP_KEY, FE_DHCP_LEASE_KEY, FE_DHCP_POOL_KEY, FE_INTERFACE_KEY, 
                      FE_MONITOR_KEY, FE_ROUTE_KEY, FE_WIRELESS_KEY, FE_CAPSMAN_KEY]
    STR_KEYS = [HOST_KEY, USER_KEY, PASSWD_KEY]


class ConfigEntry:
    MKTXPEntry = namedtuple('MKTXPEntry', [MKTXPConfigKeys.ENABLED_KEY, MKTXPConfigKeys.HOST_KEY, MKTXPConfigKeys.PORT_KEY, 
                         MKTXPConfigKeys.USER_KEY, MKTXPConfigKeys.PASSWD_KEY, 
                         MKTXPConfigKeys.SSL_KEY, MKTXPConfigKeys.SSL_CERTIFICATE, 
                         
                         MKTXPConfigKeys.FE_DHCP_KEY, MKTXPConfigKeys.FE_DHCP_LEASE_KEY, MKTXPConfigKeys.FE_DHCP_POOL_KEY, MKTXPConfigKeys.FE_INTERFACE_KEY, 
                         MKTXPConfigKeys.FE_MONITOR_KEY, MKTXPConfigKeys.FE_ROUTE_KEY, MKTXPConfigKeys.FE_WIRELESS_KEY, MKTXPConfigKeys.FE_CAPSMAN_KEY
                         ])

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
        return FSHelper.full_path('/etc/mktxp')


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
        if not os.path.exists(self.usr_conf_data_path):
            # stage from the mktxp conf template
            lookup_path = resource_filename(Requirement.parse("mktxp"), "mktxp/cli/config/mktxp.conf")
            shutil.copy(lookup_path, self.usr_conf_data_path)

        self.read_from_disk()

    def read_from_disk(self):
        ''' (Force-)Read conf data from disk
        '''
        self.config = ConfigObj(self.usr_conf_data_path)


    # MKTXP entries
    ##############
    def register_entry(self, entry_name, entry_args, quiet = False):
        ''' Registers MKTXP conf entry
        '''
        if entry_name in self.registered_entries():
            if not quiet:
                print('"{0}": entry name already registered'.format(entry_name))
            return False
        else:
            self.config[entry_name] = entry_args
            self.config.write()
            if not quiet:
                print('Entry registered: {0}'.format(entry_name))
            return True

    def unregister_entry(self, entry_name, quiet = False):
        ''' Un-registers MKTXP conf entry
        '''
        if self.config[entry_name]:
            del(self.config[entry_name])
            self.config.write()
            if not quiet:
                print('Unregistered entry: {}'.format(entry_name))
            return True
        else:
            if not quiet:
                print('Entry is not registered: {}'.format(entry_name))
            return False

    def registered_entries(self):
        ''' All MKTXP registered entries
        '''
        registered_entries = [entry_name for entry_name in self.config.keys()]
        if not registered_entries:
            registered_entries = [MKTXPConfigKeys.NO_ENTRIES_REGISTERED]

        return registered_entries

    def entry(self, entry_name):
        ''' Given an entry name, reads and returns the entry info
        '''
        entry_reader = self._entry_reader(entry_name)
        return ConfigEntry.MKTXPEntry(**entry_reader)

    # Helpers
    def _entry_reader(self, entry_name):
        entry = {}
        for key in MKTXPConfigKeys.BOOLEAN_KEYS:
            if self.config[entry_name].get(key):
                entry[key] = self.config[entry_name].as_bool(key)
            else:
                entry[key] = False

        for key in MKTXPConfigKeys.STR_KEYS:
            entry[key] = self.config[entry_name][key]

        # port
        if self.config[entry_name].get(MKTXPConfigKeys.PORT_KEY):
            entry[MKTXPConfigKeys.PORT_KEY] = self.config[entry_name].as_int(MKTXPConfigKeys.PORT_KEY)
        else:
            if entry[MKTXPConfigKeys.SSL_KEY]:
                entry[MKTXPConfigKeys.PORT_KEY] = MKTXPConfigKeys.DEFAULT_API_SSL_PORT
            else:
                entry[MKTXPConfigKeys.PORT_KEY] = MKTXPConfigKeys.DEFAULT_API_PORT

        return entry


# Simplest possible Singleton impl
config_handler = MKTXPConfigHandler()

