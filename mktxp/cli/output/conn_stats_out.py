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
from mktxp.datasource.connection_ds import IPConnectionStatsDatasource


class ConnectionsStatsOutput:
    ''' Connections Stats Output
    '''    
    @staticmethod
    def clients_summary(router_entry):
        connection_records = IPConnectionStatsDatasource.metric_records(router_entry, add_router_id = False)
        if not connection_records:
            print('No connection stats records')
            return 

        conn_cnt = 0
        output_records = []
        for registration_record in sorted(connection_records, key = lambda rt_record: rt_record['connection_count'], reverse=True):
            BaseOutputProcessor.resolve_dhcp(router_entry, registration_record, id_key = 'src_address', resolve_address = False)        
            output_records.append(registration_record)
            conn_cnt += registration_record['connection_count']

        output_records_cnt = 0
        output_entry = BaseOutputProcessor.OutputConnStatsEntry
        output_table = BaseOutputProcessor.output_table(output_entry)
        
        for record in output_records:
            output_table.add_row(output_entry(**record))
            output_table.add_row(output_entry())
            output_records_cnt += 1
                
        print (output_table.draw())

        print(f'Distinct source addresses: {output_records_cnt}')
        print(f'Total open connections: {conn_cnt}', '\n')

