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


from mktxp.datasource.base_ds import BaseDSProcessor


class RouterboardMetricsDataSource:
    ''' Routerboard Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None):
        if metric_labels is None:
            metric_labels = []                
        try:
            routerboard_records = router_entry.api_connection.router_api().get_resource('/system/routerboard').get()
            return BaseDSProcessor.trimmed_records(router_entry, router_records = routerboard_records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting system routerboard info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

    @staticmethod
    def firmware_version(router_entry):
        try:
            version_st = router_entry.api_connection.router_api().get_resource('/system/routerboard').call('print', {'proplist':'current-firmware'})[0]
            if version_st.get('current-firmware'):
                return version_st['current-firmware']
            return None
        except Exception as exc:
            print(f'Error getting routerboard current-firmware from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

    @staticmethod
    def firmware_upgrade_version(router_entry):
        try:
            version_st = router_entry.api_connection.router_api().get_resource('/system/routerboard').call('print', {'proplist':'upgrade-firmware'})[0]
            if version_st.get('upgrade-firmware'):
                return version_st['upgrade-firmware']
            return None
        except Exception as exc:
            print(f'Error getting routerboard upgrade-firmware from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

