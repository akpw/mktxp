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


from mktxp.cli.config.config import config_handler
from mktxp.flow.router_entry import RouterEntry


class RouterEntriesHandler:
    ''' Handles RouterOS entries defined in MKTXP config 
    '''         
    def __init__(self):
        self.router_entries = []
        for router_name in config_handler.registered_entries():
            router_entry = RouterEntriesHandler.router_entry(router_name, enabled_only = True)
            if router_entry:                
                self.router_entries.append(router_entry)

    @staticmethod
    def router_entry(entry_name, enabled_only = False):
        router_entry = None
        
        for router_name in config_handler.registered_entries():
            if router_name == entry_name:
                config_entry = config_handler.config_entry(router_name)
                if enabled_only and not config_entry.enabled:
                        break
                        
                router_entry = RouterEntry(router_name)
                router_entry.dhcp_entry = RouterEntriesHandler.router_entry(config_entry.remote_dhcp_entry)
                break
        
        return router_entry
