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


from mktxp.cli.output.tables import output_table, OutputNetwatchEntry
from mktxp.utils.filtering import match_record
from mktxp.datasource.netwatch_ds import NetwatchMetricsDataSource
from humanize import naturaldelta

class NetwatchOutput:
    ''' Netwatch CLI Output
    '''    
    
    @staticmethod
    def clients_summary(router_entry, include=None, exclude=None, down_only=False, up_only=False):
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
        NetwatchOutput._display_table(
            netwatch_records,
            include=include,
            exclude=exclude,
            down_only=down_only,
            up_only=up_only,
        )
            
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
    def _display_table(records, include=None, exclude=None, down_only=False, up_only=False):
        ''' Display netwatch records in a table
        '''
        if not records:
            return

        total_unfiltered = len(records)
        filtered_records = []
        for record in records:
            is_up = record.get('status', '').lower() == 'up'
            if down_only and is_up:
                continue
            if up_only and not is_up:
                continue

            if not match_record(record, include, exclude):
                continue
            filtered_records.append(record)

        if not filtered_records:
            print("Netwatch Entries: No matching entries found")
            return
            
        # Sort records by name, then by host
        sorted_records = sorted(filtered_records, key=lambda x: (x.get('name', ''), x.get('host', '')))
        
        # Create output table
        output_entry = OutputNetwatchEntry
        tbl = output_table(output_entry)
        
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
            tbl.add_row(output_entry(**filtered_record))
        
        # Print table with title
        print("Netwatch Entries:")
        print(tbl.draw())
        
        # Print summary
        total_entries = len(sorted_records)
        up_count = len([r for r in sorted_records if r.get('status', '').lower() == 'up'])
        down_count = total_entries - up_count
        
        has_filters = bool(include) or bool(exclude) or down_only or up_only
        if has_filters:
            print(f"Matching entries: {total_entries} (Total: {total_unfiltered})")
        else:
            print(f"Total entries: {total_entries}")
        print(f"Up: {up_count}")
        print(f"Down: {down_count}")