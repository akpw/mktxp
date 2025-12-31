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
from mktxp.flow.router_entry import RouterEntry, RouterEntryWirelessType


class ProbeRouterEntry(RouterEntry):
    def __init__(self, router_name, config_entry, api_connection=None, keep_connection=False):
        super().__init__(router_name)
        self.config_entry = config_entry
        self.api_connection = api_connection or RouterAPIConnection(router_name, self.config_entry)
        self._keep_connection = keep_connection
        self.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS] = self.config_entry.hostname

    def is_done(self):
        if self._keep_connection:
            if not config_handler.system_entry.persistent_dhcp_cache:
                self._dhcp_records = {}
            self._wireless_type = RouterEntryWirelessType.NONE
            return

        super().is_done()
