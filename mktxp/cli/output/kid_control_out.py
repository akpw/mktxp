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


from humanize import naturaldelta
from mktxp.cli.config import config_handler
from mktxp.cli.output.tables import output_table, OutputKidControlEntry
from mktxp.utils.filtering import match_record
from mktxp.utils.units import parse_numeric_rate, parse_bitrates, parse_timedelta_seconds, parse_rate_limit
from mktxp.flow.processor.enrichment import augment_record
from mktxp.datasource.kid_control_device_ds import KidDeviceMetricsDataSource

class KidControlOutput:
    ''' Kid Control CLI Output
    '''    
    @staticmethod
    def clients_summary(
        router_entry,
        include=None,
        exclude=None,
        active_only=False,
        rate_above=None,
        unassigned=False,
        dynamic_only=False,
        static_only=False,
        top=None,
    ):
        device_labels = [
            'name',
            'user',
            'mac_address',
            'ip_address',
            'bytes_down',
            'bytes_up',
            'rate_up',
            'rate_down',
            'idle_time',
            'dynamic',
        ]
        device_records = KidDeviceMetricsDataSource.metric_records(
            router_entry, metric_labels=device_labels, cli_output=True
        )
        if not device_records:
            print('No Kid Control device records')
            return 

        diag_conf = (
            config_handler.diag_config()
            if hasattr(config_handler, 'diag_config')
            else {}
        )

        total_unfiltered = len(device_records)
        matched_records = []
        
        for device_record in device_records:
            # Check dynamic vs static
            is_dynamic = str(device_record.get('dynamic', '')).lower() in ('true', 'yes', '1')
            if dynamic_only and not is_dynamic:
                continue
            if static_only and is_dynamic:
                continue

            augment_record(router_entry, device_record)

            # Store original numeric rates for sorting before parsing for display
            rate_up_numeric = parse_numeric_rate(device_record.get('rate_up', '0'))
            rate_down_numeric = parse_numeric_rate(device_record.get('rate_down', '0'))
            
            # Parse rates for display
            if device_record.get('rate_up'):
                device_record['rate_up'] = parse_bitrates(device_record['rate_up'])
            if device_record.get('rate_down'):
                device_record['rate_down'] = parse_bitrates(device_record['rate_down'])

            # Parse idle time for display
            if device_record.get('idle_time'):
                idle_seconds = parse_timedelta_seconds(device_record['idle_time'])
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
                '_total_rate_numeric': rate_up_numeric + rate_down_numeric,
            }

            if unassigned and filtered_record.get('user'):
                continue

            if active_only and filtered_record['_total_rate_numeric'] <= 0:
                continue

            if rate_above is not None:
                rate_limit_str = (
                    diag_conf.get('rate_above_threshold', '1M')
                    if rate_above is True
                    else rate_above
                )
                threshold_bps = parse_rate_limit(rate_limit_str)
                if threshold_bps > 0 and filtered_record['_total_rate_numeric'] < threshold_bps:
                    continue

            if not match_record(filtered_record, include, exclude):
                continue

            matched_records.append(filtered_record)

        has_filters = (
            bool(include)
            or bool(exclude)
            or active_only
            or rate_above is not None
            or unassigned
            or dynamic_only
            or static_only
            or top is not None
        )

        output_records = 0
        output_entry = OutputKidControlEntry
        tbl = output_table(output_entry)

        if top is not None:
            # Flattened leaderboard sorted by total bitrate descending across all devices
            matched_records.sort(key=lambda x: x['_total_rate_numeric'], reverse=True)
            top_limit = None
            try:
                top_limit = (
                    int(diag_conf.get('top_connections_count', 10))
                    if top is True
                    else int(top)
                )
            except (ValueError, TypeError):
                pass

            displayed_records = (
                matched_records[:top_limit]
                if (top_limit is not None and top_limit > 0)
                else matched_records
            )

            total_up_bps = sum(d['_rate_up_numeric'] for d in displayed_records)
            total_down_bps = sum(d['_rate_down_numeric'] for d in displayed_records)

            for record in displayed_records:
                clean_rec = {k: v for k, v in record.items() if not k.startswith('_')}
                tbl.add_row(output_entry(**clean_rec))
                output_records += 1

            if output_records > 0:
                print(tbl.draw())
                if total_up_bps > 0 or total_down_bps > 0:
                    print(f'Active LAN Traffic: {parse_bitrates(total_up_bps)} Up / {parse_bitrates(total_down_bps)} Down')

                if len(displayed_records) < len(matched_records):
                    print(
                        f'Top {output_records} Kid Control devices by rate (Matching: {len(matched_records)}, Total: {total_unfiltered})',
                        '\n',
                    )
                elif has_filters:
                    print(
                        f'Matching Kid Control devices: {output_records} (Total: {total_unfiltered})',
                        '\n',
                    )
                else:
                    print(f'Total Kid Control devices: {output_records}', '\n')
            else:
                print('No matching Kid Control devices found', '\n')

        else:
            devices_with_users = [r for r in matched_records if r.get('user')]
            dynamic_devices = [r for r in matched_records if not r.get('user')]

            devices_with_users.sort(key=lambda x: x['_total_rate_numeric'], reverse=True)
            dynamic_devices.sort(key=lambda x: x['_total_rate_numeric'], reverse=True)

            devices_by_user = {}
            for device in devices_with_users:
                user = device['user']
                if user in devices_by_user:
                    devices_by_user[user].append(device)
                else:
                    devices_by_user[user] = [device]

            total_up_bps = sum(d['_rate_up_numeric'] for d in matched_records)
            total_down_bps = sum(d['_rate_down_numeric'] for d in matched_records)

            user_device_count = 0
            for user, devices in devices_by_user.items():
                for record in devices:
                    clean_rec = {k: v for k, v in record.items() if not k.startswith('_')}
                    tbl.add_row(output_entry(**clean_rec))
                    output_records += 1
                    user_device_count += 1
                # Add separator line between users if there are multiple users
                if len(devices_by_user) > 1 and output_records < len(devices_with_users):
                    tbl.add_row(output_entry())

            # Add separator between user devices and dynamic devices if both exist
            if devices_with_users and dynamic_devices:
                tbl.add_row(output_entry())

            # Then add dynamic devices (no users)
            for record in dynamic_devices:
                clean_rec = {k: v for k, v in record.items() if not k.startswith('_')}
                tbl.add_row(output_entry(**clean_rec))
                output_records += 1

            if output_records > 0:
                print(tbl.draw())

                # Print summary
                if devices_with_users:
                    for user in devices_by_user.keys():
                        print(f'{user} devices: {len(devices_by_user[user])}')
                    print(f'User-assigned devices: {user_device_count}')

                if dynamic_devices:
                    print(f'Dynamic devices (no user): {len(dynamic_devices)}')

                if total_up_bps > 0 or total_down_bps > 0:
                    print(f'Active LAN Traffic: {parse_bitrates(total_up_bps)} Up / {parse_bitrates(total_down_bps)} Down')

                if has_filters:
                    print(
                        f'Matching Kid Control devices: {output_records} (Total: {total_unfiltered})',
                        '\n',
                    )
                else:
                    print(f'Total Kid Control devices: {output_records}', '\n')
            else:
                print('No matching Kid Control devices found', '\n')
