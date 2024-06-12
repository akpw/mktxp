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


class PackageMetricsDataSource:
    ''' Wireless Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, add_router_id = True):
        if metric_labels is None:
            metric_labels = []                
        try:
            package_records = router_entry.api_connection.router_api().get_resource('/system/package').get()
            return BaseDSProcessor.trimmed_records(router_entry, router_records = package_records, metric_labels = metric_labels, add_router_id = add_router_id)
        except Exception as exc:
            print(f'Error getting installed packages info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


    @staticmethod
    def is_package_installed (router_entry, package_name = None):
        if package_name:
            try:
                package_records = router_entry.api_connection.router_api().get_resource('/system/package').get()
                for package_record in package_records:
                    if package_record['name'] == package_name:
                        return True
            except Exception as exc:
                print(f'Error getting an installed package status from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')        
        return False
