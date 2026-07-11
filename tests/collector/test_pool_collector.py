import pytest
from mktxp.collector.pool_collector import PoolCollector

def test_calculate_pool_size_empty():
    assert PoolCollector._calculate_pool_size('') == 0
    assert PoolCollector._calculate_pool_size(None) == 0

def test_calculate_pool_size_single_range():
    # 10.20.10.10 to 10.20.10.254 is exactly 245 IPs
    assert PoolCollector._calculate_pool_size('10.20.10.10-10.20.10.254') == 245

def test_calculate_pool_size_multiple_ranges():
    assert PoolCollector._calculate_pool_size('192.168.1.10-192.168.1.19, 192.168.1.100-192.168.1.109') == 20

def test_calculate_pool_size_cidr_ipv4():
    # /24 has 256 addresses
    assert PoolCollector._calculate_pool_size('192.168.1.0/24') == 256

def test_calculate_pool_size_cidr_ipv6():
    # /127 has 2 addresses
    assert PoolCollector._calculate_pool_size('2001:db8::/127') == 2

def test_calculate_pool_size_single_ip():
    assert PoolCollector._calculate_pool_size('192.168.1.100') == 1

def test_calculate_pool_size_invalid_input():
    # Should ignore invalid chunks safely
    assert PoolCollector._calculate_pool_size('192.168.1.10-192.168.1.20, invalid-range') == 11
