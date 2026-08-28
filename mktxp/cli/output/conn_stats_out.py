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


from mktxp.cli.output.tables import output_table, OutputConnStatsEntry
from mktxp.utils.filtering import match_record
from mktxp.flow.processor.enrichment import resolve_dhcp
from mktxp.datasource.connection_ds import IPConnectionStatsDatasource


class ConnectionsStatsOutput:
    ''' Connections Stats Output
    '''    
    @staticmethod
    def clients_summary(router_entry, include=None, exclude=None):
        connection_records = IPConnectionStatsDatasource.metric_records(router_entry, add_router_id = False)
        if not connection_records:
            print('No connection stats records')
            return 

        conn_cnt = 0
        total_unfiltered_cnt = 0
        total_unfiltered_conns = 0
        output_records = []
        for registration_record in sorted(connection_records, key = lambda rt_record: rt_record['connection_count'], reverse=True):
            resolve_dhcp(router_entry, registration_record, id_key = 'src_address', resolve_address = False)        
            total_unfiltered_cnt += 1
            total_unfiltered_conns += registration_record.get('connection_count', 0)
            if not match_record(registration_record, include, exclude):
                continue
            output_records.append(registration_record)
            conn_cnt += registration_record.get('connection_count', 0)

        output_records_cnt = 0
        output_entry = OutputConnStatsEntry
        tbl = output_table(output_entry)
        
        for record in output_records:
            tbl.add_row(output_entry(**record))
            tbl.add_row(output_entry())
            output_records_cnt += 1
                
        if output_records_cnt > 0:
            print (tbl.draw())
            if include or exclude:
                print(f'Matching source addresses: {output_records_cnt} (Total: {total_unfiltered_cnt})')
                print(f'Matching open connections: {conn_cnt} (Total: {total_unfiltered_conns})', '\n')
            else:
                print(f'Distinct source addresses: {output_records_cnt}')
                print(f'Total open connections: {conn_cnt}', '\n')
        else:
            print('No matching connection records found', '\n')

