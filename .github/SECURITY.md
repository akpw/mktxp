# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

---

## Reporting a Vulnerability

If you have discovered a security vulnerability, please report it responsibly so that we can fix it before public disclosure.

### How to Report

Please **DO NOT** report security vulnerabilities via public GitHub issues, discussions, or pull requests.

Instead, please report vulnerabilities privately using GitHub's built-in **Private Vulnerability Reporting**:

1. Navigate to the [MKTXP Repository Security tab](https://github.com/akpw/mktxp/security).
2. Click **Report a vulnerability** under the Advisories section (or go directly to [New Security Advisory](https://github.com/akpw/mktxp/security/advisories/new)).
3. Fill in the details:
   - Clear description of the vulnerability and its potential impact.
   - Step-by-step reproduction steps or proof-of-concept (PoC).
   - Any suggested mitigations or patches.

If Private Vulnerability Reporting is unavailable or you prefer email, you may contact the maintainer directly via the contact information provided in git commit history or author profiles.

### What to Expect

- **Acknowledgment**: You will receive an acknowledgment of your report within 48–72 hours.
- **Assessment**: We will evaluate the impact, verify the issue, and collaborate on a remediation plan.
- **Coordination**: We will coordinate the release of a patch and public security advisory (GHSA / CVE if applicable) with you.
- **Credit**: You will be credited in the release notes and security advisory unless you prefer to remain anonymous.

---

## Deployment Security Best Practices

To ensure secure operation of MKTXP in your infrastructure:

1. **Network Segmentation**:
   - MKTXP exposes Prometheus metrics on HTTP port `49090`. Restrict access to this port via firewall rules or VPN so only authorized Prometheus scrape servers can reach it.
   - Do not expose port `49090` to untrusted networks or the public internet.

2. **RouterOS API Transport Security**:
   - Use `api-ssl` (port 8729) instead of plaintext `api` (port 8728) whenever possible (`use_ssl = True`).
   - Enable SSL certificate validation (`ssl_certificate_verify = True`) and provide a CA bundle (`ssl_ca_file`).

3. **Multi-Target `/probe` Safeguards**:
   - Restrict dynamic probe targets by configuring `probe_allowed_targets` with allowed CIDR subnets (e.g. `10.0.0.0/8, 192.168.88.0/24`) or hostnames in `mktxp.conf` or `_mktxp.conf`.
   - Never use wildcard `probe_allowed_targets = *` in untrusted or multi-tenant network environments.
   - When allowing hostnames or domain wildcards (`*.corp.local`), ensure the DNS resolver is trustworthy, as DNS controls which host receives the connection.
   - Target overrides are strictly permitted only for modules explicitly designated with `module_only = True`. Static router entries reject dynamic target overrides.
   - If your deployment does not use Prometheus multi-target scraping via `/probe`, disable the endpoint completely by setting `enable_probe = False` in `_mktxp.conf`.

4. **Secrets Management**:
   - Avoid keeping credentials in plain text in `mktxp.conf`.
   - Use the `credentials_file` setting to point to an external YAML file (e.g. stored in a protected directory or mounted secret in Docker/Kubernetes).
