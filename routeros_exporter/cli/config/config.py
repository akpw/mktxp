# coding=utf8
# Copyright (c) 2020 Arseniy Kuznetsov
##
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
##
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
import sys
import shutil
from collections import namedtuple
from configobj import ConfigObj
from abc import ABCMeta, abstractmethod
import importlib.resources
from routeros_exporter.utils.utils import FSHelper


''' RouterOS_Exporter conf file handling
'''

class CollectorKeys:
    IDENTITY_COLLECTOR = 'IdentityCollector'
    SYSTEM_RESOURCE_COLLECTOR = 'SystemResourceCollector'
    HEALTH_COLLECTOR = 'HealthCollector'
    PUBLIC_IP_ADDRESS_COLLECTOR = 'PublicIPAddressCollector'
    NEIGHBOR_COLLECTOR = 'NeighborCollector'
    DNS_COLLECTOR = 'DNSCollector'
    PACKAGE_COLLECTOR = 'PackageCollector'
    DHCP_COLLECTOR = 'DHCPCollector'
    POOL_COLLECTOR = 'PoolCollector'
    IP_CONNECTION_COLLECTOR = 'IPConnectionCollector'
    INTERFACE_COLLECTOR = 'InterfaceCollector'
    FIREWALL_COLLECTOR = 'FirewallCollector'
    MONITOR_COLLECTOR = 'MonitorCollector'
    W60G_COLLECTOR = 'W60gCollector'
    POE_COLLECTOR = 'POECollector'
    NETWATCH_COLLECTOR = 'NetwatchCollector'
    ROUTE_COLLECTOR = 'RouteCollector'
    WLAN_COLLECTOR = 'WLANCollector'
    CAPSMAN_COLLECTOR = 'CapsmanCollector'
    QUEUE_TREE_COLLECTOR = 'QueueTreeCollector'
    QUEUE_SIMPLE_COLLECTOR = 'QueueSimpleCollector'
    KID_CONTROL_DEVICE_COLLECTOR = 'KidControlCollector'
    USER_COLLECTOR = 'UserCollector'
    BFD_COLLECTOR = 'BFDCollector'
    BGP_COLLECTOR = 'BGPCollector'
    ROUTING_STATS_COLLECTOR = 'RoutingStatsCollector'
    EOIP_COLLECTOR = 'EOIPCollector'
    GRE_COLLECTOR = 'GRECollector'
    IPIP_COLLECTOR = 'IPIPCollector'
    IPSEC_COLLECTOR = 'IPSecCollector'
    ADDRESS_LIST_COLLECTOR = 'AddressListCollector'
    LTE_COLLECTOR = 'LTECollector'
    SWITCH_PORT_COLLECTOR = 'SwitchPortCollector'
    RouterOS_Exporter_COLLECTOR = 'RouterOSExporterCollector'
    CERTIFICATE_COLLECTOR = 'CertificateCollector'
    CONTAINER_COLLECTOR = "ContainerCollector"


