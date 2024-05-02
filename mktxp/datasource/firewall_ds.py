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
from mktxp.flow.router_entry import RouterEntry

TRANSLATION_TABLE = {
    'comment': lambda value: value if value else '',
    'log': lambda value: '1' if value == 'true' else '0'
}

class FirewallMetricsDataSource:
    ''' Firewall Metrics data provider, supports both IPv4 and IPv6
    '''
    @staticmethod
    def metric_records(router_entry, *, metric_labels=None, matching_only=True, filter_path='filter', ipv6 = False):
        if metric_labels is None:
            metric_labels = []
        try:
            ip_stack = 'ipv6' if ipv6 else 'ip'
            filter_paths = {
                'filter': f'/{ip_stack}/firewall/filter',
                'raw': f'/{ip_stack}/firewall/raw',
                'nat': f'/{ip_stack}/firewall/nat',
                'mangle': f'/{ip_stack}/firewall/mangle'
            }
            filter_path = filter_paths[filter_path]
            firewall_records = FirewallMetricsDataSource._get_records(
                router_entry,
                filter_path,
                {'stats': ''} if ipv6 else {'stats': '', 'all': ''},
                matching_only=matching_only
            )

            return BaseDSProcessor.trimmed_records(router_entry, router_records=firewall_records, metric_labels=metric_labels, translation_table=TRANSLATION_TABLE)
        except Exception as exc:
            print(
                f'Error getting {"IPv6" if ipv6 else "IPv4"} firewall filters info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}'
            )
            return None

    # helpers
    @staticmethod
    def _get_records(router_entry: RouterEntry, filter_path: str, args: dict, matching_only: bool = False):
        """
        Get firewall records from a Mikrotik ROS device.
        :param router_entry: The ROS API entry used to connect to the API
        :param filter_path:  The path to query the records for (e.g. /ip/firewall/filter)
        :param args:         A dictionary of arguments to pass to the print function used for export.
                             Looks like: '{'stats': '', 'all': ''}'
        """
        firewall_records = router_entry.api_connection.router_api().get_resource(filter_path).call('print', args)
        if matching_only:
            firewall_records = [record for record in firewall_records if int(record.get('bytes', '0')) > 0]
        return firewall_records
