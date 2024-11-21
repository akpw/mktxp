# coding=utf8
## Copyright (c) 2024 Arseniy Kuznetsov
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
from mktxp.datasource.system_resource_ds import SystemResourceMetricsDataSource
from mktxp.utils.utils import check_for_updates


class SystemResourceCollector(BaseCollector):
    ''' System Resource Metrics collector
    '''        
    @staticmethod
    def collect(router_entry):
        resource_labels = ['uptime', 'version', 'free_memory', 'total_memory', 
                           'cpu', 'cpu_count', 'cpu_frequency', 'cpu_load', 
                           'free_hdd_space', 'total_hdd_space', 
                           'architecture_name', 'board_name']
        translation_table = {'uptime': lambda value: BaseOutputProcessor.parse_timedelta_seconds(value)}

        resource_records = SystemResourceMetricsDataSource.metric_records(router_entry, metric_labels = resource_labels, translation_table=translation_table)   
        if resource_records:
            uptime_metrics = BaseCollector.gauge_collector('system_uptime', 'Time interval since boot-up', resource_records, 'uptime', ['version', 'board_name', 'cpu', 'architecture_name'])
            yield uptime_metrics

            free_memory_metrics = BaseCollector.gauge_collector('system_free_memory', 'Unused amount of RAM', resource_records, 'free_memory', ['version', 'board_name', 'cpu', 'architecture_name'])
            yield free_memory_metrics

            total_memory_metrics = BaseCollector.gauge_collector('system_total_memory', 'Amount of installed RAM', resource_records, 'total_memory', ['version', 'board_name', 'cpu', 'architecture_name'])
            yield total_memory_metrics

            free_hdd_metrics = BaseCollector.gauge_collector('system_free_hdd_space', 'Free space on hard drive or NAND', resource_records, 'free_hdd_space', ['version', 'board_name', 'cpu', 'architecture_name'])
            yield free_hdd_metrics

            total_hdd_metrics = BaseCollector.gauge_collector('system_total_hdd_space', 'Size of the hard drive or NAND', resource_records, 'total_hdd_space', ['version', 'board_name', 'cpu', 'architecture_name'])
            yield total_hdd_metrics

            cpu_load_metrics = BaseCollector.gauge_collector('system_cpu_load', 'Percentage of used CPU resources', resource_records, 'cpu_load', ['version', 'board_name', 'cpu', 'architecture_name'])
            yield cpu_load_metrics

            cpu_count_metrics = BaseCollector.gauge_collector('system_cpu_count', 'Number of CPUs present on the system', resource_records, 'cpu_count', ['version', 'board_name', 'cpu', 'architecture_name'])
            yield cpu_count_metrics

            cpu_frequency_metrics = BaseCollector.gauge_collector('system_cpu_frequency', 'Current CPU frequency', resource_records, 'cpu_frequency', ['version', 'board_name', 'cpu', 'architecture_name'])
            yield cpu_frequency_metrics

            # Check for updates
            if router_entry.config_entry.check_for_updates:
                for record in resource_records:
                    cur_version, newest_version = check_for_updates(record['version'])
                    record['newest_version'] = str(newest_version)
                    record['update_available'] = cur_version < newest_version

                update_available_metrics = BaseCollector.gauge_collector('system_update_available', 'Is there a newer version available', resource_records, 'update_available', ['newest_version',])
                yield update_available_metrics
