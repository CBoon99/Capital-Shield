# Security & Secrets Policy — BoonMindX Capital Shield

**Date**: November 14, 2025  
**Phase**: Phase 3, Day 6  
**Status**: Active Policy

---

## Purpose

This document defines how secrets and sensitive data are handled across the BoonMindX Capital Shield codebase, configuration, logs, and documentation. This policy ensures that sensitive information is never accidentally exposed in version control, logs, or public-facing documentation.

**Scope of Application**:
- **Code**: Application source code and configuration files
- **Config**: Environment variables, configuration files, deployment scripts
- **Logs**: Application logs, error logs, audit logs, performance logs
- **Documentation**: Markdown files, README files, deployment guides, status reports

---

## Scope

This policy applies to all sensitive data types:

### API Keys

- Data provider API keys (e.g., market data providers)
- Authentication API keys (internal service authentication)
- Third-party service API keys (if any)

### Secrets

- JWT secrets (for future JWT authentication)
- Database credentials (if databases are added)
- Encryption keys (if encryption is implemented)

### Network Information

- IP addresses (public and private)
- Hostnames (internal hostnames, not public domains)
- Port numbers (if sensitive)

### Access Tokens

- Slack tokens (if Slack integration is added)
- Email service tokens (if email integration is added)
- Other OAuth/API tokens

---

## Principles

### 1. No Secrets in Git

**Rule**: Never commit secrets, API keys, passwords, or sensitive configuration to version control.

**Enforcement**:
- Use `.gitignore` to exclude `.env` files
- Use environment variable templates (`.env.template`) with placeholders
- Review all commits before pushing

### 2. Environment Variables for Local Development

**Rule**: Use `.env` files for local development, never commit them.

**Practice**:
- Create `.env` from `ENVIRONMENT_VARIABLES_TEMPLATE.env`
- Add `.env` to `.gitignore`
- Use placeholders in templates: `<YOUR_API_KEY_HERE>`

### 3. Redaction in Documentation

**Rule**: All IPs, keys, and sensitive values in documentation must be redacted.

**Patterns**:
- IPs: `203.0.113.42` → `<REDACTED_IP>`
- Keys: `sk_live_abc123...` → `<REDACTED_KEY>`
- Hostnames: `internal-server-01.example.com` → `<INTERNAL_HOST>`

**Exception**: Public domain placeholders like `staging.boonmindx.com` are allowed as target labels (not actual deployed domains).

### 4. Logs Must NOT Leak Secrets

**Rule**: Application logs must never include secrets, API keys, or sensitive data.

**Requirements**:
- Do not log query parameters containing secrets
- Do not log `Authorization` or `X-API-Key` headers
- Do not echo secrets in error messages
- Redact sensitive data in log outputs

---

## Storage Rules

### Local Development

**Method**: `.env` files (git-ignored)

**Practice**:
- Create `.env` from `ENVIRONMENT_VARIABLES_TEMPLATE.env`
- Fill in actual values locally
- Never commit `.env` files
- Use `.env.local`, `.env.staging.local` for environment-specific overrides

**Example**:
```bash
# .env (local, git-ignored)
SHIELD_API_KEY_FREE=local_dev_key_12345
SHIELD_API_KEY_PRO=local_dev_key_67890
```

### Staging / Production

**Method**: Environment variables or secret managers

**Options** (placeholders):
- Environment variables set on server (systemd, Docker, etc.)
- Secret managers: `<SECRET_MANAGER_NAME>` (e.g., AWS Secrets Manager, HashiCorp Vault)
- Cloud provider secret storage (provider-specific)

**Practice**:
- Set environment variables at deployment time
- Use secret managers for sensitive production secrets
- Never hard-code secrets in application code

**Explicit Statement**: **No real keys or IPs should ever be committed to this repository.**

---

## Redaction Rules

### IP Addresses

**Pattern**: Replace all IPs with `<REDACTED_IP>`

