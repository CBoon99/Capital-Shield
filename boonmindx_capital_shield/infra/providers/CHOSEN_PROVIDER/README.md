# Provider-Specific Deployment Guide - `<CHOSEN_PROVIDER>`

**Date**: November 14, 2025  
**Phase**: Phase 3, Day 4  
**Status**: Provider-Specific Blueprint

---

## Overview

This directory contains provider-specific deployment guides for `<CHOSEN_PROVIDER>`. These guides complement the provider-agnostic `STAGING_DEPLOY_PLAYBOOK.md` with provider-specific steps for instance creation, security configuration, and deployment.

---

## Files in This Directory

- **`README.md`** (this file) - Overview and navigation
- **`CREATE_INSTANCE_STEPS.md`** - Step-by-step instance creation guide
- **`SECURITY_GROUP_TEMPLATE.md`** - Firewall/security group configuration
- **`SYSTEMD_DEPLOY_STEPS.md`** - Systemd service deployment (links to main playbook)

---

## Provider-Specific Considerations

### Instance Types

- **Minimum**: `<MIN_INSTANCE_TYPE>` (1 vCPU, 2GB RAM)
- **Recommended**: `<REC_INSTANCE_TYPE>` (2 vCPU, 4GB RAM)
- **High-Performance**: `<HP_INSTANCE_TYPE>` (4 vCPU, 8GB RAM)

### Regions

- **Recommended**: `<PRIMARY_REGION>` (closest to users)
- **Alternatives**: `<ALT_REGION_1>`, `<ALT_REGION_2>`

### Network Configuration

- **Static IP**: Provider-specific method for reserving static IPs
- **Security Groups**: Provider-specific firewall/security group configuration
- **DNS Integration**: Provider-specific DNS service (if applicable)

---

## Deployment Workflow

1. **Create Instance**: Follow `CREATE_INSTANCE_STEPS.md`
2. **Configure Security**: Follow `SECURITY_GROUP_TEMPLATE.md`
3. **Deploy Application**: Follow `STAGING_DEPLOY_PLAYBOOK.md` (provider-agnostic)
4. **Configure Systemd**: Follow `SYSTEMD_DEPLOY_STEPS.md` (if provider-specific steps needed)
5. **Validate**: Follow `CLOUD_SETUP_CHECKLIST.md`

---

## Notes

- All IP addresses, domains, and credentials are placeholders
- Replace `<CHOSEN_PROVIDER>` with actual provider name when decision is finalized
- Provider-specific steps supplement but do not replace the main deployment playbook

---

## References

- `../../STAGING_DEPLOY_PLAYBOOK.md` - Main deployment playbook
- `../../STAGING_PROVIDER_OPTIONS.md` - Provider comparison
- `../../CLOUD_SETUP_CHECKLIST.md` - Validation checklist
- `../../../PHASE3_PROVIDER_DECISION.md` - Provider decision document

---

*Last updated: November 14, 2025*

