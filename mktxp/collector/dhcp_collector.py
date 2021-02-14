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


from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.dhcp_ds import DHCPMetricsDataSource


class DHCPCollector(BaseCollector):
    ''' DHCP Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.dhcp:
            return

        dhcp_lease_labels = ['active_address', 'address', 'mac_address', 'host_name', 'comment', 'server', 'expires_after']
        dhcp_lease_records = DHCPMetricsDataSource.metric_records(router_entry, metric_labels = dhcp_lease_labels)   
        if dhcp_lease_records:
            # calculate number of leases per DHCP server
            dhcp_lease_servers = {}
            for dhcp_lease_record in dhcp_lease_records:
                dhcp_lease_servers[dhcp_lease_record['server']] = dhcp_lease_servers.get(dhcp_lease_record['server'], 0) + 1

            # compile leases-per-server records
            dhcp_lease_servers_records = [{ MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                                            MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                                            'server': key, 'count': value} for key, value in dhcp_lease_servers.items()]
            
            # yield lease-per-server metrics
            dhcp_lease_server_metrics = BaseCollector.gauge_collector('dhcp_lease_active_count', 'Number of active leases per DHCP server', dhcp_lease_servers_records, 'count', ['server'])
            yield dhcp_lease_server_metrics

            # active lease metrics
            if router_entry.config_entry.dhcp_lease:
                dhcp_lease_metrics = BaseCollector.info_collector('dhcp_lease', 'DHCP Active Leases', dhcp_lease_records, dhcp_lease_labels)
                yield dhcp_lease_metrics
            