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
import collections
from datetime import datetime
from mktxp.cli.config.config import config_handler
import functools
import yaml

# Fix UTF-8 decode error
# See: https://github.com/akpw/mktxp/issues/47
# The RouterOS-api implicitly assumes that the API response is UTF-8 encoded.
# But Mikrotik uses latin-1.
# Because the upstream dependency is currently abandoned, this is a quick hack to solve the issue

MIKROTIK_ENCODING = 'latin-1'
import routeros_api.api_structure

def _decode_bytes(bytes_to_decode):
    try:
        return bytes_to_decode.decode('utf-8')
    except UnicodeDecodeError:
        return bytes_to_decode.decode(MIKROTIK_ENCODING)

routeros_api.api_structure.StringField.get_python_value = lambda _, bytes:  _decode_bytes(bytes)
routeros_api.api_structure.default_structure = collections.defaultdict(routeros_api.api_structure.StringField)

from routeros_api import RouterOsApiPool

class RouterAPIConnectionError(Exception):
    pass

def check_connected(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_connected():
            raise RouterAPIConnectionError(f'No network connection to router: {self.router_name}@{self.config_entry.hostname}')
        else:
            return func(self, *args, **kwargs)
    return wrapper

class RouterAPIConnection:
    ''' Base wrapper interface for the routeros_api library
    '''            
    def __init__(self, router_name, config_entry):
        self.router_name = router_name
        self.config_entry = config_entry
        self.last_failure_timestamp = self.successive_failure_count = 0
        
        ctx = None
        if self.config_entry.use_ssl:
            ctx = ssl.create_default_context(
                cafile=self.config_entry.ssl_ca_file if self.config_entry.ssl_ca_file else None
            )
            if self.config_entry.no_ssl_certificate:
                ctx.check_hostname = False
                ctx.set_ciphers('ADH:@SECLEVEL=0')
            elif not self.config_entry.ssl_certificate_verify:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            else:
                ctx.check_hostname = self.config_entry.ssl_check_hostname
                ctx.verify_mode = ssl.CERT_REQUIRED

        username = self.config_entry.username
        password = self.config_entry.password
        if self.config_entry.credentials_file:
            with open(self.config_entry.credentials_file, 'r') as file:
                try:
                    credentials = yaml.safe_load(file)
                    if not isinstance(credentials, dict):
                        raise yaml.YAMLError("Credentials file is not a valid key-value map.")
                except yaml.YAMLError as e:
                    print(f"Error parsing credentials file: {e}\nCheck that it is valid YAML (e.g., 'username: user').")
                    exit(1)                    
                username = credentials.get('username', username)
                password = credentials.get('password', password)

        self.connection = RouterOsApiPool(
                host = self.config_entry.hostname,
                username = username,
                password = password,
                port = self.config_entry.port,
                plaintext_login = True,
                ssl_context = ctx)
        
        self.connection.socket_timeout = config_handler.system_entry.socket_timeout
        self.api = None
    
    def is_connected(self):
        if self.connection and self.connection.connected and self.api:
            return True
        return False

    def connect(self):
        connect_time = datetime.now()
        if self.is_connected() or self._in_connect_timeout(connect_time.timestamp()):
            return
        try:
            print(f'Connecting to router {self.router_name}@{self.config_entry.hostname}')
            if self.config_entry.use_ssl and self.config_entry.no_ssl_certificate:
                print(f'Warning: API_SSL connect without router SSL certificate is insecure and should not be used in production environments!')
            self.connection.plaintext_login = self.config_entry.plaintext_login
            self.api = self.connection.get_api()
            self._set_connect_state(success = True, connect_time = connect_time)
        except (socket.error, socket.timeout, Exception) as exc:
            self._set_connect_state(success = False, connect_time = connect_time, exc = exc)
            raise RouterAPIConnectionError(f'Failed attemp to establish network connection to router: {self.router_name}@{self.config_entry.hostname}')

    def disconnect(self):
        if self.is_connected():
            self.connection.disconnect()
            self.api = None

    @check_connected
    def router_api(self):
        return self.api

    def _in_connect_timeout(self, connect_timestamp):
        connect_delay = self._connect_delay()
        if (connect_timestamp - self.last_failure_timestamp) < connect_delay:
            if config_handler.system_entry.verbose_mode: 
                print(f'{self.router_name}@{self.config_entry.hostname}: in connect timeout, {int(connect_delay - (connect_timestamp - self.last_failure_timestamp))}secs remaining')
                print(f'Successive failure count: {self.successive_failure_count}')
            return True
        if config_handler.system_entry.verbose_mode: 
            print(f'{self.router_name}@{self.config_entry.hostname}: OK to connect')
            if self.last_failure_timestamp > 0:
                print(f'Seconds since last failure: {connect_timestamp - self.last_failure_timestamp}')
                print(f'Prior successive failure count: {self.successive_failure_count}')
        return False

    def _connect_delay(self):
        mktxp_entry = config_handler.system_entry
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
