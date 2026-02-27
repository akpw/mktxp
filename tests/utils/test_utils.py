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
from unittest.mock import patch, MagicMock
import urllib.error
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


class TestGetAvailableUpdates:
    """Tests for get_available_updates and check_for_updates."""

    def setup_method(self):
        # Clear lru_cache between tests
        utils.get_available_updates.cache_clear()

    def test_urlopen_called_with_timeout(self):
        """urlopen must be called with an explicit timeout."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'''<?xml version="1.0"?>
            <rss><channel>
                <item><title>7.16 changelog</title></item>
            </channel></rss>'''
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch('urllib.request.urlopen', return_value=mock_response) as mock_urlopen:
            utils.get_available_updates('stable', ttl_hash=0)
            mock_urlopen.assert_called_once_with(
                'https://mikrotik.com/current.rss',
                timeout=utils.UPDATE_CHECK_TIMEOUT,
            )

    def test_timeout_returns_empty_list(self):
        """A timeout should return an empty list (not raise), so lru_cache caches it."""
        with patch('urllib.request.urlopen', side_effect=TimeoutError('timed out')):
            result = utils.get_available_updates('stable', ttl_hash=1)
            assert result == []

    def test_http_error_returns_empty_list(self):
        """An HTTP error should return an empty list."""
        with patch('urllib.request.urlopen', side_effect=urllib.error.HTTPError(
            url=None, code=503, msg='Service Unavailable', hdrs=None, fp=None
        )):
            result = utils.get_available_updates('stable', ttl_hash=2)
            assert result == []

    def test_unknown_channel_returns_empty_list(self):
        """An unknown channel should return an empty list without attempting a fetch."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            result = utils.get_available_updates('nonexistent', ttl_hash=3)
            assert result == []
            mock_urlopen.assert_not_called()

    def test_failure_result_is_cached(self):
        """After a failure, the empty list result should be cached by lru_cache."""
        with patch('urllib.request.urlopen', side_effect=TimeoutError('timed out')) as mock_urlopen:
            utils.get_available_updates('stable', ttl_hash=4)
            utils.get_available_updates('stable', ttl_hash=4)
            # urlopen should only be called once; second call uses cache
            mock_urlopen.assert_called_once()

    def test_check_for_updates_on_fetch_failure(self):
        """check_for_updates should return cur == newest when the feed fetch fails."""
        with patch('urllib.request.urlopen', side_effect=TimeoutError('timed out')):
            cur, newest = utils.check_for_updates('7.15 (stable)')
            assert cur == newest == parse('7.15')

    def test_check_for_updates_success(self):
        """check_for_updates should return the newest version on success."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'''<?xml version="1.0"?>
            <rss><channel>
                <item><title>7.16 changelog</title></item>
                <item><title>7.15.3 changelog</title></item>
            </channel></rss>'''
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch('urllib.request.urlopen', return_value=mock_response):
            cur, newest = utils.check_for_updates('7.15 (stable)')
            assert cur == parse('7.15')
            assert newest == parse('7.16')