class RouterOSExporterConfigKeys:
    ''' RouterOS_Exporter config file keys
    '''
    # Section Keys
    ENABLED_KEY = 'enabled'
    HOST_KEY = 'hostname'
    PORT_KEY = 'port'
    LISTEN_KEY = 'listen'
    USER_KEY = 'username'
    PASSWD_KEY = 'password'
    CREDENTIALS_FILE_KEY = 'credentials_file'

    SSL_KEY = 'use_ssl'
    NO_SSL_CERTIFICATE = 'no_ssl_certificate'
    SSL_CERTIFICATE_VERIFY = 'ssl_certificate_verify'
    SSL_CHECK_HOSTNAME = 'ssl_check_hostname'
    SSL_CA_FILE = 'ssl_ca_file'
    PLAINTEXT_LOGIN_KEY = 'plaintext_login'

    FE_HEALTH_KEY = 'health'
    FE_PACKAGE_KEY = 'installed_packages'
    FE_DHCP_KEY = 'dhcp'
    FE_DHCP_LEASE_KEY = 'dhcp_lease'
    FE_IP_CONNECTIONS_KEY = 'connections'
    FE_CONNECTION_STATS_KEY = 'connection_stats'
    FE_INTERFACE_KEY = 'interface'
    
    FE_ROUTE_KEY = 'route'
    FE_DHCP_POOL_KEY = 'pool'
    FE_FIREWALL_KEY = 'firewall'
    FE_ADDRESS_LIST_KEY = 'address_list'
    FE_NEIGHBOR_KEY = 'neighbor'
    FE_DNS_KEY = 'dns'

    FE_IPV6_ROUTE_KEY = 'ipv6_route'
    FE_IPV6_DHCP_POOL_KEY = 'ipv6_pool'
    FE_IPV6_FIREWALL_KEY = 'ipv6_firewall'
    FE_IPV6_ADDRESS_LIST_KEY = 'ipv6_address_list'
    FE_IPV6_NEIGHBOR_KEY = 'ipv6_neighbor'

    FE_MONITOR_KEY = 'monitor'
    FE_W60G_KEY = 'w60g'
    FE_WIRELESS_KEY = 'wireless'
    FE_WIRELESS_CLIENTS_KEY = 'wireless_clients'
    FE_CAPSMAN_KEY = 'capsman'
    FE_CAPSMAN_CLIENTS_KEY = 'capsman_clients'
    FE_POE_KEY = 'poe'
    FE_PUBLIC_IP_KEY = 'public_ip'
    FE_NETWATCH_KEY = 'netwatch'

    FE_EOIP_KEY = 'eoip'
    FE_GRE_KEY = 'gre'
    FE_IPIP_KEY = 'ipip'
    FE_IPSEC_KEY = 'ipsec'
    FE_LTE_KEY = "lte"
    FE_SWITCH_PORT_KEY = "switch_port"

    FE_USER_KEY = 'user'
    FE_QUEUE_KEY = 'queue'
    FE_BFD_KEY = 'bfd'
    FE_BGP_KEY = 'bgp'

    FE_REMOTE_DHCP_ENTRY = 'remote_dhcp_entry'
    FE_REMOTE_CAPSMAN_ENTRY = 'remote_capsman_entry'

    FE_CHECK_FOR_UPDATES = 'check_for_updates'

    FE_KID_CONTROL_DEVICE = 'kid_control_assigned'
    FE_KID_CONTROL_DYNAMIC = 'kid_control_dynamic'

    FE_CONTAINER_KEY = 'container'

    FE_CERTIFICATE_KEY = 'certificate'
    FE_ROUTING_STATS_KEY = 'routing_stats'
    FE_CUSTOM_LABELS_KEY = 'custom_labels'

    RouterOS_Exporter_SOCKET_TIMEOUT = 'socket_timeout'
    RouterOS_Exporter_INITIAL_DELAY = 'initial_delay_on_failure'
    RouterOS_Exporter_MAX_DELAY = 'max_delay_on_failure'
    RouterOS_Exporter_INC_DIV = 'delay_inc_div'
    RouterOS_Exporter_BANDWIDTH_KEY = 'bandwidth'
    RouterOS_Exporter_BANDWIDTH_TEST_INTERVAL = 'bandwidth_test_interval'
    RouterOS_Exporter_VERBOSE_MODE = 'verbose_mode'
    RouterOS_Exporter_MIN_COLLECT_INTERVAL = 'minimal_collect_interval'
    RouterOS_Exporter_FETCH_IN_PARALLEL = 'fetch_routers_in_parallel'
    RouterOS_Exporter_MAX_WORKER_THREADS = 'max_worker_threads'
    RouterOS_Exporter_MAX_SCRAPE_DURATION = 'max_scrape_duration'
    RouterOS_Exporter_TOTAL_MAX_SCRAPE_DURATION = 'total_max_scrape_duration'
    RouterOS_Exporter_COMPACT_CONFIG = 'compact_default_conf_values'
    RouterOS_Exporter_PROMETHEUS_HEADERS_DEDUPLICATION = 'prometheus_headers_deduplication'
    RouterOS_Exporter_PERSISTENT_ROUTER_CONNECTION_POOL = 'persistent_router_connection_pool'
    RouterOS_Exporter_PERSISTENT_DHCP_CACHE = 'persistent_dhcp_cache'

    # UnRegistered entries placeholder
    NO_ENTRIES_REGISTERED = 'NoEntriesRegistered'

    RouterOS_Exporter_USE_COMMENTS_OVER_NAMES = 'use_comments_over_names'

    # Base router id labels
    ROUTERBOARD_NAME = 'routerboard_name'
    ROUTERBOARD_ADDRESS = 'routerboard_address'

    # Injected custom labels metadata ID 
    CUSTOM_LABELS_METADATA_ID = '__custom__labels__metadata_id__'

    # Default values    
    DEFAULT_HOST_KEY = 'localhost'
    DEFAULT_USER_KEY = 'user'
    DEFAULT_PASSWORD_KEY = 'password'
    DEFAULT_CREDENTIALS_FILE_KEY = ""

    DEFAULT_SSL_CA_FILE = ""

    DEFAULT_API_PORT = 8728
    DEFAULT_API_SSL_PORT = 8729
    DEFAULT_FE_REMOTE_DHCP_ENTRY = 'None'
    DEFAULT_FE_REMOTE_CAPSMAN_ENTRY = 'None'
    DEFAULT_FE_ADDRESS_LIST_KEY = 'None'
    DEFAULT_FE_IPV6_ADDRESS_LIST_KEY = 'None'
    DEFAULT_FE_CUSTOM_LABELS_KEY = 'None'

    DEFAULT_RouterOS_Exporter_PORT = 49090
    DEFAULT_RouterOS_Exporter_SOCKET_TIMEOUT = 2
    DEFAULT_RouterOS_Exporter_INITIAL_DELAY = 120
    DEFAULT_RouterOS_Exporter_MAX_DELAY = 900
    DEFAULT_RouterOS_Exporter_INC_DIV = 5
    DEFAULT_RouterOS_Exporter_BANDWIDTH_TEST_INTERVAL = 420
    DEFAULT_RouterOS_Exporter_MIN_COLLECT_INTERVAL = 5
    DEFAULT_RouterOS_Exporter_MAX_WORKER_THREADS = 5
    DEFAULT_RouterOS_Exporter_MAX_SCRAPE_DURATION = 10
    DEFAULT_RouterOS_Exporter_TOTAL_MAX_SCRAPE_DURATION = 30


    BOOLEAN_KEYS_NO = {ENABLED_KEY, SSL_KEY, NO_SSL_CERTIFICATE, FE_CHECK_FOR_UPDATES, FE_KID_CONTROL_DEVICE, FE_KID_CONTROL_DYNAMIC,
                       SSL_CERTIFICATE_VERIFY, FE_IPV6_ROUTE_KEY, FE_IPV6_DHCP_POOL_KEY, FE_IPV6_FIREWALL_KEY, FE_IPV6_NEIGHBOR_KEY, FE_CONNECTION_STATS_KEY, FE_BFD_KEY, FE_BGP_KEY,
                       FE_EOIP_KEY, FE_GRE_KEY, FE_IPIP_KEY, FE_IPSEC_KEY, FE_LTE_KEY, FE_SWITCH_PORT_KEY, FE_ROUTING_STATS_KEY, FE_CERTIFICATE_KEY, FE_DNS_KEY, FE_CONTAINER_KEY, FE_W60G_KEY}

    # Feature keys enabled by default
    BOOLEAN_KEYS_YES = {PLAINTEXT_LOGIN_KEY, FE_DHCP_KEY, FE_HEALTH_KEY, FE_PACKAGE_KEY, FE_DHCP_LEASE_KEY, FE_IP_CONNECTIONS_KEY, FE_INTERFACE_KEY, 
                        FE_ROUTE_KEY, FE_DHCP_POOL_KEY, FE_FIREWALL_KEY, FE_NEIGHBOR_KEY, FE_MONITOR_KEY, SSL_CHECK_HOSTNAME, RouterOS_Exporter_USE_COMMENTS_OVER_NAMES,
                        FE_WIRELESS_KEY, FE_WIRELESS_CLIENTS_KEY, FE_CAPSMAN_KEY, FE_CAPSMAN_CLIENTS_KEY, FE_POE_KEY,
                        FE_NETWATCH_KEY, FE_PUBLIC_IP_KEY, FE_USER_KEY, FE_QUEUE_KEY}

    SYSTEM_BOOLEAN_KEYS_YES = {RouterOS_Exporter_PERSISTENT_ROUTER_CONNECTION_POOL, RouterOS_Exporter_PERSISTENT_DHCP_CACHE}
    SYSTEM_BOOLEAN_KEYS_NO = {RouterOS_Exporter_BANDWIDTH_KEY, RouterOS_Exporter_VERBOSE_MODE, RouterOS_Exporter_FETCH_IN_PARALLEL, RouterOS_Exporter_COMPACT_CONFIG, RouterOS_Exporter_PROMETHEUS_HEADERS_DEDUPLICATION}

    STR_KEYS = (HOST_KEY, USER_KEY, PASSWD_KEY, CREDENTIALS_FILE_KEY, SSL_CA_FILE, FE_REMOTE_DHCP_ENTRY, FE_REMOTE_CAPSMAN_ENTRY, FE_ADDRESS_LIST_KEY, FE_IPV6_ADDRESS_LIST_KEY, FE_CUSTOM_LABELS_KEY)
    INT_KEYS =  ()
    RouterOS_Exporter_INT_KEYS = (PORT_KEY, RouterOS_Exporter_SOCKET_TIMEOUT, RouterOS_Exporter_INITIAL_DELAY, RouterOS_Exporter_MAX_DELAY,
                      RouterOS_Exporter_INC_DIV, RouterOS_Exporter_BANDWIDTH_TEST_INTERVAL, RouterOS_Exporter_MIN_COLLECT_INTERVAL,
                      RouterOS_Exporter_MAX_WORKER_THREADS, RouterOS_Exporter_MAX_SCRAPE_DURATION, RouterOS_Exporter_TOTAL_MAX_SCRAPE_DURATION)

    # RouterOS_Exporter configs entry names
    DEFAULT_ENTRY_KEY = 'default'
    RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY = 'new_default_parameters'
    RouterOS_Exporter_CONFIG_ENTRY_NAME = 'RouterOS_Exporter'
    RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY = 'new_system_parameters'


