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


from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.ipv6_neighbor_ds import IPv6NeighborDataSource


class IPv6NeighborCollector(BaseCollector):
    '''IPv6 Neighbor Collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.ipv6_neighbor:
            return
            
        metric_labels = ['address', 'interface', 'mac_address', 'status']

        records = IPv6NeighborDataSource.metric_records(
            router_entry,
            metric_labels=metric_labels
        )

        metrics = BaseCollector.gauge_collector(
            'ipv6_neighbor_info',
            'Reachable IPv6 neighbors',
            records,
            'ipv6_neighbor',
            metric_labels=metric_labels
        )
        yield metrics
