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


from mktxp.cli.config import MKTXPConfigKeys
from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.route_ds import RouteMetricsDataSource


class RouteCollector(BaseCollector):
    ''' IP Route Metrics collector
    '''
    @staticmethod
    def collect(router_entry):
        route_labels = ['connect', 'dynamic', 'static', 'bgp', 'ospf']

        # ~*~*~*~*~*~ IPv4 ~*~*~*~*~*~
        if router_entry.config_entry.route:
            route_counts = RouteMetricsDataSource.metric_records(router_entry, metric_labels=route_labels)
            if route_counts:
                # compile total routes records
                total_routes_records = [{
                    MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                    MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                    'count': route_counts['total_routes']
                }]
                total_routes_metrics = BaseCollector.gauge_collector('routes_total_routes', 'Overall number of routes in RIB', total_routes_records, 'count')
                yield total_routes_metrics

                if 'active_routes' in route_counts:
                    active_routes_records = [{
                        MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                        MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                        'count': route_counts['active_routes']
                    }]
                    yield BaseCollector.gauge_collector('routes_active_routes', 'Overall number of active routes in RIB', active_routes_records, 'count')

                # compile route-per-protocol records
                route_per_protocol_records = [{
                    MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                    MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                    'protocol': key, 'count': value
                } for key, value in route_counts['routes_per_protocol'].items()]

                # yield route-per-protocol metrics
                route_per_protocol_metrics = BaseCollector.gauge_collector('routes_protocol_count', 'Number of routes per protocol in RIB', route_per_protocol_records, 'count', ['protocol'])
                yield route_per_protocol_metrics

                if 'active_routes_per_protocol' in route_counts:
                    active_per_protocol_records = [{
                        MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                        MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                        'protocol': key, 'count': value
                    } for key, value in route_counts['active_routes_per_protocol'].items()]
                    yield BaseCollector.gauge_collector('routes_active_protocol_count', 'Number of active routes per protocol in RIB', active_per_protocol_records, 'count', ['protocol'])

        # ~*~*~*~*~*~ IPv6 ~*~*~*~*~*~
        if router_entry.config_entry.ipv6_route:
            route_counts = RouteMetricsDataSource.metric_records(router_entry, metric_labels=route_labels, ipv6=True)
            if route_counts:
                # compile total routes records
                total_routes_records = [{
                    MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                    MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                    'count': route_counts['total_routes']
                }]
                total_routes_metrics = BaseCollector.gauge_collector('routes_total_routes_ipv6', 'Overall number of routes in RIB (IPv6)', total_routes_records, 'count')
                yield total_routes_metrics

                if 'active_routes' in route_counts:
                    active_routes_records = [{
                        MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                        MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                        'count': route_counts['active_routes']
                    }]
                    yield BaseCollector.gauge_collector('routes_active_routes_ipv6', 'Overall number of active routes in RIB (IPv6)', active_routes_records, 'count')

                # compile route-per-protocol records
                route_per_protocol_records = [{
                    MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                    MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                    'protocol': key, 'count': value
                } for key, value in route_counts['routes_per_protocol'].items()]

                # yield route-per-protocol metrics
                route_per_protocol_metrics = BaseCollector.gauge_collector('routes_protocol_count_ipv6', 'Number of routes per protocol in RIB (IPv6)', route_per_protocol_records, 'count', ['protocol'])
                yield route_per_protocol_metrics

                if 'active_routes_per_protocol' in route_counts:
                    active_per_protocol_records = [{
                        MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                        MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                        'protocol': key, 'count': value
                    } for key, value in route_counts['active_routes_per_protocol'].items()]
                    yield BaseCollector.gauge_collector('routes_active_protocol_count_ipv6', 'Number of active routes per protocol in RIB (IPv6)', active_per_protocol_records, 'count', ['protocol'])

