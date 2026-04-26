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


def _connection_resource_paths():
    return (('ipv4', '/ip/firewall/connection/'), ('ipv6', '/ipv6/firewall/connection/'))


def _normalize_address(address, port = None):
    if not address:
        return ''

    if port:
        bracketed_suffix = f']:{port}'
        plain_suffix = f':{port}'

        if address.startswith('[') and address.endswith(bracketed_suffix):
            address = address[1:-len(bracketed_suffix)]
        elif address.endswith(plain_suffix):
            address = address[:-len(plain_suffix)]
    elif address.startswith('[') and address.endswith(']'):
        address = address[1:-1]

    return address


def _format_address(address, port = None):
    address = _normalize_address(address, port)
    if not address or not port:
        return address

    if ':' in address:
        return f'[{address}]:{port}'

    return f'{address}:{port}'


def _count_connection_records_by_family(router_entry):
    router_api = router_entry.api_connection.router_api()
    count_by_family = {'ipv4': 0, 'ipv6': 0}
    last_exc = None
    has_success = False

    for family, resource_path in _connection_resource_paths():
        try:
            res = router_api.get_resource(resource_path).call('print', {'count-only': ''})
            cnt_str = res.done_message.get('ret')
            try:
                count_by_family[family] = int(cnt_str)
            except (ValueError, TypeError):
                pass
            has_success = True
        except Exception as exc:
            last_exc = exc

    if not has_success:
        raise last_exc if last_exc else RuntimeError('Unable to read connection counters')

    return count_by_family


def _count_connection_records(router_entry):
    return sum(_count_connection_records_by_family(router_entry).values())


def _read_connection_records(router_entry, *, proplist):
    router_api = router_entry.api_connection.router_api()
    records = []
    last_exc = None
    has_success = False

    for _, resource_path in _connection_resource_paths():
        try:
            connection_records = router_api.get_resource(resource_path).call('print', {'proplist': proplist})
            records.extend(connection_records)
            has_success = True
        except Exception as exc:
            last_exc = exc

    if not has_success:
        raise last_exc if last_exc else RuntimeError('Unable to read connection records')

    return records


class IPConnectionDatasource:
    ''' IP connections data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, include_stack_counts = False):
        if metric_labels is None:
            metric_labels = []        
        try:
            count_by_family = _count_connection_records_by_family(router_entry)
            records = [{'count': str(sum(count_by_family.values()))}]
            if include_stack_counts:
                records[0]['ipv4_count'] = str(count_by_family['ipv4'])
                records[0]['ipv6_count'] = str(count_by_family['ipv6'])
            return BaseDSProcessor.trimmed_records(router_entry, router_records = records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting IP connection info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


class IPConnectionStatsDatasource:
    ''' IP connections stats data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, add_router_id = True):
        if metric_labels is None:
            metric_labels = []        
        try:
            # First, check if there are any connections
            count_records = IPConnectionDatasource.metric_records(router_entry)
            if count_records[0].get('count', 0) == '0':
                return []

            connection_records = _read_connection_records(router_entry,
                                                          proplist = 'src-address,src-port,dst-address,dst-port,protocol')
             # calculate number of connections per src-address
            connections_per_src_address = {}
            for connection_record in connection_records:
                address = _normalize_address(connection_record.get('src-address'), connection_record.get('src-port'))
                destination = f"{_format_address(connection_record.get('dst-address'), connection_record.get('dst-port'))}" \
                              f"({connection_record.get('protocol')})"

                count, destinations = 0, set()
                if connections_per_src_address.get(address):
                    count, destinations = connections_per_src_address[address]
                count += 1
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
ConnTrafficEntry = namedtuple('ConnTrafficEntry', ['upload_bytes', 'download_bytes'])


class IPConnectionTrafficDatasource:
    ''' IP connection traffic data provider
    '''
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, add_router_id = True):
        if metric_labels is None:
            metric_labels = []
        try:
            count_records = IPConnectionDatasource.metric_records(router_entry)
            if count_records[0].get('count', 0) == '0':
                return []

            connection_records = _read_connection_records(router_entry,
                                                          proplist = 'src-address,src-port,dst-address,dst-port,protocol,orig-bytes,repl-bytes')
            traffic_per_connection = {}
            for connection_record in connection_records:
                src_address = _normalize_address(connection_record.get('src-address'), connection_record.get('src-port'))
                dst_address = _normalize_address(connection_record.get('dst-address'), connection_record.get('dst-port'))
                protocol = connection_record.get('protocol', '')
                key = (src_address, dst_address, protocol)

                upload_bytes = int(connection_record.get('orig-bytes') or 0)
                download_bytes = int(connection_record.get('repl-bytes') or 0)

                entry = traffic_per_connection.get(key, ConnTrafficEntry(0, 0))
                traffic_per_connection[key] = ConnTrafficEntry(
                    entry.upload_bytes + upload_bytes,
                    entry.download_bytes + download_bytes,
                )

            records = []
            for (src_address, dst_address, protocol), entry in traffic_per_connection.items():
                record = {'src_address': src_address,
                          'dst_address': dst_address,
                          'protocol': protocol,
                          'upload_bytes': entry.upload_bytes,
                          'download_bytes': entry.download_bytes,
                          'total_bytes': entry.upload_bytes + entry.download_bytes}
                if add_router_id:
                    for router_key, router_value in router_entry.router_id.items():
                        record[router_key] = router_value
                records.append(record)
            return BaseDSProcessor.trimmed_records(router_entry, router_records = records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting IP connection traffic info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
