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
from mktxp.datasource.kid_control_device_ds import KidDeviceMetricsDataSource

class KidControlOutput:
    ''' Kid Control CLI Output
    '''    
    @staticmethod
    def clients_summary(router_entry):
        device_labels = ['name', 'user', 'mac_address', 'ip_address', 'bytes_down', 'bytes_up', 'rate_up', 'rate_down', 'idle_time']
        device_records = KidDeviceMetricsDataSource.metric_records(router_entry, metric_labels = device_labels, cli_output=True)
        if not device_records:
            print('No Kid Control device records')
            return 

        # translate / trim / augment device records
        devices_with_users = []
        dynamic_devices = []
        
        for device_record in device_records:
            BaseOutputProcessor.augment_record(router_entry, device_record)

            # Store original numeric rates for sorting before parsing for display
            rate_up_numeric = BaseOutputProcessor.parse_numeric_rate(device_record.get('rate_up', '0'))
            rate_down_numeric = BaseOutputProcessor.parse_numeric_rate(device_record.get('rate_down', '0'))
            
            # Parse rates for display
            if device_record.get('rate_up'):
                device_record['rate_up'] = BaseOutputProcessor.parse_bitrates(device_record['rate_up'])
            if device_record.get('rate_down'):
                device_record['rate_down'] = BaseOutputProcessor.parse_bitrates(device_record['rate_down'])

            # Parse idle time for display
            if device_record.get('idle_time'):
                from humanize import naturaldelta
                idle_seconds = BaseOutputProcessor.parse_timedelta_seconds(device_record['idle_time'])
                device_record['idle_time'] = naturaldelta(idle_seconds, minimum_unit='seconds')
                
            # Filter to only the fields we need for output
            filtered_record = {
                'dhcp_name': device_record.get('dhcp_name', ''),
                'name': device_record.get('name', ''),
                'user': device_record.get('user', ''),
                'dhcp_address': device_record.get('dhcp_address', ''),
                'mac_address': device_record.get('mac_address', ''),
                'ip_address': device_record.get('ip_address', ''),
                'rate_up': device_record.get('rate_up', ''),
                'rate_down': device_record.get('rate_down', ''),
                'idle_time': device_record.get('idle_time', ''),
                # Store numeric rates for sorting
                '_rate_up_numeric': rate_up_numeric,
                '_rate_down_numeric': rate_down_numeric,
                '_total_rate_numeric': rate_up_numeric + rate_down_numeric
            }

            # Separate devices with users from dynamic devices
            if filtered_record.get('user'):
                devices_with_users.append(filtered_record)
            else:
                dynamic_devices.append(filtered_record)
        
        # Sort devices by total rate (rate_up + rate_down), highest first
        devices_with_users.sort(key=lambda x: x['_total_rate_numeric'], reverse=True)
        dynamic_devices.sort(key=lambda x: x['_total_rate_numeric'], reverse=True)
        
        # Organize devices by user for those with users (preserving rate-based sort within each user)
        devices_by_user = {}
        for device in devices_with_users:
            user = device['user']
            if user in devices_by_user:
                devices_by_user[user].append(device)
            else:
                devices_by_user[user] = [device]
        
        # Clean up sorting helper fields before output
        for device in devices_with_users + dynamic_devices:
            device.pop('_rate_up_numeric', None)
            device.pop('_rate_down_numeric', None)
            device.pop('_total_rate_numeric', None)

        output_records = 0
        total_devices = len(device_records)                
        output_entry = BaseOutputProcessor.OutputKidControlEntry
        output_table = BaseOutputProcessor.output_table(output_entry)
                
        # First, add devices with users (grouped by user)
        user_device_count = 0
        for user, devices in devices_by_user.items():
            for record in devices:
                output_table.add_row(output_entry(**record))
                output_records += 1
                user_device_count += 1
            # Add separator line between users if there are multiple users
            if len(devices_by_user) > 1 and output_records < len(devices_with_users):
                output_table.add_row(output_entry())
        
        # Add separator between user devices and dynamic devices if both exist
        if devices_with_users and dynamic_devices:
            output_table.add_row(output_entry())
        
        # Then add dynamic devices (no users)
        for record in dynamic_devices:
            output_table.add_row(output_entry(**record))
            output_records += 1

        print (output_table.draw())

        # Print summary
        if devices_with_users:
            for user in devices_by_user.keys():
                print(f'{user} devices: {len(devices_by_user[user])}')
            print(f'User-assigned devices: {user_device_count}')
        
        if dynamic_devices:
            print(f'Dynamic devices (no user): {len(dynamic_devices)}')
            
        print(f'Total Kid Control devices: {output_records}', '\n')
