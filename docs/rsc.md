# RouterOS GitOps Configuration Management (`mktxp rsc`)

RouterOS `.rsc` export files are often difficult to maintain in version control. They mix structural configurations with arbitrary inline scripts, backslash line continuations, volatile orderings, and dynamic hardware MAC addresses that create noisy diffs.

`mktxp rsc` solves this with an AST-based tokenizer, parser, and serializer designed specifically for MikroTik configuration files. It provides deterministic formatting (`format`) and modular per-domain directory splitting (`split`) for clean, version-controlled network engineering.

---

## Table of Contents
- [Quick Start](#quick-start)
- [Input Modes: Local Files vs Live SSH](#input-modes-local-files-vs-live-ssh)
  - [SSH Authentication](#ssh-authentication)
- [Format Command (`mktxp rsc format`)](#format-command-mktxp-rsc-format)
- [Split Command (`mktxp rsc split`)](#split-command-mktxp-rsc-split)
  - [Sidecar Script Extraction (`--extract-scripts`)](#sidecar-script-extraction---extract-scripts)
  - [Output Directory Scoping](#output-directory-scoping)
- [Extensibility & Custom Domain Handlers](#extensibility--custom-domain-handlers)
- [GitOps Workflows & CI/CD Automation](#gitops-workflows--cicd-automation)

---

## Quick Start

For local `.rsc` files, `mktxp rsc` works right out of the box with zero configuration required:

```bash
# Deterministic monolithic formatting
❯ mktxp rsc format -i backup.rsc -o clean_backup.rsc

# Modular domain splitting
❯ mktxp rsc split -i backup.rsc -o ./config-repo/ --extract-scripts
```

---

## Input Modes: Local Files vs Live SSH

`mktxp rsc` supports two operational modes:

1. Local File Mode (`-i <path>`):
   Processes an existing `.rsc` file without touching network hardware.
2. Live Router Mode (`-en <router_entry>`):
   Directly connects to a configured router over SSH, initiates an export, streams the output into the AST parser, and formats or splits it on the fly.

### SSH Authentication & Port Settings

Live exports use native SSH rather than the RouterOS API to obtain raw `/export` streams:
- Uses your local SSH keys (`~/.ssh/id_ed25519`, `~/.ssh/id_rsa`) or active `ssh-agent`.
- The router user must have `ssh` permission policy enabled in RouterOS.

#### External Secrets (`secrets.yml`)

You can keep SSH credentials centralized alongside your RouterOS API credentials inside your external `credentials_file`:

```yaml
# RouterOS API monitoring credentials
username: api-reader
password: secret_password

# Live GitOps RSC SSH credentials
rsc_ssh_user: gitops_admin
ssh_key_file: ~/.ssh/id_ed25519
# rsc_ssh_port: 2222     # optional SSH port fallback
```

#### Precedence & Resolution Hierarchy

Both SSH username and port follow a strict resolution hierarchy where explicit command-line parameters always take highest precedence:

##### SSH Username Resolution:
1. **CLI Override (`--user <username>`)**: Highest priority; unconditionally overrides all configuration files and secrets.
2. **Router Entry in `mktxp.conf`**: `rsc_ssh_user = <user>` defined under a device's section `[MyRouter]`.
3. **Global Default in `mktxp.conf`**: `rsc_ssh_user = <user>` defined under `[default]`.
4. **Credentials File (`secrets.yml`)**: `rsc_ssh_user: <user>` (or `ssh_user: <user>`) defined in the YAML file.
5. **Fallback**: RouterOS API `username` from router definition / credentials file (or `"admin"`).

##### SSH Port Resolution:
1. **CLI Override (`--ssh-port <port>`)**: Highest priority; unconditionally overrides all configuration files and secrets.
2. **Router Entry in `mktxp.conf`**: `rsc_ssh_port = <port>` under `[MyRouter]` (useful for port-forwarded gateways, e.g. `rsc_ssh_port = 2222`).
3. **Global Default in `mktxp.conf`**: `rsc_ssh_port = <port>` under `[default]`.
4. **Credentials File (`secrets.yml`)**: `rsc_ssh_port: <port>` (or `ssh_port: <port>`) in the YAML file.
5. **Fallback**: `_mktxp.conf [RSC] ssh_port` setting (defaults to `22`).

---

## Format Command (`mktxp rsc format`)

Parses a raw export and formats it into a clean, deterministic monolithic `.rsc` file with standardized `# Section:` headers:

```bash
# Format from local file
❯ mktxp rsc format -i raw_export.rsc -o clean_export.rsc

# Format live directly from router entry over SSH
❯ mktxp rsc format -en MyRouter -o ./backups/MyRouter-clean.rsc

# Format live using router inventory from custom config directory
❯ mktxp --cfg-dir /path/to/custom rsc format -en MyRouter -o ./backups/MyRouter-clean.rsc
```

### Options

| Flag | Description |
| :--- | :--- |
| `--cfg-dir <path>` | Global option: Path to custom directory containing `mktxp.conf`, `_mktxp.conf` (with `[RSC]` settings), and `secrets.yml`. |
| `-i`, `--input <path>` | Input `.rsc` file path. |
| `-en`, `--entry-name <name>` | Router entry name from `mktxp.conf` for live SSH export. |
| `-o`, `--out <path>` | Output file path (defaults to stdout if omitted). |
| `--show-sensitive` | Include passwords and sensitive keys in live export (default: hidden). |
| `--user <username>` | Override SSH username for live export. |
| `--ssh-key <path>` | Path to SSH private key for live export. |
| `--ssh-port <port>` | Override SSH port (default: `22`). |
| `--wrap` | Wrap long command lines at 80 columns with trailing backslashes `\` (default: unwrapped single lines for clean git line diffs). |
| `--wrap-col <cols>` | Set custom column width for line wrapping (default: `80`). |
| `--strip-macs` | Strip dynamic/auto MAC addresses to prevent false-positive Git diffs across hardware replacements. |

---

## Split Command (`mktxp rsc split`)

Splits a raw or live `.rsc` export into modular, numbered configuration files organized by subsystem domain.

```bash
# Split from local file
❯ mktxp rsc split -i MyRouter.rsc --extract-scripts

# Split live directly from router entry
❯ mktxp rsc split -en MyRouter --extract-scripts

# Batch split all enabled routers sequentially
❯ mktxp rsc split -en __all__ --extract-scripts
```

Output Layout:
```text
Successfully split RouterOS export into 8 files in: ./exports/MyRouter/
  |- 01-base.rsc
  |- 02-wifi.rsc
  |- 03-system.rsc
  |- 04-ip.rsc
  |- 05-dhcp-leases.rsc
  |- 06-firewall.rsc
  |- 08-wireguard.rsc
  |- Watchdog.rsc
```

### Options

| Flag | Description |
| :--- | :--- |
| `-i`, `--input <path>` | Input `.rsc` file path. |
| `-en`, `--entry-name <name>` | Router entry name from `mktxp.conf` for live SSH export (or `__all__` to sequentially export and split all enabled routers). |
| `-d`, `-o`, `--out-dir <path>` | Destination directory for split `.rsc` files. |
| `--extract-scripts` | Extract multi-line scripts to standalone `.rsc` sidecar files (default: keep embedded inline). |
| `--no-numbered` | Emit plain filenames (e.g. `base.rsc`, `wifi.rsc`) without numeric order prefixes. |
| `--strip-macs` | Strip dynamic MAC addresses. |
| `--wrap` | Wrap lines with backslashes at 80 columns. |
| `--show-sensitive` | Include passwords and sensitive keys in live export. |
| `--ssh-key <path>` | Path to SSH private key for live export. |
| `--user <username>` | Override SSH username for live export. |

### Sidecar Script Extraction (`--extract-scripts`)

When `--extract-scripts` is passed:
- Multi-line `/system script` bodies are extracted into their own standalone `.rsc` files named after the script (e.g. `Watchdog.rsc`).
- Script metadata (permissions, policies, comments, and run count) is preserved as header comments within the script file.
- The parent `system.rsc` retains a reference command pointing to the extracted script, keeping configuration diffs clean when script code changes.

### Output Directory Scoping

When `-d` / `-o` is omitted, `mktxp rsc split` automatically scopes output into `<base_dir>/<Name>/` (e.g. `./exports/MyRouter/`), preventing overlapping outputs when splitting multiple routers into the same directory.

### Batch Export All Routers (`-en __all__`)

When `-en __all__` is passed:
- **Automatic Discovery**: Discovers all router entries registered in `mktxp.conf` (or the directory passed via `--cfg-dir`).
- **Sequential Execution**: Connects to and exports routers one by one to prevent resource contention.
- **Enabled Filter**: Only routers configured with `enabled = True` are processed; disabled routers are reported as skipped.
- **Scoped Subdirectories**: Each router's files are placed into `<base_dir>/<RouterName>/`.
- **Fault Tolerance**: If an individual router fails (e.g. network timeout or SSH failure), the error is logged and the remaining routers continue processing. A final summary report details successes and failures.

---

## Extensibility & Custom Domain Handlers

The splitting pipeline is entirely configurable. You can customize existing handlers, reorder them, or introduce new domain handlers (e.g. `bgp`, `switch`, `vpn`) without writing any Python code:

1. Add the handler name to `handler_order` in `_mktxp.conf` under `[RSC]` (see the [Configuration Guide](configuration.md#2-rsc--gitops-rsc-settings--custom-handlers)):
   ```ini
   handler_order = base, wifi, system, ip, dhcp-leases, firewall, lte, wireguard, bgp
   ```
2. Define matching RouterOS command paths under `handler_<name>`:
   ```ini
   handler_bgp = /routing bgp, /routing bfd, /routing filter, /routing ospf
   ```

The engine uses longest-prefix specificity matching (so `/routing bgp` takes priority over general `/routing` in `system`), automatically numbers the output file (e.g. `09-bgp.rsc`), and safely routes any unmapped command paths to `99-other.rsc`.

---

## GitOps Workflows & CI/CD Automation

Because `mktxp rsc` produces deterministic, single-line AST output with stable sorting:
- Committing split outputs to a Git repository turns every commit into an exact, audit-ready network changelog.
- Hardware replacements don't trigger spurious diffs when `--strip-macs` is enabled.
- Automated backup pipelines can run in a scheduled GitHub Action or cron job.

### Example 1: Single Command Batch Backup

Export and modularly split all active routers defined in your default configuration (`~/.config/mktxp/`):

```bash
mktxp rsc split -en __all__ --extract-scripts --strip-macs
```

### Example 2: Multi-Location GitOps Automation Script

For infrastructures with separate site profiles, you can iterate across locations using `--cfg-dir`, optionally pushing to Git as shown in this example script:

```bash
#!/usr/bin/env bash
set -e

# Multi-location GitOps pipeline covering separate site profiles
LOCATIONS=("branch-office" "data-center" "remote-site")

for LOC in "${LOCATIONS[@]}"; do
    echo "Backing up site profile: $LOC"
    mktxp --cfg-dir "/etc/mktxp/profiles/$LOC" rsc split -en __all__ --extract-scripts --strip-macs
done

git add exports/
git commit -m "Auto-backup: $(date +'%Y-%m-%d %H:%M:%S')" || exit 0
git push origin main
```
