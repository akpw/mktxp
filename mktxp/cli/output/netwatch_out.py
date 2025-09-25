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
from mktxp.datasource.netwatch_ds import NetwatchMetricsDataSource
from humanize import naturaldelta

class NetwatchOutput:
    ''' Netwatch CLI Output
    '''    
    
    @staticmethod
    def clients_summary(router_entry):
        ''' Display netwatch summary
        '''
        print(f'{router_entry.router_name}@{router_entry.config_entry.hostname}: OK to connect')
        print(f'Connecting to router {router_entry.router_name}@{router_entry.config_entry.hostname}')

        # Collect netwatch data
        netwatch_records = NetwatchOutput._collect_records(router_entry)
        
        if not netwatch_records:
            print('No netwatch entries found')
            return
            
        # Display table
        NetwatchOutput._display_table(netwatch_records)
            
    @staticmethod
    def _collect_records(router_entry):
        ''' Collect netwatch records
        '''
        metric_labels = ['name', 'host', 'type', 'status', 'since', 'timeout', 'interval', 'comment']
        translation_table = {
            'status': lambda value: 'Up' if value == 'up' else 'Down',
            'since': lambda value: value if value else '',
            'timeout': lambda value: value if value else '',
            'interval': lambda value: value if value else '',
            'comment': lambda value: value if value else ''
        }
        
        try:
            records = NetwatchMetricsDataSource.metric_records(
                router_entry,
                metric_labels=metric_labels,
                translation_table=translation_table
            )
            return records if records else []
        except Exception as exc:
            print(f'Error getting netwatch info: {exc}')
            return []
        
    @staticmethod
    def _display_table(records):
        ''' Display netwatch records in a table
        '''
        if not records:
            return
            
        # Sort records by name, then by host
        sorted_records = sorted(records, key=lambda x: (x.get('name', ''), x.get('host', '')))
        
        # Create output table
        output_entry = BaseOutputProcessor.OutputNetwatchEntry
        output_table = BaseOutputProcessor.output_table(output_entry)
        
        # Add records to table
        for record in sorted_records:
            # Filter record to only include fields we need for output in the new order
            filtered_record = {
                'name': record.get('name', ''),
                'host': record.get('host', ''),
                'comment': record.get('comment', ''),
                'status': record.get('status', ''),
                'type': record.get('type', ''),
                'since': record.get('since', ''),
                'timeout': record.get('timeout', ''),
                'interval': record.get('interval', '')
            }
            output_table.add_row(output_entry(**filtered_record))
        
        # Print table with title
        print("Netwatch Entries:")
        print(output_table.draw())
        
        # Print summary
        total_entries = len(sorted_records)
        up_count = len([r for r in sorted_records if r.get('status', '').lower() == 'up'])
        down_count = total_entries - up_count
        
        print(f"Total entries: {total_entries}")
        print(f"Up: {up_count}")
        print(f"Down: {down_count}")