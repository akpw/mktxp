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
from mktxp.utils.utils import str2bool

class RouteMetricsDataSource:
    ''' Routes Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, ipv6 = False):
        ip_stack = 'ipv6' if ipv6 else 'ip'
        if metric_labels is None:
            metric_labels = []                
        try:
            #route_records = router_entry.api_connection.router_api().get_resource(f'/{ip_stack}/route').get(active='yes')
            route_records = router_entry.api_connection.router_api().get_resource(f'/{ip_stack}/route').call('print', {'proplist':'active,connect,dynamic,static,bgp,ospf'})            
            
            #active_records = [record for record in route_records if record.get('active')]
            RouteMetricsDataSource._remove_from_list_of_dict(route_records, 'active')

            return BaseDSProcessor.trimmed_records(router_entry, router_records = route_records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting {"IPv6" if ipv6 else "IPv4"} routes info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

    # helpers
    @staticmethod
    def _remove_from_list_of_dict(dict_list, key):
        indexes = []
        for index, dict in enumerate(dict_list):
            if not str2bool(dict.get(key)):
                indexes.append(index)
        offset = 0
        for index in indexes:
            dict_list.pop(index-offset)
            offset += 1        
