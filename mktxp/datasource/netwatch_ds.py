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


class NetwatchMetricsDataSource:
    ''' Netwatch Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels=None, translation_table=None):
        if metric_labels is None:
            metric_labels = []                
        try:
            netwatch_records = router_entry.api_connection.router_api().get_resource('/tool/netwatch').get(disabled='false')
            if 'name' in metric_labels:
                for netwatch_record in netwatch_records:
                    comment = netwatch_record.get('comment')
                    host = netwatch_record.get('host')        
                    if comment:
                        netwatch_record['name'] = f'{host} ({comment[0:20]})' if not router_entry.config_entry.use_comments_over_names else comment
                    else:
                        netwatch_record['name'] = host

            return BaseDSProcessor.trimmed_records(router_entry, router_records = netwatch_records, translation_table = translation_table, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting Netwatch info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

