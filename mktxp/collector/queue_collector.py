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
from mktxp.datasource.queue_ds import QueueMetricsDataSource


class QueueTreeCollector(BaseCollector):
    '''Queue Tree collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.queue:
            return

        qt_labels = ['name', 'parent', 'packet_mark', 'limit_at', 'max_limit', 'priority', 'bytes', 'queued_bytes', 'dropped', 'rate', 'disabled']
        qt_records = QueueMetricsDataSource.metric_records(router_entry, metric_labels=qt_labels, kind = 'tree')

        if qt_records:
            qt_rate_metric = BaseCollector.counter_collector('queue_tree_rates', 'Average passing data rate in bytes per second', qt_records, 'rate', ['name'])
            yield qt_rate_metric

            qt_byte_metric = BaseCollector.counter_collector('queue_tree_bytes', 'Number of processed bytes', qt_records, 'bytes', ['name'])
            yield qt_byte_metric

            qt_queued_metric = BaseCollector.counter_collector('queue_tree_queued_bytes', 'Number of queued bytes', qt_records, 'queued_bytes', ['name'])
            yield qt_queued_metric


            qt_drop_metric = BaseCollector.counter_collector('queue_tree_dropped', 'Number of dropped bytes', qt_records, 'dropped', ['name'])
            yield qt_drop_metric


class QueueSimpleCollector(BaseCollector):
    '''Simple Queue collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.queue:
            return

        qt_labels = ['name', 'parent', 'packet_mark', 'limit_at', 'max_limit', 'priority', 'bytes', 'packets', 'queued_bytes', 'queued_packets','dropped', 'rate', 'packet_rate', 'disabled']
        qt_records = QueueMetricsDataSource.metric_records(router_entry, metric_labels=qt_labels, kind = 'simple')

        if qt_records:
            qt_rate_metric = BaseCollector.counter_collector('queue_simple_rates_upload', 'Average passing upload data rate in bytes per second', qt_records, 'rate_up', ['name'])
            yield qt_rate_metric

            qt_rate_metric = BaseCollector.counter_collector('queue_simple_rates_download', 'Average passing download data rate in bytes per second', qt_records, 'rate_down', ['name'])
            yield qt_rate_metric


            qt_byte_metric = BaseCollector.counter_collector('queue_simple_bytes_upload', 'Number of upload processed bytes', qt_records, 'bytes_up', ['name'])
            yield qt_byte_metric

            qt_byte_metric = BaseCollector.counter_collector('queue_simple_bytes_download', 'Number of download processed bytes', qt_records, 'bytes_down', ['name'])
            yield qt_byte_metric


            qt_queued_metric = BaseCollector.counter_collector('queue_simple_queued_bytes_upload', 'Number of upload queued bytes', qt_records, 'queued_bytes_up', ['name'])
            yield qt_queued_metric


            qt_queued_metric = BaseCollector.counter_collector('queue_simple_queued_bytes_downloadd', 'Number of download queued bytes', qt_records, 'queued_bytes_down', ['name'])
            yield qt_queued_metric


            qt_drop_metric = BaseCollector.counter_collector('queue_simple_dropped_upload', 'Number of upload dropped bytes', qt_records, 'dropped_up', ['name'])
            yield qt_drop_metric


            qt_drop_metric = BaseCollector.counter_collector('queue_simple_dropped_download', 'Number of download dropped bytes', qt_records, 'dropped_down', ['name'])
            yield qt_drop_metric

