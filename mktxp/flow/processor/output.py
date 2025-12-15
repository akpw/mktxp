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


import re, os
from datetime import timedelta
from collections import namedtuple
from texttable import Texttable
from humanize import naturaldelta
from mktxp.cli.config.config import config_handler
from mktxp.datasource.wireless_ds import WirelessMetricsDataSource
from mktxp.datasource.dhcp_ds import DHCPMetricsDataSource
from math import floor, log


class BaseOutputProcessor:
    OutputCapsmanEntry = namedtuple('OutputCapsmanEntry', ['dhcp_name', 'dhcp_address', 'mac_address', 'rx_signal', 'interface', 'ssid', 'tx_rate', 'rx_rate', 'uptime'])
    OutputCapsmanEntry.__new__.__defaults__ = ('',) * len(OutputCapsmanEntry._fields)

    OutputWirelessEntry = namedtuple('OutputWirelessEntry', ['dhcp_name', 'dhcp_address', 'mac_address', 'signal_strength', 'signal_to_noise', 'interface', 'tx_rate', 'rx_rate', 'uptime'])
    OutputWirelessEntry.__new__.__defaults__ = ('',) * len(OutputWirelessEntry._fields)

    OutputWiFiEntry = namedtuple('OutputWiFiEntry', ['dhcp_name', 'dhcp_address', 'mac_address', 'signal_strength', 'interface', 'tx_rate', 'rx_rate', 'uptime'])
    OutputWiFiEntry.__new__.__defaults__ = ('',) * len(OutputWiFiEntry._fields)

    OutputDHCPEntry = namedtuple('OutputDHCPEntry', ['host_name', 'server', 'mac_address', 'address', 'active_address', 'expires_after'])
    OutputDHCPEntry.__new__.__defaults__ = ('',) * len(OutputDHCPEntry._fields)

    OutputConnStatsEntry = namedtuple('OutputConnStatsEntry', ['dhcp_name', 'src_address', 'connection_count', 'dst_addresses'])
    OutputConnStatsEntry.__new__.__defaults__ = ('',) * len(OutputConnStatsEntry._fields)

    OutputKidControlEntry = namedtuple('OutputKidControlEntry', ['dhcp_name', 'name', 'user', 'dhcp_address', 'mac_address', 'ip_address', 'rate_up', 'rate_down', 'idle_time'])
    OutputKidControlEntry.__new__.__defaults__ = ('',) * len(OutputKidControlEntry._fields)

    OutputAddressListEntry = namedtuple('OutputAddressListEntry', ['list', 'address', 'comment', 'timeout', 'dynamic', 'disabled'])
    OutputAddressListEntry.__new__.__defaults__ = ('',) * len(OutputAddressListEntry._fields)

    OutputNetwatchEntry = namedtuple('OutputNetwatchEntry', ['name', 'host', 'comment', 'status', 'type', 'since', 'timeout', 'interval'])
    OutputNetwatchEntry.__new__.__defaults__ = ('',) * len(OutputNetwatchEntry._fields)

    @staticmethod
    def format_interface_name(name, comment, interface_name_format, max_length=20):
        """Formats interface/resource name based on interface_name_format configuration.
        
        Args:
            name: The base name (e.g., 'ether1', '10.0.0.1', MAC address)
            comment: Optional comment/description
            interface_name_format: One of 'name', 'comment', 'combined'
            max_length: Maximum length for truncation
        
        Returns:
            Formatted name string
        """
        # Handle None/empty values
        if not name:
            name = ''
        if not comment:
            comment = ''
        
        # Apply truncation to comment if specified
        if max_length and comment:
            comment = comment[0:max_length]
        
        # Format based on interface_name_format
        if interface_name_format == 'name':
            # Use name only, ignore comment
            return name
        elif interface_name_format == 'comment':
            # Use comment if available, fallback to name
            return comment if comment else name
        elif interface_name_format == 'combined':
            # Use "name (comment)" if comment exists, else just name
            if comment:
                return f'{name} ({comment})'
            else:
                return name
        else:
            # Invalid format, fallback to name with warning
            print(f'Warning: Invalid interface_name_format "{interface_name_format}". Using "name" format.')
            return name

    @staticmethod
    def augment_record(router_entry, registration_record, id_key = 'mac_address'):
        BaseOutputProcessor.resolve_dhcp(router_entry, registration_record, id_key)

        # split out tx/rx bytes
        if registration_record.get('bytes'):
            registration_record['tx_bytes'] = registration_record['bytes'].split(',')[0]
            registration_record['rx_bytes'] = registration_record['bytes'].split(',')[1]
            del registration_record['bytes']

        if registration_record.get('tx_rate'):
            registration_record['tx_rate'] = BaseOutputProcessor.parse_bitrates(registration_record['tx_rate'])
        if registration_record.get('rx_rate'):
            registration_record['rx_rate'] = BaseOutputProcessor.parse_bitrates(registration_record['rx_rate'])
        if registration_record.get('uptime'):
            registration_record['uptime'] = naturaldelta(BaseOutputProcessor.parse_timedelta_seconds(registration_record['uptime']), months=True, minimum_unit='seconds')

        if registration_record.get('signal_strength'):
            registration_record['signal_strength'] = BaseOutputProcessor.parse_signal_strength(registration_record['signal_strength'])
        if registration_record.get('rx_signal'):
            registration_record['rx_signal'] = BaseOutputProcessor.parse_signal_strength(registration_record['rx_signal'])

    @staticmethod
    def dhcp_name(router_entry, dhcp_lease_record, drop_comment = False):
        dhcp_name = dhcp_lease_record.get('host_name')
        dhcp_comment = dhcp_lease_record.get('comment')
        
        # If no hostname, use MAC address as the base name
        if not dhcp_name:
            dhcp_name = dhcp_lease_record.get('mac_address', '')
        
        # Format using the centralized function 
        formatted_name = BaseOutputProcessor.format_interface_name(
            dhcp_name, 
            dhcp_comment, 
            router_entry.config_entry.interface_name_format
        )
        
        if drop_comment:
            del dhcp_lease_record['comment']

        return formatted_name if formatted_name else ''

    @staticmethod
    def resolve_dhcp(router_entry, registration_record, id_key = 'mac_address', resolve_address = True):
        if not router_entry.dhcp_records:
            DHCPMetricsDataSource.metric_records(router_entry)
        dhcp_name = registration_record.get(id_key)
        dhcp_address = 'No DHCP Record'              

        dhcp_lease_record = router_entry.dhcp_record(dhcp_name)
        if dhcp_lease_record:
            dhcp_name = BaseOutputProcessor.dhcp_name(router_entry, dhcp_lease_record)
            dhcp_address = dhcp_lease_record.get('address', '')

        registration_record['dhcp_name'] = dhcp_name
        if resolve_address:
            registration_record['dhcp_address'] = dhcp_address

    @staticmethod
    def parse_rates(rate):
        rates_rgx = config_handler.re_compiled.get('rates_rgx')
        if not rates_rgx:
            rates_rgx = re.compile(r'(\d*(?:\.\d*)?)([GgMmKk]bps?)')
            config_handler.re_compiled['rates_rgx'] = rates_rgx
        rc = rates_rgx.search(rate)
        return f'{int(float(rc[1]))} {rc[2]}' if rc and len(rc.groups()) == 2 else rate

    @staticmethod
    def parse_bitrates(rate):
        try:
            rate = int(rate)
        except:
            return BaseOutputProcessor.parse_rates(rate)
        
        # Handle zero rate
        if rate <= 0:
            return "0 bps"
        
        power = floor(log(rate, 1000))
        return f"{int(rate / 1000 ** power)} {['bps', 'Kbps', 'Mbps', 'Gbps'][int(power)]}"

    @staticmethod
    def parse_timedelta(time, ms_span=False):
        # ms_span for milliseconds-long durations, since otherwise minutes would match the ms in the value
        rgx_key = 'duration_interval_rgx_sp' if ms_span else 'duration_interval_rgx'
        duration_interval_rgx = config_handler.re_compiled.get(rgx_key)
        if not duration_interval_rgx:
            duration_interval_rgx = re.compile(r'((?P<seconds>\d+)s)?((?P<milliseconds>\d+)ms)?((?P<microseconds>\d+)us)?') if ms_span else\
                    re.compile(r'((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?((?P<milliseconds>\d+)ms)?')
            config_handler.re_compiled[rgx_key] = duration_interval_rgx                        
        time_dict = duration_interval_rgx.match(time).groupdict()
        return timedelta(**{key: int(value) for key, value in time_dict.items() if value})

    @staticmethod
    def parse_timedelta_seconds(time, ms_span=False):
        return BaseOutputProcessor.parse_timedelta(time, ms_span=ms_span).total_seconds()

    @staticmethod
    def parse_timedelta_milliseconds(time, ms_span=False):
        return BaseOutputProcessor.parse_timedelta(time, ms_span=ms_span) / timedelta(milliseconds=1)

    @staticmethod
    def parse_signal_strength(signal_strength):
        wifi_signal_strength_rgx = config_handler.re_compiled.get('wifi_signal_strength_rgx')
        if not wifi_signal_strength_rgx:
            # wifi_signal_strength_rgx = re.compile(r'(-?\d+(?:\.\d+)?)(dBm)?')
            wifi_signal_strength_rgx = re.compile(r'(-?\d+(?:\.\d+)?)')           
            config_handler.re_compiled['wifi_signal_strength_rgx'] = wifi_signal_strength_rgx
        return wifi_signal_strength_rgx.search(signal_strength).group()

    @staticmethod
    def parse_numeric_rate(rate_str):
        """Extract numeric value from rate strings for sorting/comparison purposes.
        Handles both raw numeric strings and parsed rate strings like '1 Kbps', '53 Mbps'.
        Returns the rate in bps (bits per second) as an integer.
        """
        if not rate_str or rate_str == '0':
            return 0
        
        # Handle raw numeric strings first
        try:
            return int(rate_str)
        except (ValueError, TypeError):
            pass
        
        # Handle parsed rate strings like '1 Kbps', '53 Mbps', '1.5 Gbps'
        if isinstance(rate_str, str):
            parts = rate_str.strip().split()
            if len(parts) >= 1:
                try:
                    num = float(parts[0])
                    if len(parts) > 1:
                        unit = parts[1].lower()
                        if 'gbps' in unit:
                            return int(num * 1000000000)
                        elif 'mbps' in unit:
                            return int(num * 1000000)
                        elif 'kbps' in unit:
                            return int(num * 1000)
                        elif 'bps' in unit:
                            return int(num)
                    return int(num)  # Default to bps if no unit
                except ValueError:
                    pass
        
        return 0

    @staticmethod
    def parse_interface_rate(interface_rate):
        interface_rate_rgx = config_handler.re_compiled.get('interface_rate_rgx')
        if not interface_rate_rgx:
            interface_rate_rgx = re.compile(r'[^.\-\d]')
            config_handler.re_compiled['interface_rate_rgx'] = interface_rate_rgx
        rate = lambda interface_rate: 1000 if interface_rate.find('Mbps') < 0 else 1
        return(int(float(interface_rate_rgx.sub('', interface_rate)) * rate(interface_rate)))

    @staticmethod
    def output_table(outputEntry = None):
        table = Texttable(max_width = os.get_terminal_size().columns)
        table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES )        
        if outputEntry:
            table.header(outputEntry._fields)
            table.set_cols_align(['l']+ ['c']*(len(outputEntry._fields)-1))
        return table
