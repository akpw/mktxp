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

from typing import List, Dict, Optional
from mktxp.rsc.ast import SectionNode
from .base import BaseHandler
from .configured import ConfiguredHandler
from .fallback import DefaultHandler


DEFAULT_HANDLER_ORDER = [
    'base',
    'wifi',
    'system',
    'ip',
    'dhcp-leases',
    'firewall',
    'routing',
    'lte',
    'wireguard'
]

DEFAULT_HANDLER_CONFIG: Dict[str, List[str]] = {
    'handler_base': [
        '/interface bridge',
        '/interface ethernet',
        '/interface vlan',
        '/interface list',
        '/interface macvlan',
        '/interface ovpn-server'
    ],
    'handler_wifi': [
        '/caps-man',
        '/interface wifi',
        '/interface wireless'
    ],
    'handler_system': [
        '/system',
        '/user',
        '/certificate',
        '/zerotier',
        '/ppp',
        '/queue',
        '/snmp',
        '/interface l2tp-server',
        '/interface sstp-server',
        '/interface ovpn-server',
        '/ip smb',
        '/ip neighbor discovery-settings',
        '/ip settings',
        '/ipv6 settings',
        '/ip ipsec',
        '/ip service',
        '/ip ssh',
        '/ipv6 nd',
        '/routing bfd',
        '/routing bgp',
        '/routing ospf',
        '/tool bandwidth-server',
        '/tool mac-server',
        '/tool romon',
        '/tool e-mail',
        '/tool netwatch',
        '/tool traffic-monitor',
        '/app',
        '/ip kid-control',
        '/caps-man access-list'
    ],
    'handler_dhcp-leases': [
        '/ip dhcp-server lease'
    ],
    'handler_dhcp_leases': [
        '/ip dhcp-server lease'
    ],
    'handler_ip': [
        '/ip address',
        '/ipv6 address',
        '/ip pool',
        '/ipv6 pool',
        '/ip dhcp-client',
        '/ip dhcp-server',
        '/ipv6 dhcp-client',
        '/ipv6 dhcp-server',
        '/ip dns',
        '/ip route',
        '/ipv6 route',
        '/ip cloud',
        '/routing table',
        '/routing rule'
    ],
    'handler_firewall': [
        '/ip firewall',
        '/ipv6 firewall'
    ],
    'handler_routing': [
        '/routing'
    ],
    'handler_lte': [
        '/interface lte',
        '/tool sms'
    ],
    'handler_wireguard': [
        '/interface wireguard'
    ]
}


class HandlerChain:
    """
    Builds and executes the Chain of Responsibility for AST sections.
    """

    def __init__(self, handler_order: Optional[List[str]] = None, handler_config: Optional[Dict[str, List[str]]] = None):
        self.handler_order = handler_order or list(DEFAULT_HANDLER_ORDER)
        self.handler_config = handler_config or dict(DEFAULT_HANDLER_CONFIG)
        self.handlers: List[BaseHandler] = self._build_chain()

    def _build_chain(self) -> List[BaseHandler]:
        handlers: List[BaseHandler] = []

        for idx, name in enumerate(self.handler_order, start=1):
            config_key = f"handler_{name}"
            patterns = self.handler_config.get(config_key, [])
            if isinstance(patterns, str):
                patterns = [p.strip() for p in patterns.split(',') if p.strip()]
            handler = ConfiguredHandler(name=name, patterns=patterns, index=idx)
            handlers.append(handler)

        # Add fallback handler at the end
        default_handler = DefaultHandler(name='other', index=99)
        handlers.append(default_handler)

        # Link chain
        for i in range(len(handlers) - 1):
            handlers[i].next_handler = handlers[i + 1]

        return handlers

    def match_handler(self, path: str) -> BaseHandler:
        """
        Finds the handler with the most specific (longest) matching pattern for the given path.
        If multiple handlers have the same specificity, preserves the configured handler_order.
        """
        best_handler = None
        best_match_len = -1
        best_order_idx = 999999

        for order_idx, handler in enumerate(self.handlers):
            for pattern in handler.patterns:
                p = pattern.strip()
                norm = path.strip()
                if norm == p or norm.startswith(p + ' ') or norm.startswith(p + '/'):
                    match_len = len(p)
                    # Prefer longer match (specificity); tie-break with handler order index
                    if match_len > best_match_len or (match_len == best_match_len and order_idx < best_order_idx):
                        best_handler = handler
                        best_match_len = match_len
                        best_order_idx = order_idx

        return best_handler or self.handlers[-1]

    def process_sections(self, sections: List[SectionNode]) -> List[BaseHandler]:
        for section in sections:
            handler = self.match_handler(section.path)
            handler.claimed_sections.append(section)

        # Return only handlers that have claimed sections
        return [h for h in self.handlers if h.claimed_sections]
