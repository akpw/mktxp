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


class PoolMetricsDataSource:
    ''' Pool Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = []):
        try:
            pool_records = router_entry.api_connection.router_api().get_resource('/ip/pool').get()
            return BaseDSProcessor.trimmed_records(router_entry, router_records = pool_records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting pool info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


class PoolUsedMetricsDataSource:
    ''' Pool/Used Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = []):
        try:
            pool_used_records = router_entry.api_connection.router_api().get_resource('/ip/pool/used').get()
            return BaseDSProcessor.trimmed_records(router_entry, router_records = pool_used_records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting pool used info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None