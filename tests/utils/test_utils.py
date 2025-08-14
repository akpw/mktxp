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
import pytest
from mktxp.utils import utils
from packaging.version import parse


@pytest.mark.parametrize("time_string, expected", [
    ("5w4d3h2m1s", timedelta(weeks=5, days=4, hours=3, minutes=2, seconds=1)),
    ("7w3s", timedelta(weeks=7, seconds=3)),
    ("8d2m", timedelta(days=8, minutes=2)),
    ("xyz", timedelta()),
])
def test_parse_mkt_uptime(time_string, expected):
    assert utils.parse_mkt_uptime(time_string) == int(expected.total_seconds())


@pytest.mark.parametrize("version_str, expected", [
    ("abc", False),
    ("6.13", False),
    ("7.13", True),
    ("7.13 (stable)", True),
])
def test_routerOS7_version(version_str, expected):
    assert utils.routerOS7_version(version_str) == expected


@pytest.mark.parametrize(
    "version_string, expected_version, expected_channel",
    [
        ("2.1.5 (stable)", "2.1.5", "stable"),
        ("2.2.0 (long-term)", "2.2.0", "long-term"),
        ("2.3.1 (development)", "2.3.1", "development"),
        ("2.4.0 (testing)", "2.4.0", "testing"),
        ("2.5.5", "2.5.5", "stable"),
    ],
)
def test_parse_ros_version(version_string, expected_version, expected_channel):
    version, channel = utils.parse_ros_version(version_string)
    assert version == parse(expected_version)
    assert channel == expected_channel


def test_parse_ros_version_invalid():
    with pytest.raises(ValueError):
        utils.parse_ros_version("invalid_version")

@pytest.mark.parametrize("str_value, expected", [
    ("y", True),
    ("yes", True),
    ("t", True),
    ("true", True),
    ("on", True),
    ("ok", True),
    ("1", True),
    ("n", False),
    ("no", False),
    ("f", False),
    ("false", False),
    ("off", False),
    ("fail", False),
    ("0", False),
    (0, False),
    (1, False),
    ([], False),
    ({}, False),
])
def test_str2bool_true_false_return(str_value, expected):
    assert utils.str2bool(str_value) == expected
    assert utils.str2bool(str_value, False) == expected
    assert utils.str2bool(str_value, True) == expected

@pytest.mark.parametrize("str_value", [
    "abc",
    "p",
    "x",
    "10",
])
def test_str2bool_raise_value_error(str_value):
    with pytest.raises(ValueError):
        utils.str2bool(str_value)

    assert utils.str2bool(str_value, False) == False
    assert utils.str2bool(str_value, True) == True
