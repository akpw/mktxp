# MKTXP

![License](https://img.shields.io/badge/License-GNU%20GPL-blue.svg)
![Language](https://img.shields.io/badge/python-v3.9+-blue)
![Platform](https://img.shields.io/badge/mikrotik-routeros-orange)
![Diagnostics](https://img.shields.io/badge/cli-diagnostics-blue)
![GitOps](https://img.shields.io/badge/gitops-rsc%20config-2ea44f)
![Prometheus](https://img.shields.io/badge/prometheus-exporter-blueviolet)
[![Docker Pulls](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fghcr-badge.elias.eu.org%2Fapi%2Fakpw%2Fmktxp%2Fmktxp&query=%24.downloadCount&label=docker%20pulls&logo=docker&logoColor=white&color=2496ed)](https://github.com/akpw/mktxp/pkgs/container/mktxp)

MKTXP is an extensible toolkit for MikroTik RouterOS network engineering. It provides interactive terminal diagnostics, deterministic GitOps configuration management, and a Prometheus metrics exporter within a single command-line tool.

---

## Choose Your Workflow

| I need to … | Start with | Full Guide |
| :--- | :--- | :--- |
| Troubleshoot a router now | `mktxp diag …` | [Diagnostics Guide](https://github.com/akpw/mktxp/blob/main/docs/diagnostics.md) |
| Clean up / version RouterOS configs | `mktxp rsc …` | [GitOps RSC Guide](https://github.com/akpw/mktxp/blob/main/docs/rsc.md) |
| Monitor routers continuously | `mktxp export` | [Exporter Guide](https://github.com/akpw/mktxp/blob/main/docs/exporter.md) |

---

## Install

### Standalone CLI & Exporter

```bash
# Recommended for local CLI usage
❯ pipx install mktxp

# Or via standard pip
❯ pip install mktxp

# Via Homebrew
❯ brew install mktxp

# Via Docker
❯ docker pull ghcr.io/akpw/mktxp:latest
```

*Requirements: Python >= 3.9. Supported on Linux, macOS, and FreeBSD.*

### Ready-to-Run Monitoring & Logging Stack ([MKTXP Stack](https://github.com/akpw/mktxp-stack))

If you need a turnkey environment without manually wiring services, [MKTXP Stack](https://github.com/akpw/mktxp-stack) is an out-of-the-box Docker Compose deployment that packages MKTXP alongside Prometheus, pre-configured Grafana dashboards, and adds centralized MikroTik syslog processing via Grafana Loki and Promtail.

---

## Quick Start: GitOps Configuration (`mktxp rsc`)

For local `.rsc` files, `mktxp rsc` works with zero configuration or router setup required:

```bash
# Deterministic formatting: single-line commands, standardized headers, and clean Git diffs
❯ mktxp rsc format -i backup.rsc -o clean_backup.rsc

# Modular domain splitting: break a monolithic export into numbered component files and extracted scripts
❯ mktxp rsc split -i backup.rsc -o ./config-repo/ --extract-scripts
```

> 📖 *For AST architecture, custom domain handlers, live backups over SSH, and CI/CD automation, see the [GitOps RSC Guide](https://github.com/akpw/mktxp/blob/main/docs/rsc.md).*

---

## Connect to a Router

Both Live Diagnostics and the Prometheus Exporter connect to your routers via the standard RouterOS API.

MKTXP uses two configuration files:
- `mktxp.conf`: Router connection profiles, credentials, custom labels, and metrics switches. Edit with `mktxp edit`.
- `_mktxp.conf`: Daemon listen sockets, timeouts, parallel scraping, GitOps rules, and CLI diagnostic thresholds. Edit with `mktxp edit -i`.

Files are resolved automatically from `~/.config/mktxp/` (XDG standard) or `/etc/mktxp/` (system/Docker). Check active paths anytime with `mktxp show -cfg`.

### 1. Minimal Configuration (`mktxp.conf`)

Add your router entry to `mktxp.conf`:

```ini
[My-Router]
    hostname = 192.168.88.1
    username = mktxp_user
    password = secret_password
```

*(For Docker, simply mount your config directory: `-v "$(pwd)/mktxp-config:/etc/mktxp"`)*

### 2. Router User Setup

Create a dedicated monitoring user on your MikroTik router:

```routeros
/user group add name=mktxp_group policy=api,read
/user add name=mktxp_user group=mktxp_group password=secret_password
```

*(Note: For LTE metrics on RouterOS v6, the user also needs the `test` permission policy.)*

> 📖 *For complete parameter references, `[default]` section inheritance, custom labels, parallel fetching, and diagnostic tuning, see the [Configuration Guide](https://github.com/akpw/mktxp/blob/main/docs/configuration.md).*

---

## Quick Start: Live Diagnostics (`mktxp diag`)

Run targeted, domain-specific diagnostic one-liners directly in your terminal:

```bash
# Find sticky wireless clients clinging to distant APs with poor signal or low rates
❯ mktxp diag -en My-Router -cc --low-signal --low-rate 1M

# Surface top bandwidth consumers across the network
❯ mktxp diag -en My-Router -kc --top 5

# Audit mystery DHCP devices with no hostname
❯ mktxp diag -en My-Router -dc --unidentified

# Check active dynamic firewall threat bans
❯ mktxp diag -en My-Router -al blacklist --dynamic-only
```

Sample output:
```text
+----------------------+--------------+-------------------+-----------+------------------+--------+---------+---------+---------+
|      dhcp_name       | dhcp_address |    mac_address    | rx_signal |    interface     |  ssid  | tx_rate | rx_rate | uptime  |
+======================+==============+===================+===========+==================+========+=========+=========+=========+
| wlan0 (Conf Printer) | 10.20.10.49  | D8:1F:12:AD:3C:55 |    -87    | AP-Breakroom-2G  | Office | 36 Mbps | 1 Mbps  | 6 hours |
| wlan0 (Boardroom Tab)| 10.20.10.97  | 10:5A:17:0C:B9:C8 |    -84    | AP-Reception-2G  | Office | 24 Mbps | 1 Mbps  |  a day  |
+----------------------+--------------+-------------------+-----------+------------------+--------+---------+---------+---------+
Matching CAPsMAN clients: 2 (Total connected: 127)
```

> 💡 Tip: Appending `-h` to any command (e.g. `mktxp diag -kc -h`) dynamically scopes help to only that command's filters.  
> 📖 *For more diagnostic domains, table schemas, and recipes, see the [Diagnostics Guide](https://github.com/akpw/mktxp/blob/main/docs/diagnostics.md).*

---

## Quick Start: Prometheus Exporter (`mktxp export`)

Start the exporter daemon to scrape configured routers and serve metrics to Prometheus:

```bash
❯ mktxp export
# Serving Prometheus metrics at http://localhost:49090/metrics
```

Add the scrape target to `/etc/prometheus/prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'mktxp'
    static_configs:
      - targets: ['localhost:49090']
```

Import the official [Grafana Dashboard (ID: 13679)](https://grafana.com/grafana/dashboards/13679):

<img width="32%" alt="Traffic & Interface" src="https://user-images.githubusercontent.com/5028474/217029083-3c2f561e-853f-45a7-b9f1-d818a830daf5.png"> <img width="32%" alt="Wireless Clients" src="https://user-images.githubusercontent.com/5028474/217029092-2b86b41b-1f89-4383-ac48-16652e820f7e.png"> <img width="32%" alt="Device Health" src="https://user-images.githubusercontent.com/5028474/217029096-dbf6b46c-3ed7-4c76-a57b-8cebfb3b671c.png">

> Want centralized RouterOS logs too? [MKTXP Stack](https://github.com/akpw/mktxp-stack) adds Grafana Loki and Promtail alongside Prometheus and MKTXP. The screenshot below is the Stack's log-analysis dashboard; the three screenshots above are the standard MKTXP metrics dashboard.

<img width="50%" alt="MKTXP Stack Centralized Logging" src="https://user-images.githubusercontent.com/5028474/210771516-06a3e6ab-8eab-458c-9f38-5d44f95d23d4.png">

> 📖 *For dynamic multi-target discovery (`/probe`), Docker/Kubernetes, and systemd/FreeBSD service deployment, see the [Exporter Guide](https://github.com/akpw/mktxp/blob/main/docs/exporter.md).*

---

## Detailed Documentation

- [Live CLI Diagnostics Guide](https://github.com/akpw/mktxp/blob/main/docs/diagnostics.md): Detailed filter reference, table schemas, and recipes for multiple diagnostic domains.
- [RouterOS GitOps RSC Guide](https://github.com/akpw/mktxp/blob/main/docs/rsc.md): AST formatting, modular domain splitting, script extraction, and CI/CD pipelines.
- [Prometheus Exporter Guide](https://github.com/akpw/mktxp/blob/main/docs/exporter.md): Metrics catalog, `/probe` multi-target pattern, container manifests, and service files.
- [Configuration Reference Guide](https://github.com/akpw/mktxp/blob/main/docs/configuration.md): Complete anatomy of `mktxp.conf` and `_mktxp.conf`, multi-router inheritance, tuning, and Docker mounts.

---

## Blogs

- [Beyond Metrics: Instant RouterOS Diagnostics with MKTXP 2.0](https://akpw.github.io/articles/2026/09/06/MKTXP-2.0-Live-CLI-Diagnostics.html)
- [Under the Hood: Refactoring MKTXP for 2.0](https://akpw.github.io/articles/2026/08/28/Refactoring-MKTXP-2.0-Modular-Architecture.html)
- [Wrangling RouterOS Configs: Introducing GitOps for MikroTik with MKTXP](https://akpw.github.io/articles/2026/08/16/GitOps-for-Mikrotik-RSC.html)

---

## License & Contributing

- Distributed under the [GNU General Public License v2](LICENSE).
- Local development: create a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`), install editable with test dependencies (`pip install -e ".[test]"`), and run `pytest`.
