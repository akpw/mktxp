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


class KidDeviceMetricsDataSource:
    """ Kid-control device Metrics data provider
    """

    @staticmethod
    def metric_records(router_entry, *, metric_labels=None, translation_table=None):
        if metric_labels is None:
            metric_labels = []
        try:
            device_records = []
            records = router_entry.api_connection.router_api().get_resource('/ip/kid-control/device').get()
            for record in records:
                if record.get('user') or router_entry.config_entry.kid_control_dynamic:
                    device_records.append(record)
            return BaseDSProcessor.trimmed_records(router_entry, router_records=device_records, metric_labels=metric_labels, translation_table=translation_table)
        except Exception as exc:
            print(
                f'Error getting Kid-control device info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
