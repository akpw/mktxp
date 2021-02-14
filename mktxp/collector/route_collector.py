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


from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.route_ds import RouteMetricsDataSource


class RouteCollector(BaseCollector):
    ''' IP Route Metrics collector
    '''        
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.route:
            return

        route_labels = ['connect', 'dynamic', 'static', 'bgp', 'ospf']
        route_records = RouteMetricsDataSource.metric_records(router_entry, metric_labels = route_labels)   
        if route_records:       
            # compile total routes records
            total_routes = len(route_records)
            total_routes_records = [{ MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                                      MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                                      'count': total_routes
                                    }]
            total_routes_metrics = BaseCollector.gauge_collector('routes_total_routes', 'Overall number of routes in RIB', total_routes_records, 'count')
            yield total_routes_metrics


            # init routes per protocol (with 0)
            routes_per_protocol = {route_label: 0 for route_label in route_labels}
            for route_record in route_records:
                for route_label in route_labels:
                    if route_record.get(route_label):
                        routes_per_protocol[route_label] += 1 

            # compile route-per-protocol records
            route_per_protocol_records = [{ MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                                            MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                                            'protocol': key, 'count': value} for key, value in routes_per_protocol.items()]
            
            # yield route-per-protocol metrics
            route_per_protocol_metrics = BaseCollector.gauge_collector('routes_protocol_count', 'Number of routes per protocol in RIB', route_per_protocol_records, 'count', ['protocol'])
            yield route_per_protocol_metrics

