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
from mktxp.cli.config.config import CollectorKeys
from mktxp.collector.dhcp_collector import DHCPCollector
from mktxp.collector.package_collector import PackageCollector
from mktxp.collector.connection_collector import IPConnectionCollector
from mktxp.collector.interface_collector import InterfaceCollector
from mktxp.collector.health_collector import HealthCollector
from mktxp.collector.identity_collector import IdentityCollector
from mktxp.collector.ipsec_collector import IPSecCollector
from mktxp.collector.public_ip_collector import PublicIPAddressCollector
from mktxp.collector.neighbor_collector import NeighborCollector
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
from mktxp.collector.user_collector import UserCollector
from mktxp.collector.queue_collector import QueueTreeCollector
from mktxp.collector.queue_collector import QueueSimpleCollector
from mktxp.collector.kid_control_device_collector import KidDeviceCollector
from mktxp.collector.bfd_collector import BFDCollector
from mktxp.collector.bgp_collector import BGPCollector
from mktxp.collector.routing_stats_collector import RoutingStatsCollector
from mktxp.collector.eoip_collector import EOIPCollector
from mktxp.collector.gre_collector import GRECollector
from mktxp.collector.ipip_collector import IPIPCollector
from mktxp.collector.lte_collector import LTECollector
from mktxp.collector.switch_collector import SwitchPortCollector
from mktxp.collector.certificate_collector import CertificateCollector
from mktxp.collector.dns_collector import DNSCollector

class CollectorRegistry:
    ''' MKTXP Collectors Registry
    '''
    def __init__(self):
        self.registered_collectors = OrderedDict()

        # bandwidth collector is not router-entry related, so registering directly
        self.bandwidthCollector = BandwidthCollector()

        self.register(CollectorKeys.IDENTITY_COLLECTOR, IdentityCollector.collect)
        self.register(CollectorKeys.SYSTEM_RESOURCE_COLLECTOR, SystemResourceCollector.collect)
        self.register(CollectorKeys.HEALTH_COLLECTOR, HealthCollector.collect)
        self.register(CollectorKeys.PUBLIC_IP_ADDRESS_COLLECTOR, PublicIPAddressCollector.collect)

        self.register(CollectorKeys.NEIGHBOR_COLLECTOR, NeighborCollector.collect)
        self.register(CollectorKeys.DNS_COLLECTOR, DNSCollector.collect)

        self.register(CollectorKeys.PACKAGE_COLLECTOR, PackageCollector.collect)
        self.register(CollectorKeys.DHCP_COLLECTOR, DHCPCollector.collect)
        self.register(CollectorKeys.IP_CONNECTION_COLLECTOR, IPConnectionCollector.collect)
        self.register(CollectorKeys.IPSEC_COLLECTOR, IPSecCollector.collect)
        self.register(CollectorKeys.POOL_COLLECTOR, PoolCollector.collect)
        self.register(CollectorKeys.INTERFACE_COLLECTOR, InterfaceCollector.collect)

        self.register(CollectorKeys.FIREWALL_COLLECTOR, FirewallCollector.collect)
        self.register(CollectorKeys.MONITOR_COLLECTOR, MonitorCollector.collect)
        self.register(CollectorKeys.POE_COLLECTOR, POECollector.collect)
        self.register(CollectorKeys.NETWATCH_COLLECTOR, NetwatchCollector.collect)
        self.register(CollectorKeys.ROUTE_COLLECTOR, RouteCollector.collect)

        self.register(CollectorKeys.WLAN_COLLECTOR, WLANCollector.collect)
        self.register(CollectorKeys.CAPSMAN_COLLECTOR, CapsmanCollector.collect)

        self.register(CollectorKeys.USER_COLLECTOR, UserCollector.collect)
        self.register(CollectorKeys.QUEUE_TREE_COLLECTOR, QueueTreeCollector.collect)
        self.register(CollectorKeys.QUEUE_SIMPLE_COLLECTOR, QueueSimpleCollector.collect)

        self.register(CollectorKeys.KID_CONTROL_DEVICE_COLLECTOR, KidDeviceCollector.collect)
        self.register(CollectorKeys.BFD_COLLECTOR, BFDCollector.collect)
        self.register(CollectorKeys.BGP_COLLECTOR, BGPCollector.collect)
        self.register(CollectorKeys.EOIP_COLLECTOR, EOIPCollector.collect)
        self.register(CollectorKeys.GRE_COLLECTOR, GRECollector.collect)
        self.register(CollectorKeys.IPIP_COLLECTOR, IPIPCollector.collect)
        self.register(CollectorKeys.LTE_COLLECTOR, LTECollector.collect)
        self.register(CollectorKeys.SWITCH_PORT_COLLECTOR, SwitchPortCollector.collect)

        self.register(CollectorKeys.ROUTING_STATS_COLLECTOR, RoutingStatsCollector.collect)
        self.register(CollectorKeys.CERTIFICATE_COLLECTOR, CertificateCollector.collect)

        self.register(CollectorKeys.MKTXP_COLLECTOR, MKTXPCollector.collect)
        

    def register(self, collector_ID, collect_func):
        self.registered_collectors[collector_ID] = collect_func


