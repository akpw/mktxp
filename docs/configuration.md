# MKTXP Configuration Guide

MKTXP uses two configuration files to cleanly separate router inventory from system daemon and workflow settings:

- `mktxp.conf`: Router definitions, credentials, connection parameters, custom labels, and metrics collection switches.
- `_mktxp.conf`: System daemon settings (`[MKTXP]`), GitOps formatting rules (`[RSC]`), and interactive CLI diagnostic thresholds (`[DIAG]`).

---

## Configuration File Locations & Resolution

MKTXP automatically resolves configuration files in the following order:

1. XDG Standard Directory (Recommended):
   - `$XDG_CONFIG_HOME/mktxp/` (defaults to `~/.config/mktxp/`)
   - Files: `~/.config/mktxp/mktxp.conf` and `~/.config/mktxp/_mktxp.conf`
2. System-wide / Container Directory:
   - `/etc/mktxp/`
   - Files: `/etc/mktxp/mktxp.conf` and `/etc/mktxp/_mktxp.conf`
3. Legacy Home Directory:
   - `~/mktxp/`
   - Files: `~/mktxp/mktxp.conf` and `~/mktxp/_mktxp.conf`

> 💡 Migration Tip: To migrate from the legacy `~/mktxp/` directory to the modern XDG standard:
> ```bash
> mv ~/mktxp ~/.config/mktxp
> ```

---

## Managing Configuration via CLI

MKTXP provides built-in commands to inspect and edit your configuration files:

```bash
# Print resolved configuration file paths
❯ mktxp show -cfg
MKTXP data config: /Users/username/.config/mktxp/mktxp.conf
MKTXP internal config: /Users/username/.config/mktxp/_mktxp.conf

# List all configured router profiles and their active parameters
❯ mktxp show

# Inspect a specific router profile
❯ mktxp show Core-Router

# Open mktxp.conf (router configuration) in your system's default editor ($EDITOR)
❯ mktxp edit

# Open _mktxp.conf (system, GitOps, and diagnostic configuration) in your default editor
❯ mktxp edit -i

# Open either file using a specific editor
❯ mktxp edit -ed nano
❯ mktxp edit -i -ed vim
```

---

## Router Configuration (`mktxp.conf`)

`mktxp.conf` uses INI format and consists of individual router sections and an optional `[default]` section.

### Minimal Router Entry

```ini
[Core-Router]
    hostname = 192.168.88.1
    username = mktxp_user
    password = secret_password
```

### The `[default]` Section & Inheritance

Parameters defined under `[default]` apply to all configured routers unless explicitly overridden in a router's individual section:

```ini
[default]
    username = mktxp_user
    password = global_secret_password
    port = 8728
    use_ssl = False
    interface = True
    wireless = True
    dhcp = True

[Core-Router]
    hostname = 192.168.88.1
    custom_labels = dc:lon1, rack:a1, role:gateway

[Edge-AP]
    hostname = 192.168.88.2
    wireless_clients = True
    custom_labels = dc:lon1, rack:b3, role:access-point
```

### Connection & Authentication Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `hostname` | String | `localhost` | IP address or FQDN of the RouterOS device. |
| `port` | Integer | `8728` | RouterOS API port (`8728` for plaintext, `8729` for SSL). |
| `username` | String | `username` | RouterOS user with `api` and `read` permissions. |
| `password` | String | `password` | Password for the monitoring user. |
| `credentials_file` | String | `""` | Path to an external YAML file containing `username` and `password`. |
| `enabled` | Boolean | `True` | Enables or disables metrics collection for this device. |
| `module_only` | Boolean | `False` | When `True`, skips default `/metrics` scraping; device is used exclusively as a probe module via `/probe`. |
| `use_ssl` | Boolean | `False` | Connect via RouterOS API-SSL service (port 8729). |
| `no_ssl_certificate`| Boolean | `False` | Connect via API-SSL without validating router SSL certificate. |
| `ssl_certificate_verify` | Boolean | `False` | Verify SSL certificate against CA store. |
| `ssl_check_hostname`| Boolean | `True` | Verify that router hostname matches certificate hostname. |
| `ssl_ca_file` | String | `""` | Path to custom CA certificate bundle (leave empty for system store). |
| `plaintext_login` | Boolean | `True` | Use post-6.43 plaintext authentication handshake (set to `False` for legacy ROS < 6.43). |

### Custom Labels & Naming

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `custom_labels` | String | `None` | Comma-separated `key:value` or `key=value` pairs attached to all metrics emitted for this router (e.g. `dc:london, rack=a1, service:prod`). |
| `interface_name_format` | String | `name` | Format for interface labels: `'name'` (e.g. `ether1`), `'comment'` (comment with fallback to name), or `'combined'` (e.g. `ether1 (Uplink)`). |
| `interface_with_default_name` | Boolean | `False` | Appends `default_name` label to interface metrics. |

