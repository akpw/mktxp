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


from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.interface_ds import BridgeVlanMetricsDataSource


class BridgeVlanCollector(BaseCollector):
    ''' Bridge VLAN Metrics collector
    '''
    @staticmethod
    def collect(router_entry):
        if not getattr(router_entry.config_entry, 'bridge_vlan', False):
            return

        vlan_labels = ['name', 'bridge', 'vlan_ids', 'current_tagged', 'current_untagged']
        vlan_records = BridgeVlanMetricsDataSource.metric_records(
            router_entry,
            metric_labels=vlan_labels
        )

        if not vlan_records:
            return

        yield BaseCollector.info_collector(
            'interface_bridge_vlan',
            'Bridge VLAN membership information',
            vlan_records,
            metric_labels=vlan_labels
        )
