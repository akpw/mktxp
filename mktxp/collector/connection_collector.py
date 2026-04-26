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
from mktxp.flow.processor.output import BaseOutputProcessor
from mktxp.datasource.connection_ds import IPConnectionDatasource, IPConnectionStatsDatasource, IPConnectionTrafficDatasource


class IPConnectionCollector(BaseCollector):
    ''' IP Connection Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if router_entry.config_entry.connections:       
            connection_records = IPConnectionDatasource.metric_records(router_entry, include_stack_counts = True)
            if connection_records:
                connection_metrics = (
                    ('ip_connections_total', 'Number of IP connections', 'count'),
                    ('ipv4_connections_total', 'Number of IPv4 connections', 'ipv4_count'),
                    ('ipv6_connections_total', 'Number of IPv6 connections', 'ipv6_count'),
                )

                for metric_name, metric_desc, metric_key in connection_metrics:
                    yield BaseCollector.gauge_collector(metric_name, metric_desc, connection_records, metric_key,)

        if router_entry.config_entry.connection_stats:
            connection_stats_records = IPConnectionStatsDatasource.metric_records(router_entry)
            if connection_stats_records:
                for connection_stat_record in connection_stats_records:
                    BaseOutputProcessor.augment_record(router_entry, connection_stat_record, id_key = 'src_address')

                connection_stats_labels = ['src_address', 'dst_addresses', 'dhcp_name']                
                connection_stats_metrics_gauge = BaseCollector.gauge_collector('connection_stats', 'Open connection stats', 
                                                                    connection_stats_records, 'connection_count', connection_stats_labels)
                yield connection_stats_metrics_gauge

        if router_entry.config_entry.connection_traffic:
            connection_traffic_records = IPConnectionTrafficDatasource.metric_records(router_entry)
            if connection_traffic_records:
                for connection_traffic_record in connection_traffic_records:
                    BaseOutputProcessor.augment_record(router_entry, connection_traffic_record, id_key = 'src_address')

                connection_traffic_labels = ['src_address', 'dst_address', 'protocol', 'dhcp_name']
                connection_traffic_metrics = (
                    ('connection_upload_bytes', 'Observed uploaded bytes on active src to dst connections', 'upload_bytes'),
                    ('connection_download_bytes', 'Observed downloaded bytes on active src to dst connections', 'download_bytes'),
                    ('connection_total_bytes', 'Observed total bytes on active src to dst connections', 'total_bytes'),
                )

                for metric_name, metric_desc, metric_key in connection_traffic_metrics:
                    yield BaseCollector.gauge_collector(metric_name, metric_desc,
                                                        connection_traffic_records, metric_key, connection_traffic_labels)
