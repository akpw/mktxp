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
import fnmatch
from mktxp.cli.config import config_handler
from mktxp.utils.units import (
    parse_rate_limit,
    parse_numeric_rate,
    parse_duration_limit,
    parse_timedelta_seconds,
)


def parse_patterns(patterns):
    """Parses patterns separated by ';' (e.g. 'OF-5G;Pro' -> ['OF-5G', 'Pro'])."""
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


def match_record(record_dict, include_patterns=None, exclude_patterns=None):
    """Evaluates whether a record dictionary matches include and exclude filter patterns.
    Supports semicolon/comma delimited patterns and Unix glob wildcards (*, ?).
    - include_patterns: if provided, at least one value in record must match ANY include pattern
    - exclude_patterns: if provided, no value in record may match ANY exclude pattern
    """
    include_list = parse_patterns(include_patterns)
    exclude_list = parse_patterns(exclude_patterns)

    if not include_list and not exclude_list:
        return True

    values = [
        str(v).lower()
        for v in record_dict.values()
        if v is not None and str(v) != ''
    ]

    def _val_matches_pat(val_lower, pat_lower):
        if '*' in pat_lower or '?' in pat_lower:
            return fnmatch.fnmatchcase(val_lower, pat_lower) or fnmatch.fnmatchcase(
                val_lower, f'*{pat_lower}*'
            )
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


def match_wireless_record(
    record_dict,
    diag_conf=None,
    low_signal=None,
    min_signal=None,
    low_rate=None,
    recent=None,
    band=None,
    raw_uptime=None,
):
    """Checks if a wireless client record matches specialized wireless diagnostic filters.
    - low_signal: if set, matches signal <= threshold (e.g. <= -75 dBm)
    - min_signal: if set, matches signal >= threshold (e.g. >= -60 dBm)
    - low_rate: if set, matches min(tx_rate, rx_rate) <= rate_limit (e.g. <= 18M)
    - recent: if set, matches uptime <= duration (e.g. <= 15m)
    - band: if set ('2g', '5g', '6g'), matches band in native band, interface, or ssid
    """
    if (
        low_signal is None
        and min_signal is None
        and low_rate is None
        and recent is None
        and band is None
    ):
        return True

    if diag_conf is None:
        diag_conf = (
            config_handler.diag_config()
            if hasattr(config_handler, 'diag_config')
            else {}
        )

    # 1. Signal strength filtering
    signal_val_str = record_dict.get('rx_signal') or record_dict.get('signal_strength')
    if signal_val_str is not None:
        try:
            sig_match = re.search(r'-?\d+', str(signal_val_str))
            if sig_match:
                signal_int = int(sig_match.group())

                if low_signal is not None:
                    threshold = (
                        -abs(int(diag_conf.get('low_signal_threshold', -75)))
                        if low_signal is True
                        else -abs(int(low_signal))
                    )
                    if signal_int > threshold:
                        return False

                if min_signal is not None:
                    threshold = (
                        -abs(int(diag_conf.get('min_signal_threshold', -60)))
                        if min_signal is True
                        else -abs(int(min_signal))
                    )
                    if signal_int < threshold:
                        return False
        except (ValueError, TypeError):
            pass

    # 2. Low negotiated rate filtering
    if low_rate is not None:
        rate_limit_str = (
            diag_conf.get('low_rate_threshold', '18M')
            if low_rate is True
            else low_rate
        )
        rate_limit_bps = parse_rate_limit(rate_limit_str)
        if rate_limit_bps > 0:
            tx_bps = parse_numeric_rate(record_dict.get('tx_rate', 0))
            rx_bps = parse_numeric_rate(record_dict.get('rx_rate', 0))
            rates = [r for r in (tx_bps, rx_bps) if r > 0]
            if rates and min(rates) > rate_limit_bps:
                return False

    # 3. Recent connection duration filtering
    if recent is not None:
        duration_str = (
            diag_conf.get('recent_duration', '15m')
            if recent is True
            else recent
        )
        max_seconds = parse_duration_limit(duration_str)
        if max_seconds > 0:
            uptime_val = (
                raw_uptime if raw_uptime is not None else record_dict.get('uptime')
            )
            if uptime_val:
                try:
                    uptime_seconds = parse_timedelta_seconds(str(uptime_val))
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
                if not any(
                    token in native_band
                    for token in ('2ghz', '2.4', '2.4ghz', '2g')
                ):
                    return False
            elif not any(
                token in combined
                for token in ('2g', '2.4', '2.4ghz', '2ghz', 'wlan1', 'wifi1')
            ):
                return False
        elif band_str in ('5g', '5ghz'):
            if native_band:
                if not any(token in native_band for token in ('5ghz', '5g')):
                    return False
            elif not any(
                token in combined
                for token in ('5g', '5ghz', 'wlan2', 'wifi2')
            ):
                return False
        elif band_str in ('6g', '6ghz'):
            if native_band:
                if not any(token in native_band for token in ('6ghz', '6g')):
                    return False
            elif not any(
                token in combined
                for token in ('6g', '6ghz', 'wlan3', 'wifi3')
            ):
                return False
        else:
            if band_str not in combined:
                return False

    return True