class ConfigEntry:
    RouterOSExporterConfigEntry = namedtuple('RouterOSExporterConfigEntry', [RouterOSExporterConfigKeys.ENABLED_KEY, RouterOSExporterConfigKeys.HOST_KEY, RouterOSExporterConfigKeys.PORT_KEY,
                                                       RouterOSExporterConfigKeys.USER_KEY, RouterOSExporterConfigKeys.PASSWD_KEY, RouterOSExporterConfigKeys.CREDENTIALS_FILE_KEY,
                                                       RouterOSExporterConfigKeys.SSL_KEY, RouterOSExporterConfigKeys.NO_SSL_CERTIFICATE, RouterOSExporterConfigKeys.SSL_CERTIFICATE_VERIFY, RouterOSExporterConfigKeys.SSL_CHECK_HOSTNAME, RouterOSExporterConfigKeys.SSL_CA_FILE, RouterOSExporterConfigKeys.PLAINTEXT_LOGIN_KEY,
                                                       RouterOSExporterConfigKeys.FE_DHCP_KEY, RouterOSExporterConfigKeys.FE_HEALTH_KEY, RouterOSExporterConfigKeys.FE_PACKAGE_KEY, RouterOSExporterConfigKeys.FE_DHCP_LEASE_KEY, RouterOSExporterConfigKeys.FE_INTERFACE_KEY,
                                                       RouterOSExporterConfigKeys.FE_MONITOR_KEY, RouterOSExporterConfigKeys.FE_W60G_KEY, RouterOSExporterConfigKeys.FE_WIRELESS_KEY, RouterOSExporterConfigKeys.FE_WIRELESS_CLIENTS_KEY,
                                                       RouterOSExporterConfigKeys.FE_IP_CONNECTIONS_KEY, RouterOSExporterConfigKeys.FE_CONNECTION_STATS_KEY, RouterOSExporterConfigKeys.FE_CAPSMAN_KEY, RouterOSExporterConfigKeys.FE_CAPSMAN_CLIENTS_KEY, RouterOSExporterConfigKeys.FE_POE_KEY, 
                                                       RouterOSExporterConfigKeys.FE_NETWATCH_KEY, RouterOSExporterConfigKeys.RouterOS_Exporter_USE_COMMENTS_OVER_NAMES, RouterOSExporterConfigKeys.FE_PUBLIC_IP_KEY,
                                                       RouterOSExporterConfigKeys.FE_ROUTE_KEY, RouterOSExporterConfigKeys.FE_DHCP_POOL_KEY, RouterOSExporterConfigKeys.FE_FIREWALL_KEY, RouterOSExporterConfigKeys.FE_ADDRESS_LIST_KEY, RouterOSExporterConfigKeys.FE_NEIGHBOR_KEY, RouterOSExporterConfigKeys.FE_DNS_KEY,
                                                       RouterOSExporterConfigKeys.FE_IPV6_ROUTE_KEY, RouterOSExporterConfigKeys.FE_IPV6_DHCP_POOL_KEY, RouterOSExporterConfigKeys.FE_IPV6_FIREWALL_KEY, RouterOSExporterConfigKeys.FE_IPV6_ADDRESS_LIST_KEY, RouterOSExporterConfigKeys.FE_IPV6_NEIGHBOR_KEY,                                               
                                                       RouterOSExporterConfigKeys.FE_USER_KEY, RouterOSExporterConfigKeys.FE_QUEUE_KEY, RouterOSExporterConfigKeys.FE_REMOTE_DHCP_ENTRY, RouterOSExporterConfigKeys.FE_REMOTE_CAPSMAN_ENTRY, RouterOSExporterConfigKeys.FE_CHECK_FOR_UPDATES, RouterOSExporterConfigKeys.FE_BFD_KEY, RouterOSExporterConfigKeys.FE_BGP_KEY,
                                                       RouterOSExporterConfigKeys.FE_KID_CONTROL_DEVICE, RouterOSExporterConfigKeys.FE_KID_CONTROL_DYNAMIC, RouterOSExporterConfigKeys.FE_EOIP_KEY, RouterOSExporterConfigKeys.FE_GRE_KEY, RouterOSExporterConfigKeys.FE_IPIP_KEY, RouterOSExporterConfigKeys.FE_LTE_KEY, RouterOSExporterConfigKeys.FE_IPSEC_KEY, RouterOSExporterConfigKeys.FE_SWITCH_PORT_KEY,
                                                       RouterOSExporterConfigKeys.FE_ROUTING_STATS_KEY, RouterOSExporterConfigKeys.FE_CERTIFICATE_KEY, RouterOSExporterConfigKeys.FE_CONTAINER_KEY,
                                                       RouterOSExporterConfigKeys.FE_CUSTOM_LABELS_KEY
                                                       ])
    RouterOSExporterSystemEntry = namedtuple('RouterOSExporterSystemEntry', [RouterOSExporterConfigKeys.PORT_KEY, RouterOSExporterConfigKeys.LISTEN_KEY, RouterOSExporterConfigKeys.RouterOS_Exporter_SOCKET_TIMEOUT,
                                                       RouterOSExporterConfigKeys.RouterOS_Exporter_INITIAL_DELAY, RouterOSExporterConfigKeys.RouterOS_Exporter_MAX_DELAY,
                                                       RouterOSExporterConfigKeys.RouterOS_Exporter_INC_DIV, RouterOSExporterConfigKeys.RouterOS_Exporter_BANDWIDTH_KEY,
                                                       RouterOSExporterConfigKeys.RouterOS_Exporter_VERBOSE_MODE, RouterOSExporterConfigKeys.RouterOS_Exporter_BANDWIDTH_TEST_INTERVAL,
                                                       RouterOSExporterConfigKeys.RouterOS_Exporter_MIN_COLLECT_INTERVAL, RouterOSExporterConfigKeys.RouterOS_Exporter_FETCH_IN_PARALLEL,
                                                       RouterOSExporterConfigKeys.RouterOS_Exporter_MAX_WORKER_THREADS, RouterOSExporterConfigKeys.RouterOS_Exporter_MAX_SCRAPE_DURATION, 
                                                       RouterOSExporterConfigKeys.RouterOS_Exporter_TOTAL_MAX_SCRAPE_DURATION, RouterOSExporterConfigKeys.RouterOS_Exporter_COMPACT_CONFIG, 
                                                       RouterOSExporterConfigKeys.RouterOS_Exporter_PROMETHEUS_HEADERS_DEDUPLICATION, RouterOSExporterConfigKeys.RouterOS_Exporter_PERSISTENT_ROUTER_CONNECTION_POOL,
                                                       RouterOSExporterConfigKeys.RouterOS_Exporter_PERSISTENT_DHCP_CACHE])


