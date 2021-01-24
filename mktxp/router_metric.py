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


from mktxp.cli.config.config import config_handler, MKTXPConfigKeys
from mktxp.router_connection import RouterAPIConnection

class RouterMetric:
    ''' RouterOS Metrics data provider
    '''             
    def __init__(self, router_name):
        self.router_name = router_name
        self.router_entry  = config_handler.entry(router_name)
        self.api_connection = RouterAPIConnection(router_name, self.router_entry)
        self.router_id = {
            MKTXPConfigKeys.ROUTERBOARD_NAME: self.router_name,
            MKTXPConfigKeys.ROUTERBOARD_ADDRESS: self.router_entry.hostname
            }
        self.time_spent =  { 'IdentityCollector': 0,
                            'SystemResourceCollector': 0,
                            'HealthCollector': 0,
                            'DHCPCollector': 0,
                            'PoolCollector': 0,
                            'InterfaceCollector': 0,
                            'FirewallCollector': 0,
                            'MonitorCollector': 0,
                            'RouteCollector': 0,
                            'WLANCollector': 0,
                            'CapsmanCollector': 0
                            }            

    def identity_records(self, identity_labels = []):
        try:
            identity_records = self.api_connection.router_api().get_resource('/system/identity').get()
            return self._trimmed_records(identity_records, identity_labels)
        except Exception as exc:
            print(f'Error getting system identity info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def routerboard_records(self, routerboard_labels = []):
        try:
            routerboard_records = self.api_connection.router_api().get_resource('/system/routerboard').get()
            return self._trimmed_records(routerboard_records, routerboard_labels)
        except Exception as exc:
            print(f'Error getting system routerboard info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def health_records(self, health_labels = []):
        try:
            health_records = self.api_connection.router_api().get_resource('/system/health').get()
            return self._trimmed_records(health_records, health_labels)
        except Exception as exc:
            print(f'Error getting system health info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def system_resource_records(self, resource_labels = []):
        try:
            system_resource_records = self.api_connection.router_api().get_resource('/system/resource').get()
            return self._trimmed_records(system_resource_records, resource_labels)
        except Exception as exc:
            print(f'Error getting system resource info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def dhcp_lease_records(self, dhcp_lease_labels = [], add_router_id = True):
        try:
            #dhcp_lease_records = self.api_connection.router_api().get_resource('/ip/dhcp-server/lease').get(status='bound')
            dhcp_lease_records = self.api_connection.router_api().get_resource('/ip/dhcp-server/lease').call('print', {'active':''})
            return self._trimmed_records(dhcp_lease_records, dhcp_lease_labels, add_router_id)
        except Exception as exc:
            print(f'Error getting dhcp info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def interface_traffic_records(self, interface_traffic_labels = []):
        try:
            traffic_records = self.api_connection.router_api().get_resource('/interface').get(running='yes', disabled='no')
            return self._trimmed_records(traffic_records, interface_traffic_labels)
        except Exception as exc:
            print(f'Error getting interface traffic info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def interface_monitor_records(self, interface_monitor_labels = [], kind = 'ethernet', include_comments = False):
        try:
            interfaces = self.api_connection.router_api().get_resource(f'/interface/{kind}').get()
            interface_names = [(interface['name'], interface.get('comment'), interface.get('running')) for interface in interfaces]

            interface_monitor = lambda int_num : self.api_connection.router_api().get_resource(f'/interface/{kind}').call('monitor', {'once':'', 'numbers':f'{int_num}'})
            interface_monitor_records = [interface_monitor(int_num)[0] for int_num in range(len(interface_names))]

            if include_comments:
                # combine interfaces names with comments
                for interface_monitor_record in interface_monitor_records:
                    for interface_name in interface_names:
                        if interface_name[1] and interface_name[0] == interface_monitor_record['name']:
                            interface_monitor_record['name'] = interface_name[1] if self.router_entry.use_comments_over_names else \
                                                                                 f"{interface_name[0]} ({interface_name[1]})"
            return self._trimmed_records(interface_monitor_records, interface_monitor_labels)
        except Exception as exc:
            print(f'Error getting {kind} interface monitor info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def pool_records(self, pool_labels = []):
        try:
            pool_records = self.api_connection.router_api().get_resource('/ip/pool').get()
            return self._trimmed_records(pool_records, pool_labels)
        except Exception as exc:
            print(f'Error getting pool info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def pool_used_records(self, pool_used_labels = []):
        try:
            pool_used_records = self.api_connection.router_api().get_resource('/ip/pool/used').get()
            return self._trimmed_records(pool_used_records, pool_used_labels)
        except Exception as exc:
            print(f'Error getting pool used info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def route_records(self, route_labels = []):
        try:
            route_records = self.api_connection.router_api().get_resource('/ip/route').get(active='yes')
            return self._trimmed_records(route_records, route_labels)
        except Exception as exc:
            print(f'Error getting routes info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None
            
    def wireless_registration_table_records(self, registration_table_labels = [], add_router_id = True):
        try:
            registration_table_records = self.api_connection.router_api().get_resource('/interface/wireless/registration-table').get()
            return self._trimmed_records(registration_table_records, registration_table_labels, add_router_id)
        except Exception as exc:
            print(f'Error getting wireless registration table info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def capsman_remote_caps_records(self, remote_caps_labels = []):
        try:
            remote_caps_records = self.api_connection.router_api().get_resource('/caps-man/remote-cap').get()
            return self._trimmed_records(remote_caps_records, remote_caps_labels)
        except Exception as exc:
            print(f'Error getting caps-man remote caps info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def capsman_registration_table_records(self, registration_table_labels = [], add_router_id = True):
        try:
            registration_table_records = self.api_connection.router_api().get_resource('/caps-man/registration-table').get()
            return self._trimmed_records(registration_table_records, registration_table_labels, add_router_id)
        except Exception as exc:
            print(f'Error getting caps-man registration table info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def firewall_records(self, firewall_labels = [], raw = False, matching_only = True):
        try:
            filter_path = '/ip/firewall/filter' if not raw else '/ip/firewall/raw'
            firewall_records = self.api_connection.router_api().get_resource(filter_path).call('print', {'stats':'', 'all':''})
            if matching_only:
                firewall_records = [record for record in firewall_records if int(record.get('bytes', '0')) > 0]
            # translation rules
            translation_table = {}
#            if 'id' in firewall_labels:
#                translation_table['id'] = lambda id: str(int(id[1:], 16) - 1)
            if 'comment' in firewall_labels:
                translation_table['comment'] = lambda c: c if c else ''
            return self._trimmed_records(firewall_records, firewall_labels, translation_table = translation_table)
        except Exception as exc:
            print(f'Error getting firewall filters info from router{self.router_name}@{self.router_entry.hostname}: {exc}')
            return None

    def mktxp_records(self):
        mktxp_records = []
        for key in self.time_spent.keys():
            mktxp_records.append({'name': key, 'duration': self.time_spent[key]})
        # translation rules            
        translation_table = {'duration': lambda d: d*1000}
        return self._trimmed_records(mktxp_records, translation_table = translation_table)

    # Helpers
    def _trimmed_records(self, router_records, metric_labels = [], add_router_id = True, translation_table = {}):
        if len(metric_labels) == 0 and len(router_records) > 0:
            metric_labels = router_records[0].keys()
        metric_labels = set(metric_labels)      

        labeled_records = []
        dash2_ = lambda x : x.replace('-', '_')
        for router_record in router_records:
            translated_record = {dash2_(key): value for (key, value) in router_record.items() if dash2_(key) in metric_labels}
            if add_router_id:
                for key, value in self.router_id.items():
                    translated_record[key] = value
            # translate fields if needed
            for key, func in translation_table.items():
                translated_record[key] = func(translated_record.get(key))
            labeled_records.append(translated_record)
        return labeled_records
