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
from mktxp.datasource.address_list_ds import AddressListMetricsDataSource
from humanize import naturaldelta

class AddressListOutput:
    ''' Address List CLI Output
    '''
    
    @staticmethod
    def clients_summary(router_entry, address_lists_str):
        ''' Display address list summary for the specified lists
        '''
        if not address_lists_str:
            print('No address lists specified')
            return
        
        # Parse the address lists string
        requested_lists = [name.strip() for name in address_lists_str.split(',') if name.strip()]
        if not requested_lists:
            print('No valid address list names provided')
            return
            
        print(f'{router_entry.router_name}@{router_entry.config_entry.hostname}: OK to connect')
        print(f'Connecting to router {router_entry.router_name}@{router_entry.config_entry.hostname}')

        # Collect data for both IPv4 and IPv6
        ipv4_records = AddressListOutput._collect_records(router_entry, requested_lists, 'ip')
        ipv6_records = AddressListOutput._collect_records(router_entry, requested_lists, 'ipv6')
        
        # Check which lists were found
        found_ipv4_lists = set()
        found_ipv6_lists = set()
        
        if ipv4_records:
            found_ipv4_lists = {record.get('list', '') for record in ipv4_records}
            
        if ipv6_records:
            found_ipv6_lists = {record.get('list', '') for record in ipv6_records}
            
        # Report missing lists
        missing_lists = set(requested_lists) - (found_ipv4_lists | found_ipv6_lists)
        if missing_lists:
            print(f"Warning: The following address lists were not found: {', '.join(missing_lists)}")
            
        # Display tables
        tables_displayed = 0
        
        if ipv4_records:
            AddressListOutput._display_table(ipv4_records, 'IPv4')
            tables_displayed += 1
            
        if ipv6_records:
            if tables_displayed > 0:
                print()  # Add spacing between tables
            AddressListOutput._display_table(ipv6_records, 'IPv6')
            tables_displayed += 1
            
        if tables_displayed == 0:
            print('No address list entries found for the specified lists')
            
    @staticmethod
    def _collect_records(router_entry, requested_lists, ip_version):
        ''' Collect address list records for a specific IP version
        '''
        metric_labels = ['list', 'address', 'dynamic', 'timeout', 'disabled', 'comment']
        translation_table = {
            'dynamic': lambda value: 'Yes' if value == 'true' else 'No',
            'disabled': lambda value: 'Yes' if value == 'true' else 'No',
            'timeout': lambda value: AddressListOutput._format_timeout(value),
            'comment': lambda value: value if value else ''
        }
        
        try:
            records = AddressListMetricsDataSource.metric_records(
                router_entry,
                requested_lists, 
                ip_version,
                metric_labels=metric_labels,
                translation_table=translation_table
            )
            return records if records else []
        except Exception as exc:
            print(f'Error getting {ip_version.upper()} address list info: {exc}')
            return []
            
    @staticmethod
    def _format_timeout(timeout_value):
        ''' Format timeout value to match Mikrotik UI format (e.g., 9d 22:50:18)
        '''
        if not timeout_value or timeout_value == '0':
            return ''
        
        # Convert RouterOS format like '1d16h45m4s' to Mikrotik UI format like '1d 16:45:04'
        if isinstance(timeout_value, str):
            import re
            # More strict check - must have digit followed by time unit
            if re.search(r'\d+[wdhms]', timeout_value.strip()):
                return AddressListOutput._convert_ros_to_ui_format(timeout_value.strip())
        
        return str(timeout_value)
    
    @staticmethod
    def _convert_ros_to_ui_format(ros_timeout):
        ''' Convert RouterOS timeout format to Mikrotik UI format        
        Examples:
        1d16h45m4s -> 1d 16:45:04
        9h7m24s -> 9:07:24
        1w4d12h55m42s -> 1w4d 12:55:42
        '''
        import re
        
        # Parse the RouterOS format using regex
        pattern = r'(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        match = re.match(pattern, ros_timeout)
        
        if not match:
            return ros_timeout  # Return as-is if we can't parse it
        
        weeks, days, hours, minutes, seconds = match.groups()
        weeks = int(weeks) if weeks else 0
        days = int(days) if days else 0
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0
        
        # Build the UI format
        parts = []
        
        # Add weeks and days if present
        if weeks > 0:
            if days > 0:
                parts.append(f'{weeks}w{days}d')
            else:
                parts.append(f'{weeks}w')
        elif days > 0:
            parts.append(f'{days}d')
        
        # Add time part in HH:MM:SS format
        time_part = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        
        # If we have days/weeks, add a space before time
        if parts:
            return f'{parts[0]} {time_part}'
        else:
            # No days/weeks, just return time
            return time_part
        
    @staticmethod
    def _display_table(records, ip_version):
        ''' Display address list records in a table
        '''
        if not records:
            return
            
        # Sort records by list name, then by address
        sorted_records = sorted(records, key=lambda x: (x.get('list', ''), x.get('address', '')))
        
        # Create output table
        output_entry = BaseOutputProcessor.OutputAddressListEntry
        output_table = BaseOutputProcessor.output_table(output_entry)
        
        # Add records to table
        for record in sorted_records:
            # Filter record to only include fields we need for output in the new order
            filtered_record = {
                'list': record.get('list', ''),
                'address': record.get('address', ''),
                'comment': record.get('comment', ''),
                'timeout': record.get('timeout', ''),
                'dynamic': record.get('dynamic', ''),
                'disabled': record.get('disabled', '')
            }
            output_table.add_row(output_entry(**filtered_record))
        
        # Print table with title
        print(f"Address Lists ({ip_version}):")
        print(output_table.draw())
        
        # Print summary
        total_entries = len(sorted_records)
        unique_lists = len(set(record.get('list', '') for record in sorted_records))
        print(f"Total entries: {total_entries}")
        print(f"Unique lists: {unique_lists}")