class OSConfig(metaclass=ABCMeta):
    ''' OS-related config
    '''
    @staticmethod
    def os_config():
        ''' Factory method
        '''
        if sys.platform == 'linux':
            return LinuxConfig()
        elif sys.platform == 'darwin':
            return OSXConfig()
        elif sys.platform.startswith('freebsd'):
            return FreeBSDConfig()
        else:
            print(f'Non-supported platform: {sys.platform}')
            return None

    @property
    @abstractmethod
    def routeros_exporter_user_dir_path(self):
        pass


class FreeBSDConfig(OSConfig):
    ''' FreeBSD-related config
    '''
    @property
    def routeros_exporter_user_dir_path(self):
        return FSHelper.full_path('~/routeros_exporter')


class OSXConfig(OSConfig):
    ''' OSX-related config
    '''
    @property
    def routeros_exporter_user_dir_path(self):
        return FSHelper.full_path('~/routeros_exporter')


class LinuxConfig(OSConfig):
    ''' Linux-related config
    '''
    @property
    def routeros_exporter_user_dir_path(self):
        return '/app'


class CustomConfig(OSConfig):
    ''' Custom config
    '''
    def __init__(self, path):
        self._user_dir_path = path

    @property
    def routeros_exporter_user_dir_path(self):
        return FSHelper.full_path(self._user_dir_path)

