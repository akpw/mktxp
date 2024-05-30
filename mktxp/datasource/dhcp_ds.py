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
from mktxp.utils.utils import parse_mkt_uptime


class DHCPMetricsDataSource:
    ''' DHCP Metrics data provider
    '''
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, add_router_id = True, dhcp_cache = True, translate = True, bound = False):
        if metric_labels is None or dhcp_cache:
            metric_labels = ['host_name', 'comment', 'active_address', 'address', 'mac_address', 'server', 'expires_after', 'client_id', 'active_mac_address']

        if dhcp_cache and router_entry.dhcp_records:
            return router_entry.dhcp_records
        try:
            if bound:
                dhcp_lease_records = router_entry.dhcp_entry.api_connection.router_api().get_resource('/ip/dhcp-server/lease').get(status='bound')
            else:
                dhcp_lease_records = router_entry.dhcp_entry.api_connection.router_api().get_resource('/ip/dhcp-server/lease').call('print', {'active':''})

            # translation rules
            translation_table = {}
            if 'comment' in metric_labels:
                translation_table['comment'] = lambda c: c if c else ''
            if 'host_name' in metric_labels:
                translation_table['host_name'] = lambda c: c if c else ''
            if 'expires_after' in metric_labels and translate:
                translation_table['expires_after'] = lambda c: parse_mkt_uptime(c) if c else 0
            if 'active_address' in metric_labels:
                translation_table['active_address'] = lambda c: c if c else ''

            records = BaseDSProcessor.trimmed_records(router_entry, router_records = dhcp_lease_records, metric_labels = metric_labels, add_router_id = add_router_id, translation_table = translation_table)
            if dhcp_cache:
                router_entry.dhcp_records = records
            return records

        except Exception as exc:
            print(f'Error getting dhcp info from router {router_entry.dhcp_entry.router_name}@{router_entry.dhcp_entry.config_entry.hostname}: {exc}')
            return None
