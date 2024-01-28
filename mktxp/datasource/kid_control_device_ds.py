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


from mktxp.datasource.base_ds import BaseDSProcessor
from mktxp.flow.processor.output import BaseOutputProcessor
from mktxp.utils.utils import parse_mkt_uptime


class KidDeviceMetricsDataSource:
    """ Kid-control device Metrics data provider
    """

    @staticmethod
    def metric_records(router_entry, *, metric_labels=None):
        if metric_labels is None:
            metric_labels = []
        try:
            device_records = []
            records = router_entry.api_connection.router_api().get_resource('/ip/kid-control/device').get()
            for record in records:
                if record.get('user'):
                    device_records.append(record)


            translation_table = {
                'rate_up': lambda value: BaseOutputProcessor.parse_rates(value),
                'rate_down': lambda value: BaseOutputProcessor.parse_rates(value),
                'idle_time': lambda value: parse_mkt_uptime(value) if value else 0,
                'blocked': lambda value: '1' if value == 'true' else '0',
                'limited': lambda value: '1' if value == 'true' else '0',
                'inactive': lambda value: '1' if value == 'true' else '0',
                'disabled': lambda value: '1' if value == 'true' else '0'
            }
            return BaseDSProcessor.trimmed_records(router_entry, router_records=device_records, metric_labels=metric_labels, translation_table=translation_table)
        except Exception as exc:
            print(
                f'Error getting Kid-control device info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