# Mock system entry to enable running tests
mockSystemEntry = ConfigEntry.RouterOSExporterSystemEntry(
            port=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_PORT,
            listen=f'0.0.0.0:{RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_PORT}',
            socket_timeout=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_SOCKET_TIMEOUT,
            initial_delay_on_failure=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_INITIAL_DELAY,
            max_delay_on_failure=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_MAX_DELAY,
            delay_inc_div=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_INC_DIV,
            bandwidth=False,
            verbose_mode=False,
            bandwidth_test_interval=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_BANDWIDTH_TEST_INTERVAL,
            minimal_collect_interval=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_MIN_COLLECT_INTERVAL,
            fetch_routers_in_parallel=False,
            max_worker_threads=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_MAX_WORKER_THREADS,
            max_scrape_duration=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_MAX_SCRAPE_DURATION,
            total_max_scrape_duration=RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_TOTAL_MAX_SCRAPE_DURATION,
            compact_default_conf_values=False,
            prometheus_headers_deduplication=False,
            persistent_router_connection_pool=True,
            persistent_dhcp_cache=True
        )

class RouterOSExporterConfigHandler:
    # two-phase init
    def __init__(self):
        # to be re-inisialised properly in the second phase
        self.system_entry = mockSystemEntry

    # two-phase init, to enable custom config
    def __call__(self, os_config = None):
        self.os_config = os_config if os_config else OSConfig.os_config()
        if not self.os_config:
            sys.exit(1)

        # routeros_exporter user config folder
        if not os.path.exists(self.os_config.routeros_exporter_user_dir_path):
            os.makedirs(self.os_config.routeros_exporter_user_dir_path)

        # if needed, stage the user config data
        # 在 Linux 环境下使用 device.conf，其他环境使用 routeros_exporter.conf
        conf_filename = 'device.conf' if sys.platform == 'linux' else 'routeros_exporter.conf'
        self.usr_conf_data_path = os.path.join(
            self.os_config.routeros_exporter_user_dir_path, conf_filename)
        self.routeros_exporter_conf_path = os.path.join(
            self.os_config.routeros_exporter_user_dir_path, 'exporter.conf')

        self._create_os_path(self.usr_conf_data_path,
                             'cli/config/routeros_exporter.conf')
        self._create_os_path(self.routeros_exporter_conf_path,
                             'cli/config/_routeros_exporter.conf')

        self.re_compiled = {}

        self._read_from_disk()

        self.default_config_entry_reader = self._default_config_entry_reader()
        self.system_entry = self._system_entry()

    # RouterOS_Exporter entries
    def registered_entries(self):
        ''' All RouterOS_Exporter registered entries
        '''
        return (entry_name for entry_name in self.config.keys() if entry_name not in
                (RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY, RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY))

    def registered_entry(self, entry_name):
        ''' A specific RouterOS_Exporter registered entry by name
        '''
        return self.config.get(entry_name)

    def config_entry(self, entry_name):
        ''' Given an entry name, reads and returns the entry info
        '''
        entry_reader = self._config_entry_reader(entry_name)
        return ConfigEntry.RouterOSExporterConfigEntry(**entry_reader) if entry_reader else None

    # Helpers
    def _system_entry(self):
        ''' RouterOS_Exporter internal config entry
        '''
        _entry_reader = self._system_entry_reader()
        return ConfigEntry.RouterOSExporterSystemEntry(**_entry_reader)

    def _read_from_disk(self):
        ''' (Force-)Read conf data from disk
        '''
        self.config = ConfigObj(self.usr_conf_data_path, indent_type = '    ', encoding='utf-8')
        self.config.preserve_comments = True

        self._config = ConfigObj(self.routeros_exporter_conf_path, indent_type = '    ', encoding='utf-8')
        self._config.preserve_comments = True

    def _create_os_path(self, os_path, resource_path):
        if not os.path.exists(os_path):
            # stage from the conf templates
            ref = importlib.resources.files('routeros_exporter') / resource_path
            with importlib.resources.as_file(ref) as path:
                shutil.copy(path, os_path)

    def _system_entry_reader(self):
        system_entry_reader = {}
        entry_name = RouterOSExporterConfigKeys.RouterOS_Exporter_CONFIG_ENTRY_NAME
        new_keys, new_keys_values = [], {}

        if not self._config.get(RouterOSExporterConfigKeys.RouterOS_Exporter_CONFIG_ENTRY_NAME):
            self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_CONFIG_ENTRY_NAME] = {}
        if not self._config.get(RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY):
            self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY] = {}

        for key in RouterOSExporterConfigKeys.RouterOS_Exporter_INT_KEYS:
            if self._config[entry_name].get(key):
                system_entry_reader[key] = self._config[entry_name].as_int(key)
            elif self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY].get(key):
                system_entry_reader[key] = self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY].as_int(key)
            else:
                system_entry_reader[key] = self._default_value_for_key(key)
                if key not in (RouterOSExporterConfigKeys.PORT_KEY):  # Port key has been depricated
                    new_keys.append(key) # read from disk next time
                    new_keys_values[key] = system_entry_reader[key]

        for key in RouterOSExporterConfigKeys.SYSTEM_BOOLEAN_KEYS_NO.union(RouterOSExporterConfigKeys.SYSTEM_BOOLEAN_KEYS_YES):
            if self._config[entry_name].get(key) is not None:
                system_entry_reader[key] = self._config[entry_name].as_bool(key)
            elif self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY].get(key) is not None:
                system_entry_reader[key] = self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY].as_bool(key)
            else:
                system_entry_reader[key] = True if key in RouterOSExporterConfigKeys.SYSTEM_BOOLEAN_KEYS_YES else False
                new_keys.append(key) # read from disk next time
                new_keys_values[key] = system_entry_reader[key]

        # listen
        if self._config[entry_name].get(RouterOSExporterConfigKeys.LISTEN_KEY):
            system_entry_reader[RouterOSExporterConfigKeys.LISTEN_KEY] = self._config[entry_name].get(RouterOSExporterConfigKeys.LISTEN_KEY)
        elif self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY].get(RouterOSExporterConfigKeys.LISTEN_KEY):
            system_entry_reader[RouterOSExporterConfigKeys.LISTEN_KEY] = self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY].get(RouterOSExporterConfigKeys.LISTEN_KEY)
        else:
            system_entry_reader[RouterOSExporterConfigKeys.LISTEN_KEY] = f'0.0.0.0:{system_entry_reader.get(RouterOSExporterConfigKeys.PORT_KEY, RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_PORT)}'
            new_keys.append(RouterOSExporterConfigKeys.LISTEN_KEY) # read from disk next time
            new_keys_values[RouterOSExporterConfigKeys.LISTEN_KEY] = system_entry_reader[RouterOSExporterConfigKeys.LISTEN_KEY]

        if new_keys:
            self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY].update(new_keys_values)
            self._config.comments[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY] = \
                ['', '# The section below contains the latest system parameters introduced by RouterOS_Exporter',
                 f'# For organizational purposes, you can move these parameters to the [{RouterOSExporterConfigKeys.RouterOS_Exporter_CONFIG_ENTRY_NAME}] section']
            try:
                self._config[entry_name].pop(RouterOSExporterConfigKeys.PORT_KEY, None) # Port key has been depricated
                self._config.write()
                if self._config[entry_name].as_bool(RouterOSExporterConfigKeys.RouterOS_Exporter_VERBOSE_MODE):
                    print(f'Updated system entry {entry_name} with new system keys {new_keys}')
            except Exception as exc:
                print(f'Error updating system entry {entry_name} with new system keys {new_keys}: {exc}')
                print('Please update _routeros_exporter.conf to its latest version manually')

        return system_entry_reader

    def _config_entry_reader(self, entry_name):
        config_entry_reader = {}
        compact_config = self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_CONFIG_ENTRY_NAME].as_bool(RouterOSExporterConfigKeys.RouterOS_Exporter_COMPACT_CONFIG)
        drop_keys = []

        for key in RouterOSExporterConfigKeys.BOOLEAN_KEYS_NO.union(RouterOSExporterConfigKeys.BOOLEAN_KEYS_YES):
            if self.config[entry_name].get(key) is not None:
                config_entry_reader[key] = self.config[entry_name].as_bool(key)
                if compact_config and config_entry_reader[key] == self.default_config_entry_reader[key]:
                    drop_keys.append(key)
            else:
                config_entry_reader[key] = self.default_config_entry_reader[key]

        for key in RouterOSExporterConfigKeys.STR_KEYS:
            if self.config[entry_name].get(key):
                config_entry_reader[key] = self.config[entry_name].get(key)
                if key is RouterOSExporterConfigKeys.PASSWD_KEY and type(config_entry_reader[key]) is list:
                    config_entry_reader[key] = ','.join(config_entry_reader[key])         

                if compact_config and config_entry_reader[key] == self.default_config_entry_reader[key]:
                    drop_keys.append(key)
            else:
                config_entry_reader[key] = self.default_config_entry_reader[key]

        for key in RouterOSExporterConfigKeys.INT_KEYS:
            if self.config[entry_name].get(key):
                config_entry_reader[key] = self.config[entry_name].as_int(key)
                if compact_config and config_entry_reader[key] == self.default_config_entry_reader[key]:
                    drop_keys.append(key)                
            else:
                config_entry_reader[key] = self.default_config_entry_reader[key]

        # port
        if self.config[entry_name].get(RouterOSExporterConfigKeys.PORT_KEY):
            config_entry_reader[RouterOSExporterConfigKeys.PORT_KEY] = self.config[entry_name].as_int(RouterOSExporterConfigKeys.PORT_KEY)
            if compact_config and config_entry_reader[RouterOSExporterConfigKeys.PORT_KEY] == self.default_config_entry_reader[RouterOSExporterConfigKeys.PORT_KEY]:
                drop_keys.append(RouterOSExporterConfigKeys.PORT_KEY)    
        else:
            config_entry_reader[RouterOSExporterConfigKeys.PORT_KEY] = self.default_config_entry_reader[RouterOSExporterConfigKeys.PORT_KEY]

        # If allowed, compact routeros_exporter.conf entry
        if drop_keys and compact_config:
            for key in drop_keys:
                self.config[entry_name].pop(key, None)
            try:
                self.config.write()
                if self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_CONFIG_ENTRY_NAME].as_bool(RouterOSExporterConfigKeys.RouterOS_Exporter_VERBOSE_MODE):
                    print(f'compacted router entry {entry_name} for default values of the feature keys {drop_keys}')                    
            except Exception as exc:
                print(f'Error compacting router entry {entry_name} for default values of feature keys {drop_keys}: {exc}')
                print(f'Error compacting router entry {entry_name} for default values of feature keys {drop_keys}: {exc}')
                print('Please compact routeros_exporter.conf manually')

        return config_entry_reader

    def _default_config_entry_reader(self):
        default_config_entry_reader = {}
        new_keys, new_keys_values = [], {}

        if not self.config.get(RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY):
            self.config[RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY] = {}
        if not self.config.get(RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY):
            self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY] = {}

        for key in RouterOSExporterConfigKeys.BOOLEAN_KEYS_NO.union(RouterOSExporterConfigKeys.BOOLEAN_KEYS_YES):
            if self.config[RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY].get(key) is not None:
                default_config_entry_reader[key] = self.config[RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY].as_bool(key)
            elif self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].get(key) is not None:
                default_config_entry_reader[key] = self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].as_bool(key)
            else:
                default_config_entry_reader[key] = True if key in RouterOSExporterConfigKeys.BOOLEAN_KEYS_YES else False
                new_keys.append(key) # read from disk next time
                new_keys_values[key] = default_config_entry_reader[key]

        for key in RouterOSExporterConfigKeys.STR_KEYS:
            if self.config[RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY].get(key) is not None:
                default_config_entry_reader[key] = self.config[RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY].get(key)
            elif self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].get(key) is not None:
                default_config_entry_reader[key] = self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].get(key)
            else:
                default_config_entry_reader[key] = self._default_value_for_key(key)
                new_keys.append(key) # read from disk next time
                new_keys_values[key] = default_config_entry_reader[key]

        for key in RouterOSExporterConfigKeys.INT_KEYS:
            if self.config[RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY].get(key):
                default_config_entry_reader[key] = self.config[RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY].as_int(key)
            elif self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].get(key):
                default_config_entry_reader[key] = self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].as_int(key)
            else:
                default_config_entry_reader[key] = self._default_value_for_key(key)
                new_keys.append(key) # read from disk next time
                new_keys_values[key] = default_config_entry_reader[key]

        # port
        if self.config[RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY].get(RouterOSExporterConfigKeys.PORT_KEY):
            default_config_entry_reader[RouterOSExporterConfigKeys.PORT_KEY] = self.config[RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY].as_int(RouterOSExporterConfigKeys.PORT_KEY)
        elif self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].get(RouterOSExporterConfigKeys.PORT_KEY):
            default_config_entry_reader[RouterOSExporterConfigKeys.PORT_KEY] = self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].as_int(RouterOSExporterConfigKeys.PORT_KEY)
        else:
            default_config_entry_reader[RouterOSExporterConfigKeys.PORT_KEY] = self._default_value_for_key(
                RouterOSExporterConfigKeys.SSL_KEY, default_config_entry_reader[RouterOSExporterConfigKeys.SSL_KEY])
            new_keys.append(RouterOSExporterConfigKeys.PORT_KEY) # read from disk next time
            new_keys_values[RouterOSExporterConfigKeys.PORT_KEY] = default_config_entry_reader[RouterOSExporterConfigKeys.PORT_KEY]

        if new_keys:
            self.config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].update(new_keys_values)
            self.config.comments[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY] = \
                ['', '# The section below contains the latest default parameters introduced by RouterOS_Exporter',
                 f'# For organizational purposes, you can move these parameters to the [{RouterOSExporterConfigKeys.DEFAULT_ENTRY_KEY}] section']
            try:
                self.config.write()
                if self._config[RouterOSExporterConfigKeys.RouterOS_Exporter_CONFIG_ENTRY_NAME].as_bool(RouterOSExporterConfigKeys.RouterOS_Exporter_VERBOSE_MODE):
                    print(f'Updated default router entry with new feature keys {new_keys}')
            except Exception as exc:
                print(f'Error updating default router entry with new feature keys {new_keys}: {exc}')
                print('Please update routeros_exporter.conf to its latest version manually')

        return default_config_entry_reader

    def _default_value_for_key(self, key, value=None):
        return {
            RouterOSExporterConfigKeys.SSL_KEY: lambda value: RouterOSExporterConfigKeys.DEFAULT_API_SSL_PORT if value else RouterOSExporterConfigKeys.DEFAULT_API_PORT,
            RouterOSExporterConfigKeys.HOST_KEY: lambda _: RouterOSExporterConfigKeys.DEFAULT_HOST_KEY,
            RouterOSExporterConfigKeys.USER_KEY: lambda _: RouterOSExporterConfigKeys.DEFAULT_USER_KEY,
            RouterOSExporterConfigKeys.PASSWD_KEY: lambda _: RouterOSExporterConfigKeys.DEFAULT_PASSWORD_KEY,
            RouterOSExporterConfigKeys.CREDENTIALS_FILE_KEY: lambda _: RouterOSExporterConfigKeys.DEFAULT_CREDENTIALS_FILE_KEY,
            RouterOSExporterConfigKeys.FE_CUSTOM_LABELS_KEY: lambda _: RouterOSExporterConfigKeys.DEFAULT_FE_CUSTOM_LABELS_KEY,
            RouterOSExporterConfigKeys.PORT_KEY: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_PORT,
            RouterOSExporterConfigKeys.SSL_CA_FILE: lambda _: RouterOSExporterConfigKeys.DEFAULT_SSL_CA_FILE,
            RouterOSExporterConfigKeys.FE_REMOTE_DHCP_ENTRY:  lambda _: RouterOSExporterConfigKeys.DEFAULT_FE_REMOTE_DHCP_ENTRY,
            RouterOSExporterConfigKeys.FE_REMOTE_CAPSMAN_ENTRY:  lambda _: RouterOSExporterConfigKeys.DEFAULT_FE_REMOTE_CAPSMAN_ENTRY,
            RouterOSExporterConfigKeys.FE_ADDRESS_LIST_KEY: lambda _: RouterOSExporterConfigKeys.DEFAULT_FE_ADDRESS_LIST_KEY,
            RouterOSExporterConfigKeys.FE_IPV6_ADDRESS_LIST_KEY: lambda _: RouterOSExporterConfigKeys.DEFAULT_FE_IPV6_ADDRESS_LIST_KEY,
            RouterOSExporterConfigKeys.RouterOS_Exporter_SOCKET_TIMEOUT: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_SOCKET_TIMEOUT,
            RouterOSExporterConfigKeys.RouterOS_Exporter_INITIAL_DELAY: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_INITIAL_DELAY,
            RouterOSExporterConfigKeys.RouterOS_Exporter_MAX_DELAY: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_MAX_DELAY,
            RouterOSExporterConfigKeys.RouterOS_Exporter_INC_DIV: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_INC_DIV,
            RouterOSExporterConfigKeys.RouterOS_Exporter_BANDWIDTH_TEST_INTERVAL: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_BANDWIDTH_TEST_INTERVAL,
            RouterOSExporterConfigKeys.RouterOS_Exporter_MIN_COLLECT_INTERVAL: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_MIN_COLLECT_INTERVAL,
            RouterOSExporterConfigKeys.RouterOS_Exporter_MAX_WORKER_THREADS: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_MAX_WORKER_THREADS,
            RouterOSExporterConfigKeys.RouterOS_Exporter_MAX_SCRAPE_DURATION: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_MAX_SCRAPE_DURATION,
            RouterOSExporterConfigKeys.RouterOS_Exporter_TOTAL_MAX_SCRAPE_DURATION: lambda _: RouterOSExporterConfigKeys.DEFAULT_RouterOS_Exporter_TOTAL_MAX_SCRAPE_DURATION,
            RouterOSExporterConfigKeys.RouterOS_Exporter_PERSISTENT_DHCP_CACHE: lambda _: True,
        }[key](value)


# Simplest possible Singleton impl
config_handler = RouterOSExporterConfigHandler()
