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

from mktxp.utils.filtering import (
    parse_patterns,
    match_record,
    match_wireless_record,
)


def test_parse_patterns():
    assert parse_patterns("OF-5G;Pro") == ["OF-5G", "Pro"]
    assert parse_patterns(["OF-5G", "Pro;Air"]) == ["OF-5G", "Pro", "Air"]
    assert parse_patterns(None) == []


def test_match_record_include():
    rec = {'name': 'MacBookPro', 'ip': '10.10.10.16', 'mac': '82:61:A1:0B:16:CA'}
    assert match_record(rec, include_patterns='MacBook') is True
    assert match_record(rec, include_patterns='*10.16*') is True
    assert match_record(rec, include_patterns='iPhone') is False


def test_match_record_exclude():
    rec = {'name': 'MacBookPro', 'ip': '10.10.10.16', 'mac': '82:61:A1:0B:16:CA'}
    assert match_record(rec, exclude_patterns='iPhone') is True
    assert match_record(rec, exclude_patterns='MacBook') is False


def test_match_wireless_record_signal():
    rec_good = {'rx_signal': '-55', 'tx_rate': '866 Mbps', 'rx_rate': '866 Mbps', 'uptime': '1h'}
    rec_weak = {'rx_signal': '-80', 'tx_rate': '6 Mbps', 'rx_rate': '6 Mbps', 'uptime': '5m'}

    # low_signal (threshold <= -75)
    assert match_wireless_record(rec_good, low_signal=True) is False
    assert match_wireless_record(rec_weak, low_signal=True) is True

    # min_signal (threshold >= -60)
    assert match_wireless_record(rec_good, min_signal=True) is True
    assert match_wireless_record(rec_weak, min_signal=True) is False


def test_match_wireless_record_rate():
    rec_fast = {'tx_rate': '866 Mbps', 'rx_rate': '866 Mbps'}
    rec_slow = {'tx_rate': '6 Mbps', 'rx_rate': '54 Mbps'}

    assert match_wireless_record(rec_fast, low_rate='18M') is False
    assert match_wireless_record(rec_slow, low_rate='18M') is True


def test_match_wireless_record_band():
    rec_2g = {'interface': 'wlan1', 'ssid': 'Home2G', 'band': '2.4GHz'}
    rec_5g = {'interface': 'wlan2', 'ssid': 'Home5G', 'band': '5GHz'}

    assert match_wireless_record(rec_2g, band='2g') is True
    assert match_wireless_record(rec_2g, band='5g') is False

    assert match_wireless_record(rec_5g, band='5g') is True
    assert match_wireless_record(rec_5g, band='2g') is False
