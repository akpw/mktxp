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
from mktxp.datasource.bgp_ds import BGPMetricsDataSource


class BGPCollector(BaseCollector):
    '''BGP collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.bgp:
            return

        bgp_labels = ['name', 'remote_address', 'remote_as', 'local_as', 'remote_afi', 'local_afi', 'remote_messages', 'remote_bytes', 'local_messages', 'local_bytes', 'prefix_count', 'established', 'uptime']
        translation_table = {
                'established': lambda value: '1' if value=='true' else '0',
                'uptime': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value) if value else '0'
                }
        bgp_records = BGPMetricsDataSource.metric_records(router_entry, metric_labels=bgp_labels, translation_table = translation_table)
        
        if bgp_records:
            session_info_labes = ['name', 'remote_address', 'remote_as', 'local_as', 'remote_afi', 'local_afi']
            bgp_sessions_metrics = BaseCollector.info_collector('bgp_sessions', 'BGP sessions info', bgp_records, session_info_labes)
            yield bgp_sessions_metrics

            session_id_labes = ['name']
            remote_messages_metrics = BaseCollector.counter_collector('bgp_remote_messages', 'Number of remote messages', bgp_records, 'remote_messages', session_id_labes)
            yield remote_messages_metrics


            local_messages_metrics = BaseCollector.counter_collector('bgp_local_messages', 'Number of local messages', bgp_records, 'local_messages', session_id_labes)
            yield local_messages_metrics


            remote_bytes_metrics = BaseCollector.counter_collector('bgp_remote_bytes', 'Number of remote bytes', bgp_records, 'remote_bytes', session_id_labes)
            yield remote_bytes_metrics


            local_bytes_metrics = BaseCollector.counter_collector('bgp_local_bytes', 'Number of local bytes', bgp_records, 'local_bytes', session_id_labes)
            yield local_bytes_metrics


            prefix_count_metrics = BaseCollector.gauge_collector('bgp_prefix_count', 'BGP prefix count', bgp_records, 'prefix_count', session_id_labes)
            yield prefix_count_metrics


            established_metrics = BaseCollector.gauge_collector('bgp_established', 'BGP established', bgp_records, 'established', session_id_labes)
            yield established_metrics


            uptime_metrics = BaseCollector.gauge_collector('bgp_uptime', 'BGP uptime in milliseconds', bgp_records, 'uptime', session_id_labes)
            yield uptime_metrics

