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
from mktxp.datasource.ospf_ds import OSPFMetricsDataSource
from mktxp.utils.units import parse_timedelta_milliseconds


class OSPFCollector(BaseCollector):
    """OSPF neighbors and LSA count collector."""

    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.ospf:
            return

        ospf_labels = [
            'instance', 'area', 'router_id', 'address',
            'state', 'state_changes', 'adjacency', 'priority',
        ]
        translation_table = {
            'adjacency': lambda value: parse_timedelta_milliseconds(value) if value else '0',
        }
        neighbor_records = OSPFMetricsDataSource.neighbor_records(
            router_entry,
            metric_labels=ospf_labels,
            translation_table=translation_table,
        )

        if neighbor_records:
            for record in neighbor_records:
                record['full'] = '1' if str(record.get('state', '')).lower() == 'full' else '0'

            neighbor_info_labels = ['instance', 'area', 'router_id', 'address', 'state']
            yield BaseCollector.info_collector(
                'ospf_neighbors',
                'OSPF active neighbors info',
                neighbor_records,
                neighbor_info_labels,
            )

            neighbor_id_labels = ['instance', 'area', 'router_id', 'address']
            yield BaseCollector.gauge_collector(
                'ospf_neighbor_full',
                'OSPF neighbor is in Full state (1 = Full, 0 = otherwise)',
                neighbor_records,
                'full',
                neighbor_id_labels,
            )
            yield BaseCollector.counter_collector(
                'ospf_neighbor_state_changes',
                'Number of OSPF neighbor state changes',
                neighbor_records,
                'state_changes',
                neighbor_id_labels,
            )
            yield BaseCollector.gauge_collector(
                'ospf_neighbor_adjacency',
                'OSPF neighbor adjacency uptime in milliseconds',
                neighbor_records,
                'adjacency',
                neighbor_id_labels,
            )

        lsa_records = OSPFMetricsDataSource.lsa_count(router_entry)
        if lsa_records:
            yield BaseCollector.gauge_collector(
                'ospf_lsa_count',
                'Total number of OSPF LSAs in database',
                lsa_records,
                'count',
            )
