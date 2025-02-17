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


from enum import IntEnum
from collections import namedtuple
from mktxp.cli.config.config import config_handler, MKTXPConfigKeys, CollectorKeys
from mktxp.flow.router_connection import RouterAPIConnection
from mktxp.datasource.package_ds import PackageMetricsDataSource
from mktxp.datasource.system_resource_ds import SystemResourceMetricsDataSource
from mktxp.flow.router_connection import RouterAPIConnectionError

class RouterEntryWirelessType(IntEnum):
    NONE = 0
    WIRELESS = 1
    WIFIWAVE2 = 2
    WIFI = 3
    DUAL = 4

class RouterEntryWirelessPackage:
    WIFI_PACKAGE = 'wifi-qcom'
    WIFI_AC_PACKAGE = 'wifi-qcom-ac'
    WIFIWAVE2_PACKAGE = 'wifiwave2'
    WIRELESS_PACKAGE = 'wireless'

class RouterEntryConnectionState(IntEnum):
    NOT_CONNECTED = 0
    PARTIALLY_CONNECTED = 1
    CONNECTED = 2

class RouterEntry:
    ''' RouterOS Entry
    '''                 
    def __init__(self, router_name):
        self.router_name = router_name
        self.config_entry = config_handler.config_entry(router_name)
        self.api_connection = RouterAPIConnection(router_name, self.config_entry)
        self.router_id = {
            MKTXPConfigKeys.ROUTERBOARD_NAME: self.router_name,
            MKTXPConfigKeys.ROUTERBOARD_ADDRESS: self.config_entry.hostname
            }
        
        self.time_spent =  { CollectorKeys.IDENTITY_COLLECTOR: 0,
                            CollectorKeys.SYSTEM_RESOURCE_COLLECTOR: 0,
                            CollectorKeys.HEALTH_COLLECTOR: 0,
                            CollectorKeys.PUBLIC_IP_ADDRESS_COLLECTOR: 0,
                            CollectorKeys.NEIGHBOR_COLLECTOR: 0,
                            CollectorKeys.DNS_COLLECTOR: 0,
                            CollectorKeys.PACKAGE_COLLECTOR: 0,
                            CollectorKeys.DHCP_COLLECTOR: 0,
                            CollectorKeys.POOL_COLLECTOR: 0,
                            CollectorKeys.IP_CONNECTION_COLLECTOR: 0,
                            CollectorKeys.IPSEC_COLLECTOR: 0,
                            CollectorKeys.INTERFACE_COLLECTOR: 0,
                            CollectorKeys.FIREWALL_COLLECTOR: 0,
                            CollectorKeys.MONITOR_COLLECTOR: 0,
                            CollectorKeys.POE_COLLECTOR: 0,
                            CollectorKeys.NETWATCH_COLLECTOR: 0,
                            CollectorKeys.ROUTE_COLLECTOR: 0,
                            CollectorKeys.WLAN_COLLECTOR: 0,
                            CollectorKeys.CAPSMAN_COLLECTOR: 0,
                            CollectorKeys.QUEUE_TREE_COLLECTOR: 0,
                            CollectorKeys.QUEUE_SIMPLE_COLLECTOR: 0,                            
                            CollectorKeys.KID_CONTROL_DEVICE_COLLECTOR: 0,
                            CollectorKeys.USER_COLLECTOR: 0,
                            CollectorKeys.BFD_COLLECTOR: 0,
                            CollectorKeys.BGP_COLLECTOR: 0,
                            CollectorKeys.ROUTING_STATS_COLLECTOR: 0,
                            CollectorKeys.EOIP_COLLECTOR: 0,
                            CollectorKeys.GRE_COLLECTOR: 0,
                            CollectorKeys.IPIP_COLLECTOR: 0,
                            CollectorKeys.LTE_COLLECTOR: 0,
                            CollectorKeys.SWITCH_PORT_COLLECTOR: 0,
                            CollectorKeys.MKTXP_COLLECTOR: 0,
                            CollectorKeys.CERTIFICATE_COLLECTOR: 0
                            }         
        self._dhcp_entry = None        
        self._dhcp_records = {}
        self._capsman_entry = None
        self._wireless_type = RouterEntryWirelessType.NONE                                    

    @property
    def wireless_type(self):
        router_entry = self
        if self._wireless_type == RouterEntryWirelessType.NONE:
            if PackageMetricsDataSource.is_package_installed(router_entry, package_name = RouterEntryWirelessPackage.WIFI_PACKAGE):
              self._wireless_type = RouterEntryWirelessType.WIFI
            elif PackageMetricsDataSource.is_package_installed(router_entry, package_name = RouterEntryWirelessPackage.WIFI_AC_PACKAGE):
              self._wireless_type = RouterEntryWirelessType.WIFI
            elif PackageMetricsDataSource.is_package_installed(router_entry, package_name = RouterEntryWirelessPackage.WIFIWAVE2_PACKAGE):
              self._wireless_type = RouterEntryWirelessType.WIFIWAVE2
            elif PackageMetricsDataSource.is_package_installed(router_entry, package_name = RouterEntryWirelessPackage.WIRELESS_PACKAGE):
              self._wireless_type = RouterEntryWirelessType.DUAL
            elif SystemResourceMetricsDataSource.has_builtin_wifi_capsman(router_entry):
              self._wireless_type = RouterEntryWirelessType.WIFI
            else:
              self._wireless_type = RouterEntryWirelessType.WIRELESS
        return self._wireless_type

    @property
    def dhcp_entry(self):
        if self._dhcp_entry:
            return self._dhcp_entry
        return self
    @dhcp_entry.setter
    def dhcp_entry(self, dhcp_entry):
        self._dhcp_entry = dhcp_entry

    @property
    def capsman_entry(self):
        if self._capsman_entry:
            return self._capsman_entry
        return self
    @capsman_entry.setter
    def capsman_entry(self, capsman_entry):
        self._capsman_entry = capsman_entry

    @property
    def dhcp_records(self):
        return (entry.record for key, entry in  self._dhcp_records.items() if entry.type == 'mac_address') \
                                                                                if self._dhcp_records else None   
    @dhcp_records.setter
    def dhcp_records(self, dhcp_records):
        for dhcp_record in dhcp_records:
            if dhcp_record.get('mac_address'):
                self._dhcp_records[dhcp_record.get('mac_address')] = DHCPCacheEntry('mac_address', dhcp_record)
            if dhcp_record.get('address'):
                dhcp_record['type'] = 'address'
                self._dhcp_records[dhcp_record.get('address')] = DHCPCacheEntry('address', dhcp_record)

    def dhcp_record(self, key):
        if self._dhcp_records and self._dhcp_records.get(key):
            return self._dhcp_records[key].record
        return None

    def connection_status(self):
        primary_connection_status = self.api_connection.is_connected()
        dhcp_connection_status = self.dhcp_entry.api_connection.is_connected()
        capsman_connection_status = self.capsman_entry.api_connection.is_connected()

        if primary_connection_status and dhcp_connection_status and capsman_connection_status:
            return RouterEntryConnectionState.CONNECTED

        if primary_connection_status or dhcp_connection_status or capsman_connection_status:
            return RouterEntryConnectionState.PARTIALLY_CONNECTED

        return RouterEntryConnectionState.NOT_CONNECTED

    def connect(self):
        if not self.api_connection.is_connected():
            try:
                self.api_connection.connect()
            except RouterAPIConnectionError as exc:
                print (f'{exc}')
        
        if self._dhcp_entry and not self._dhcp_entry.api_connection.is_connected():            
            try:
                self._dhcp_entry.api_connection.connect()
            except RouterAPIConnectionError as exc:
                print (f'{exc}')

        if self._capsman_entry and not self._capsman_entry.api_connection.is_connected():
            try:
                self._capsman_entry.api_connection.connect()
            except RouterAPIConnectionError as exc:
                print (f'{exc}')

    def is_ready(self):           
        self.is_done() #flush caches, just in case
        is_ready = False

        if self.connection_status() in (RouterEntryConnectionState.NOT_CONNECTED, RouterEntryConnectionState.PARTIALLY_CONNECTED):
            self.connect()
        if self.connection_status() in (RouterEntryConnectionState.CONNECTED, RouterEntryConnectionState.PARTIALLY_CONNECTED):            
            is_ready = True        
        
        return is_ready

    def is_done(self):
        self._dhcp_records = {}
        self._wireless_type = RouterEntryWirelessType.NONE

DHCPCacheEntry = namedtuple('DHCPCacheEntry', ['type', 'record'])
