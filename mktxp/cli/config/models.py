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

from collections import namedtuple
from mktxp.cli.config.keys import MKTXPConfigKeys


class ConfigEntry:
    """Namedtuple definitions for Router and System configuration entries."""

    MKTXPConfigEntry = namedtuple(
        'MKTXPConfigEntry',
        [
            MKTXPConfigKeys.ENABLED_KEY,
            MKTXPConfigKeys.HOST_KEY,
            MKTXPConfigKeys.PORT_KEY,
            MKTXPConfigKeys.USER_KEY,
            MKTXPConfigKeys.PASSWD_KEY,
            MKTXPConfigKeys.CREDENTIALS_FILE_KEY,
            MKTXPConfigKeys.SSL_KEY,
            MKTXPConfigKeys.NO_SSL_CERTIFICATE,
            MKTXPConfigKeys.SSL_CERTIFICATE_VERIFY,
            MKTXPConfigKeys.SSL_CHECK_HOSTNAME,
            MKTXPConfigKeys.SSL_CA_FILE,
            MKTXPConfigKeys.PLAINTEXT_LOGIN_KEY,
            MKTXPConfigKeys.FE_DHCP_KEY,
            MKTXPConfigKeys.FE_ROUTERBOARD_KEY,
            MKTXPConfigKeys.FE_HEALTH_KEY,
            MKTXPConfigKeys.FE_PACKAGE_KEY,
            MKTXPConfigKeys.FE_DHCP_LEASE_KEY,
            MKTXPConfigKeys.FE_INTERFACE_KEY,
            MKTXPConfigKeys.FE_WG_PEER_KEY,
            MKTXPConfigKeys.FE_MONITOR_KEY,
            MKTXPConfigKeys.FE_W60G_KEY,
            MKTXPConfigKeys.FE_WIRELESS_KEY,
            MKTXPConfigKeys.FE_WIRELESS_CLIENTS_KEY,
            MKTXPConfigKeys.FE_IP_CONNECTIONS_KEY,
            MKTXPConfigKeys.FE_CONNECTION_STATS_KEY,
            MKTXPConfigKeys.FE_CONNECTION_STATS_DESTINATIONS_KEY,
            MKTXPConfigKeys.FE_CAPSMAN_KEY,
            MKTXPConfigKeys.FE_CAPSMAN_CLIENTS_KEY,
            MKTXPConfigKeys.FE_POE_KEY,
            MKTXPConfigKeys.FE_NETWATCH_KEY,
            MKTXPConfigKeys.FE_INTERFACE_NAME_FORMAT,
            MKTXPConfigKeys.FE_PUBLIC_IP_KEY,
            MKTXPConfigKeys.FE_ROUTE_KEY,
            MKTXPConfigKeys.FE_DHCP_POOL_KEY,
            MKTXPConfigKeys.FE_FIREWALL_KEY,
            MKTXPConfigKeys.FE_ADDRESS_LIST_KEY,
            MKTXPConfigKeys.FE_TOTAL_ADDRESS_LIST_COUNTS_KEY,
            MKTXPConfigKeys.FE_NEIGHBOR_KEY,
            MKTXPConfigKeys.FE_DNS_KEY,
            MKTXPConfigKeys.FE_IPV6_ROUTE_KEY,
            MKTXPConfigKeys.FE_IPV6_DHCP_POOL_KEY,
            MKTXPConfigKeys.FE_IPV6_FIREWALL_KEY,
            MKTXPConfigKeys.FE_IPV6_ADDRESS_LIST_KEY,
            MKTXPConfigKeys.FE_IPV6_TOTAL_ADDRESS_LIST_COUNTS_KEY,
            MKTXPConfigKeys.FE_IPV6_NEIGHBOR_KEY,
            MKTXPConfigKeys.FE_USER_KEY,
            MKTXPConfigKeys.FE_QUEUE_KEY,
            MKTXPConfigKeys.FE_REMOTE_DHCP_ENTRY,
            MKTXPConfigKeys.FE_REMOTE_CAPSMAN_ENTRY,
            MKTXPConfigKeys.FE_CHECK_FOR_UPDATES,
            MKTXPConfigKeys.FE_BFD_KEY,
            MKTXPConfigKeys.FE_BGP_KEY,
            MKTXPConfigKeys.FE_KID_CONTROL_DEVICE,
            MKTXPConfigKeys.FE_KID_CONTROL_DYNAMIC,
            MKTXPConfigKeys.FE_EOIP_KEY,
            MKTXPConfigKeys.FE_GRE_KEY,
            MKTXPConfigKeys.FE_IPIP_KEY,
            MKTXPConfigKeys.FE_LTE_KEY,
            MKTXPConfigKeys.FE_IPSEC_KEY,
            MKTXPConfigKeys.FE_SWITCH_PORT_KEY,
            MKTXPConfigKeys.FE_ROUTING_STATS_KEY,
            MKTXPConfigKeys.FE_CERTIFICATE_KEY,
            MKTXPConfigKeys.FE_CONTAINER_KEY,
            MKTXPConfigKeys.FE_BRIDGE_VLAN_KEY,
            MKTXPConfigKeys.FE_CUSTOM_LABELS_KEY,
            MKTXPConfigKeys.FE_MODULE_ONLY_KEY,
            MKTXPConfigKeys.FE_INTERFACE_WITH_DEFAULT_NAME,
        ],
    )

    MKTXPSystemEntry = namedtuple(
        'MKTXPSystemEntry',
        [
            MKTXPConfigKeys.PORT_KEY,
            MKTXPConfigKeys.LISTEN_KEY,
            MKTXPConfigKeys.MKTXP_SOCKET_TIMEOUT,
            MKTXPConfigKeys.MKTXP_INITIAL_DELAY,
            MKTXPConfigKeys.MKTXP_MAX_DELAY,
            MKTXPConfigKeys.MKTXP_INC_DIV,
            MKTXPConfigKeys.MKTXP_BANDWIDTH_KEY,
            MKTXPConfigKeys.MKTXP_VERBOSE_MODE,
            MKTXPConfigKeys.MKTXP_BANDWIDTH_TEST_INTERVAL,
            MKTXPConfigKeys.MKTXP_MIN_COLLECT_INTERVAL,
            MKTXPConfigKeys.MKTXP_FETCH_IN_PARALLEL,
            MKTXPConfigKeys.MKTXP_MAX_WORKER_THREADS,
            MKTXPConfigKeys.MKTXP_MAX_SCRAPE_DURATION,
            MKTXPConfigKeys.MKTXP_TOTAL_MAX_SCRAPE_DURATION,
            MKTXPConfigKeys.MKTXP_COMPACT_CONFIG,
            MKTXPConfigKeys.MKTXP_PROMETHEUS_HEADERS_DEDUPLICATION,
            MKTXPConfigKeys.MKTXP_PERSISTENT_ROUTER_CONNECTION_POOL,
            MKTXPConfigKeys.MKTXP_PERSISTENT_DHCP_CACHE,
            MKTXPConfigKeys.MKTXP_BANDWIDTH_TEST_DNS_SERVER,
            MKTXPConfigKeys.MKTXP_PROBE_CONNECTION_POOL,
            MKTXPConfigKeys.MKTXP_PROBE_CONNECTION_POOL_TTL,
            MKTXPConfigKeys.MKTXP_PROBE_CONNECTION_POOL_MAX_SIZE,
            MKTXPConfigKeys.MKTXP_HTTP_SERVER_THREADS,
        ],
    )


