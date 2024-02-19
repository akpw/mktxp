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
        if not router_entry.config_entry.kid_control_devices:
            return

        labels = ['name', 'user', 'mac_address', 'ip_address', 'bytes_down', 'bytes_up', 'rate_up', 'rate_down',
                  'bytes_up', 'idle_time',
                  'blocked', 'limited', 'inactive', 'disabled']
        info_labels = ['name', 'user', 'mac_address', 'ip_address', 'disabled']
        records = KidDeviceMetricsDataSource.metric_records(router_entry, metric_labels=labels)

        if records:
            # translate records to appropriate values
            for record in records:
                for label in record:
                    value = record.get(label, None)
                    if value:
                        record[label] = KidDeviceCollector._translated_values(label, value)

            yield BaseCollector.info_collector('kid_control_device', 'Kid-control device Info', records, info_labels)
            yield BaseCollector.gauge_collector('kid_control_device_bytes_down', 'Number of received bytes', records, 'bytes_down', ['name', 'mac_address', 'user', 'ip_address'])
            yield BaseCollector.gauge_collector('kid_control_device_bytes_up', 'Number of transmitted bytes', records, 'bytes_up', ['name', 'mac_address', 'user', 'ip_address'])
            yield BaseCollector.gauge_collector('kid_control_device_rate_down', 'Device rate down', records, 'rate_down', ['name', 'mac_address', 'user', 'ip_address'])
            yield BaseCollector.gauge_collector('kid_control_device_rate_up', 'Device rate up', records, 'rate_up', ['name', 'mac_address', 'user', 'ip_address'])
            yield BaseCollector.gauge_collector('kid_control_device_idle_time', 'Device idle time', records, 'idle_time', ['name', 'mac_address', 'user', 'ip_address'])

    # Helpers
    @staticmethod
    def _translated_values(monitor_label, value):
        try:
            return {
                'rate_up': lambda value: BaseOutputProcessor.parse_rates(value),
                'rate_down': lambda value: BaseOutputProcessor.parse_rates(value),
                'idle_time': lambda value: BaseOutputProcessor.parse_timedelta_seconds(value),
                'blocked': lambda value: '1' if value == 'true' else '0',
                'limited': lambda value: '1' if value == 'true' else '0',
                'inactive': lambda value: '1' if value == 'true' else '0',
                'disabled': lambda value: '1' if value == 'true' else '0',
            }[monitor_label](value)
        except KeyError:
            # default to just returning the value
            return value
