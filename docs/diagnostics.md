# Live CLI Diagnostics (`mktxp diag`)

`mktxp diag` (alias: `mktxp print`) provides interactive visibility into MikroTik RouterOS devices directly in your terminal. It renders clean ASCII tables with domain-specific filtering, automatic MAC-to-hostname DHCP enrichment, human-readable bitrates, and activity durations.

---

## Table of Contents
- [Quick Reference](#quick-reference)
- [CLI Ergonomics & Scoped Help](#cli-ergonomics--scoped-help)
- [Diagnostic Domains](#diagnostic-domains)
  - [1. Wireless & CAPsMAN (`-wc`, `-cc`)](#1-wireless--capsman--wc--cc)
  - [2. DHCP Leases & Device Discovery (`-dc`)](#2-dhcp-leases--device-discovery--dc)
  - [3. IP Connection Tracking (`-cn`)](#3-ip-connection-tracking--cn)
  - [4. Firewall Address Lists (`-al`)](#4-firewall-address-lists--al)
  - [5. Bandwidth & Top Talkers (`-kc`)](#5-bandwidth--top-talkers--kc)
  - [6. Upstream & Netwatch Health (`-nw`)](#6-upstream--netwatch-health--nw)
  - [7. Ethernet & SFP Interface Monitor (`-im`)](#7-ethernet--sfp-interface-monitor--im)
- [General Pattern Filters (`-in`, `-ex`)](#general-pattern-filters--in--ex)
- [RouterOS Prerequisites & Permissions](#routeros-prerequisites--permissions)

---

## Quick Reference

| Command | Shortcut | Purpose | Primary Filters |
| :--- | :--- | :--- | :--- |
| `mktxp diag -wc` | `--wifi` | Standalone RouterOS v7 WiFi / WiFiWave2 clients | `--low-signal`, `--low-rate`, `--band`, `--recent` |
| `mktxp diag -cc` | `--caps` | CAPsMAN managed wireless clients across APs | `--low-signal`, `--low-rate`, `--band`, `--recent`, `-in` |
| `mktxp diag -dc` | `--dhcp` | DHCP server leases and rogue device auditing | `--unidentified`, `--dynamic`, `--active-only` |
| `mktxp diag -cn` | `--conn` | Open IP connection sockets per source host | `--top [N]`, `--min-conns [N]` |
| `mktxp diag -al` | `--addr` | Firewall address lists (IPv4 and IPv6) | `--dynamic-only`, `--static-only` |
| `mktxp diag -kc` | `--kid` | Real-time per-device bandwidth & LAN throughput | `--top [N]`, `--active`, `--rate-above [RATE]` |
| `mktxp diag -nw` | `--net` | Netwatch ICMP ping monitors & gateway checks | `--down-only`, `--up-only` |
| `mktxp diag -im` | `--interface` | Ethernet & SFP link status, PHY rates & optical DOM | `--degraded [RATE]`, `--plugged`, `--unplugged`, `--rate`, `--sfp-only` |

---

## CLI Ergonomics & Scoped Help

1. Prefix Matching: You don't have to type full flags. The options parser matches any unique initial prefix sequence—`--wifi`, `--caps`, `--dhcp`, `--conn`, `--kid`, `--addr`, `--net`, and `--interface` resolve cleanly.
2. Context-Aware Scoped Help: Appending `-h` to any domain narrows help down to the switches relevant to that command, printing active thresholds from your `_mktxp.conf` (see the [Configuration Guide](configuration.md#3-diag--live-diagnostics-thresholds) to tune defaults):
   ```bash
   ❯ mktxp diag -en ROUTER -kc -h
   ```
3. Transparent Alias: `mktxp print` remains available as an alias for `mktxp diag`.
4. Global Config Directory Override: Use `--cfg-dir <path>` to run diagnostics against isolated or staging router inventories (`mktxp.conf`, `_mktxp.conf`, and `secrets.yml`):
   ```bash
   ❯ mktxp --cfg-dir /path/to/custom diag -en ROUTER -wc
   ```

---

## Diagnostic Domains

### 1. Wireless & CAPsMAN (`-wc`, `-cc`)

Inspects wireless associations, grouping records by AP interface with automatic separators and client counts.

Available Filters:
- `--low-signal [dBm]`: Filter clients with weak signal (default: `<= -75 dBm`)
- `--min-signal [dBm]`: Filter clients with strong signal (default: `>= -60 dBm`)
- `--low-rate [rate]`: Filter clients with low negotiated PHY rate (e.g. `1M`, `18M`)
- `--recent [duration]`: Filter newly joined clients (e.g. `15m`, `1h`)
- `--band [2g|5g|6g]`: Filter clients by frequency band

Examples:

```bash
# Pinpoint sticky clients on distant APs with weak signal and bottom-tier rates
❯ mktxp diag -en ROUTER -cc --low-signal --low-rate 1M
```

```text
+----------------------+--------------+-------------------+-----------+------------------+--------+---------+---------+---------+
|      dhcp_name       | dhcp_address |    mac_address    | rx_signal |    interface     |  ssid  | tx_rate | rx_rate | uptime  |
+======================+==============+===================+===========+==================+========+=========+=========+=========+
| wlan0 (Conf Printer) | 10.20.10.49  | D8:1F:12:AD:3C:55 |    -87    | AP-Breakroom-2G  | Office | 36 Mbps | 1 Mbps  | 6 hours |
| wlan0 (Sales Laptop) | 10.20.10.53  | D8:1F:12:AD:32:00 |    -87    | AP-Breakroom-2G  | Office | 11 Mbps | 1 Mbps  | 3 hours |
|                      |              |                   |           |                  |        |         |         |         |
| wlan0 (Boardroom Tab)| 10.20.10.97  | 10:5A:17:0C:B9:C8 |    -84    | AP-Reception-2G  | Office | 24 Mbps | 1 Mbps  |  a day  |
+----------------------+--------------+-------------------+-----------+------------------+--------+---------+---------+---------+
AP-Breakroom-2G clients: 2
AP-Reception-2G clients: 1
Matching CAPsMAN clients: 3 (Total connected: 127)
```

```bash
# Locate one known device: AP, SSID, interface, and leased IP
❯ mktxp diag -en ROUTER -cc -in "Boardroom Tab"

# Find newly joined clients still using the 2.4 GHz band
❯ mktxp diag -en ROUTER -cc --band 2g --recent 15m
```

---

### 2. DHCP Leases & Device Discovery (`-dc`)

Queries DHCP server lease tables to identify active clients, stale assignments, and unidentified devices.

Available Filters:
- `--unidentified`: Show mystery devices with no DHCP hostname and no comment (falls back to displaying MAC address)
- `--dynamic` / `--static`: Filter dynamic vs. static lease configurations
- `--active-only` / `--inactive-only`: Show online/active devices vs. stale/waiting leases

Examples:

```bash
# Surface mystery devices plugged into the network
❯ mktxp diag -en ROUTER -dc --unidentified
```

```text
+-------------------+---------+-------------------+--------------+----------------+---------------+
|     host_name     | server  |    mac_address    |   address    | active_address | expires_after |
+===================+=========+===================+==============+================+===============+
| 70:EE:50:AA:BB:CC | defconf | 70:EE:50:AA:BB:CC | 10.20.10.189 | 10.20.10.189   | 11h 22m       |
| 94:E6:86:DD:EE:FF | defconf | 94:E6:86:DD:EE:FF | 10.20.10.204 | 10.20.10.204   | 8h 05m        |
+-------------------+---------+-------------------+--------------+----------------+---------------+
defconf clients: 2
Matching DHCP clients: 2 (Total: 46)
```

---

### 3. IP Connection Tracking (`-cn`)

Aggregates active firewall connections per source IP to spot infected hosts, heavy BitTorrent clients, or socket exhaustion.

Available Filters:
- `--top [N]`: Show top N connection holders (default: `10`)
- `--min-conns [N]`: Filter out background hosts with fewer than N active connections

*(Note: Destination addresses are displayed when `connection_stats_destinations = True` is enabled in `mktxp.conf`.)*

Example:

```bash
❯ mktxp diag -en ROUTER -cn --top 3
```

```text
+----------------------+--------------+------------------+------------------------------------+
|      dhcp_name       | src_address  | connection_count |           dst_addresses            |
+======================+==============+==================+====================================+
| Workstation-Pro      | 10.20.10.88  |       482        | 198.51.100.1, 203.0.113.50, ...    |
|                      |              |                  |                                    |
| Apple-TV (Living Rm) | 10.20.10.145 |       118        | 198.51.100.25, 203.0.113.88, ...   |
|                      |              |                  |                                    |
| Home-Server          | 10.20.10.50  |        94        | 198.51.100.10, 192.0.2.14, ...     |
+----------------------+--------------+------------------+------------------------------------+
Matching source addresses: 3 (Total: 42)
Matching open connections: 694 (Total: 1170)
```

---

### 4. Firewall Address Lists (`-al`)

Inspects dynamic and static firewall address lists across IPv4 and IPv6 simultaneously.

Available Filters:
- `--dynamic-only`: Show temporary dynamic bans (e.g. brute-force honeypots, port-knock drops) with remaining timeouts
- `--static-only`: Show permanent configured entries

Example:

```bash
# Verify active dynamic threat drop lists
❯ mktxp diag -en ROUTER -al blacklist,port_scanners --dynamic-only
```

```text
Address Lists (IPv4):
+---------------+---------------+--------------------+----------+---------+----------+
|     list      |    address    |      comment       | timeout  | dynamic | disabled |
+===============+===============+====================+==========+=========+==========+
| blacklist     | 198.51.100.42 | SSH brute force    | 23:48:12 |   Yes   |    No    |
| blacklist     | 203.0.113.19  | Port knock scanner | 14:12:05 |   Yes   |    No    |
| port_scanners | 192.0.2.77    | TCP SYN probe      | 01:05:44 |   Yes   |    No    |
+---------------+---------------+--------------------+----------+---------+----------+
Matching entries: 3 (Total: 48)
Unique lists: 2
```

---

### 5. Bandwidth & Top Talkers (`-kc`)

Pulls RouterOS Kid Control counters, translates them into human-readable bitrates, and calculates aggregate LAN throughput on the fly.

> 💡 Tip: Using Kid Control as a Passive LAN Monitor  
> MikroTik RouterOS does not natively track per-device real-time transfer rates (`rate_up`, `rate_down`), cumulative volume, or activity recency (`idle_time`) anywhere else without custom firewall mangle rules.  
> You can repurpose Kid Control as an automated, passive LAN monitor without blocking or restricting traffic:
> 1. In RouterOS, create a single 24/7 unlimited user profile to activate packet accounting:
>    ```routeros
>    /ip kid-control add name=DeviceMonitor mon=0s-1d tue=0s-1d wed=0s-1d thu=0s-1d fri=0s-1d sat=0s-1d sun=0s-1d
>    ```
> 2. RouterOS will automatically discover and track all connected devices under `/ip kid-control device`.
> 3. Run `mktxp diag -kc --top 5` or `mktxp diag -kc --active` to view top talkers and live LAN throughput.

Available Filters:
- `--top [N]`: Show top N talkers flattened into a global leaderboard by combined transfer rate ($Tx + Rx$, default: `10`)
- `--active`: Show devices with non-zero active throughput only
- `--rate-above [RATE]`: Filter devices exceeding bandwidth threshold (e.g. `2M`, `500k`)
- `--dynamic-only` / `--static-only`: Filter auto-discovered dynamic entries vs. manually added static Kid Control entries
- `--unassigned`: Show devices not assigned to any specific user profile

Example:

```bash
# Surface top 5 talkers with active throughput
❯ mktxp diag -en ROUTER -kc --top 5
```

```text
+----------------------+-----------------+------+--------------+-------------------+---------------+-----------+-----------+-----------+
|      dhcp_name       |      name       | user | dhcp_address |    mac_address    |  ip_address   |  rate_up  | rate_down | idle_time |
+======================+=================+======+==============+===================+===============+===========+===========+===========+
| Apple-TV (Living Rm) | Apple-TV-Living |      | 10.20.10.145 | 40:A1:08:12:34:56 | 10.20.10.145  | 1.1 Mbps  | 23.7 Mbps | 2 seconds |
| Workstation-Pro      | Workstation-Pro | Alex | 10.20.10.88  | 3C:06:30:AB:CD:EF | 10.20.10.88   | 180 kbps  | 4.1 Mbps  | 5 seconds |
| Kid-Tablet           | Kid-Tablet      | Kids | 10.20.10.210 | 74:83:C2:55:66:77 | 10.20.10.210  | 45 kbps   | 2.1 Mbps  | 12 seconds|
| Laptop-Guest         | Laptop-Guest    |      | 10.20.10.199 | B8:27:EB:11:22:33 | 10.20.10.199  | 12 kbps   | 520 kbps  | 30 seconds|
| Smart-TV-Office      | Smart-TV-Office |      | 10.20.10.160 | 50:C7:BF:88:99:AA | 10.20.10.160  | 8 kbps    | 310 kbps  | 1 minute  |
+----------------------+-----------------+------+--------------+-------------------+---------------+-----------+-----------+-----------+
Active LAN Traffic: 1.3 Mbps Up / 30.7 Mbps Down
Top 5 Kid Control devices by rate (Matching: 18, Total: 18)
```

---

### 6. Upstream & Netwatch Health (`-nw`)

Monitors RouterOS Netwatch ICMP probe targets for WAN gateway and DNS availability.

Available Filters:
- `--down-only`: Show unreachable or failing probe targets
- `--up-only`: Show passing / reachable targets

Example:

```bash
❯ mktxp diag -en ROUTER -nw --down-only
```

```text
Netwatch Entries:
+-----------+---------+-------------------+--------+------+----------+---------+----------+
|   name    |  host   |      comment      | status | type |  since   | timeout | interval |
+===========+=========+===================+========+======+==========+=========+==========+
| gw-backup | 1.1.1.1 | Cloudflare Backup |  Down  | icmp | 00:14:32 | 1000ms  |   10s    |
+-----------+---------+-------------------+--------+------+----------+---------+----------+
Matching entries: 1 (Total: 6)
Up: 0
Down: 1
```

---

### 7. Ethernet & SFP Interface Monitor (`-im`)

Monitors physical Ethernet and SFP port link status (`Plugged-In` vs `Unplugged`), negotiated PHY data rates (`1 Gbps`, `100 Mbps`, `10 Gbps`), duplex, auto-negotiation, and optical transceiver DOM diagnostics.

Available Filters:
- `--degraded [RATE]`: Instantly surfaces active/linked ports operating below the sub-rate threshold (default: `< 100M`, configurable in `_mktxp.conf`) or at half-duplex—the classic "bad cable / damaged pair" detector. Can also be set to a custom threshold (e.g. `--degraded 1G` to isolate sub-gigabit links).
- `--plugged`: Show only active/linked ports (`status: link-ok`).
- `--unplugged`: Show only disconnected ports (`status: no-link`).
- `--rate [RATE]`: Filter by exact negotiated rate (e.g. `100M`, `1G`, `10G`, `2.5G`).
- `--rate-below [RATE]`: Filter ports with negotiated rate below threshold (e.g. `1G`).
- `--sfp-only`: Isolate SFP/QSFP ports and render detailed optical transceiver DOM diagnostics (Rx/Tx optical power levels, temperature, connector types).

Examples:

```bash
# Audit all switch and router ports
❯ mktxp diag -en ROUTER -im
```

```text
Interface Monitor:
+------------------------+------------+----------+--------+----------+---------------------+
|       Interface        |   Status   |   Rate   | Duplex | Auto-Neg |         SFP         |
+========================+============+==========+========+==========+=====================+
| INet Provider          | Plugged-In | 100 Mbps |  Full  |   Done   | -                   |
| ether2                 | Plugged-In | 1 Gbps   |  Full  |   Done   | -                   |
| SMLIGHT SLZB-06        | Plugged-In | 100 Mbps |  Full  |   Done   | -                   |
| QNAP                   | Plugged-In | 1 Gbps   |  Full  |   Done   | -                   |
| Eufy Base              | Plugged-In | 100 Mbps |  Full  |   Done   | -                   |
| AKP-MB (Ubuntu)        | Plugged-In | 1 Gbps   |  Full  |   Done   | -                   |
| Trunk to MKT-LR        | Plugged-In | 1 Gbps   |  Full  |   Done   | -                   |
| Trunk (GMKTec K8+)     | Plugged-In | 1 Gbps   |  Full  |   Done   | -                   |
| ether9 (Damaged Cable) | Plugged-In | 10 Mbps  |  Half  |   Done   | -                   |
| sfp-sfpplus1           | Unplugged  | -        | -      | -        | -                   |
| sfp-sfpplus2           | Plugged-In | 10 Gbps  |  Full  |   Done   | SFP+ (MikroTik)     |
| PxProvision (GMKTec)   | Plugged-In | 1 Gbps   |  Full  |   Done   | -                   |
| Trunk MKT-Switch (Wi)  | Plugged-In | 1 Gbps   |  Full  |   Done   | -                   |
+------------------------+------------+----------+--------+----------+---------------------+
Total interfaces: 13
Plugged: 12
Unplugged: 1
Degraded (< 100M): 1
```

```bash
# Pinpoint degraded cables or ports negotiating down below 100 Mbps or running half-duplex
❯ mktxp diag -en ROUTER -im --degraded
```

```text
Interface Monitor:
+------------------------+------------+---------+--------+----------+-----+
|       Interface        |   Status   |  Rate   | Duplex | Auto-Neg | SFP |
+========================+============+=========+========+==========+=====+
| ether9 (Damaged Cable) | Plugged-In | 10 Mbps |  Half  |   Done   | -   |
+------------------------+------------+---------+--------+----------+-----+
Matching interfaces: 1 (Total: 13)
Plugged: 1
Unplugged: 0
Degraded (< 100M): 1
```

```bash
# Surface all sub-gigabit links (< 1 Gbps) across the device
❯ mktxp diag -en ROUTER -im --degraded 1G
```

```text
Interface Monitor:
+------------------------+------------+----------+--------+----------+-----+
|       Interface        |   Status   |   Rate   | Duplex | Auto-Neg | SFP |
+========================+============+==========+========+==========+=====+
| INet Provider          | Plugged-In | 100 Mbps |  Full  |   Done   | -   |
| SMLIGHT SLZB-06        | Plugged-In | 100 Mbps |  Full  |   Done   | -   |
| Eufy Base              | Plugged-In | 100 Mbps |  Full  |   Done   | -   |
| ether9 (Damaged Cable) | Plugged-In | 10 Mbps  |  Half  |   Done   | -   |
+------------------------+------------+----------+--------+----------+-----+
Matching interfaces: 4 (Total: 13)
Plugged: 4
Unplugged: 0
Degraded (< 1G): 4
```

```bash
# Inspect optical transceivers and DOM light levels
❯ mktxp diag -en ROUTER -im --sfp-only
```

```text
SFP Interface Monitor:
+--------------+------------+---------+-------------+---------------------+-----------+----------+----------+-------+
|  Interface   |   Status   |  Rate   |    Type     |    Vendor / Part    | Connector | Rx Power | Tx Power | Temp  |
+==============+============+=========+=============+=====================+===========+==========+==========+=======+
| sfp-sfpplus1 | Unplugged  | -       | -           | -                   | -         | -        | -        | -     |
| sfp-sfpplus2 | Plugged-In | 10 Gbps | SFP-or-SFP+ | MikroTik S+85DLC03D |    LC     | -5.2 dBm | -2.1 dBm | 42 °C |
+--------------+------------+---------+-------------+---------------------+-----------+----------+----------+-------+
Total SFP interfaces: 2
Plugged: 1
Unplugged: 1
```

---

## General Pattern Filters (`-in`, `-ex`)

Every diagnostic domain accepts general pattern matching:
- `-in, --include`: Semicolon-separated patterns. Matches if ANY pattern matches ANY field in the record.
- `-ex, --exclude`: Semicolon-separated patterns. Excludes record if ANY pattern matches.

Wildcards (`*`, `?`) are supported:
```bash
# Inspect only 5 GHz CAPsMAN clients on office APs
❯ mktxp diag -en ROUTER -cc -in "AP-Office*;5G"

# Exclude guest networks from DHCP analysis
❯ mktxp diag -en ROUTER -dc -ex "guest;iot"
```

---

## RouterOS Prerequisites & Permissions

For diagnostic queries to succeed, ensure the router user has minimal required permissions:
```routeros
/user group add name=mktxp_group policy=api,read
/user add name=mktxp_user group=mktxp_group password=your_password
```

*(Note: For LTE metrics on RouterOS v6, the user also needs the `test` permission policy.)*
