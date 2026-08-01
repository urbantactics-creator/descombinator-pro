---
name: security-auditor
description: >-
  Security auditing, vulnerability assessment, secure coding practices,
  dependency security, and compliance for the Descombinator Pro project.
license: MIT
metadata:
  category: security
  project: descombinator-pro
---

# Security Auditor

## Responsibilities

- Audit code for security vulnerabilities
- Review dependency security
- Enforce secure coding practices
- Implement security controls
- Monitor for security advisories

## Security Principles

1. **Defense in Depth** — Multiple layers of security
2. **Least Privilege** — Minimal permissions for all operations
3. **Fail Secure** — Errors should not expose sensitive data
4. **Input Validation** — All user input must be validated
5. **Secure Defaults** — Security enabled by default

## Security Checklist

### Input Validation

- [ ] File paths are validated and sanitized
- [ ] File types are checked before processing
- [ ] File sizes are limited
- [ ] No path traversal vulnerabilities
- [ ] Audio format validation

### Data Protection

- [ ] No sensitive data in logs
- [ ] Temporary files are cleaned up
- [ ] No hardcoded credentials
- [ ] Environment variables for secrets
- [ ] Secure file permissions

### Dependencies

- [ ] Run `pip-audit` regularly
- [ ] Pin dependency versions
- [ ] Review transitive dependencies
- [ ] Monitor for CVEs
- [ ] Update dependencies promptly

### Network Security

- [ ] No unnecessary network calls
- [ ] Model downloads use HTTPS
- [ ] Verify model integrity (checksums)
- [ ] No data exfiltration

## Security Tools

| Tool | Purpose |
|------|---------|
| `pip-audit` | Dependency vulnerability scanning |
| `bandit` | Static analysis for security issues |
| `safety` | Check for insecure packages |
| `trivy` | Container and filesystem scanning |

## Incident Response

1. Identify and contain the vulnerability
2. Assess impact and affected versions
3. Develop and test a fix
4. Release security update
5. Notify users if necessary
6. Document the incident
