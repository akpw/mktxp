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
from mktxp.datasource.routing_stats_ds import RoutingStatsMetricsDataSource
from mktxp.utils.utils import parse_mkt_uptime


class RoutingStatsCollector(BaseCollector):
    '''Routing Stats collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.routing_stats:
            return

        routing_stats_labels = ['tasks', 'id', 'private_mem_blocks', 'shared_mem_blocks', 'kernel_time', 'process_time', 'max_busy', 'max_calc']
        translation_table = {
                'kernel_time': lambda value:  parse_mkt_uptime(value),
                'process_time': lambda value:  parse_mkt_uptime(value),
                'max_busy': lambda value:  parse_mkt_uptime(value),
                'max_calc': lambda value:  parse_mkt_uptime(value),
            }
        routing_stats_records = RoutingStatsMetricsDataSource.metric_records(router_entry, metric_labels=routing_stats_labels, translation_table = translation_table)
                
        if routing_stats_records:
            session_info_labels = ['tasks', 'id', 'pid']
            routing_stats_processes_metrics = BaseCollector.info_collector('routing_stats_processes', 'Routing Process Stats', routing_stats_records, session_info_labels)
            yield routing_stats_processes_metrics

            session_id_labels = ['tasks']
            routing_stats_private_mem_metrics = BaseCollector.gauge_collector('routing_stats_private_mem', 'Private Memory Blocks Used', routing_stats_records, 'private_mem_blocks', session_id_labels)
            yield routing_stats_private_mem_metrics

            routing_stats_shared_mem_metrics = BaseCollector.gauge_collector('routing_stats_shared_mem', 'Shared Memory Blocks Used', routing_stats_records, 'shared_mem_blocks', session_id_labels)
            yield routing_stats_shared_mem_metrics
            
            kernel_time_metrics = BaseCollector.counter_collector('routing_stats_kernel_time', 'Process Kernel Time', routing_stats_records, 'kernel_time', session_id_labels)
            yield kernel_time_metrics

            process_time_metrics = BaseCollector.counter_collector('routing_stats_process_time', 'Process Time', routing_stats_records, 'process_time', session_id_labels)
            yield process_time_metrics

            max_busy_metrics = BaseCollector.counter_collector('routing_stats_max_busy', 'Max Busy Time', routing_stats_records, 'max_busy', session_id_labels)
            yield max_busy_metrics
            
            max_calc_metrics = BaseCollector.counter_collector('routing_stats_max_calc', 'Max Calc Time', routing_stats_records, 'max_calc', session_id_labels)
            yield max_calc_metrics
