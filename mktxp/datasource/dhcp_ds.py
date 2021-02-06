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


class DHCPMetricsDataSource:
    ''' DHCP Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = [], add_router_id = True):
        try:
            #dhcp_lease_records = router_entry.api_connection.router_api().get_resource('/ip/dhcp-server/lease').get(status='bound')
            dhcp_lease_records = router_entry.api_connection.router_api().get_resource('/ip/dhcp-server/lease').call('print', {'active':''})

            # translation rules
            translation_table = {}
            if 'comment' in metric_labels:
                translation_table['comment'] = lambda c: c if c else ''           
            if 'host_name' in metric_labels:
                translation_table['host_name'] = lambda c: c if c else ''           
            if 'expires_after' in metric_labels:
                translation_table['expires_after'] = lambda c: c if c else ''        
            if 'active_address' in metric_labels:
                translation_table['active_address'] = lambda c: c if c else ''        

            return BaseDSProcessor.trimmed_records(router_entry, router_records = dhcp_lease_records, metric_labels = metric_labels, add_router_id = add_router_id, translation_table = translation_table)
        except Exception as exc:
            print(f'Error getting dhcp info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


