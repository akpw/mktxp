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


class AddressListMetricsDataSource:
    """Address List Metrics data provider"""
    @staticmethod
    def metric_records(router_entry, address_lists, ip_version, *, metric_labels=None, translation_table=None):
        if metric_labels is None:
            metric_labels = []
        
        all_records = []
        try:
            api_path = f"/{ip_version}/firewall/address-list"
            resource = router_entry.api_connection.router_api().get_resource(api_path)
            for list_name in address_lists:
                # Use memory-safe fetching by querying specific list
                records = resource.get(list=list_name)
                all_records.extend(records)

            return BaseDSProcessor.trimmed_records(router_entry, router_records=all_records,
                                                   metric_labels=metric_labels, translation_table=translation_table)
        except Exception as exc:
            print(f'Error getting Address List info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

    @staticmethod
    def count_metric_records(router_entry, address_lists, ip_version):
        api_path = f'/{ip_version}/firewall/address-list'
        queries = {
            'total': {},
            'dynamic': {'dynamic': 'yes'},
            'static': {'dynamic': 'no'}
        }
        
        # Count entries in all lists
        all_lists_counts = {}
        for count_type, query in queries.items():
            count = BaseDSProcessor.count_records(router_entry, api_path=api_path, api_query=query)
            if count is None:
                return None  # Some error occurred
            all_lists_counts[count_type] = count

        # Count entries in selected lists
        selected_lists_counts = {}
        for list_name in address_lists:
            selected_lists_counts[list_name] = {}
            for count_type, query in queries.items():
                query['list'] = list_name
                count = BaseDSProcessor.count_records(router_entry, api_path=api_path, api_query=query)
                if count is None:
                    return None  # Some error occurred
                selected_lists_counts[list_name][count_type] = count
        
        return {
            'all_lists': all_lists_counts,
            'selected_lists': selected_lists_counts
        }
