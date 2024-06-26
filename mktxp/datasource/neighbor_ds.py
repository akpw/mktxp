# coding=utf8
# Copyright (c) 2020 Arseniy Kuznetsov
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


from mktxp.datasource.base_ds import BaseDSProcessor


class NeighborDataSource:
    def metric_records(router_entry, metric_labels, ipv6=False):    
        
        metric_labels = metric_labels or []                        
        router_records = []        
        
        try:
            if ipv6:
                router_records = router_entry.api_connection.router_api().get_resource(f'/ipv6/neighbor').get(status='reachable')
            else:
                router_records = router_entry.api_connection.router_api().get_resource(f'/ip/neighbor').get()
            return BaseDSProcessor.trimmed_records(router_entry, router_records=router_records, metric_labels=metric_labels)
        except Exception as exc:
            print(f'Error getting Neighbors info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