**Examples**:
- `203.0.113.42` → `<REDACTED_IP>`
- `192.168.1.100` → `<REDACTED_IP>`
- `10.0.0.5` → `<REDACTED_IP>`

**Exception**: Generic placeholders like `<STAGING_IP>`, `<PUBLIC_IP>` are acceptable in planning docs.

### API Keys and Tokens

**Pattern**: Replace keys/tokens with `<REDACTED_KEY>` or `<API_KEY>`

**Examples**:
- `sk_live_abc123def456...` → `<REDACTED_KEY>`
- `test_pro_key_67890` → `<REDACTED_KEY>`
- `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` → `<REDACTED_TOKEN>`

### Hostnames

**Pattern**: Replace internal hostnames with `<INTERNAL_HOST>`

**Examples**:
- `internal-db-01.example.com` → `<INTERNAL_HOST>`
- `staging-server-01.internal` → `<INTERNAL_HOST>`

**Exception**: Public domain placeholders like `staging.boonmindx.com` are allowed as target labels in planning docs.

### Usernames and Emails

**Pattern**: Replace with `<REDACTED_USER>` or `<REDACTED_EMAIL>`

**Examples**:
- `admin@example.com` → `<REDACTED_EMAIL>`
- `deploy-user` → `<deploy-user>` (generic placeholder OK)

---

## Logging Rules

### Request Logging

**Do NOT Log**:
- `Authorization` header values
- `X-API-Key` header values
- Query parameters containing secrets (e.g., `?api_key=...`)
- Request bodies containing passwords or tokens

**Do Log**:
- Request paths (e.g., `/api/v1/signal`)
- Request methods (GET, POST, etc.)
- Response status codes
- Request IDs (non-sensitive identifiers)
- Timestamps

### Error Logging

**Do NOT Log**:
- Full stack traces containing environment variables
- Error messages that echo user input containing secrets
- Database connection strings with credentials

**Do Log**:
- Error types and codes
- Error messages (sanitized)
- Stack traces (with sensitive data redacted)
- Request context (non-sensitive)

### Example: Logging Request Headers

**BAD**:
```python
logger.info(f"Request headers: {request.headers}")  # May include X-API-Key
```

**GOOD**:
```python
safe_headers = {k: v for k, v in request.headers.items() if k.lower() not in ['authorization', 'x-api-key']}
logger.info(f"Request headers: {safe_headers}")
```

---

## Incident Handling

### If a Secret Is Committed

**Immediate Actions**:

1. **Rotate Key at Provider**:
   - Immediately revoke/rotate the exposed key at the provider
   - Generate new key
   - Update all systems using the old key

2. **Remove from Git History** (if necessary):
   - Use `git filter-branch` or `git filter-repo` to remove secret from history
   - Force-push only if absolutely necessary (coordinate with team)
   - Consider if secret is already exposed (may not be worth rewriting history)

3. **Document Incident** (locally, not committed):
   - Create local incident log (not in git)
   - Document what was exposed, when, and remediation steps
   - Review policy to prevent recurrence

4. **Notify Team**:
   - Inform team members to update their local `.env` files
   - Update any shared secret storage

### Prevention

- Review all commits before pushing
- Use pre-commit hooks to scan for secrets (optional)
- Regular audits of repository for accidentally committed secrets

---

## Status

**As of Phase 3 Day 6**: No real secrets or IPs are present in the repository. This policy is preventative and establishes guardrails before any real staging secrets or IPs are introduced.

**Verification**:
- All documentation uses placeholders (`<REDACTED_IP>`, `<API_KEY>`, etc.)
- All environment variable templates use placeholders (`<YOUR_API_KEY_HERE>`)
- No `.env` files are committed
- No real API keys or IPs in code or documentation

---

## References

- `REDACTION_GUIDE.md` - Practical guide for redacting sensitive information
- `ENV_AND_GITIGNORE_POLICY.md` - Environment variable and gitignore policy
- `ENVIRONMENT_VARIABLES_TEMPLATE.env` - Environment variable template

---

*Last updated: November 14, 2025*

