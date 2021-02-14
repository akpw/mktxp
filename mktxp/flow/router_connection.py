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


import ssl
import socket
from datetime import datetime
from routeros_api import RouterOsApiPool
from mktxp.cli.config.config import config_handler


class RouterAPIConnectionError(Exception):
    pass


class RouterAPIConnection:
    ''' Base wrapper interface for the routeros_api library
    '''            
    def __init__(self, router_name, config_entry):
        self.router_name = router_name
        self.config_entry = config_entry
        self.last_failure_timestamp = self.successive_failure_count = 0
        
        ctx = None
        if self.config_entry.use_ssl and self.config_entry.no_ssl_certificate:
            ctx = ssl.create_default_context()
            ctx.set_ciphers('ADH:@SECLEVEL=0')       

        self.connection = RouterOsApiPool(
                host = self.config_entry.hostname,
                username = self.config_entry.username,
                password = self.config_entry.password,
                port = self.config_entry.port,
                plaintext_login = True,
                use_ssl = self.config_entry.use_ssl,
                ssl_verify = self.config_entry.ssl_certificate_verify,
                ssl_context = ctx)
        
        self.connection.socket_timeout = config_handler.system_entry().socket_timeout
        self.api = None

    def is_connected(self):
        if not (self.connection and self.connection.connected and self.api):
            return False
        try:
            self.api.get_resource('/system/identity').get()
            return True
        except (socket.error, socket.timeout, Exception) as exc:
            self._set_connect_state(success = False, exc = exc)
            return False

    def connect(self):
        connect_time = datetime.now()
        if self.is_connected() or self._in_connect_timeout(connect_time.timestamp()):
            return
        try:
            print(f'Connecting to router {self.router_name}@{self.config_entry.hostname}')
            self.api = self.connection.get_api()
            self._set_connect_state(success = True, connect_time = connect_time)
        except (socket.error, socket.timeout, Exception) as exc:
            self._set_connect_state(success = False, connect_time = connect_time, exc = exc)
            #raise RouterAPIConnectionError

    def router_api(self):
        if not self.is_connected():
            self.connect()
        return self.api

    def _in_connect_timeout(self, connect_timestamp, quiet = True):
        connect_delay = self._connect_delay()
        if (connect_timestamp - self.last_failure_timestamp) < connect_delay:
            if not quiet: 
                print(f'{self.router_name}@{self.config_entry.hostname}: in connect timeout, {int(connect_delay - (connect_timestamp - self.last_failure_timestamp))}secs remaining')
                print(f'Successive failure count: {self.successive_failure_count}')
            return True
        if not quiet: 
            print(f'{self.router_name}@{self.config_entry.hostname}: OK to connect')
            if self.last_failure_timestamp > 0:
                print(f'Seconds since last failure: {connect_timestamp - self.last_failure_timestamp}')
                print(f'Prior successive failure count: {self.successive_failure_count}')
        return False

    def _connect_delay(self):
        mktxp_entry = config_handler.system_entry()
        connect_delay = (1 + self.successive_failure_count / mktxp_entry.delay_inc_div) * mktxp_entry.initial_delay_on_failure
        return connect_delay if connect_delay < mktxp_entry.max_delay_on_failure else mktxp_entry.max_delay_on_failure


    def _set_connect_state(self, success = False, connect_time = datetime.now(), exc = None):
        if success:
            self.last_failure_timestamp = 0
            self.successive_failure_count = 0
            print(f'{connect_time.strftime("%Y-%m-%d %H:%M:%S")} Connection to router {self.router_name}@{self.config_entry.hostname} has been established')
        else:
            self.api = None
            self.successive_failure_count += 1
            self.last_failure_timestamp = connect_time.timestamp() 
            print(f'{connect_time.strftime("%Y-%m-%d %H:%M:%S")} Connection to router {self.router_name}@{self.config_entry.hostname} has failed: {exc}')









