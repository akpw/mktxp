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


class RouteMetricsDataSource:
    ''' Routes Metrics data provider
    '''
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, ipv6 = False):
        if metric_labels is None:
            metric_labels = []
        
        ip_stack = 'ipv6' if ipv6 else 'ip'
        api_path = f'/{ip_stack}/route'

        try:
            # Get total routes
            total_routes = BaseDSProcessor.count_records(router_entry, api_path=api_path)
            if total_routes is None:
                # Abort if there was an error
                return None

            # Get counts per protocol
            routes_per_protocol = {}
            for label in metric_labels:
                count = BaseDSProcessor.count_records(router_entry, api_path=api_path, api_query={f'{label}': 'yes'})
                if count is None:
                    # Abort if there was an error
                    return None
                routes_per_protocol[label] = count

            return {
                'total_routes': total_routes,
                'routes_per_protocol': routes_per_protocol
            }
        except Exception as exc:
            print(f'Error getting {"IPv6" if ipv6 else "IPv4"} routes info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
