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


class RouterAPIConnectionError(Exception):
    pass


class RouterAPIConnection:
    ''' Base wrapper interface for the routeros_api library
    '''            
    def __init__(self, router_name, router_entry):
        self.router_name = router_name
        self.router_entry  = router_entry
        
        ctx = None
        if self.router_entry.use_ssl and not self.router_entry.ssl_certificate:
            ctx = ssl.create_default_context()
            ctx.set_ciphers('ADH:@SECLEVEL=0')       

        self.connection = RouterOsApiPool(
                host = self.router_entry.hostname,
                username = self.router_entry.username,
                password = self.router_entry.password,
                port = self.router_entry.port,
                plaintext_login = True,
                use_ssl = self.router_entry.use_ssl,
                ssl_context = ctx)
        
        self.connection.socket_timeout = 2
        self.api = None

    def is_connected(self):
        if not (self.connection and self.connection.connected and self.api):
            return False
        try:
            self.api.get_resource('/system/identity').get()
            return True
        except (socket.error, socket.timeout, Exception) as ex:
            print(f'Connection to router {self.router_name}@{self.router_entry.hostname} has been lost: {ex}')
            self.api = None
            return False

    def connect(self):
        if self.is_connected():
            return
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            print(f'Connecting to router {self.router_name}@{self.router_entry.hostname}')
            self.api = self.connection.get_api()
            print(f'{current_time} Connection to router {self.router_name}@{self.router_entry.hostname} has been established')
        except (socket.error, socket.timeout, Exception) as ex:
            print(f'{current_time} Connection to router {self.router_name}@{self.router_entry.hostname} has failed: {ex}')
            raise 

    def router_api(self):
        if not self.is_connected():
            self.connect()
        return self.api
