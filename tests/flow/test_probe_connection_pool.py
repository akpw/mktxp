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

import types
from mktxp.flow.probe_connection_pool import ProbeConnectionPool


class DummyConn:
    def __init__(self, name):
        self.name = name
        self.disconnected = False

    def disconnect(self):
        self.disconnected = True


def _config_entry(hostname):
    return types.SimpleNamespace(
        hostname=hostname,
        port=8728,
        username='user',
        password='pass',
        credentials_file='',
        use_ssl=False,
        no_ssl_certificate=False,
        ssl_certificate_verify=False,
        ssl_check_hostname=True,
        ssl_ca_file='',
        plaintext_login=True,
    )


def test_probe_connection_pool_reuses_connection():
    created = []

    def factory(module, config_entry):
        conn = DummyConn(f'{module}@{config_entry.hostname}')
        created.append(conn)
        return conn

    pool = ProbeConnectionPool(max_size=10, ttl_seconds=300, connection_factory=factory)
    conn1 = pool.get('module', _config_entry('host1'))
    conn2 = pool.get('module', _config_entry('host1'))

    assert conn1 is conn2
    assert len(created) == 1


def test_probe_connection_pool_eviction_disconnects_oldest():
    created = []

    def factory(module, config_entry):
        conn = DummyConn(f'{module}@{config_entry.hostname}')
        created.append(conn)
        return conn

    pool = ProbeConnectionPool(max_size=1, ttl_seconds=300, connection_factory=factory)
    conn1 = pool.get('module', _config_entry('host1'))
    conn2 = pool.get('module', _config_entry('host2'))

    assert conn1 is not conn2
    assert conn1.disconnected is True
    assert conn2.disconnected is False
