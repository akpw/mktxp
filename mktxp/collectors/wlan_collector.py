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

import re
from mktxp.collectors.base_collector import BaseCollector
from mktxp.router_metric import RouterMetric


class WLANCollector(BaseCollector):
    ''' Wireless Metrics collector
    '''    
    @staticmethod
    def collect(router_metric):
        monitor_labels = ['channel', 'noise_floor', 'overall_tx_ccq', 'registered_clients']
        monitor_records = router_metric.interface_monitor_records(monitor_labels, 'wireless')
        if not monitor_records:
            return range(0)

        # sanitize records for relevant labels
        noise_floor_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('noise_floor')]
        tx_ccq_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('overall_tx_ccq')]
        registered_clients_records  = [monitor_record for monitor_record in monitor_records if monitor_record.get('registered_clients')]

        if noise_floor_records:
            noise_floor_metrics = BaseCollector.gauge_collector('wlan_noise_floor', 'Noise floor threshold', noise_floor_records, 'noise_floor', ['channel'])
            yield noise_floor_metrics

        if tx_ccq_records:
            overall_tx_ccq_metrics = BaseCollector.gauge_collector('wlan_overall_tx_ccq', 'Client Connection Quality for transmitting', tx_ccq_records, 'overall_tx_ccq', ['channel'])
            yield overall_tx_ccq_metrics

        if registered_clients_records:
            registered_clients_metrics = BaseCollector.gauge_collector('wlan_registered_clients', 'Number of registered clients', registered_clients_records, 'registered_clients', ['channel'])
            yield registered_clients_metrics


        # the client info metrics
        if router_metric.router_entry.wireless_clients:
            registration_labels = ['interface', 'ssid', 'mac_address', 'tx_rate', 'rx_rate', 'uptime', 'bytes', 'signal_to_noise', 'tx_ccq', 'signal_strength']
            registration_records = router_metric.wireless_registration_table_records(registration_labels)
            if not registration_records:
                return range(0)

            dhcp_lease_labels = ['mac_address', 'host_name', 'comment']
            dhcp_lease_records = router_metric.dhcp_lease_records(dhcp_lease_labels)
  
            for registration_record in registration_records:
                try:
                    dhcp_lease_record = next((dhcp_lease_record for dhcp_lease_record in dhcp_lease_records if dhcp_lease_record['mac_address']==registration_record['mac_address']))
                    registration_record['name'] = dhcp_lease_record.get('comment', dhcp_lease_record.get('host_name', dhcp_lease_record.get('mac_address')))
                except StopIteration:
                    registration_record['name'] = registration_record['mac_address']            

                # split out tx/rx bytes
                registration_record['tx_bytes'] = registration_record['bytes'].split(',')[0]
                registration_record['rx_bytes'] = registration_record['bytes'].split(',')[1]

                # average signal strength
                registration_record['signal_strength'] = re.search(r'-\d+', registration_record['signal_strength']).group()

                del registration_record['bytes']

            tx_byte_metrics = BaseCollector.counter_collector('wlan_clients_tx_bytes', 'Number of sent packet bytes', registration_records, 'tx_bytes', ['name'])
            yield tx_byte_metrics

            rx_byte_metrics = BaseCollector.counter_collector('wlan_clients_rx_bytes', 'Number of received packet bytes', registration_records, 'rx_bytes', ['name'])
            yield rx_byte_metrics

            signal_strength_metrics = BaseCollector.gauge_collector('wlan_clients_signal_strength', 'Average strength of the client signal recevied by AP', registration_records, 'signal_strength', ['name'])
            yield signal_strength_metrics

            signal_to_noise_metrics = BaseCollector.gauge_collector('wlan_clients_signal_to_noise', 'Client devices signal to noise ratio', registration_records, 'signal_to_noise', ['name'])
            yield signal_to_noise_metrics

            tx_ccq_metrics = BaseCollector.gauge_collector('wlan_clients_tx_ccq', 'Client Connection Quality (CCQ) for transmit', registration_records, 'tx_ccq', ['name'])
            yield tx_ccq_metrics

            registration_metrics = BaseCollector.info_collector('wlan_clients_devices', 'Client devices info', 
                                    registration_records, ['name', 'rx_signal', 'ssid', 'tx_rate', 'rx_rate', 'interface', 'mac_address', 'uptime'])
            yield registration_metrics


            return range(0)



