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


from collections import namedtuple
from mktxp.datasource.base_ds import BaseDSProcessor


class IPConnectionDatasource:
    ''' IP connections data provider
    '''
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None):
        if metric_labels is None:
            metric_labels = []
        try:
            api = router_entry.api_connection.router_api()
            ipv4_cnt_str = '0'
            ipv6_cnt_str = '0'

            res = api.get_resource('/ip/firewall/connection/').call('print', {'count-only': ''})
            cnt_str = res.done_message.get('ret')
            if cnt_str is not None:
                ipv4_cnt_str = cnt_str

            try:
                res_v6 = api.get_resource('/ipv6/firewall/connection/').call('print', {'count-only': ''})
                cnt_str_v6 = res_v6.done_message.get('ret')
                if cnt_str_v6 is not None:
                    ipv6_cnt_str = cnt_str_v6
            except Exception:
                pass

            try:
                ipv4_count = int(ipv4_cnt_str)
            except (ValueError, TypeError):
                ipv4_count = 0

            try:
                ipv6_count = int(ipv6_cnt_str)
            except (ValueError, TypeError):
                ipv6_count = 0

            records = [{
                'count': str(ipv4_count + ipv6_count),
                'ipv4_count': str(ipv4_count),
                'ipv6_count': str(ipv6_count)
            }]
            return BaseDSProcessor.trimmed_records(router_entry, router_records = records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting IP connection info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


class IPConnectionStatsDatasource:
    ''' IP connections stats data provider
    '''
    @staticmethod
    def strip_port(address):
        if address.startswith('['):
            return address[1:address.find(']')]
        colons = address.count(':')
        if colons == 1:
            return address.split(':')[0]
        return address

    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, add_router_id = True):
        if metric_labels is None:
            metric_labels = []
        try:
            # First, check if there are any connections
            count_records = IPConnectionDatasource.metric_records(router_entry)
            if count_records[0].get('count', 0) == '0':
                return []

            if router_entry.config_entry.connection_stats_destinations:
                proplist = 'src-address,dst-address,protocol'
            else:
                proplist = 'src-address'

            api = router_entry.api_connection.router_api()
            connection_records = api.get_resource('/ip/firewall/connection/').call('print', {'.proplist': proplist})
            try:
                connection_records_v6 = api.get_resource('/ipv6/firewall/connection/').call('print', {'.proplist': proplist})
                connection_records.extend(connection_records_v6)
            except Exception:
                pass

             # calculate number of connections per src-address
            connections_per_src_address = {}
            for connection_record in connection_records:
                address = IPConnectionStatsDatasource.strip_port(connection_record.get('src-address', ''))

                count, destinations = 0, set()
                if connections_per_src_address.get(address):
                    count, destinations = connections_per_src_address[address]
                count += 1
                if router_entry.config_entry.connection_stats_destinations:
                    destination = f"{connection_record.get('dst-address')}({connection_record.get('protocol')})"
                    destinations.add(destination)
                connections_per_src_address[address] = ConnStatsEntry(count, destinations)

            # compile connections-per-interface records
            records = []
            for key, entry in connections_per_src_address.items():
                record = {'src_address': key, 'connection_count': entry.count, 'dst_addresses': ', '.join(entry.destinations)}
                if add_router_id:
                    for router_key, router_value in router_entry.router_id.items():
                        record[router_key] = router_value
                records.append(record)
            return records
        except Exception as exc:
            print(f'Error getting IP connection stats info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


ConnStatsEntry = namedtuple('ConnStatsEntry', ['count', 'destinations'])