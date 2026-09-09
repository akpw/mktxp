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

import re
from datetime import timedelta
from math import floor, log

_re_compiled = {}


def _get_re(key, pattern):
    rgx = _re_compiled.get(key)
    if not rgx:
        rgx = re.compile(pattern) if isinstance(pattern, str) else pattern
        _re_compiled[key] = rgx
    return rgx


def parse_rates(rate):
    """Formats rate string with clean spacing (e.g. '54Mbps' -> '54 Mbps')."""
    if not rate:
        return ""
    rates_rgx = _get_re('rates_rgx', r'(\d*(?:\.\d*)?)([GgMmKk]bps?)')
    rc = rates_rgx.search(str(rate))
    return f"{int(float(rc[1]))} {rc[2]}" if rc and len(rc.groups()) == 2 else str(rate)


def parse_bitrates(rate):
    """Formats raw numeric bitrate into human-readable representation (e.g. 54000000 -> '54 Mbps')."""
    try:
        rate = int(rate)
    except (ValueError, TypeError):
        return parse_rates(rate)

    if rate <= 0:
        return "0 bps"

    power = floor(log(rate, 1000))
    power = max(0, min(int(power), 3))
    units = ['bps', 'Kbps', 'Mbps', 'Gbps']
    return f"{int(rate / 1000 ** power)} {units[power]}"


def parse_numeric_rate(rate_str):
    """Extracts numeric rate in bits per second (bps) as integer for sorting and filtering."""
    if not rate_str or rate_str == '0':
        return 0

    # Handle raw numeric strings first
    try:
        return int(rate_str)
    except (ValueError, TypeError):
        pass

    # Handle parsed rate strings like '1 Kbps', '53 Mbps', '1.5 Gbps', '18M', '100 Mb/s'
    if isinstance(rate_str, str):
        rate_clean = rate_str.strip().replace('/', '')
        match = re.match(r'^([\d.]+)\s*([A-Za-z]+)$', rate_clean)
        if match:
            try:
                num = float(match.group(1))
                unit = match.group(2).lower()
                if 'tbps' in unit or unit in ('t', 'tb', 'tbs'):
                    return int(num * 1000000000000)
                elif 'gbps' in unit or unit in ('g', 'gb', 'gbs'):
                    return int(num * 1000000000)
                elif 'mbps' in unit or unit in ('m', 'mb', 'mbs'):
                    return int(num * 1000000)
                elif 'kbps' in unit or unit in ('k', 'kb', 'kbs'):
                    return int(num * 1000)
                elif 'bps' in unit or unit in ('b', 'bs'):
                    return int(num)
                return int(num)
            except ValueError:
                pass

    return 0


def parse_rate_limit(rate_str):
    """Converts user-supplied rate filter string (e.g. '18', '18M', '54 Mbps', '500k') to integer bps."""
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
    return parse_numeric_rate(rate_str)


def parse_interface_rate(interface_rate):
    """Extracts interface speed in Mbps."""
    interface_rate_rgx = _get_re('interface_rate_rgx', r'[^.\-\d]')
    mult = 1000 if str(interface_rate).find('Mbps') < 0 else 1
    return int(float(interface_rate_rgx.sub('', str(interface_rate))) * mult)


def parse_timedelta(time, ms_span=False):
    """Parses RouterOS duration string (e.g. '1w2d3h4m5s' or '50ms') into timedelta."""
    rgx_key = 'duration_interval_rgx_sp' if ms_span else 'duration_interval_rgx'
    pattern = (
        r'((?P<seconds>\d+)s)?((?P<milliseconds>\d+)ms)?((?P<microseconds>\d+)us)?'
        if ms_span
        else r'((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?((?P<milliseconds>\d+)ms)?'
    )
    duration_interval_rgx = _get_re(rgx_key, pattern)
    matched = duration_interval_rgx.match(str(time))
    if not matched:
        return timedelta()
    time_dict = matched.groupdict()
    return timedelta(**{key: int(value) for key, value in time_dict.items() if value})


def parse_timedelta_seconds(time, ms_span=False):
    """Converts RouterOS duration string to float total seconds."""
    return parse_timedelta(time, ms_span=ms_span).total_seconds()


def parse_timedelta_milliseconds(time, ms_span=False):
    """Converts RouterOS duration string to float total milliseconds."""
    return parse_timedelta(time, ms_span=ms_span) / timedelta(milliseconds=1)


def parse_duration_limit(duration_str):
    """Converts user-supplied duration filter string (e.g. '15m', '1h', '30s', '16') to integer seconds."""
    if duration_str is None:
        return 0
    if isinstance(duration_str, (int, float)):
        return int(duration_str * 60)
    if isinstance(duration_str, str):
        dur_clean = duration_str.strip()
        if re.match(r'^\d+(\.\d+)?$', dur_clean):
            return int(float(dur_clean) * 60)
        try:
            return int(parse_timedelta_seconds(dur_clean))
        except Exception:
            pass
    return 0


def parse_signal_strength(signal_strength):
    """Extracts numeric dBm signal strength string from raw value."""
    if signal_strength is None:
        return ""
    wifi_signal_strength_rgx = _get_re('wifi_signal_strength_rgx', r'(-?\d+(?:\.\d+)?)')
    match = wifi_signal_strength_rgx.search(str(signal_strength))
    return match.group() if match else ""


def parse_uptime_seconds(uptime):
    """Parses RouterOS uptime string (e.g. '1w2d3h4m5s', '45s') into integer seconds.
    Unlike parse_timedelta, the whole string must be a valid duration; returns None otherwise."""
    if uptime is None:
        return None
    uptime_rgx = _get_re(
        'uptime_rgx',
        r'^((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?((?P<milliseconds>\d+)ms)?$',
    )
    matched = uptime_rgx.match(str(uptime).strip())
    if not matched or not matched.group():
        return None
    return int(timedelta(**{key: int(value) for key, value in matched.groupdict().items() if value}).total_seconds())


def parse_rate_bps(rate):
    """Parses RouterOS wireless rate string (e.g. '866.6Mbps-80MHz/2S/SGI', '6Mbps', raw '866000000') into integer bps.
    Returns None when the value does not start with a recognizable rate."""
    if rate is None:
        return None
    rate_str = str(rate).strip()
    if rate_str.isdigit():
        return int(rate_str)
    rate_bps_rgx = _get_re('rate_bps_rgx', r'(?i)^(\d+(?:\.\d+)?)\s*([kmg]?)bps')
    matched = rate_bps_rgx.match(rate_str)
    if not matched:
        return None
    multiplier = {'': 1, 'k': 1000, 'm': 1000 ** 2, 'g': 1000 ** 3}[matched.group(2).lower()]
    return int(round(float(matched.group(1)) * multiplier))