### Metrics Collection Switches

Enable or disable specific metric collectors per router or globally under `[default]`:

| Switch | Default | Domain / Metric Group |
| :--- | :--- | :--- |
| `health` | `True` | System health (voltage, temperature, board stats). |
| `installed_packages` | `True` | Installed RouterOS packages and versions. |
| `routerboard` | `False` | RouterBOARD model, serial number, and firmware status. |
| `user` | `True` | Active management sessions and users. |
| `certificate` | `False` | X.509 certificate expiry and status. |
| `container` | `False` | RouterOS container runtime stats (ROS v7+). |
| `check_for_updates` | `False` | Checks for available RouterOS software upgrades. |
| `interface` | `True` | Interface traffic, packets, errors, and link status. |
| `monitor` | `True` | Interface monitor statistics (rates, duplex, flow control). |
| `bridge_vlan` | `False` | Bridge VLAN table and untagged/tagged port mappings. |
| `switch_port` | `False` | Switch chip port counters and statistics. |
| `poe` | `True` | PoE output wattage, current, and port status. |
| `route` / `ipv6_route` | `True` / `False` | Active routing table route counts. |
| `pool` / `ipv6_pool` | `True` / `False` | IP address pool utilization and counts. |
| `firewall` / `ipv6_firewall` | `True` / `False` | Firewall filter and NAT rule byte/packet counters. |
| `neighbor` / `ipv6_neighbor` | `True` / `False` | ARP and IPv6 neighbor discovery counts. |
| `address_list` / `ipv6_address_list` | `None` | Comma-separated list of firewall address-lists to track specifically. |
| `total_address_list_counts` | `True` | Emit aggregate entry counts across all address lists. |
| `dhcp` / `dhcp_lease` | `True` | DHCP server statistics and active lease details. |
| `connections` | `True` | Active IP connection tracking totals. |
| `connection_stats` | `False` | Detailed TCP/UDP/ICMP connection breakdowns. |
| `connection_stats_destinations` | `False` | Tracks per-destination IP/port traffic (*Caution: High Cardinality*). |
| `wireless` / `wireless_clients` | `True` | Legacy WLAN interface stats and connected station details. |
| `capsman` / `capsman_clients` | `True` | CAPsMAN controller status and connected client stats. |
| `w60g` | `False` | 60 GHz wireless link alignment and signal quality. |
| `wireguard_peers` | `False` | WireGuard peer handshake, transfer, and endpoint metrics. |
| `netwatch` | `True` | Netwatch host probe status and response intervals. |
| `kid_control_assigned` | `False` | Kid Control traffic metrics for devices with assigned users. |
| `kid_control_dynamic` | `False` | Kid Control traffic metrics for all devices. |
| `public_ip` | `True` | Public WAN IP detection. |
| `queue` | `True` | Simple queue and tree queue bandwidth utilization. |
| `bfd` / `bgp` | `False` | BFD and BGP routing protocol peering states. |
| `routing_stats` | `False` | Routing engine process statistics. |
| `eoip` / `gre` / `ipip` / `ipsec` | `False` | Tunnel interface states and IPSec active peers. |
| `lte` | `False` | Cellular LTE signal strength and modem parameters. |
| `remote_dhcp_entry` | `None` | Name of a configured router to use as a remote DHCP lease resolver. |
| `remote_capsman_entry` | `None` | Name of a configured router to use as a remote CAPsMAN controller resolver. |

---

## System Configuration (`_mktxp.conf`)

`_mktxp.conf` controls daemon-level behavior, GitOps AST transformations, and CLI diagnostic thresholds across three distinct sections:

### 1. `[MKTXP]` — Daemon & Exporter Settings

```ini
[MKTXP]
    # Sockets to bind to (IPv4 and IPv6 supported)
    listen = '0.0.0.0:49090 [::1]:49090'
    socket_timeout = 5

    # Failure backoff delays (seconds)
    initial_delay_on_failure = 120
    max_delay_on_failure = 900
    delay_inc_div = 5

    # Periodic bandwidth testing
    bandwidth = False
    bandwidth_test_dns_server = 8.8.8.8
    bandwidth_test_interval = 600

    # Scrape concurrency and timeouts
    fetch_routers_in_parallel = False
    max_worker_threads = 5
    max_scrape_duration = 30
    total_max_scrape_duration = 90
    http_server_threads = 16

    # Connection pooling and caching
    persistent_router_connection_pool = True
    persistent_dhcp_cache = True
    compact_default_conf_values = False
    prometheus_headers_deduplication = False

    # Multi-target /probe connection pool
    probe_connection_pool = False
    probe_connection_pool_ttl = 300
    probe_connection_pool_max_size = 128
```

