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
from mktxp.datasource.queue_ds import QueueTreeMetricsDataSource


class QueueTreeCollector(BaseCollector):
    '''Queue Tree collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.installed_packages:
            return

        qt_labels = ['name', 'parent', 'packet_mark', 'limit_at', 'max_limit', 'priority', 'bytes', 'packets', 'queued_bytes', 'queued_packets','dropped', 'rate', 'packet_rate', 'disabled']
        qt_records = QueueTreeMetricsDataSource.metric_records(router_entry, metric_labels=qt_labels)

        if qt_records:
            qt_rate_metric = BaseCollector.counter_collector('queue_tree_rates', 'Average passing data rate in bytes per second', qt_records, 'rate', ['name'])
            yield qt_rate_metric

            qt_packet_rate_metric = BaseCollector.counter_collector('queue_tree_packet_rates', 'Average passing data rate in packets per second', qt_records, 'packet_rate', ['name'])
            yield qt_packet_rate_metric

            qt_byte_metric = BaseCollector.counter_collector('queue_tree_bytes', 'Number of processed bytes', qt_records, 'bytes', ['name'])
            yield qt_byte_metric

            qt_packet_metric = BaseCollector.counter_collector('queue_tree_pakets', 'Number of processed packets', qt_records, 'packets', ['name'])
            yield qt_packet_metric

            qt_queued_metric = BaseCollector.counter_collector('queue_tree_queued_bytes', 'Number of queued bytes', qt_records, 'queued_bytes', ['name'])
            yield qt_queued_metric


            qt_queued_packets_metric = BaseCollector.counter_collector('queue_tree_queued_packets', 'Number of queued packets', qt_records, 'queued_packets', ['name'])
            yield qt_queued_packets_metric


            qt_drop_metric = BaseCollector.counter_collector('queue_tree_dropped', 'Number of dropped packets', qt_records, 'dropped', ['name'])
            yield qt_drop_metric


class SimpleCollector(BaseCollector):
    '''Simple Queue collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.installed_packages:
            return

        qt_labels = ['name', 'parent', 'packet_mark', 'limit_at', 'max_limit', 'priority', 'bytes', 'packets', 'queued_bytes', 'queued_packets','dropped', 'rate', 'packet_rate', 'disabled']
        qt_records = QueueTreeMetricsDataSource.metric_records(router_entry, metric_labels=qt_labels)

        if qt_records:
            qt_rate_metric = BaseCollector.counter_collector('queue_tree_rates', 'Average passing data rate in bytes per second', qt_records, 'rate', ['name'])
            yield qt_rate_metric

            qt_packet_rate_metric = BaseCollector.counter_collector('queue_tree_packet_rates', 'Average passing data rate in packets per second', qt_records, 'packet_rate', ['name'])
            yield qt_packet_rate_metric

            qt_byte_metric = BaseCollector.counter_collector('queue_tree_bytes', 'Number of processed bytes', qt_records, 'bytes', ['name'])
            yield qt_byte_metric

            qt_packet_metric = BaseCollector.counter_collector('queue_tree_pakets', 'Number of processed packets', qt_records, 'packets', ['name'])
            yield qt_packet_metric

            qt_queued_metric = BaseCollector.counter_collector('queue_tree_queued_bytes', 'Number of queued bytes', qt_records, 'queued_bytes', ['name'])
            yield qt_queued_metric


            qt_queued_packets_metric = BaseCollector.counter_collector('queue_tree_queued_packets', 'Number of queued packets', qt_records, 'queued_packets', ['name'])
            yield qt_queued_packets_metric


            qt_drop_metric = BaseCollector.counter_collector('queue_tree_dropped', 'Number of dropped packets', qt_records, 'dropped', ['name'])
            yield qt_drop_metric

