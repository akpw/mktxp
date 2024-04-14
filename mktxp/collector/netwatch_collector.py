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
from mktxp.datasource.netwatch_ds import NetwatchMetricsDataSource


class NetwatchCollector(BaseCollector):
    ''' Netwatch Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.netwatch:
            return

        netwatch_labels = ['host', 'timeout', 'interval', 'since', 'status', 'comment', 'name', "done_tests", "type", "failed_tests",
                           "loss_count", "loss_percent", "rtt_avg", "rtt_min", "rtt_max", "rtt_jitter", "rtt_stdev",
                           "tcp_connect_time", "http_status_code", "http_resp_time",                           ]
        translation_table = {
            'status': lambda value: '1' if value == 'up' else '0',      
            'rtt_avg': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'rtt_min': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'rtt_max': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'rtt_jitter': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'rtt_stdev': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'tcp_connect_time': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'http_resp_time': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0'}
        netwatch_records = NetwatchMetricsDataSource.metric_records(router_entry, metric_labels = netwatch_labels, translation_table=translation_table)

        if netwatch_records:
            netwatch_info_labels = ['host', 'timeout', 'interval', 'since', 'status', 'comment', 'name']
            yield BaseCollector.info_collector('netwatch', 'Netwatch Info Metrics', netwatch_records, netwatch_info_labels)

            yield BaseCollector.gauge_collector('netwatch_status', 'Netwatch Status Metrics', netwatch_records, 'status', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_done_tests', 'Netwatch Done Tests', netwatch_records, 'done_tests', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_failed_tests', 'Netwatch Failed Tests', netwatch_records, 'failed_tests', ['name', 'type'])

            # ICMP specific
            icmp_records = [record for record in netwatch_records if record.get("type", None) == "icmp"]
            yield BaseCollector.gauge_collector('netwatch_icmp_loss_count', 'Netwatch ICMP Loss Count', icmp_records, 'loss_count', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_loss_percent', 'Netwatch ICMP Loss Percent', icmp_records, 'loss_percent', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_avg_ms', 'Netwatch ICMP Round Trip Average', icmp_records, 'rtt_avg', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_min_ms', 'Netwatch ICMP Round Trip Min', icmp_records, 'rtt_min', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_max_ms', 'Netwatch ICMP Round Trip Max', icmp_records, 'rtt_max', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_jitter_ms', 'Netwatch ICMP Round Trip Jitter', icmp_records, 'rtt_jitter', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_stdev_ms', 'Netwatch ICMP Round Trip Stdev', icmp_records, 'rtt_stdev', ['name', 'type'])

            # TCP specific
            tcp_records = [record for record in netwatch_records if record.get("type", None) == "tcp-conn"]
            yield BaseCollector.gauge_collector('netwatch_tcp_connect_time_ms', 'Netwatch TCP Connect Time', tcp_records, 'tcp_connect_time', ['name', 'type'])

            # HTTP(s) specific
            http_records = [record for record in netwatch_records if record.get("type", None) in ["http-get", "https-get"]]
            yield BaseCollector.gauge_collector('netwatch_http_status_code', 'Netwatch HTTP status code', http_records, 'http_status_code', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_http_resp_time', 'Netwatch HTTP status code', http_records, 'http_resp_time', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_tcp_connect_time_ms', 'Netwatch TCP Connect Time', http_records, 'tcp_connect_time', ['name', 'type'])
