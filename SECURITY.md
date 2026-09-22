# Security notes

This repository is a reference implementation, not a universal security baseline. Network interfaces, subnets, service names and threat models differ between hosts.

Before running any apply script:

1. Use a local console or out-of-band recovery path.
2. Capture the baseline and confirm the backup files are readable.
3. Keep the current SSH session open and verify public-key access in a second session.
4. Review the generated commands and configuration for the target host.
5. Apply one module, verify it, then cancel its rollback timer.

Do not commit real environment files, host inventories, private addresses, SSH keys, API credentials, VPN profiles or AdGuard configuration. Report vulnerabilities through GitHub's private security reporting rather than a public issue.

