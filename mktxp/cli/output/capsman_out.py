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

from tabulate import tabulate   
from mktxp.cli.output.base_out import BaseOutputProcessor

class CapsmanOutput:
    ''' CAPsMAN CLI Output
    '''    
    @staticmethod
    def clients_summary(router_metric):
        registration_labels = ['interface', 'ssid', 'mac_address', 'rx_signal', 'uptime', 'tx_rate', 'rx_rate']
        registration_records = router_metric.capsman_registration_table_records(registration_labels, False)
        if not registration_records:
            print('No CAPsMAN registration records')
            return 

        # translate / trim / augment registration records
        dhcp_lease_labels = ['host_name', 'comment', 'address', 'mac_address']
        dhcp_lease_records = router_metric.dhcp_lease_records(dhcp_lease_labels, False)

        dhcp_rt_by_interface = {}
        for registration_record in sorted(registration_records, key = lambda rt_record: rt_record['rx_signal'], reverse=True):
            BaseOutputProcessor.augment_record(router_metric, registration_record, dhcp_lease_records)

            interface = registration_record['interface']
            if interface in dhcp_rt_by_interface.keys():
                dhcp_rt_by_interface[interface].append(registration_record)
            else:
                dhcp_rt_by_interface[interface] = [registration_record]         

        num_records = 0
        output_table = []
        for key in dhcp_rt_by_interface.keys():
            for record in dhcp_rt_by_interface[key]:
                output_table.append(BaseOutputProcessor.OutputCapsmanEntry(**record))
                num_records += 1
            output_table.append({})
        print()
        print(tabulate(output_table, headers = "keys",  tablefmt="github"))
        print(tabulate([{0:'Connected Wifi Devices:', 1:num_records}], tablefmt="text"))

