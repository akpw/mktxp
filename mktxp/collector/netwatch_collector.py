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

        netwatch_labels = ['host', 'comment', 'timeout', 'interval', 'type']
        netwatch_values = ['since', 'status', 'loss_count', 'response_count', 'rtt_avg', 'rtt_jitter', 'rtt_max', 'rtt_min', 'rtt_stdev', 'sent_count', 'http_status_code', 'http_resp_time', 'tcp_connect_time']
        netwatch_records = NetwatchMetricsDataSource.metric_records(router_entry, metric_labels = netwatch_labels + netwatch_values)

        if netwatch_records:
            yield BaseCollector.gauge_collector('netwatch_status', 'Netwatch Status Metrics', netwatch_records, 'status', netwatch_labels)
            yield BaseCollector.gauge_collector('netwatch_since', 'Netwatch Status Since Metrics', netwatch_records, 'since', netwatch_labels)
            
            # ICMP
            yield BaseCollector.gauge_collector('netwatch_icmp_loss_count', 'Netwatch ICMP Loss Count', netwatch_records, 'loss_count', netwatch_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_response_count', 'Netwatch ICMP Loss Count', netwatch_records, 'response_count', netwatch_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_avg', 'Netwatch ICMP RTT Average', netwatch_records, 'rtt_avg', netwatch_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_jitter', 'Netwatch ICMP RTT Jitter', netwatch_records, 'rtt_jitter', netwatch_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_max', 'Netwatch ICMP RTT Max', netwatch_records, 'rtt_max', netwatch_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_min', 'Netwatch ICMP RTT Min', netwatch_records, 'rtt_min', netwatch_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_stdev', 'Netwatch ICMP RTT Standard Deviation', netwatch_records, 'rtt_stdev', netwatch_labels)
            yield BaseCollector.gauge_collector('netwatch_icmp_sent_count', 'Netwatch ICMP Sent Count', netwatch_records, 'sent_count', netwatch_labels)

            # HTTP(S)
            yield BaseCollector.gauge_collector('netwatch_http_status_code', 'Netwatch HTTP Status Code', netwatch_records, 'http_status_code', netwatch_labels)
            yield BaseCollector.gauge_collector('netwatch_http_response_time', 'Netwatch HTTP Response Time', netwatch_records, 'http_resp_time', netwatch_labels)
            yield BaseCollector.gauge_collector('tcp_connect_time', 'Netwatch HTTP TCP Connect Time', netwatch_records, 'tcp_connect_time', netwatch_labels)
            
