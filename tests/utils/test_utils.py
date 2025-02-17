from datetime import timedelta
import pytest

from mktxp.utils import utils


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
