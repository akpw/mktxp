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
from mktxp.datasource.kid_control_device_ds import KidDeviceMetricsDataSource


class KidDeviceCollector(BaseCollector):
    """ Kid-control device Metrics collector
    """

    @staticmethod
    def collect(router_entry):
        if not (router_entry.config_entry.kid_control_assigned or router_entry.config_entry.kid_control_dynamic):
            return

        labels = ['name', 'user', 'mac_address', 'ip_address', 'bytes_down', 'bytes_up', 'rate_up', 
                    'rate_down','bytes_up', 'idle_time','blocked', 'limited', 'inactive', 'disabled']

        translation_table = {
            'rate_up': lambda value: BaseOutputProcessor.parse_rates(value),
            'rate_down': lambda value: BaseOutputProcessor.parse_rates(value),
            'idle_time': lambda value: BaseOutputProcessor.parse_timedelta_seconds(value) if value else 0,
            'blocked': lambda value: '1' if value == 'true' else '0',
            'limited': lambda value: '1' if value == 'true' else '0',
            'inactive': lambda value: '1' if value == 'true' else '0',
            'disabled': lambda value: '1' if value == 'true' else '0'}

        records = KidDeviceMetricsDataSource.metric_records(router_entry, metric_labels=labels, translation_table=translation_table)
        if records:
            # dhcp resolution
            for registration_record in records:
                BaseOutputProcessor.resolve_dhcp(router_entry, registration_record, resolve_address=False)

            info_labels = ['name', 'dhcp_name', 'mac_address', 'user', 'ip_address', 'disabled']
            yield BaseCollector.info_collector('kid_control_device', 'Kid-control device Info', records, info_labels)

            id_labels = ['name', 'dhcp_name', 'mac_address', 'user']
            yield BaseCollector.counter_collector('kid_control_device_bytes_down', 'Number of received bytes', records, 'bytes_down', id_labels)
            yield BaseCollector.counter_collector('kid_control_device_bytes_up', 'Number of transmitted bytes', records, 'bytes_up', id_labels)

            yield BaseCollector.gauge_collector('kid_control_device_rate_up', 'Device rate up', records, 'rate_up', id_labels)        
            yield BaseCollector.gauge_collector('kid_control_device_idle_time', 'Device idle time', records, 'idle_time', id_labels)
            yield BaseCollector.gauge_collector('kid_control_device_rate_down', 'Device rate down', records, 'rate_down', id_labels)
