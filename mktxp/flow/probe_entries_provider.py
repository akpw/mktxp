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

from mktxp.flow.probe_router_entry import ProbeRouterEntry
from mktxp.flow.router_entries_handler import RouterEntriesHandler


class ProbeEntriesProvider:
    def __init__(self, module_name, config_entry, connection_pool=None):
        self.module_name = module_name
        self.config_entry = config_entry
        self.connection_pool = connection_pool

    @property
    def router_entries(self):
        entry = self._build_entry()
        return (router for router in (entry,))

    def _build_entry(self):
        connection = None
        keep_connection = False
        if self.connection_pool:
            connection = self.connection_pool.get(self.module_name, self.config_entry)
            keep_connection = True

        entry = ProbeRouterEntry(
            self.module_name,
            self.config_entry,
            api_connection=connection,
            keep_connection=keep_connection,
        )
        RouterEntriesHandler._set_child_entries(entry)
        return entry
