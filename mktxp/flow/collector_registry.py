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


from collections import OrderedDict
from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.collector.dhcp_collector import DHCPCollector
from mktxp.collector.interface_collector import InterfaceCollector
from mktxp.collector.health_collector import HealthCollector
from mktxp.collector.identity_collector import IdentityCollector
from mktxp.collector.monitor_collector import MonitorCollector
from mktxp.collector.poe_collector import POECollector
from mktxp.collector.netwatch_collector import NetwatchCollector
from mktxp.collector.pool_collector import PoolCollector
from mktxp.collector.resource_collector import SystemResourceCollector
from mktxp.collector.route_collector import RouteCollector
from mktxp.collector.wlan_collector import WLANCollector
from mktxp.collector.capsman_collector import CapsmanCollector
from mktxp.collector.bandwidth_collector import BandwidthCollector
from mktxp.collector.firewall_collector import FirewallCollector
from mktxp.collector.mktxp_collector import MKTXPCollector


class CollectorRegistry:
    ''' MKTXP Collectors Registry
    '''
    def __init__(self):
        self.registered_collectors = OrderedDict()

        # bandwidth collector is not router-entry related, so registering directly
        self.bandwidthCollector = BandwidthCollector()

        self.register('IdentityCollector', IdentityCollector.collect)
        self.register('SystemResourceCollector', SystemResourceCollector.collect)
        self.register('HealthCollector', HealthCollector.collect)

        self.register('DHCPCollector', DHCPCollector.collect)
        self.register('PoolCollector', PoolCollector.collect)
        self.register('InterfaceCollector', InterfaceCollector.collect)

        self.register('FirewallCollector', FirewallCollector.collect)
        self.register('MonitorCollector', MonitorCollector.collect)
        self.register('POECollector', POECollector.collect)
        self.register('NetwatchCollector', NetwatchCollector.collect)
        self.register('RouteCollector', RouteCollector.collect)

        self.register('WLANCollector', WLANCollector.collect)
        self.register('CapsmanCollector', CapsmanCollector.collect)

        self.register('MKTXPCollector', MKTXPCollector.collect)

    def register(self, collector_ID, collect_func):
        self.registered_collectors[collector_ID] = collect_func


