# coding=utf8
## Copyright (c) 2026 Arseniy Kuznetsov
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

from mktxp.rsc.ast import RSCConfig
from .base import BaseMiddleware


class Sanitizer(BaseMiddleware):
    """
    Sanitizes dynamic hardware artifacts or volatile parameters that cause false-positive Git diffs.
    """

    def __init__(self, strip_dynamic_macs: bool = False):
        self.strip_dynamic_macs = strip_dynamic_macs

    def process(self, config: RSCConfig) -> RSCConfig:
        if not self.strip_dynamic_macs:
            return config

        for section in config.sections:
            if section.path.strip() == '/interface bridge':
                for cmd in section.commands:
                    # Strip auto/dynamic mac address if auto-mac is yes
                    if cmd.params.get('auto-mac') == 'yes' and 'mac-address' in cmd.params:
                        del cmd.params['mac-address']

        return config
