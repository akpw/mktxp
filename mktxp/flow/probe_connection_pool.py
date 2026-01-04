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

import time
from threading import Lock
from mktxp.flow.router_connection import RouterAPIConnection


class ProbeConnectionPool:
    def __init__(self, max_size, ttl_seconds, connection_factory=None):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._connection_factory = connection_factory or RouterAPIConnection
        self._lock = Lock()
        self._pool = {}

    def get(self, module_name, config_entry):
        key = self._conn_key(module_name, config_entry)
        now = time.time()
        with self._lock:
            self._evict_expired(now)
            if key in self._pool:
                conn, _ = self._pool[key]
                self._pool[key] = (conn, now)
                return conn

            if self.max_size and len(self._pool) >= self.max_size:
                self._evict_oldest()

            conn = self._connection_factory(module_name, config_entry)
            self._pool[key] = (conn, now)
            return conn

    def _evict_expired(self, now):
        expired_keys = []
        for key, (conn, last_used) in self._pool.items():
            if self.ttl_seconds and (now - last_used) > self.ttl_seconds:
                expired_keys.append(key)
        for key in expired_keys:
            conn, _ = self._pool.pop(key, (None, None))
            if conn:
                self._disconnect(conn)

    def _evict_oldest(self):
        oldest_key = None
        oldest_ts = None
        for key, (_, last_used) in self._pool.items():
            if oldest_ts is None or last_used < oldest_ts:
                oldest_ts = last_used
                oldest_key = key
        if oldest_key is not None:
            conn, _ = self._pool.pop(oldest_key, (None, None))
            if conn:
                self._disconnect(conn)

    @staticmethod
    def _disconnect(conn):
        try:
            conn.disconnect()
        except Exception:
            pass

    @staticmethod
    def _conn_key(module_name, config_entry):
        password = config_entry.password
        if isinstance(password, list):
            password = tuple(password)
        return (
            module_name,
            config_entry.hostname,
            config_entry.port,
            config_entry.username,
            password,
            config_entry.credentials_file,
            config_entry.use_ssl,
            config_entry.no_ssl_certificate,
            config_entry.ssl_certificate_verify,
            config_entry.ssl_check_hostname,
            config_entry.ssl_ca_file,
            config_entry.plaintext_login,
        )
