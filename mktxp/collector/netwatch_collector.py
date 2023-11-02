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


import re
from datetime import timedelta
from mktxp.collector.base_collector import BaseCollector
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
                           "tcp_connect_time", "http_status_code", "http_resp_time",
                           ]
        netwatch_info_labels = ['host', 'timeout', 'interval', 'since', 'status', 'comment', 'name']
        netwatch_records = NetwatchMetricsDataSource.metric_records(router_entry, metric_labels = netwatch_labels)

        if netwatch_records:
            for record in netwatch_records:
                for label in record:
                    value = record.get(label, None)
                    if value:
                        record[label] = NetwatchCollector._translated_values(label, value)

            yield BaseCollector.info_collector('netwatch', 'Netwatch Info Metrics', netwatch_records, netwatch_info_labels)

            yield BaseCollector.gauge_collector('netwatch_status', 'Netwatch Status Metrics', netwatch_records, 'status', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_done_tests', 'Netwatch Done Tests', netwatch_records, 'done_tests', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_failed_tests', 'Netwatch Failed Tests', netwatch_records, 'failed_tests', ['name', 'type'])

            # ICMP specific
            yield BaseCollector.gauge_collector('netwatch_icmp_loss_count', 'Netwatch ICMP Loss Count', [record for record in netwatch_records if record.get("type", None) == "icmp"], 'loss_count', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_loss_percent', 'Netwatch ICMP Loss Percent', [record for record in netwatch_records if record.get("type", None) == "icmp"], 'loss_percent', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_avg_ms', 'Netwatch ICMP Round Trip Average', [record for record in netwatch_records if record.get("type", None) == "icmp"], 'rtt_avg', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_min_ms', 'Netwatch ICMP Round Trip Min', [record for record in netwatch_records if record.get("type", None) == "icmp"], 'rtt_min', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_max_ms', 'Netwatch ICMP Round Trip Max', [record for record in netwatch_records if record.get("type", None) == "icmp"], 'rtt_max', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_jitter_ms', 'Netwatch ICMP Round Trip Jitter', [record for record in netwatch_records if record.get("type", None) == "icmp"], 'rtt_jitter', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_icmp_rtt_stdev_ms', 'Netwatch ICMP Round Trip Stdev', [record for record in netwatch_records if record.get("type", None) == "icmp"], 'rtt_stdev', ['name', 'type'])

            # TCP specific
            yield BaseCollector.gauge_collector('netwatch_tcp_connect_time_ms', 'Netwatch TCP Connect Time', [record for record in netwatch_records if record.get("type", None) == "tcp-conn"], 'tcp_connect_time', ['name', 'type'])

            # HTTP(s) specific
            yield BaseCollector.gauge_collector('netwatch_http_status_code', 'Netwatch HTTP status code', [record for record in netwatch_records if record.get("type", None) in ["http-get", "https-get"]], 'http_status_code', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_http_resp_time', 'Netwatch HTTP status code', [record for record in netwatch_records if record.get("type", None) in ["http-get", "https-get"]], 'http_resp_time', ['name', 'type'])
            yield BaseCollector.gauge_collector('netwatch_tcp_connect_time_ms', 'Netwatch TCP Connect Time', [record for record in netwatch_records if record.get("type", None) in ["http-get", "https-get"]], 'tcp_connect_time', ['name', 'type'])

    # Helpers
    @staticmethod
    def _translated_values(label, value):
        try:
            return {
                'rtt_avg': lambda value: NetwatchCollector.parse_timedelta(value).microseconds/1000,
                'rtt_min': lambda value: NetwatchCollector.parse_timedelta(value).microseconds/1000,
                'rtt_max': lambda value: NetwatchCollector.parse_timedelta(value).microseconds/1000,
                'rtt_jitter': lambda value: NetwatchCollector.parse_timedelta(value).microseconds/1000,
                'rtt_stdev': lambda value: NetwatchCollector.parse_timedelta(value).microseconds/1000,
                'tcp_connect_time': lambda value: NetwatchCollector.parse_timedelta(value).microseconds/1000,
                'http_resp_time': lambda value: NetwatchCollector.parse_timedelta(value).microseconds/1000,
            }[label](value)
        except KeyError:
            return value

    @staticmethod
    def parse_timedelta(time):
        duration_interval_rgx = re.compile(r'((?P<seconds>\d+)s)?((?P<milliseconds>\d+)ms)?((?P<microseconds>\d+)us)?')
        time_dict = duration_interval_rgx.match(time).groupdict()
        return timedelta(**{key: int(value) for key, value in time_dict.items() if value})
