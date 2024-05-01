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


class QueueMetricsDataSource:
    ''' Queue Metrics data provider
    '''             
    @staticmethod    
    def metric_records(router_entry, *, metric_labels = None, kind = 'tree'):
        if metric_labels is None:
            metric_labels = []                
        try:
            queue_records = router_entry.api_connection.router_api().get_resource(f'/queue/{kind}/').get()
            queue_records = BaseDSProcessor.trimmed_records(router_entry, router_records = queue_records, metric_labels = metric_labels)            
        except Exception as exc:
            print(f'Error getting system resource info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

        if kind == 'tree':            
            return queue_records

        # simple queue records need splitting upload/download values
        splitted_queue_records = []
        for queue_record in queue_records:
            splitted_queue_record = {}
            for key, value in queue_record.items():
                split_values = value.split('/')
                if split_values and len(split_values) > 1:
                    splitted_queue_record[f'{key}_up'] = split_values[0]
                    splitted_queue_record[f'{key}_down'] = split_values[1]
                else:
                    splitted_queue_record[key] = value
            splitted_queue_records.append(splitted_queue_record)            
        return splitted_queue_records

        


