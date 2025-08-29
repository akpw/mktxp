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
from ipaddress import ip_address

class NetwatchCollector(BaseCollector):
    ''' Netwatch Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.netwatch:
            return

        netwatch_labels = [
                           # common
                           'host', 'timeout', 'interval', 'since', 'status', 'comment', 'name', "done_tests", "type", "failed_tests", "id" ,"src_address",
                           # ICMP
                           "loss_count", "loss_percent", "rtt_avg", "rtt_min", "rtt_max", "rtt_jitter", "rtt_stdev", "ttl",  "sent_count", 
                           # TCP+HTTP(s)
                           "tcp_connect_time", "port", 
                           # HTTP 
                           "http_status_code", "http_resp_time",
                           # DNS
                           "dns_server", "record_type", "ip"
                          ]
        translation_table = {
            'status': lambda value: '1' if value == 'up' else '0',      
            'rtt_avg': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'rtt_min': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'rtt_max': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'rtt_jitter': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'rtt_stdev': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'tcp_connect_time': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'http_resp_time': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else '0',
            'ip': lambda value: int(ip_address(value)) if value else '0',
        }
        netwatch_records = NetwatchMetricsDataSource.metric_records(router_entry, metric_labels = netwatch_labels, translation_table=translation_table)

        if netwatch_records:
            netwatch_info_labels = ['host', 'timeout', 'interval', 'since', 'status', 'comment', 'name']
            if router_entry.config_entry.netwatch_target_details:
                netwatch_info_labels.extend(['type', 'src_address'])
            yield BaseCollector.info_collector('netwatch', 'Netwatch Info Metrics', netwatch_records, netwatch_info_labels)

            base_metrics_labels = ['name', 'type']
            if router_entry.config_entry.netwatch_target_details:
                base_metrics_labels.extend(['host', 'src_address', 'id'])

            status_labels = base_metrics_labels.copy()
            yield BaseCollector.gauge_collector('netwatch_status', 'Netwatch Status Metrics', netwatch_records, 'status', status_labels)
            yield BaseCollector.gauge_collector('netwatch_done_tests', 'Netwatch Done Tests', netwatch_records, 'done_tests', status_labels)
            yield BaseCollector.gauge_collector('netwatch_failed_tests', 'Netwatch Failed Tests', netwatch_records, 'failed_tests', status_labels)

            # ICMP specific
            icmp_records = [record for record in netwatch_records if record.get("type", None) == "icmp"]
            icmp_labels  = base_metrics_labels.copy()
            if router_entry.config_entry.netwatch_target_details:
                icmp_labels.extend(['sent_count', 'ttl'])
            yield BaseCollector.gauge_collector('netwatch_icmp_loss_count', 'Netwatch ICMP Loss Count', icmp_records, 'loss_count', icmp_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_loss_percent', 'Netwatch ICMP Loss Percent', icmp_records, 'loss_percent', icmp_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_avg_ms', 'Netwatch ICMP Round Trip Average', icmp_records, 'rtt_avg', icmp_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_min_ms', 'Netwatch ICMP Round Trip Min', icmp_records, 'rtt_min', icmp_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_max_ms', 'Netwatch ICMP Round Trip Max', icmp_records, 'rtt_max', icmp_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_jitter_ms', 'Netwatch ICMP Round Trip Jitter', icmp_records, 'rtt_jitter', icmp_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_stdev_ms', 'Netwatch ICMP Round Trip Stdev', icmp_records, 'rtt_stdev', icmp_labels)

            # TCP specific
            tcp_records = [record for record in netwatch_records if record.get("type", None) == "tcp-conn"]
            tcp_labels  = base_metrics_labels.copy()
            if router_entry.config_entry.netwatch_target_details:
                tcp_labels.extend(['port'])
            yield BaseCollector.gauge_collector('netwatch_tcp_connect_time_ms', 'Netwatch TCP Connect Time', tcp_records, 'tcp_connect_time', tcp_labels)

            # HTTP(s) specific
            http_records = [record for record in netwatch_records if record.get("type", None) in ["http-get", "https-get"]]
            http_labels  = base_metrics_labels.copy()
            yield BaseCollector.gauge_collector('netwatch_http_status_code', 'Netwatch HTTP status code', http_records, 'http_status_code', http_labels)
            yield BaseCollector.gauge_collector('netwatch_http_resp_time', 'Netwatch HTTP status code', http_records, 'http_resp_time', http_labels)
            yield BaseCollector.gauge_collector('netwatch_tcp_connect_time_ms', 'Netwatch TCP Connect Time', http_records, 'tcp_connect_time', http_labels)
            
            # DNS specific
            dns_records = [record for record in netwatch_records if record.get("type", None) == "dns"]
            dns_labels  = base_metrics_labels.copy()
            if router_entry.config_entry.netwatch_target_details:
                dns_labels.extend(['dns_server', 'record_type', 'src_address'])
            yield BaseCollector.gauge_collector('netwatch_dns_resolved_address', 'Netwatch TCP Connect Time', dns_records, 'ip', dns_labels)
