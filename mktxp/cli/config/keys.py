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


class CollectorKeys:
    IDENTITY_COLLECTOR = 'IdentityCollector'
    SYSTEM_RESOURCE_COLLECTOR = 'SystemResourceCollector'
    ROUTERBOARD_COLLECTOR = 'RouterboardCollector'
    HEALTH_COLLECTOR = 'HealthCollector'
    PUBLIC_IP_ADDRESS_COLLECTOR = 'PublicIPAddressCollector'
    NEIGHBOR_COLLECTOR = 'NeighborCollector'
    DNS_COLLECTOR = 'DNSCollector'
    PACKAGE_COLLECTOR = 'PackageCollector'
    DHCP_COLLECTOR = 'DHCPCollector'
    POOL_COLLECTOR = 'PoolCollector'
    IP_CONNECTION_COLLECTOR = 'IPConnectionCollector'
    BRIDGE_VLAN_COLLECTOR = 'BridgeVlanCollector'
    INTERFACE_COLLECTOR = 'InterfaceCollector'
    WG_PEER_COLLECTOR = 'WireGuardPeerCollector'
    FIREWALL_COLLECTOR = 'FirewallCollector'
    MONITOR_COLLECTOR = 'MonitorCollector'
    W60G_COLLECTOR = 'W60gCollector'
    POE_COLLECTOR = 'POECollector'
    NETWATCH_COLLECTOR = 'NetwatchCollector'
    ROUTE_COLLECTOR = 'RouteCollector'
    WLAN_COLLECTOR = 'WLANCollector'
    CAPSMAN_COLLECTOR = 'CapsmanCollector'
    QUEUE_TREE_COLLECTOR = 'QueueTreeCollector'
    QUEUE_SIMPLE_COLLECTOR = 'QueueSimpleCollector'
    KID_CONTROL_DEVICE_COLLECTOR = 'KidControlCollector'
    USER_COLLECTOR = 'UserCollector'
    BFD_COLLECTOR = 'BFDCollector'
    BGP_COLLECTOR = 'BGPCollector'
    ROUTING_STATS_COLLECTOR = 'RoutingStatsCollector'
    EOIP_COLLECTOR = 'EOIPCollector'
    GRE_COLLECTOR = 'GRECollector'
    IPIP_COLLECTOR = 'IPIPCollector'
    IPSEC_COLLECTOR = 'IPSecCollector'
    ADDRESS_LIST_COLLECTOR = 'AddressListCollector'
    LTE_COLLECTOR = 'LTECollector'
    SWITCH_PORT_COLLECTOR = 'SwitchPortCollector'
    MKTXP_COLLECTOR = 'MKTXPCollector'
    CERTIFICATE_COLLECTOR = 'CertificateCollector'
    CONTAINER_COLLECTOR = "ContainerCollector"


