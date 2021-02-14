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


class FirewallMetricsDataSource:
    ''' Firewall Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = [], raw = False, matching_only = True):
        try:
            filter_path = '/ip/firewall/filter' if not raw else '/ip/firewall/raw'
            firewall_records = router_entry.api_connection.router_api().get_resource(filter_path).call('print', {'stats':'', 'all':''})
            if matching_only:
                firewall_records = [record for record in firewall_records if int(record.get('bytes', '0')) > 0]

            # translation rules
            translation_table = {}
            if 'comment' in metric_labels:
                translation_table['comment'] = lambda value: value if value else ''           
            if 'log' in metric_labels:
                translation_table['log'] = lambda value: '1' if value == 'true' else '0'           

            return BaseDSProcessor.trimmed_records(router_entry, router_records = firewall_records, metric_labels = metric_labels, translation_table = translation_table)
        except Exception as exc:
            print(f'Error getting firewall filters info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


