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


class DHCPOutput:
    ''' DHCP Clients CLI Output
    '''    
    @staticmethod
    def clients_summary(router_entry):
        dhcp_lease_labels = ['host_name', 'comment', 'active_address', 'address', 'mac_address', 'server', 'expires_after']
        dhcp_lease_records = DHCPMetricsDataSource.metric_records(router_entry, metric_labels = dhcp_lease_labels, add_router_id = False)
        if not dhcp_lease_records:
            print('No DHCP registration records')
            return 

        dhcp_by_server = {}
        for dhcp_lease_record in sorted(dhcp_lease_records, key = lambda dhcp_record: dhcp_record['active_address'], reverse=True):
            server = dhcp_lease_record['server']
            if server in dhcp_by_server.keys():
                dhcp_by_server[server].append(dhcp_lease_record)
            else:
                dhcp_by_server[server] = [dhcp_lease_record]         
        
        output_records = 0
        lease_records = len(dhcp_lease_records)        
        output_entry = BaseOutputProcessor.OutputDHCPEntry
        output_table = BaseOutputProcessor.output_table(output_entry)
                
        for key in dhcp_by_server.keys():
            for record in dhcp_by_server[key]:
                record['host_name'] = BaseOutputProcessor.dhcp_name(router_entry, record, drop_comment = True)
                output_table.add_row(output_entry(**record))
                output_records += 1
            if output_records < lease_records:
                output_table.add_row(output_entry())

        print (output_table.draw())

        for server in dhcp_by_server.keys():
            print(f'{server} clients: {len(dhcp_by_server[server])}')
        print(f'Total DHCP clients: {output_records}', '\n')
