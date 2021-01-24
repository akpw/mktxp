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

from mktxp.cli.output.base_out import BaseOutputProcessor
from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.collectors.base_collector import BaseCollector

class CapsmanCollector(BaseCollector):
    ''' CAPsMAN Metrics collector
    '''    
    @staticmethod
    def collect(router_metric):
        remote_caps_labels = ['identity', 'version', 'base_mac', 'board', 'base_mac']
        remote_caps_records = router_metric.capsman_remote_caps_records(remote_caps_labels)
        if remote_caps_records:
            remote_caps_metrics = BaseCollector.info_collector('capsman_remote_caps', 'CAPsMAN remote caps', remote_caps_records, remote_caps_labels)
            yield remote_caps_metrics

        registration_labels = ['interface', 'ssid', 'mac_address', 'tx_rate', 'rx_rate', 'rx_signal', 'uptime', 'bytes']
        registration_records = router_metric.capsman_registration_table_records(registration_labels)
        if registration_records:
            # calculate number of registrations per interface
            registration_per_interface = {}
            for registration_record in registration_records:
                registration_per_interface[registration_record['interface']] = registration_per_interface.get(registration_record['interface'], 0) + 1
            # compile registrations-per-interface records
            registration_per_interface_records = [{ MKTXPConfigKeys.ROUTERBOARD_NAME: router_metric.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                                            MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_metric.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                                            'interface': key, 'count': value} for key, value in registration_per_interface.items()]
            # yield registrations-per-interface metrics
            registration_per_interface_metrics = BaseCollector.gauge_collector('capsman_registrations_count', 'Number of active registration per CAPsMAN interface', registration_per_interface_records, 'count', ['interface'])
            yield registration_per_interface_metrics

            # the client info metrics
            if router_metric.router_entry.capsman_clients:
                # translate / trim / augment registration records
                dhcp_lease_labels = ['mac_address', 'address', 'host_name', 'comment']
                dhcp_lease_records = router_metric.dhcp_lease_records(dhcp_lease_labels)
                for registration_record in registration_records:
                    BaseOutputProcessor.augment_record(router_metric, registration_record, dhcp_lease_records)
                    
                tx_byte_metrics = BaseCollector.counter_collector('capsman_clients_tx_bytes', 'Number of sent packet bytes', registration_records, 'tx_bytes', ['dhcp_name'])
                yield tx_byte_metrics

                rx_byte_metrics = BaseCollector.counter_collector('capsman_clients_rx_bytes', 'Number of received packet bytes', registration_records, 'rx_bytes', ['dhcp_name'])
                yield rx_byte_metrics

                signal_strength_metrics = BaseCollector.gauge_collector('capsman_clients_signal_strength', 'Client devices signal strength', registration_records, 'rx_signal', ['dhcp_name'])
                yield signal_strength_metrics

                registration_metrics = BaseCollector.info_collector('capsman_clients_devices', 'Registered client devices info', 
                                        registration_records, ['dhcp_name', 'dhcp_address', 'rx_signal', 'ssid', 'tx_rate', 'rx_rate', 'interface', 'mac_address', 'uptime'])
                yield registration_metrics
    

