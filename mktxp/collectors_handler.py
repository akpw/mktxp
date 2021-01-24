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
from mktxp.collectors.dhcp_collector import DHCPCollector
from mktxp.collectors.interface_collector import InterfaceCollector
from mktxp.collectors.health_collector import HealthCollector
from mktxp.collectors.identity_collector import IdentityCollector
from mktxp.collectors.monitor_collector import MonitorCollector
from mktxp.collectors.pool_collector import PoolCollector
from mktxp.collectors.resource_collector import SystemResourceCollector
from mktxp.collectors.route_collector import RouteCollector
from mktxp.collectors.wlan_collector import WLANCollector
from mktxp.collectors.capsman_collector import CapsmanCollector
from mktxp.collectors.bandwidth_collector import BandwidthCollector
from mktxp.collectors.firewall_collector import FirewallCollector
from mktxp.collectors.mktxp_collector import MKTXPCollector


class CollectorsHandler:
    ''' MKTXP Collectors Handler
    '''
    def __init__(self, metrics_handler):
        self.metrics_handler = metrics_handler
        self.bandwidthCollector = BandwidthCollector()

    def collect(self):
        # process mktxp internal metrics
        yield from self.bandwidthCollector.collect()

        for router_metric in self.metrics_handler.router_metrics:           
            if not router_metric.api_connection.is_connected():
                # let's pick up on things in the next run
                router_metric.api_connection.connect()
                continue

            start = default_timer()
            yield from IdentityCollector.collect(router_metric)
            router_metric.time_spent['IdentityCollector'] += default_timer() - start

            start = default_timer()
            yield from SystemResourceCollector.collect(router_metric)
            router_metric.time_spent['SystemResourceCollector'] += default_timer() - start

            start = default_timer()
            yield from HealthCollector.collect(router_metric)
            router_metric.time_spent['HealthCollector'] += default_timer() - start

            if router_metric.router_entry.dhcp:
                start = default_timer()
                yield from DHCPCollector.collect(router_metric)                
                router_metric.time_spent['DHCPCollector'] += default_timer() - start

            if router_metric.router_entry.pool:
                start = default_timer()
                yield from PoolCollector.collect(router_metric)
                router_metric.time_spent['PoolCollector'] += default_timer() - start
            
            if router_metric.router_entry.interface:
                start = default_timer()
                yield from InterfaceCollector.collect(router_metric)
                router_metric.time_spent['InterfaceCollector'] += default_timer() - start

            if router_metric.router_entry.firewall:
                start = default_timer()
                yield from FirewallCollector.collect(router_metric)
                router_metric.time_spent['FirewallCollector'] += default_timer() - start
            
            if router_metric.router_entry.monitor:
                start = default_timer()
                yield from MonitorCollector.collect(router_metric)
                router_metric.time_spent['MonitorCollector'] += default_timer() - start
            
            if router_metric.router_entry.route:
                start = default_timer()
                yield from RouteCollector.collect(router_metric)
                router_metric.time_spent['RouteCollector'] += default_timer() - start
       
            if router_metric.router_entry.wireless:
                start = default_timer()
                yield from WLANCollector.collect(router_metric)
                router_metric.time_spent['WLANCollector'] += default_timer() - start

            if router_metric.router_entry.capsman:
                start = default_timer()
                yield from CapsmanCollector.collect(router_metric)
                router_metric.time_spent['CapsmanCollector'] += default_timer() - start
            
            yield from MKTXPCollector.collect(router_metric)




