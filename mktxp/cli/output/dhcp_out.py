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
    def clients_summary(router_entry, include=None, exclude=None):
        dhcp_lease_labels = ['host_name', 'comment', 'active_address', 'address', 'mac_address', 'server', 'expires_after']
        dhcp_lease_records = DHCPMetricsDataSource.metric_records(router_entry, metric_labels = dhcp_lease_labels, add_router_id = False, translate = False, dhcp_cache = False)
        if not dhcp_lease_records:
            print('No DHCP registration records')
            return 

        dhcp_by_server = {}
        total_unfiltered = len(dhcp_lease_records)
        filtered_records = []
        for dhcp_lease_record in sorted(dhcp_lease_records, key = lambda dhcp_record: dhcp_record['address'], reverse=True):
            dhcp_lease_record['host_name'] = BaseOutputProcessor.dhcp_name(router_entry, dhcp_lease_record, drop_comment = True)
            if not BaseOutputProcessor.match_record(dhcp_lease_record, include, exclude):
                continue
            filtered_records.append(dhcp_lease_record)

            server = dhcp_lease_record.get('server', 'all')
            if server == 'all':
                dhcp_lease_record['server'] = server
            if server in dhcp_by_server.keys():
                dhcp_by_server[server].append(dhcp_lease_record)
            else:
                dhcp_by_server[server] = [dhcp_lease_record]         

        output_records = 0
        total_displayed = len(filtered_records)        
        output_entry = BaseOutputProcessor.OutputDHCPEntry
        output_table = BaseOutputProcessor.output_table(output_entry)
                
        for key in dhcp_by_server.keys():
            for record in dhcp_by_server[key]:
                output_table.add_row(output_entry(**record))
                output_records += 1
            if output_records < total_displayed:
                output_table.add_row(output_entry())

        if total_displayed > 0:
            print (output_table.draw())
            for server in dhcp_by_server.keys():
                print(f'{server} clients: {len(dhcp_by_server[server])}')
            if include or exclude:
                print(f'Matching DHCP clients: {output_records} (Total: {total_unfiltered})', '\n')
            else:
                print(f'Total DHCP clients: {output_records}', '\n')
        else:
            print('No matching DHCP clients found', '\n')
