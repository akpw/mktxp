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


from mktxp.cli.config.config import config_handler, MKTXPConfigKeys
from mktxp.flow.router_connection import RouterAPIConnection


class RouterEntry:
    ''' RouterOS Entry
    '''                 
    def __init__(self, router_name):
        self.router_name = router_name
        self.config_entry  = config_handler.config_entry(router_name)
        self.api_connection = RouterAPIConnection(router_name, self.config_entry)
        self.router_id = {
            MKTXPConfigKeys.ROUTERBOARD_NAME: self.router_name,
            MKTXPConfigKeys.ROUTERBOARD_ADDRESS: self.config_entry.hostname
            }
        self.time_spent =  { 'IdentityCollector': 0,
                            'SystemResourceCollector': 0,
                            'HealthCollector': 0,
                            'DHCPCollector': 0,
                            'PoolCollector': 0,
                            'InterfaceCollector': 0,
                            'FirewallCollector': 0,
                            'MonitorCollector': 0,
                            'POECollector': 0,
                            'NetwatchCollector': 0,
                            'RouteCollector': 0,
                            'WLANCollector': 0,
                            'CapsmanCollector': 0,
                            'MKTXPCollector': 0
                            }            
