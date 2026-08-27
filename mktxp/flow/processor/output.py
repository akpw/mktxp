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


import re, os, fnmatch
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

    _re_compiled = {}

    @classmethod
    def _get_re(cls, key, pattern):
        rgx = cls._re_compiled.get(key)
        if not rgx:
            rgx = re.compile(pattern) if isinstance(pattern, str) else pattern
            cls._re_compiled[key] = rgx
        return rgx

    @classmethod
    def parse_rates(cls, rate):
        rates_rgx = cls._get_re('rates_rgx', r'(\d*(?:\.\d*)?)([GgMmKk]bps?)')
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

    @classmethod
    def parse_timedelta(cls, time, ms_span=False):
        # ms_span for milliseconds-long durations, since otherwise minutes would match the ms in the value
        rgx_key = 'duration_interval_rgx_sp' if ms_span else 'duration_interval_rgx'
        pattern = r'((?P<seconds>\d+)s)?((?P<milliseconds>\d+)ms)?((?P<microseconds>\d+)us)?' if ms_span else\
                  r'((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?((?P<milliseconds>\d+)ms)?'
        duration_interval_rgx = cls._get_re(rgx_key, pattern)
        time_dict = duration_interval_rgx.match(time).groupdict()
        return timedelta(**{key: int(value) for key, value in time_dict.items() if value})

    @staticmethod
    def parse_timedelta_seconds(time, ms_span=False):
        return BaseOutputProcessor.parse_timedelta(time, ms_span=ms_span).total_seconds()

    @staticmethod
    def parse_timedelta_milliseconds(time, ms_span=False):
        return BaseOutputProcessor.parse_timedelta(time, ms_span=ms_span) / timedelta(milliseconds=1)

    @classmethod
    def parse_signal_strength(cls, signal_strength):
        wifi_signal_strength_rgx = cls._get_re('wifi_signal_strength_rgx', r'(-?\d+(?:\.\d+)?)')
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
        
        # Handle parsed rate strings like '1 Kbps', '53 Mbps', '1.5 Gbps', '18M'
        if isinstance(rate_str, str):
            rate_clean = rate_str.strip()
            match = re.match(r'^([\d.]+)\s*([A-Za-z]+)$', rate_clean)
            if match:
                try:
                    num = float(match.group(1))
                    unit = match.group(2).lower()
                    if 'tbps' in unit or unit == 't' or unit == 'tb':
                        return int(num * 1000000000000)
                    elif 'gbps' in unit or unit == 'g' or unit == 'gb':
                        return int(num * 1000000000)
                    elif 'mbps' in unit or unit == 'm' or unit == 'mb':
                        return int(num * 1000000)
                    elif 'kbps' in unit or unit == 'k' or unit == 'kb':
                        return int(num * 1000)
                    elif 'bps' in unit or unit == 'b':
                        return int(num)
                    return int(num)
                except ValueError:
                    pass
        
        return 0

    @classmethod
    def parse_duration_limit(cls, duration_str):
        """Converts user-supplied duration filter string (e.g. '15m', '1h', '30s', '16')
        to integer seconds. If a pure number without unit is supplied, treats it as minutes ('m').
        """
        if duration_str is None:
            return 0
        if isinstance(duration_str, (int, float)):
            return int(duration_str * 60)
        if isinstance(duration_str, str):
            dur_clean = duration_str.strip()
            if re.match(r'^\d+(\.\d+)?$', dur_clean):
                return int(float(dur_clean) * 60)
            try:
                return int(cls.parse_timedelta_seconds(dur_clean))
            except Exception:
                pass
        return 0

    @classmethod
    def parse_rate_limit(cls, rate_str):
        """Converts user-supplied rate filter string (e.g. '18', '18M', '54 Mbps', '500k')
        to integer bps. If a pure number without unit is supplied, treats it as Mbps (matching CLI table units).
        """
        if rate_str is None:
            return 0
        if isinstance(rate_str, (int, float)):
            if rate_str < 10000:
                return int(rate_str * 1000 ** 2)
            return int(rate_str)
        if isinstance(rate_str, str):
            rate_clean = rate_str.strip()
            if re.match(r'^\d+(\.\d+)?$', rate_clean):
                try:
                    val = float(rate_clean)
                    if val < 10000:
                        return int(val * 1000 ** 2)
                    return int(val)
                except ValueError:
                    pass
        return cls.parse_numeric_rate(rate_str)

    @classmethod
    def parse_interface_rate(cls, interface_rate):
        interface_rate_rgx = cls._get_re('interface_rate_rgx', r'[^.\-\d]')
        rate = lambda interface_rate: 1000 if interface_rate.find('Mbps') < 0 else 1
        return(int(float(interface_rate_rgx.sub('', interface_rate)) * rate(interface_rate)))

    @staticmethod
    def parse_patterns(patterns):
        ''' Parses patterns separated by ';'
        Example: "OF-5G;Pro" -> ["OF-5G", "Pro"]
        '''
        if not patterns:
            return []
        if isinstance(patterns, str):
            return [p.strip() for p in patterns.split(';') if p.strip()]
        if isinstance(patterns, (list, tuple)):
            res = []
            for item in patterns:
                if item:
                    res.extend([p.strip() for p in str(item).split(';') if p.strip()])
            return res
        return []

    @staticmethod
    def match_record(record_dict, include_patterns=None, exclude_patterns=None):
        ''' Evaluates whether a record matches include and exclude filter patterns.
        Supports semicolon/comma delimited patterns and Unix glob wildcards (*, ?).
        - include_patterns: if provided, at least one value in record must match ANY include pattern (case-insensitive substring or glob)
        - exclude_patterns: if provided, no value in record may match ANY exclude pattern (case-insensitive substring or glob)
        '''
        include_list = BaseOutputProcessor.parse_patterns(include_patterns)
        exclude_list = BaseOutputProcessor.parse_patterns(exclude_patterns)

        if not include_list and not exclude_list:
            return True
            
        values = [str(v).lower() for v in record_dict.values() if v is not None and str(v) != '']

        def _val_matches_pat(val_lower, pat_lower):
            if '*' in pat_lower or '?' in pat_lower:
                return fnmatch.fnmatchcase(val_lower, pat_lower) or fnmatch.fnmatchcase(val_lower, f'*{pat_lower}*')
            return pat_lower in val_lower
        
        if include_list:
            matched = False
            for pat in include_list:
                pat_lower = pat.lower()
                for val in values:
                    if _val_matches_pat(val, pat_lower):
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                return False
                
        if exclude_list:
            for pat in exclude_list:
                pat_lower = pat.lower()
                for val in values:
                    if _val_matches_pat(val, pat_lower):
                        return False
                        
        return True

    @classmethod
    def match_wireless_record(cls, record_dict, diag_conf=None, low_signal=None, min_signal=None, low_rate=None, recent=None, band=None, raw_uptime=None):
        ''' Checks if a wireless client record matches specialized wireless diagnostic filters.
        - low_signal: if set, matches signal <= threshold (e.g. <= -75 dBm)
        - min_signal: if set, matches signal >= threshold (e.g. >= -60 dBm)
        - low_rate: if set, matches min(tx_rate, rx_rate) <= rate_limit (e.g. <= 18M)
        - recent: if set, matches uptime <= duration (e.g. <= 15m)
        - band: if set (2g, 5g, 6g), matches band in interface/ssid
        '''
        if low_signal is None and min_signal is None and low_rate is None and recent is None and band is None:
            return True

        if diag_conf is None:
            diag_conf = config_handler.diag_config() if hasattr(config_handler, 'diag_config') else {}

        # 1. Signal strength filtering
        signal_val_str = record_dict.get('rx_signal') or record_dict.get('signal_strength')
        if signal_val_str is not None:
            try:
                sig_match = re.search(r'-?\d+', str(signal_val_str))
                if sig_match:
                    signal_int = int(sig_match.group())

                    if low_signal is not None:
                        threshold = -abs(int(diag_conf.get('low_signal_threshold', -75))) if low_signal is True else -abs(int(low_signal))
                        if signal_int > threshold:
                            return False

                    if min_signal is not None:
                        threshold = -abs(int(diag_conf.get('min_signal_threshold', -60))) if min_signal is True else -abs(int(min_signal))
                        if signal_int < threshold:
                            return False
            except (ValueError, TypeError):
                pass

        # 2. Low negotiated rate filtering
        if low_rate is not None:
            if low_rate is True:
                rate_limit_str = diag_conf.get('low_rate_threshold', '18M')
            else:
                rate_limit_str = low_rate
            rate_limit_bps = cls.parse_rate_limit(rate_limit_str)
            if rate_limit_bps > 0:
                tx_bps = cls.parse_numeric_rate(record_dict.get('tx_rate', 0))
                rx_bps = cls.parse_numeric_rate(record_dict.get('rx_rate', 0))
                rates = [r for r in (tx_bps, rx_bps) if r > 0]
                if rates and min(rates) > rate_limit_bps:
                    return False

        # 3. Recent connection duration filtering
        if recent is not None:
            duration_str = diag_conf.get('recent_duration', '15m') if recent is True else recent
            max_seconds = cls.parse_duration_limit(duration_str)
            if max_seconds > 0:
                uptime_val = raw_uptime if raw_uptime is not None else record_dict.get('uptime')
                if uptime_val:
                    try:
                        uptime_seconds = cls.parse_timedelta_seconds(str(uptime_val))
                        if uptime_seconds > max_seconds:
                            return False
                    except Exception:
                        pass

        # 4. Frequency band filtering (2g / 5g / 6g)
        if band is not None:
            band_str = str(band).lower().strip()
            native_band = str(record_dict.get('band', '')).lower()
            interface_str = str(record_dict.get('interface', '')).lower()
            ssid_str = str(record_dict.get('ssid', '')).lower()
            combined = f'{native_band} {interface_str} {ssid_str}'

            if band_str in ('2g', '2.4', '2.4g', '2.4ghz'):
                if native_band:
                    if not any(token in native_band for token in ('2ghz', '2.4', '2.4ghz', '2g')):
                        return False
                elif not any(token in combined for token in ('2g', '2.4', '2.4ghz', '2ghz', 'wlan1', 'wifi1')):
                    return False
            elif band_str in ('5g', '5ghz'):
                if native_band:
                    if not any(token in native_band for token in ('5ghz', '5g')):
                        return False
                elif not any(token in combined for token in ('5g', '5ghz', 'wlan2', 'wifi2')):
                    return False
            elif band_str in ('6g', '6ghz'):
                if native_band:
                    if not any(token in native_band for token in ('6ghz', '6g')):
                        return False
                elif not any(token in combined for token in ('6g', '6ghz', 'wlan3', 'wifi3')):
                    return False
            else:
                if band_str not in combined:
                    return False

        return True

    @staticmethod
    def output_table(outputEntry = None):
        try:
            terminal_columns = os.get_terminal_size().columns
        except (OSError, ValueError):
            terminal_columns = 0
        table = Texttable(max_width = terminal_columns)
        table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES )        
        if outputEntry:
            table.header(outputEntry._fields)
            table.set_cols_align(['l']+ ['c']*(len(outputEntry._fields)-1))
        return table
