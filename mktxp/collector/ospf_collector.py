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
from mktxp.datasource.base_ds import BaseDSProcessor
from mktxp.datasource.ospf_ds import OSPFMetricsDataSource
from mktxp.utils.units import parse_timedelta_milliseconds


OSPF_NEIGHBOR_STATE_MAP = {
    'down': 0,
    'attempt': 1,
    'init': 2,
    '2-way': 3,
    'exstart': 4,
    'exchange': 5,
    'loading': 6,
    'full': 7,
}


class OSPFCollector(BaseCollector):
    """OSPF neighbors and LSA count collector."""

    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.ospf:
            return

        ospf_labels = [
            'instance', 'area', 'interface', 'router_id', 'address',
            'state', 'state_changes', 'adjacency', 'priority',
            'ls_retransmits', 'ls_requests', 'db_summaries',
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
            area_counts = {}
            for record in neighbor_records:
                state_key = str(record.get('state', '')).strip().lower()
                record['state_code'] = OSPF_NEIGHBOR_STATE_MAP.get(state_key, -1)
                record['full'] = '1' if state_key == 'full' else '0'

                # RouterOS 7 omits these counters while they are 0 (RouterOS 6 always returns them)
                for counter in ('ls_retransmits', 'ls_requests', 'db_summaries'):
                    record.setdefault(counter, '0')

                area = record.get('area')
                if area:
                    area_key = (record.get('instance', ''), area)
                    area_counts[area_key] = area_counts.get(area_key, 0) + 1

            neighbor_info_labels = ['instance', 'area', 'interface', 'router_id', 'address', 'state']
            yield BaseCollector.info_collector(
                'ospf_neighbors',
                'OSPF active neighbors info',
                neighbor_records,
                neighbor_info_labels,
            )

            neighbor_id_labels = ['instance', 'area', 'interface', 'router_id', 'address']
            yield BaseCollector.gauge_collector(
                'ospf_neighbor_state',
                'OSPF neighbor FSM state (0=Down, 1=Attempt, 2=Init, 3=2-Way, 4=ExStart, 5=Exchange, 6=Loading, 7=Full)',
                neighbor_records,
                'state_code',
                neighbor_id_labels,
            )
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

            yield BaseCollector.gauge_collector(
                'ospf_neighbor_ls_retransmits',
                'Number of pending OSPF LS retransmits per neighbor',
                neighbor_records,
                'ls_retransmits',
                neighbor_id_labels,
            )
            yield BaseCollector.gauge_collector(
                'ospf_neighbor_ls_requests',
                'Number of pending OSPF LS requests per neighbor',
                neighbor_records,
                'ls_requests',
                neighbor_id_labels,
            )
            yield BaseCollector.gauge_collector(
                'ospf_neighbor_db_summaries',
                'Number of pending OSPF DB summaries per neighbor',
                neighbor_records,
                'db_summaries',
                neighbor_id_labels,
            )

            if area_counts:
                area_records = BaseDSProcessor.trimmed_records(
                    router_entry,
                    router_records=[
                        {'instance': instance, 'area': area, 'count': count}
                        for (instance, area), count in area_counts.items()
                    ],
                    metric_labels=['instance', 'area', 'count'],
                )
                yield BaseCollector.gauge_collector(
                    'ospf_area_neighbors_count',
                    'Number of active OSPF neighbors per area',
                    area_records,
                    'count',
                    ['instance', 'area'],
                )

        lsa_records = OSPFMetricsDataSource.lsa_count(router_entry)
        if lsa_records:
            yield BaseCollector.gauge_collector(
                'ospf_lsa_count',
                'Total number of OSPF LSAs in database',
                lsa_records,
                'count',
            )