class MKTXPConfigKeys:
    """MKTXP config file keys and constants"""

    # Section Keys
    ENABLED_KEY = 'enabled'
    HOST_KEY = 'hostname'
    PORT_KEY = 'port'
    LISTEN_KEY = 'listen'
    USER_KEY = 'username'
    PASSWD_KEY = 'password'
    CREDENTIALS_FILE_KEY = 'credentials_file'

    SSL_KEY = 'use_ssl'
    NO_SSL_CERTIFICATE = 'no_ssl_certificate'
    SSL_CERTIFICATE_VERIFY = 'ssl_certificate_verify'
    SSL_CHECK_HOSTNAME = 'ssl_check_hostname'
    SSL_CA_FILE = 'ssl_ca_file'
    PLAINTEXT_LOGIN_KEY = 'plaintext_login'

    FE_ROUTERBOARD_KEY = 'routerboard'
    FE_HEALTH_KEY = 'health'
    FE_PACKAGE_KEY = 'installed_packages'
    FE_DHCP_KEY = 'dhcp'
    FE_DHCP_LEASE_KEY = 'dhcp_lease'
    FE_IP_CONNECTIONS_KEY = 'connections'
    FE_CONNECTION_STATS_KEY = 'connection_stats'
    FE_CONNECTION_STATS_DESTINATIONS_KEY = 'connection_stats_destinations'
    FE_INTERFACE_KEY = 'interface'
    FE_INTERFACE_WITH_DEFAULT_NAME = 'interface_with_default_name'
    FE_WG_PEER_KEY = 'wireguard_peers'

    FE_ROUTE_KEY = 'route'
    FE_DHCP_POOL_KEY = 'pool'
    FE_FIREWALL_KEY = 'firewall'
    FE_ADDRESS_LIST_KEY = 'address_list'
    FE_TOTAL_ADDRESS_LIST_COUNTS_KEY = 'total_address_list_counts'
    FE_NEIGHBOR_KEY = 'neighbor'
    FE_DNS_KEY = 'dns'

    FE_IPV6_ROUTE_KEY = 'ipv6_route'
    FE_IPV6_DHCP_POOL_KEY = 'ipv6_pool'
    FE_IPV6_FIREWALL_KEY = 'ipv6_firewall'
    FE_IPV6_ADDRESS_LIST_KEY = 'ipv6_address_list'
    FE_IPV6_TOTAL_ADDRESS_LIST_COUNTS_KEY = 'ipv6_total_address_list_counts'
    FE_IPV6_NEIGHBOR_KEY = 'ipv6_neighbor'

    FE_MONITOR_KEY = 'monitor'
    FE_W60G_KEY = 'w60g'
    FE_WIRELESS_KEY = 'wireless'
    FE_WIRELESS_CLIENTS_KEY = 'wireless_clients'
    FE_CAPSMAN_KEY = 'capsman'
    FE_CAPSMAN_CLIENTS_KEY = 'capsman_clients'
    FE_POE_KEY = 'poe'
    FE_PUBLIC_IP_KEY = 'public_ip'
    FE_NETWATCH_KEY = 'netwatch'

    FE_EOIP_KEY = 'eoip'
    FE_GRE_KEY = 'gre'
    FE_IPIP_KEY = 'ipip'
    FE_IPSEC_KEY = 'ipsec'
    FE_LTE_KEY = "lte"
    FE_SWITCH_PORT_KEY = "switch_port"
    FE_BRIDGE_VLAN_KEY = "bridge_vlan"

    FE_USER_KEY = 'user'
    FE_QUEUE_KEY = 'queue'
    FE_BFD_KEY = 'bfd'
    FE_BGP_KEY = 'bgp'

    FE_REMOTE_DHCP_ENTRY = 'remote_dhcp_entry'
    FE_REMOTE_CAPSMAN_ENTRY = 'remote_capsman_entry'

    FE_CHECK_FOR_UPDATES = 'check_for_updates'

    FE_KID_CONTROL_DEVICE = 'kid_control_assigned'
    FE_KID_CONTROL_DYNAMIC = 'kid_control_dynamic'

    FE_CONTAINER_KEY = 'container'

    FE_CERTIFICATE_KEY = 'certificate'
    FE_ROUTING_STATS_KEY = 'routing_stats'
    FE_CUSTOM_LABELS_KEY = 'custom_labels'
    FE_MODULE_ONLY_KEY = 'module_only'

    MKTXP_SOCKET_TIMEOUT = 'socket_timeout'
    MKTXP_INITIAL_DELAY = 'initial_delay_on_failure'
    MKTXP_MAX_DELAY = 'max_delay_on_failure'
    MKTXP_INC_DIV = 'delay_inc_div'
    MKTXP_BANDWIDTH_KEY = 'bandwidth'
    MKTXP_BANDWIDTH_TEST_INTERVAL = 'bandwidth_test_interval'
    MKTXP_VERBOSE_MODE = 'verbose_mode'
    MKTXP_MIN_COLLECT_INTERVAL = 'minimal_collect_interval'
    MKTXP_FETCH_IN_PARALLEL = 'fetch_routers_in_parallel'
    MKTXP_MAX_WORKER_THREADS = 'max_worker_threads'
    MKTXP_MAX_SCRAPE_DURATION = 'max_scrape_duration'
    MKTXP_TOTAL_MAX_SCRAPE_DURATION = 'total_max_scrape_duration'
    MKTXP_COMPACT_CONFIG = 'compact_default_conf_values'
    MKTXP_PROMETHEUS_HEADERS_DEDUPLICATION = 'prometheus_headers_deduplication'
    MKTXP_PERSISTENT_ROUTER_CONNECTION_POOL = 'persistent_router_connection_pool'
    MKTXP_PERSISTENT_DHCP_CACHE = 'persistent_dhcp_cache'
    MKTXP_BANDWIDTH_TEST_DNS_SERVER = 'bandwidth_test_dns_server'
    MKTXP_HTTP_SERVER_THREADS = 'http_server_threads'
    MKTXP_PROBE_CONNECTION_POOL = 'probe_connection_pool'
    MKTXP_PROBE_CONNECTION_POOL_TTL = 'probe_connection_pool_ttl'
    MKTXP_PROBE_CONNECTION_POOL_MAX_SIZE = 'probe_connection_pool_max_size'

    # UnRegistered entries placeholder
    NO_ENTRIES_REGISTERED = 'NoEntriesRegistered'

    MKTXP_USE_COMMENTS_OVER_NAMES = 'use_comments_over_names'  # Legacy option, deprecated
    FE_INTERFACE_NAME_FORMAT = 'interface_name_format'

    # Base router id labels
    ROUTERBOARD_NAME = 'routerboard_name'
    ROUTERBOARD_ADDRESS = 'routerboard_address'

    # Injected custom labels metadata ID
    CUSTOM_LABELS_METADATA_ID = '__custom__labels__metadata_id__'

    # Default values
    DEFAULT_HOST_KEY = 'localhost'
    DEFAULT_USER_KEY = 'user'
    DEFAULT_PASSWORD_KEY = 'password'
    DEFAULT_CREDENTIALS_FILE_KEY = ""

    DEFAULT_SSL_CA_FILE = ""

    DEFAULT_API_PORT = 8728
    DEFAULT_API_SSL_PORT = 8729
    DEFAULT_FE_REMOTE_DHCP_ENTRY = 'None'
    DEFAULT_FE_REMOTE_CAPSMAN_ENTRY = 'None'
    DEFAULT_FE_ADDRESS_LIST_KEY = 'None'
    DEFAULT_FE_IPV6_ADDRESS_LIST_KEY = 'None'
    DEFAULT_FE_CUSTOM_LABELS_KEY = 'None'
    DEFAULT_FE_INTERFACE_NAME_FORMAT = 'name'

    DEFAULT_MKTXP_PORT = 49090
    DEFAULT_MKTXP_SOCKET_TIMEOUT = 2
    DEFAULT_MKTXP_INITIAL_DELAY = 120
    DEFAULT_MKTXP_MAX_DELAY = 900
    DEFAULT_MKTXP_INC_DIV = 5
    DEFAULT_MKTXP_BANDWIDTH_TEST_INTERVAL = 420
    DEFAULT_MKTXP_MIN_COLLECT_INTERVAL = 5
    DEFAULT_MKTXP_MAX_WORKER_THREADS = 5
    DEFAULT_MKTXP_MAX_SCRAPE_DURATION = 10
    DEFAULT_MKTXP_TOTAL_MAX_SCRAPE_DURATION = 30
    DEFAULT_MKTXP_BANDWIDTH_TEST_DNS_SERVER = "8.8.8.8"
    DEFAULT_MKTXP_HTTP_SERVER_THREADS = 16
    DEFAULT_MKTXP_PROBE_CONNECTION_POOL_TTL = 300
    DEFAULT_MKTXP_PROBE_CONNECTION_POOL_MAX_SIZE = 128

    BOOLEAN_KEYS_NO = {
        ENABLED_KEY, SSL_KEY, NO_SSL_CERTIFICATE, FE_CHECK_FOR_UPDATES,
        FE_KID_CONTROL_DEVICE, FE_KID_CONTROL_DYNAMIC, FE_WG_PEER_KEY,
        FE_ROUTERBOARD_KEY, SSL_CERTIFICATE_VERIFY, FE_IPV6_ROUTE_KEY,
        FE_IPV6_DHCP_POOL_KEY, FE_IPV6_FIREWALL_KEY, FE_IPV6_NEIGHBOR_KEY,
        FE_CONNECTION_STATS_KEY, FE_CONNECTION_STATS_DESTINATIONS_KEY,
        FE_BFD_KEY, FE_BGP_KEY, FE_EOIP_KEY, FE_GRE_KEY, FE_IPIP_KEY,
        FE_IPSEC_KEY, FE_LTE_KEY, FE_SWITCH_PORT_KEY, FE_ROUTING_STATS_KEY,
        FE_CERTIFICATE_KEY, FE_DNS_KEY, FE_CONTAINER_KEY, FE_W60G_KEY,
        FE_MODULE_ONLY_KEY, FE_BRIDGE_VLAN_KEY, FE_INTERFACE_WITH_DEFAULT_NAME
    }

    # Feature keys enabled by default
    BOOLEAN_KEYS_YES = {
        PLAINTEXT_LOGIN_KEY, FE_DHCP_KEY, FE_HEALTH_KEY, FE_PACKAGE_KEY,
        FE_DHCP_LEASE_KEY, FE_IP_CONNECTIONS_KEY, FE_INTERFACE_KEY,
        FE_ROUTE_KEY, FE_DHCP_POOL_KEY, FE_FIREWALL_KEY,
        FE_TOTAL_ADDRESS_LIST_COUNTS_KEY, FE_NEIGHBOR_KEY, FE_MONITOR_KEY,
        SSL_CHECK_HOSTNAME, FE_WIRELESS_KEY, FE_WIRELESS_CLIENTS_KEY,
        FE_CAPSMAN_KEY, FE_CAPSMAN_CLIENTS_KEY, FE_POE_KEY,
        FE_NETWATCH_KEY, FE_PUBLIC_IP_KEY, FE_USER_KEY, FE_QUEUE_KEY,
        FE_IPV6_TOTAL_ADDRESS_LIST_COUNTS_KEY
    }

    SYSTEM_BOOLEAN_KEYS_YES = {MKTXP_PERSISTENT_ROUTER_CONNECTION_POOL, MKTXP_PERSISTENT_DHCP_CACHE}
    SYSTEM_BOOLEAN_KEYS_NO = {
        MKTXP_BANDWIDTH_KEY, MKTXP_VERBOSE_MODE, MKTXP_FETCH_IN_PARALLEL,
        MKTXP_COMPACT_CONFIG, MKTXP_PROMETHEUS_HEADERS_DEDUPLICATION,
        MKTXP_PROBE_CONNECTION_POOL
    }

    STR_KEYS = (
        HOST_KEY, USER_KEY, PASSWD_KEY, CREDENTIALS_FILE_KEY, SSL_CA_FILE,
        FE_REMOTE_DHCP_ENTRY, FE_REMOTE_CAPSMAN_ENTRY, FE_ADDRESS_LIST_KEY,
        FE_IPV6_ADDRESS_LIST_KEY, FE_CUSTOM_LABELS_KEY, FE_INTERFACE_NAME_FORMAT
    )
    MKTXP_STR_KEYS = (MKTXP_BANDWIDTH_TEST_DNS_SERVER,)
    INT_KEYS = ()
    MKTXP_INT_KEYS = (
        PORT_KEY, MKTXP_SOCKET_TIMEOUT, MKTXP_INITIAL_DELAY, MKTXP_MAX_DELAY,
        MKTXP_INC_DIV, MKTXP_BANDWIDTH_TEST_INTERVAL, MKTXP_MIN_COLLECT_INTERVAL,
        MKTXP_MAX_WORKER_THREADS, MKTXP_MAX_SCRAPE_DURATION, MKTXP_TOTAL_MAX_SCRAPE_DURATION,
        MKTXP_PROBE_CONNECTION_POOL_TTL, MKTXP_PROBE_CONNECTION_POOL_MAX_SIZE,
        MKTXP_HTTP_SERVER_THREADS
    )

    # MKTXP configs entry names
    DEFAULT_ENTRY_KEY = 'default'
    MKTXP_LATEST_DEFAULT_ENTRY_KEY = 'new_default_parameters'
    MKTXP_CONFIG_ENTRY_NAME = 'MKTXP'
    MKTXP_LATEST_SYSTEM_ENTRY_KEY = 'new_system_parameters'
