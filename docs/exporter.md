# Prometheus Metrics Exporter (`mktxp export`)

`mktxp export` is a production-grade metrics daemon for MikroTik RouterOS devices. It connects to configured routers via the RouterOS API, collects device health and network performance counters, performs DHCP address resolution and metric enrichment, and serves Prometheus-formatted telemetry over HTTP on default port `49090`.

---

## Table of Contents
- [Quick Start](#quick-start)
- [Grafana Dashboard Integration](#grafana-dashboard-integration)
- [Configuration Reference](#configuration-reference)
  - [Minimal Router Entry](#minimal-router-entry)
  - [Canonical Template](#canonical-template)
  - [System Settings (`_mktxp.conf`)](#system-settings-_mktxpconf)
- [Prometheus Scrape Configuration](#prometheus-scrape-configuration)
- [Multi-Target Exporter Pattern (`/probe`)](#multi-target-exporter-pattern-probe)
- [Production Daemon Deployments](#production-daemon-deployments)
  - [Docker & Docker Compose](#docker--docker-compose)
  - [Kubernetes](#kubernetes)
  - [Linux `systemd` Service](#linux-systemd-service)
  - [FreeBSD Service](#freebsd-service)
- [Companion Monitoring Stack](#companion-monitoring-stack)

---

## Quick Start

1. Start the exporter daemon:
   ```bash
   ❯ mktxp export
   ```
2. Verify metrics are being served:
   ```bash
   ❯ curl http://localhost:49090/metrics
   ```

---

## Grafana Dashboard Integration

MKTXP includes an official, turnkey [Grafana Dashboard (ID: 13679)](https://grafana.com/grafana/dashboards/13679):

<img width="32%" alt="Traffic & Interface" src="https://user-images.githubusercontent.com/5028474/217029083-3c2f561e-853f-45a7-b9f1-d818a830daf5.png"> <img width="32%" alt="Wireless Clients" src="https://user-images.githubusercontent.com/5028474/217029092-2b86b41b-1f89-4383-ac48-16652e820f7e.png"> <img width="32%" alt="Device Health" src="https://user-images.githubusercontent.com/5028474/217029096-dbf6b46c-3ed7-4c76-a57b-8cebfb3b671c.png">

The dashboard provides out-of-the-box panels for:
- WAN and LAN interface traffic, error rates, and packet loss
- Wireless client registrations, signal levels (RSSI), and negotiated rates
- System resource monitoring (CPU load, memory, voltage, temperature)
- DHCP active lease tracking and DNS request statistics
- IP connection tracking socket count and active host accounting
- Firewall rule traffic and address-list counters

---

## Configuration Reference

### Minimal Router Entry

At minimum, each router entry in `mktxp.conf` needs connection credentials:

```ini
[Core-Router]
    hostname = 192.168.88.1
    username = mktxp_user
    password = secret_password
```

### Canonical Template

To view or customize the comprehensive list of metrics collected by MKTXP (including PoE, BGP, WireGuard, LTE, Kid Control, and bridge VLANs), refer to the canonical template:
- [`mktxp/cli/config/mktxp.conf`](../mktxp/cli/config/mktxp.conf) in this repository.
- Edit locally using `mktxp edit`.

### System Settings (`_mktxp.conf`)

Tune daemon-level parameters with `mktxp edit -i`:
```ini
[MKTXP]
    listen = 0.0.0.0:49090          # Listen address (IPv4 and IPv6)
    socket_timeout = 2               # Socket connection timeout in seconds
    initial_delay_on_failure = 120   # Backoff delay when router is unreachable
    max_delay_on_failure = 900
    bandwidth = False                # Built-in periodic bandwidth testing
    compact_default_conf_values = True
```

> 📖 *For the complete configuration reference, multi-router `[default]` inheritance, parallel scraping, and Docker deployment, see the [Configuration Guide](configuration.md).*

---

## Prometheus Scrape Configuration

Add MKTXP to your `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'mktxp'
    static_configs:
      - targets: ['mktxp_host_ip:49090']
```

---

## Multi-Target Exporter Pattern (`/probe`)

For large or dynamic infrastructure, MKTXP supports Prometheus dynamic target discovery via `/probe`:

1. Define a probe module in `mktxp.conf`:
   ```ini
   [router-module]
       module_only = True
       username = mktxp_user
       password = secret_password
   ```

2. Configure Prometheus relabeling:
   ```yaml
   scrape_configs:
     - job_name: 'mktxp-multi-target'
       metrics_path: /probe
       params:
         module: [router-module]
       static_configs:
         - targets:
           - 192.168.88.1
           - 192.168.88.2
       relabel_configs:
         - source_labels: [__address__]
           target_label: __param_target
         - source_labels: [__param_target]
           target_label: instance
         - target_label: __address__
           replacement: mktxp_host_ip:49090
   ```

---

## Production Daemon Deployments

### Docker & Docker Compose

Run official multi-arch containers as non-root (UID 1000):

```bash
docker run -d \
  --name mktxp \
  -v "$(pwd)/mktxp-config:/etc/mktxp" \
  -p 49090:49090 \
  --restart unless-stopped \
  ghcr.io/akpw/mktxp:latest
```

### Kubernetes

A complete manifest is provided in [deploy/kubernetes/deployment.yaml](../deploy/kubernetes/deployment.yaml):
```bash
kubectl apply -f deploy/kubernetes/deployment.yaml
```

### Linux `systemd` Service

Create `/etc/systemd/system/mktxp.service`:

```ini
[Unit]
Description=MKTXP MikroTik Prometheus Exporter
After=network.target

[Service]
User=mktxp
ExecStart=/usr/local/bin/mktxp export
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
❯ sudo systemctl daemon-reload
❯ sudo systemctl enable --now mktxp
❯ systemctl status mktxp
```

### FreeBSD Service

Create `/usr/local/etc/rc.d/mktxp`:

```sh
#!/bin/sh
# PROVIDE: mktxp
# REQUIRE: DAEMON NETWORKING
# KEYWORD: shutdown

. /etc/rc.subr

name=mktxp
rcvar=mktxp_enable
: ${mktxp_enable:="NO"}
: ${mktxp_user:="root"}

pidfile="/var/run/${name}.pid"
command="/usr/sbin/daemon"
command_args="-c -f -P ${pidfile} /usr/local/bin/mktxp export"

load_rc_config $name
run_rc_command "$1"
```

Enable and start:
```bash
❯ sudo sysrc mktxp_enable="YES"
❯ sudo service mktxp start
```

---

## Companion Monitoring Stack

For a complete turn-key monitoring environment including Prometheus, Grafana dashboards, and centralized MikroTik syslog ingestion with Grafana Loki, check out the companion project:
- [MKTXP Stack (GitHub)](https://github.com/akpw/mktxp-stack)

<img width="50%" alt="MKTXP Stack Centralized Logging" src="https://user-images.githubusercontent.com/5028474/210771516-06a3e6ab-8eab-458c-9f38-5d44f95d23d4.png">