# Mock system entry to enable running tests and fallback before initialization
mockSystemEntry = ConfigEntry.MKTXPSystemEntry(
    port=MKTXPConfigKeys.DEFAULT_MKTXP_PORT,
    listen=f'0.0.0.0:{MKTXPConfigKeys.DEFAULT_MKTXP_PORT}',
    socket_timeout=MKTXPConfigKeys.DEFAULT_MKTXP_SOCKET_TIMEOUT,
    initial_delay_on_failure=MKTXPConfigKeys.DEFAULT_MKTXP_INITIAL_DELAY,
    max_delay_on_failure=MKTXPConfigKeys.DEFAULT_MKTXP_MAX_DELAY,
    delay_inc_div=MKTXPConfigKeys.DEFAULT_MKTXP_INC_DIV,
    bandwidth=False,
    verbose_mode=False,
    bandwidth_test_interval=MKTXPConfigKeys.DEFAULT_MKTXP_BANDWIDTH_TEST_INTERVAL,
    minimal_collect_interval=MKTXPConfigKeys.DEFAULT_MKTXP_MIN_COLLECT_INTERVAL,
    fetch_routers_in_parallel=False,
    max_worker_threads=MKTXPConfigKeys.DEFAULT_MKTXP_MAX_WORKER_THREADS,
    max_scrape_duration=MKTXPConfigKeys.DEFAULT_MKTXP_MAX_SCRAPE_DURATION,
    total_max_scrape_duration=MKTXPConfigKeys.DEFAULT_MKTXP_TOTAL_MAX_SCRAPE_DURATION,
    compact_default_conf_values=False,
    prometheus_headers_deduplication=False,
    persistent_router_connection_pool=True,
    persistent_dhcp_cache=True,
    bandwidth_test_dns_server=MKTXPConfigKeys.DEFAULT_MKTXP_BANDWIDTH_TEST_DNS_SERVER,
    probe_connection_pool=False,
    probe_connection_pool_ttl=MKTXPConfigKeys.DEFAULT_MKTXP_PROBE_CONNECTION_POOL_TTL,
    probe_connection_pool_max_size=MKTXPConfigKeys.DEFAULT_MKTXP_PROBE_CONNECTION_POOL_MAX_SIZE,
    http_server_threads=MKTXPConfigKeys.DEFAULT_MKTXP_HTTP_SERVER_THREADS,
)
