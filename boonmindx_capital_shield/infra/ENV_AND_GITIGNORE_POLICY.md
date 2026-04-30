# Environment Variables & Gitignore Policy — BoonMindX Capital Shield

**Date**: November 14, 2025  
**Phase**: Phase 3, Day 6  
**Status**: Active Policy

---

## Purpose

This document ties together environment variable usage and `.gitignore` rules to ensure secrets and sensitive configuration are never committed to version control.

---

## Environment Files

### Local-Only Files (Git-Ignored)

These files contain actual secrets and must **never** be committed:

- **`.env`**: Primary local development environment file
- **`.env.local`**: Local overrides (if used)
- **`.env.staging.local`**: Staging-specific local overrides (if used)
- **`.env.production.local`**: Production-specific local overrides (if used)
- **`.env.*.local`**: Any environment-specific local files

**Rule**: All `.env*` files (except templates) are git-ignored.

---

### Template-Only Files (Committed)

These files contain placeholders and are safe to commit:

- **`infra/ENVIRONMENT_VARIABLES_TEMPLATE.env`**: Main environment variable template
- **`.env.example`**: Example file (if created, uses placeholders only)
- **`.env.template`**: Alternative template name (if used)

**Rule**: Only template files with placeholders go into git.

---

## Git Ignore Policy

### Required Ignore Entries

The `.gitignore` file must include these entries (or equivalent patterns):

```
# Environment files
.env
.env.*
!.env.example
!.env.template
!infra/ENVIRONMENT_VARIABLES_TEMPLATE.env

# Logs
logs/
*.log

# Reports (raw data may contain sensitive info)
reports/raw/

# Private datasets
datasets/private/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

**Note**: This document specifies expectations. The actual `.gitignore` file may contain additional entries. Cross-check the actual `.gitignore` file to ensure these patterns are present.

---

### Verification

To verify `.gitignore` is working:

```bash
# Check if .env is ignored
git check-ignore .env
# Expected: .env

# Check if template is NOT ignored
git check-ignore infra/ENVIRONMENT_VARIABLES_TEMPLATE.env
# Expected: (no output, file is tracked)
```

---

## How to Add New Secrets

### Step 1: Add to Local `.env`

Add the new secret to your local `.env` file:

```bash
# .env (local, git-ignored)
NEW_SECRET_KEY=your_actual_secret_value_here
```

---

### Step 2: Add to Template

Add the new secret to `infra/ENVIRONMENT_VARIABLES_TEMPLATE.env` as a placeholder:

```bash
# infra/ENVIRONMENT_VARIABLES_TEMPLATE.env (committed)
# New Secret Key
NEW_SECRET_KEY="<YOUR_NEW_SECRET_KEY_HERE>"
```

**Important**: Use a clear placeholder name, never a real-looking value.

---

### Step 3: Document (If Needed)

If the secret requires special documentation:

- Add to `infra/STAGING_PLAN.md` if staging-specific
- Add to `infra/SECURITY_SECRETS_POLICY.md` if security-related
- Add to application README if user-facing

---

### Step 4: Update Application Code

Update application code to read from environment variable:

```python
# app/core/config.py
import os

NEW_SECRET_KEY = os.getenv("NEW_SECRET_KEY", "")
```

---

## Environment Variable Naming

### Conventions

- **UPPERCASE**: All environment variable names use UPPERCASE
- **SNAKE_CASE**: Use underscores to separate words
- **Prefix**: Use `SHIELD_` prefix for BoonMindX Capital Shield-specific variables

**Examples**:
- `SHIELD_API_KEY_FREE`
- `SHIELD_API_KEY_PRO`
- `SHIELD_API_DEBUG`
- `LOG_DIR`
- `RATE_LIMIT_PER_SECOND`

---

## Staging / Production Environment Variables

### Setting Variables

**Staging**:
- Set via systemd `EnvironmentFile` (see `STAGING_DEPLOY_PLAYBOOK.md`)
- Or via cloud provider environment variable configuration
- Or via secret manager (future)

**Production**:
- Use secret manager (e.g., `<SECRET_MANAGER_NAME>`)
- Or cloud provider secret storage
- Never hard-code in application code

---

## Best Practices

### 1. Never Commit `.env` Files

**Always**:
- Add `.env` to `.gitignore`
- Use templates for examples
- Review commits before pushing

**Never**:
- Commit `.env` files
- Commit files with real secrets
- Use real-looking example values in templates

---

### 2. Use Clear Placeholders

**Good**:
```bash
SHIELD_API_KEY_FREE="<YOUR_API_KEY_HERE>"
```

**Bad**:
```bash
SHIELD_API_KEY_FREE="test_key_12345"  # Looks real!
```

---

### 3. Document Required Variables

- List all required environment variables in `ENVIRONMENT_VARIABLES_TEMPLATE.env`
- Add comments explaining what each variable does
- Note which variables are optional vs required

---

### 4. Validate on Startup

Application should validate required environment variables on startup:

```python
# app/core/config.py
required_vars = ["SHIELD_API_KEY_FREE", "LOG_DIR"]
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    raise ValueError(f"Missing required environment variables: {missing}")
```

---

## References

- `SECURITY_SECRETS_POLICY.md` - Security and secrets policy
- `REDACTION_GUIDE.md` - Redaction guide
- `ENVIRONMENT_VARIABLES_TEMPLATE.env` - Environment variable template
- `.gitignore` - Actual gitignore file (verify entries)

---

*Last updated: November 14, 2025*

