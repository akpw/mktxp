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
from mktxp.collectors.mktxp_collector import MKTXPCollector

class CollectorsHandler:
    ''' MKTXP Collectors Handler
    '''
    def __init__(self, metrics_handler):
        self.metrics_handler = metrics_handler
        self.mktxpCollector = MKTXPCollector()

    def collect(self):
        # process mktxp internal metrics
        self.mktxpCollector.collect()

        for router_metric in self.metrics_handler.router_metrics:           
            if not router_metric.api_connection.is_connected():
                # let's pick up on things in the next run
                router_metric.api_connection.connect()
                continue

            yield from IdentityCollector.collect(router_metric)
            yield from SystemResourceCollector.collect(router_metric)
            yield from HealthCollector.collect(router_metric)

            if router_metric.router_entry.dhcp:
                yield from DHCPCollector.collect(router_metric)

            if router_metric.router_entry.pool:
                yield from PoolCollector.collect(router_metric)
            
            if router_metric.router_entry.interface:
                yield from InterfaceCollector.collect(router_metric)
            
            if router_metric.router_entry.monitor:
                yield from MonitorCollector.collect(router_metric)
            
            if router_metric.router_entry.route:
                yield from RouteCollector.collect(router_metric)
        
            if router_metric.router_entry.wireless:
                yield from WLANCollector.collect(router_metric)

            if router_metric.router_entry.capsman:
                yield from CapsmanCollector.collect(router_metric)

        return range(0)
