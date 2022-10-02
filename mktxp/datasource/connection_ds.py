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


class IPConnectionDatasource:
    ''' IP connections data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None):
        if metric_labels is None:
            metric_labels = []        
        try:
            answer = router_entry.api_connection.router_api().get_binary_resource('/ip/firewall/connection/').call('print', {'count-only': b''})
            # answer looks and feels like an empty list: [], but it has a special attribute `done_message`
            done_message = answer.done_message
            # `done_msg` is a dict with the return code as a key - which is the count that we are looking for
            cnt = done_message['ret'].decode()
            records = [{'count': cnt}]
            return BaseDSProcessor.trimmed_records(router_entry, router_records = records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting IP connection info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