#### Key Daemon Settings Explained:
- `listen`: Space-separated list of socket addresses. Wildcards and simultaneous IPv4/IPv6 binding are fully supported.
- `fetch_routers_in_parallel`: When scraping many routers, enable this to fetch metrics concurrently using worker threads rather than sequentially.
- `max_scrape_duration` & `total_max_scrape_duration`: Bound individual and total collection times to avoid Prometheus scrape timeouts.
- `compact_default_conf_values`: Automatically compacts `mktxp.conf` so only non-default values are preserved on router sections.
- `probe_connection_pool`: Reuses open API connections for incoming `/probe` requests keyed by `module + target`.

---

### 2. `[RSC]` — GitOps RSC Settings & Custom Handlers

```ini
[RSC]
    base_dir = './exports'
    numbered_files = True
    wrap_lines = False
    wrap_column = 80
    extract_scripts = False
    strip_mac_addresses = False
    ssh_port = 22
    ssh_timeout = 15
    show_sensitive = False

    handler_order = base, wifi, system, ip, dhcp-leases, firewall, lte, wireguard

    handler_base = /interface bridge, /interface ethernet, /interface vlan, /interface list, /interface macvlan, /interface ovpn-server
    handler_wifi = /caps-man, /interface wifi, /interface wireless
    handler_system = /system, /user, /certificate, /zerotier, /ppp, /queue, /snmp, /interface l2tp-server, /interface sstp-server, /ip smb, /ip neighbor discovery-settings, /ip settings, /ipv6 settings, /ip ipsec, /ip service, /ip ssh, /ipv6 nd, /routing bfd, /routing bgp, /routing ospf, /tool bandwidth-server, /tool mac-server, /tool romon, /tool e-mail, /tool netwatch, /tool traffic-monitor, /app, /ip kid-control, /caps-man access-list
    handler_dhcp-leases = /ip dhcp-server lease
    handler_ip = /ip address, /ipv6 address, /ip pool, /ipv6 pool, /ip dhcp-client, /ip dhcp-server, /ipv6 dhcp-client, /ipv6 dhcp-server, /ip dns, /ip route, /ipv6 route, /ip cloud, /routing table, /routing rule
    handler_firewall = /ip firewall, /ipv6 firewall
    handler_lte = /interface lte, /tool sms
    handler_wireguard = /interface wireguard
```

#### Custom Handlers & Extensibility:
You can introduce new domain files without modifying Python code:
1. Add the domain name to `handler_order` (e.g. append `bgp`).
2. Define matching paths under `handler_<name>`:
   ```ini
   handler_bgp = /routing bgp, /routing bfd, /routing filter, /routing ospf
   ```
The engine automatically routes those command blocks into `09-bgp.rsc`. Any unmatched paths are cleanly routed to `99-other.rsc`.

---

### 3. `[DIAG]` — Live Diagnostics Thresholds

```ini
[DIAG]
    # Wireless & CAPsMAN thresholds
    low_signal_threshold = -75          # Default dBm threshold for --low-signal (matches <= -75 dBm)
    min_signal_threshold = -60          # Default dBm threshold for --min-signal (matches >= -60 dBm)
    low_rate_threshold = '18M'          # Default rate for --low-rate (matches <= 18 Mbps)
    recent_duration = '15m'             # Default duration for --recent (matches uptime <= 15m)

    # IP Connections & Bandwidth thresholds
    top_connections_count = 10          # Default limit for connection stats --top
    rate_above_threshold = '1M'         # Default rate for kid control / bandwidth --rate-above
```

Values set here serve as the runtime defaults when running `mktxp diag` commands without explicit CLI thresholds (e.g. `mktxp diag -cc --low-signal`). Appending `-h` to any diagnostic command displays the currently active threshold loaded from this section.

---

## Docker & Container Deployment

The official MKTXP container image runs as non-root UID 1000 and resolves configuration from `/etc/mktxp`:

### Option 1: Mount Dedicated Config Directory (Recommended)

```bash
mkdir mktxp-config
nano mktxp-config/mktxp.conf     # Configure your routers
nano mktxp-config/_mktxp.conf    # (Optional) Tune system parameters

docker run -d \
  --name mktxp \
  -p 49090:49090 \
  -v "$(pwd)/mktxp-config:/etc/mktxp" \
  ghcr.io/akpw/mktxp:latest
```

### Option 2: Mount Single Router Config File

If only `mktxp.conf` is mounted, MKTXP will automatically create default internal system settings:

```bash
docker run -d \
  --name mktxp \
  -p 49090:49090 \
  -v "$(pwd)/mktxp.conf:/etc/mktxp/mktxp.conf" \
  ghcr.io/akpw/mktxp:latest
```

> ⚠️ Docker Swarm Tip: In Docker Swarm or read-only container filesystems, always provide **both** `mktxp.conf` and `_mktxp.conf` explicitly to prevent initialization errors when the container attempts to create missing config files on a read-only filesystem.
