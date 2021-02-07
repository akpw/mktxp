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


from timeit import default_timer
from mktxp.collector.dhcp_collector import DHCPCollector
from mktxp.collector.interface_collector import InterfaceCollector
from mktxp.collector.health_collector import HealthCollector
from mktxp.collector.identity_collector import IdentityCollector
from mktxp.collector.monitor_collector import MonitorCollector
from mktxp.collector.pool_collector import PoolCollector
from mktxp.collector.resource_collector import SystemResourceCollector
from mktxp.collector.route_collector import RouteCollector
from mktxp.collector.wlan_collector import WLANCollector
from mktxp.collector.capsman_collector import CapsmanCollector
from mktxp.collector.bandwidth_collector import BandwidthCollector
from mktxp.collector.firewall_collector import FirewallCollector
from mktxp.collector.mktxp_collector import MKTXPCollector


class CollectorsHandler:
    ''' MKTXP Collectors Handler
    '''
    def __init__(self, entries_handler):
        self.entries_handler = entries_handler
        self.bandwidthCollector = BandwidthCollector()

    def collect(self):
        # process mktxp internal metrics
        yield from self.bandwidthCollector.collect()

        for router_entry in self.entries_handler.router_entries:
            if not router_entry.api_connection.is_connected():
                # let's pick up on things in the next run
                router_entry.api_connection.connect()
                continue

            start = default_timer()
            yield from IdentityCollector.collect(router_entry)
            router_entry.time_spent['IdentityCollector'] += default_timer() - start

            start = default_timer()
            yield from SystemResourceCollector.collect(router_entry)
            router_entry.time_spent['SystemResourceCollector'] += default_timer() - start

            start = default_timer()
            yield from HealthCollector.collect(router_entry)
            router_entry.time_spent['HealthCollector'] += default_timer() - start

            if router_entry.config_entry.dhcp:
                start = default_timer()
                yield from DHCPCollector.collect(router_entry)                
                router_entry.time_spent['DHCPCollector'] += default_timer() - start

            if router_entry.config_entry.pool:
                start = default_timer()
                yield from PoolCollector.collect(router_entry)
                router_entry.time_spent['PoolCollector'] += default_timer() - start
            
            if router_entry.config_entry.interface:
                start = default_timer()
                yield from InterfaceCollector.collect(router_entry)
                router_entry.time_spent['InterfaceCollector'] += default_timer() - start

            if router_entry.config_entry.firewall:
                start = default_timer()
                yield from FirewallCollector.collect(router_entry)
                router_entry.time_spent['FirewallCollector'] += default_timer() - start
            
            if router_entry.config_entry.monitor:
                start = default_timer()
                yield from MonitorCollector.collect(router_entry)
                router_entry.time_spent['MonitorCollector'] += default_timer() - start
            
            if router_entry.config_entry.route:
                start = default_timer()
                yield from RouteCollector.collect(router_entry)
                router_entry.time_spent['RouteCollector'] += default_timer() - start
       
            if router_entry.config_entry.wireless:
                start = default_timer()
                yield from WLANCollector.collect(router_entry)
                router_entry.time_spent['WLANCollector'] += default_timer() - start

            if router_entry.config_entry.capsman:
                start = default_timer()
                yield from CapsmanCollector.collect(router_entry)
                router_entry.time_spent['CapsmanCollector'] += default_timer() - start
            
            yield from MKTXPCollector.collect(router_entry)




