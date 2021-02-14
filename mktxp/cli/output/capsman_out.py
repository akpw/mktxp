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


from mktxp.flow.processor.output import BaseOutputProcessor
from mktxp.datasource.dhcp_ds import DHCPMetricsDataSource
from mktxp.datasource.capsman_ds import CapsmanRegistrationsMetricsDataSource


class CapsmanOutput:
    ''' CAPsMAN CLI Output
    '''    
    @staticmethod
    def clients_summary(router_entry):
        registration_labels = ['interface', 'ssid', 'mac_address', 'rx_signal', 'uptime', 'tx_rate', 'rx_rate']
        registration_records = CapsmanRegistrationsMetricsDataSource.metric_records(router_entry, metric_labels = registration_labels, add_router_id = False)
        if not registration_records:
            print('No CAPsMAN registration records')
            return 

        # translate / trim / augment registration records
        dhcp_lease_labels = ['host_name', 'comment', 'address', 'mac_address']
        dhcp_lease_records = DHCPMetricsDataSource.metric_records(router_entry, metric_labels = dhcp_lease_labels, add_router_id = False)   

        dhcp_rt_by_interface = {}
        for registration_record in sorted(registration_records, key = lambda rt_record: rt_record['rx_signal'], reverse=True):
            BaseOutputProcessor.augment_record(router_entry, registration_record, dhcp_lease_records)

            interface = registration_record['interface']
            if interface in dhcp_rt_by_interface.keys():
                dhcp_rt_by_interface[interface].append(registration_record)
            else:
                dhcp_rt_by_interface[interface] = [registration_record]         

        output_records = 0
        registration_records = len(registration_records)                
        output_entry = BaseOutputProcessor.OutputCapsmanEntry
        output_table = BaseOutputProcessor.output_table(output_entry)
                
        for key in dhcp_rt_by_interface.keys():
            for record in dhcp_rt_by_interface[key]:
                output_table.add_row(output_entry(**record))
                output_records += 1
            if output_records < registration_records:
                output_table.add_row(output_entry())

        print (output_table.draw())

        for server in dhcp_rt_by_interface.keys():
            print(f'{server} clients: {len(dhcp_rt_by_interface[server])}')
        print(f'Total connected CAPsMAN clients: {output_records}', '\n')


