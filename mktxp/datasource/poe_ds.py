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
from mktxp.datasource.interface_ds import InterfaceTrafficMetricsDataSource

class POEMetricsDataSource:
    ''' POE Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None):
        if metric_labels is None:
            metric_labels = []                
        try:
            poe_records = router_entry.api_connection.router_api().get_resource('/interface/ethernet/poe').get()
            
            for poe_record in poe_records:
                poe_monitor_records = router_entry.api_connection.router_api().get_resource('/interface/ethernet/poe').call('monitor', {'once':'', '.id':poe_record['id']})
                
                poe_monitor_records = BaseDSProcessor.trimmed_records(router_entry, router_records = poe_monitor_records)

                if poe_monitor_records[0].get('poe_out_status'):
                    poe_record['poe_out_status'] = poe_monitor_records[0]['poe_out_status']

                if poe_monitor_records[0].get('poe_out_voltage'):
                    poe_record['poe_out_voltage'] = poe_monitor_records[0]['poe_out_voltage']

                if poe_monitor_records[0].get('poe_out_current'):
                    poe_record['poe_out_current'] = poe_monitor_records[0]['poe_out_current']

                if poe_monitor_records[0].get('poe_out_power'):
                    poe_record['poe_out_power'] = poe_monitor_records[0]['poe_out_power']

            return BaseDSProcessor.trimmed_records(router_entry, router_records = poe_records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting PoE info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None