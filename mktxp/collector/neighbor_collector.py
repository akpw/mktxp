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
from mktxp.datasource.neighbor_ds import NeighborDataSource


class NeighborCollector(BaseCollector):
    '''Neighbor Collector'''

    @staticmethod
    def collect(router_entry):
        if router_entry.config_entry.neighbor:
            metric_labels = ['address', 'interface', 'mac_address', 'identity']
            records = NeighborDataSource.metric_records(router_entry, metric_labels=metric_labels)
            metrics = BaseCollector.info_collector('neighbor', 'Reachable neighbors (IPv4)', records, metric_labels=metric_labels)
            yield metrics

        if router_entry.config_entry.ipv6_neighbor:
            metric_labels = ['address', 'interface', 'mac_address', 'status', 'comment']
            records = NeighborDataSource.metric_records(router_entry, metric_labels=metric_labels)
            metrics = BaseCollector.info_collector('ipv6_neighbor', 'Reachable neighbors (IPv6)', records, metric_labels=metric_labels)
            yield metrics
