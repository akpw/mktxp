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
from mktxp.utils.units import parse_timedelta_milliseconds
from mktxp.datasource.bgp_ds import BGPMetricsDataSource


class BGPCollector(BaseCollector):
    '''BGP collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.bgp:
            return

        bgp_labels = [
            'name', 'remote_address', 'remote_as', 'local_as', 'remote_afi', 'local_afi',
            'remote_id', 'local_id', 'remote_capabilities', 'local_capabilities',
            'remote_messages', 'remote_bytes', 'local_messages', 'local_bytes',
            'prefix_count', 'output_prefix_count', 'established', 'uptime', 'last_notification',
        ]
        translation_table = {
            'established': lambda value: '1' if value == 'true' else '0',
            'uptime': lambda value: parse_timedelta_milliseconds(value) if value else '0',
        }
        bgp_records = BGPMetricsDataSource.metric_records(router_entry, metric_labels=bgp_labels, translation_table = translation_table)

        if bgp_records:
            session_info_labels = [
                'name', 'remote_address', 'remote_as', 'local_as', 'remote_afi', 'local_afi',
                'remote_id', 'local_id', 'remote_capabilities', 'local_capabilities',
                'last_notification',
            ]
            yield BaseCollector.info_collector(
                'bgp_sessions', 'BGP sessions info', bgp_records, session_info_labels
            )

            session_id_labels = ['name']
            yield BaseCollector.counter_collector(
                'bgp_remote_messages', 'Number of remote messages',
                bgp_records, 'remote_messages', session_id_labels
            )
            yield BaseCollector.counter_collector(
                'bgp_local_messages', 'Number of local messages',
                bgp_records, 'local_messages', session_id_labels
            )
            yield BaseCollector.counter_collector(
                'bgp_remote_bytes', 'Number of remote bytes',
                bgp_records, 'remote_bytes', session_id_labels
            )
            yield BaseCollector.counter_collector(
                'bgp_local_bytes', 'Number of local bytes',
                bgp_records, 'local_bytes', session_id_labels
            )
            yield BaseCollector.gauge_collector(
                'bgp_prefix_count', 'BGP prefix count',
                bgp_records, 'prefix_count', session_id_labels
            )
            advertised_prefix_counts = BGPMetricsDataSource.advertised_prefix_counts(
                router_entry, [record['name'] for record in bgp_records if record.get('name')]
            )
            if advertised_prefix_counts:
                yield BaseCollector.gauge_collector(
                    'bgp_advertised_prefixes',
                    'Current number of prefixes advertised to each BGP peer by address family',
                    advertised_prefix_counts,
                    'count',
                    ['peer', 'afi'],
                )
            advertised_prefix_records = [
                record for record in bgp_records
                if record.get('output_prefix_count') not in (None, '')
            ]
            if advertised_prefix_records:
                yield BaseCollector.gauge_collector(
                    'bgp_advertised_prefix_count',
                    'Current number of prefixes advertised to each BGP peer',
                    advertised_prefix_records,
                    'output_prefix_count',
                    session_id_labels,
                )
            yield BaseCollector.gauge_collector(
                'bgp_established', 'BGP established',
                bgp_records, 'established', session_id_labels
            )
            yield BaseCollector.gauge_collector(
                'bgp_uptime', 'BGP uptime in milliseconds',
                bgp_records, 'uptime', session_id_labels
            )

        connection_labels = [
            'name', 'instance', 'templates', 'connect', 'listen', 'local_address',
            'remote_address', 'remote_as', 'local_role', 'local_ttl', 'remote_port',
        ]
        bgp_connections = BGPMetricsDataSource.metric_records(
            router_entry, metric_labels=connection_labels, path='connection'
        )
        if bgp_connections:
            yield BaseCollector.info_collector(
                'bgp_connections', 'BGP connection configuration info',
                bgp_connections, connection_labels
            )

        instance_labels = [
            'name', 'as', 'cluster_id', 'ignore_as_path_len', 'multipath',
            'router_id', 'routing_table', 'vrf', 'inactive',
        ]
        bgp_instances = BGPMetricsDataSource.metric_records(
            router_entry, metric_labels=instance_labels, path='instance'
        )
        if bgp_instances:
            yield BaseCollector.info_collector(
                'bgp_instances', 'BGP instances info', bgp_instances, instance_labels
            )
