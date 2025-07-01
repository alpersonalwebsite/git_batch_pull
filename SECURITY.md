# Security Policy

## Threat Model
- All secrets (tokens) must be stored securely (preferably with `keyring` or in a protected `.env` file).
- All subprocesses are run with `shell=False` and validated input to prevent injection.
- User input is always validated and sanitized.
- Only the latest version is supported for security updates.

## Reporting a Vulnerability
If you discover a security vulnerability, please email the maintainer at your@email.com. Do not open a public issue.

- We will respond as quickly as possible and coordinate a fix.
- Responsible disclosure is appreciated and encouraged.

## Security Contact
- Email: your@email.com

## Supported Versions
Only the latest version is supported for security updates. Please update to the latest release before reporting issues.

## Security Best Practices
- Never commit secrets or sensitive data to the repository.
- Always validate and sanitize user input.
- Follow the principle of least privilege for all tokens and credentials.

---
See `README.md` and `CONTRIBUTING.md` for more security guidelines.
