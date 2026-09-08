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

from datetime import timedelta
from mktxp.utils.units import (
    parse_rates,
    parse_bitrates,
    parse_numeric_rate,
    parse_rate_limit,
    parse_interface_rate,
    parse_timedelta,
    parse_timedelta_seconds,
    parse_timedelta_milliseconds,
    parse_duration_limit,
    parse_signal_strength,
    parse_uptime_seconds,
    parse_rate_bps,
)


def test_parse_rates():
    assert parse_rates('54Mbps') == '54 Mbps'
    assert parse_rates('866.7Mbps') == '866 Mbps'
    assert parse_rates('1Gbps') == '1 Gbps'
    assert parse_rates('') == ''


def test_parse_bitrates():
    assert parse_bitrates(0) == '0 bps'
    assert parse_bitrates(1000) == '1 Kbps'
    assert parse_bitrates(54000000) == '54 Mbps'
    assert parse_bitrates(1000000000) == '1 Gbps'
    assert parse_bitrates('54Mbps') == '54 Mbps'


def test_parse_numeric_rate():
    assert parse_numeric_rate('0') == 0
    assert parse_numeric_rate(1000) == 1000
    assert parse_numeric_rate('54 Mbps') == 54000000
    assert parse_numeric_rate('100 Mb/s') == 100000000
    assert parse_numeric_rate('1 Gb/s') == 1000000000
    assert parse_numeric_rate('1.5 Gbps') == 1500000000
    assert parse_numeric_rate('500k') == 500000
    assert parse_numeric_rate('18M') == 18000000


def test_parse_rate_limit():
    assert parse_rate_limit(None) == 0
    assert parse_rate_limit(18) == 18000000
    assert parse_rate_limit('18') == 18000000
    assert parse_rate_limit('18M') == 18000000
    assert parse_rate_limit('54 Mbps') == 54000000
    assert parse_rate_limit('100 Mb/s') == 100000000
    assert parse_rate_limit('1 Gb/s') == 1000000000


def test_parse_interface_rate():
    assert parse_interface_rate('1Gbps') == 1000
    assert parse_interface_rate('100Mbps') == 100


def test_parse_timedelta():
    td = parse_timedelta('1w2d3h4m5s')
    assert td == timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5)
    assert parse_timedelta_seconds('1m30s') == 90.0
    assert parse_timedelta_milliseconds('50ms', ms_span=True) == 50.0


def test_parse_duration_limit():
    assert parse_duration_limit(None) == 0
    assert parse_duration_limit(15) == 900  # 15 min -> 900s
    assert parse_duration_limit('15') == 900
    assert parse_duration_limit('15m') == 900
    assert parse_duration_limit('1h') == 3600
    assert parse_duration_limit('30s') == 30


def test_parse_signal_strength():
    assert parse_signal_strength('-65dBm') == '-65'
    assert parse_signal_strength('-72') == '-72'
    assert parse_signal_strength(None) == ''


def test_parse_uptime_seconds():
    assert parse_uptime_seconds('45s') == 45
    assert parse_uptime_seconds('3h15m2s') == 11702
    assert parse_uptime_seconds('1d2h3m4s') == 93784
    assert parse_uptime_seconds('1w2d3h4m5s') == 788645
    assert parse_uptime_seconds('4s830ms') == 4


def test_parse_uptime_seconds_invalid():
    assert parse_uptime_seconds(None) is None
    assert parse_uptime_seconds('') is None
    assert parse_uptime_seconds('02:03:04') is None
    assert parse_uptime_seconds('1d 2h') is None
    assert parse_uptime_seconds('abc') is None


def test_parse_rate_bps():
    assert parse_rate_bps('866.6Mbps-80MHz/2S/SGI') == 866600000
    assert parse_rate_bps('1.2Gbps-160MHz/2S/SGI') == 1200000000
    assert parse_rate_bps('144.4Mbps') == 144400000
    assert parse_rate_bps('6Mbps') == 6000000
    assert parse_rate_bps('54kbps') == 54000
    assert parse_rate_bps('866000000') == 866000000


def test_parse_rate_bps_invalid():
    assert parse_rate_bps(None) is None
    assert parse_rate_bps('') is None
    assert parse_rate_bps('unknown') is None
    assert parse_rate_bps('-80MHz') is None
    assert parse_rate_bps('Mbps') is None
