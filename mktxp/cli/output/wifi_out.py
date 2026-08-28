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


from mktxp.cli.output.tables import output_table, OutputWirelessEntry, OutputWiFiEntry
from mktxp.utils.filtering import match_record, match_wireless_record
from mktxp.flow.processor.enrichment import augment_record
from mktxp.datasource.wireless_ds import WirelessMetricsDataSource
from mktxp.flow.router_entry import RouterEntryWirelessType

class WirelessOutput:
    ''' Wireless Clients CLI Output
    '''    
    @staticmethod
    def clients_summary(router_entry, include=None, exclude=None, diag_conf=None, low_signal=None, min_signal=None, low_rate=None, recent=None, band=None):
        registration_labels = ['interface', 'mac_address', 'signal_strength', 'uptime', 'tx_rate', 'rx_rate', 'signal_to_noise', 'band', 'ssid']
        registration_records = WirelessMetricsDataSource.metric_records(router_entry, metric_labels = registration_labels, add_router_id = False)
        if not registration_records:
            print('No wireless registration records')
            return 

        # translate / trim / augment registration records
        dhcp_rt_by_interface = {}
        total_unfiltered = len(registration_records)
        filtered_records = []

        key = lambda rt_record: rt_record['signal_strength'] if rt_record.get('signal_strength') else rt_record['interface']
        for registration_record in sorted(registration_records, key = key, reverse=True):
            raw_uptime = registration_record.get('uptime')
            raw_tx_rate = registration_record.get('tx_rate')
            raw_rx_rate = registration_record.get('rx_rate')
            augment_record(router_entry, registration_record)
            if not match_record(registration_record, include, exclude):
                continue
            if not match_wireless_record(
                registration_record,
                diag_conf=diag_conf,
                low_signal=low_signal,
                min_signal=min_signal,
                low_rate=low_rate,
                recent=recent,
                band=band,
                raw_uptime=raw_uptime
            ):
                continue
            filtered_records.append(registration_record)

            interface = registration_record['interface']
            if interface in dhcp_rt_by_interface.keys():
                dhcp_rt_by_interface[interface].append(registration_record)
            else:
                dhcp_rt_by_interface[interface] = [registration_record]         

        output_records = 0
        total_displayed = len(filtered_records)                
        output_entry = OutputWirelessEntry \
                        if router_entry.wireless_type in (RouterEntryWirelessType.DUAL, RouterEntryWirelessType.WIRELESS) else OutputWiFiEntry
        tbl = output_table(output_entry)
        
        for key in dhcp_rt_by_interface.keys():
            for record in dhcp_rt_by_interface[key]:
                entry_dict = {f: record.get(f, '') for f in output_entry._fields}
                tbl.add_row(output_entry(**entry_dict))
                output_records += 1
            if output_records < total_displayed:
                tbl.add_row(output_entry())

        has_filters = include or exclude or low_signal is not None or min_signal is not None or low_rate is not None or recent is not None or band is not None
                
        if total_displayed > 0:
            print (tbl.draw())
            for server in dhcp_rt_by_interface.keys():
                print(f'{server} clients: {len(dhcp_rt_by_interface[server])}')
            if has_filters:
                print(f'Matching WiFi devices: {output_records} (Total connected: {total_unfiltered})', '\n')
            else:
                print(f'Total connected WiFi devices: {output_records}', '\n')
        else:
            print('No matching WiFi devices found', '\n')

