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
from mktxp.flow.router_connection import RouterAPIConnectionError

class RouterEntriesHandler:
    ''' Handles RouterOS entries defined in MKTXP config 
    '''
    def __init__(self, module_names=None, config_overrides=None, connection_overrides=None):
        self._router_entries = {}
        self._module_names = module_names
        config_overrides = config_overrides or {}
        connection_overrides = connection_overrides or {}
        if isinstance(module_names, str):
            module_names = [module_names]

        entry_names = module_names if module_names is not None else config_handler.registered_entries()
        for router_name in entry_names:
            if not config_handler.registered_entry(router_name):
                continue
            if module_names is None and config_handler.config_entry(router_name).module_only:
                continue
            connection_override = connection_overrides.get(router_name)
            router_entry = RouterEntry(
                router_name,
                config_overrides.get(router_name),
                connection_override,
                keep_connection=bool(connection_override),
            )
            RouterEntriesHandler._set_child_entries(router_entry)
            self._router_entries[router_name] = router_entry

    @property
    def router_entries(self):
        if not self._router_entries:
            return None

        if self._module_names is None:
            return (entry for key, entry in self._router_entries.items()
                    if entry.config_entry.enabled and not entry.config_entry.module_only)

        return (entry for key, entry in self._router_entries.items() if entry.config_entry.enabled)

    @staticmethod
    def router_entry(entry_name, enabled_only = False):
        ''' A static router entry initialiser
        '''
        config_entry = config_handler.config_entry(entry_name)
        if enabled_only and not config_entry.enabled:
            return None

        router_entry = RouterEntry(entry_name)
        RouterEntriesHandler._set_child_entries(router_entry)
        try:
            router_entry.connect()
        except RouterAPIConnectionError as exc:
            print (f'{exc}')
        return router_entry

    @staticmethod
    def _set_child_entries(router_entry):
        if router_entry.config_entry.remote_dhcp_entry and config_handler.registered_entry(router_entry.config_entry.remote_dhcp_entry):
            router_entry.dhcp_entry = RouterEntry(router_entry.config_entry.remote_dhcp_entry)        
        else:
            remote_dhcp_entry_name = router_entry.config_entry.remote_dhcp_entry
            if remote_dhcp_entry_name != 'None':
                print(f"Error in configuration for {router_entry.router_name}: remote_dhcp_entry must a name of another router entry or 'None', but it is '{remote_dhcp_entry_name}'. Ignoring.")

        if router_entry.config_entry.remote_capsman_entry and config_handler.registered_entry(router_entry.config_entry.remote_capsman_entry):
            router_entry.capsman_entry = RouterEntry(router_entry.config_entry.remote_capsman_entry)       
        else:
            remote_capsman_entry_name = router_entry.config_entry.remote_capsman_entry
            if remote_capsman_entry_name != 'None':
                print(f"Error in configuration for {router_entry.router_name}: remote_capsman_entry must a name of another router entry or 'None', but it is '{remote_capsman_entry_name}'. Ignoring.")
