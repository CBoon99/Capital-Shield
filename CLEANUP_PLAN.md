# Repository Cleanup Plan — Commercial Trading Bot Release
**Date**: 2025-11-16  
**Status**: ⚠️ **AWAITING APPROVAL** — Do not execute until approved

---

## Overview

This plan proposes **safe, reversible** cleanup operations to prepare the repository for commercial release. All operations use **ARCHIVE** (move) over **DELETE** where possible, preserving history while cleaning the production repo.

---

## Cleanup Strategy

### 1. Create Archive Structure
```
archive/
├── 2025-11-16/
│   ├── investor_docs/          # BearHunter Prime investor documents
│   ├── legacy_code/            # Root-level old Python files
│   ├── experimental/          # testing_area/ contents
│   ├── backtest_results/       # Old backtest outputs
│   └── phase_docs/            # Phase status documents
```

### 2. Operation Types
- **ARCHIVE**: Move to `archive/2025-11-16/` (preserves history)
- **DELETE**: Permanent removal (logs, bloat, duplicates)
- **KEEP**: Remains in repo (production code)
- **REVIEW**: Flagged for human decision

---

## Proposed Actions by Category

### Category 1: Financial Forecasts & Investor Docs (HIGH RISK)

**Action**: **ARCHIVE** to `archive/2025-11-16/investor_docs/`

**Rationale**: These documents contain unvalidated financial forecasts, profit claims, and speculative business projections. They create legal/credibility risk for commercial release but may be useful for historical reference.

**Files to Archive**:
- `BearHunter_Prime_Financial_Forecast.md` — £48M revenue projections
- `BearHunter_Prime_Investor_QA.md` — Speculative Q&A
- `BearHunter_Prime_Due_Diligence_Package.md` — DD package (verify claims)
- `BearHunter_Prime_IP_Portfolio_Submission.md` — IP claims (verify)
- `BearHunter_Prime_Survival_Validation_Report.md` — Validation (verify methodology)
- `BearHunter_Prime_Mathematical_Framework.md` — Math framework (verify)
- `BearHunter_Prime_Research_Paper.md` — Research paper (verify)
- `BearHunter_Prime_Technical_Specification.md` — Tech spec (verify)
- `Capital_Shield_Class_Threat_Model_Proof.md` — Threat model (verify)
- `System_Determinism_Failure_Bound_Analysis.md` — Analysis (verify)
- `Bear_Business_Docs_README.md` — Index of business docs
- `BearHunter_Deployment_Checklist.md` — Deployment checklist (may be useful)

**Commands**:
```bash
mkdir -p archive/2025-11-16/investor_docs
mv BearHunter_Prime_*.md archive/2025-11-16/investor_docs/
mv Capital_Shield_Class_Threat_Model_Proof.md archive/2025-11-16/investor_docs/
mv System_Determinism_Failure_Bound_Analysis.md archive/2025-11-16/investor_docs/
mv Bear_Business_Docs_README.md archive/2025-11-16/investor_docs/
mv BearHunter_Deployment_Checklist.md archive/2025-11-16/investor_docs/
```

---

### Category 2: Legacy Code (Superseded)

**Action**: **ARCHIVE** to `archive/2025-11-16/legacy_code/`

**Rationale**: Root-level Python files are superseded by `boonmindx_capital_shield/`. They may contain useful logic but are not part of the production system.

**Files to Archive**:
- `bear_detector.py` — Old bear detection
- `trading_engine.py` — Old trading engine
- `swarm_system.py` — Old orchestration
- `data_fetcher.py` — Old data fetcher
- `dashboard.py` — Old Flask dashboard
- `real_time_monte_carlo.py` — Old Monte Carlo
- `monte_carlo_backtest.py` — Old backtest script
- `config.py` — Old config (root level)
- `test_bear_bull_data.py` — Old test
- `run.sh` — Old run script
- `requirements.txt` — Old requirements (root level)
- `Dockerfile` — Old Dockerfile (root level)
- `docker-compose.yml` — Old docker-compose (root level)
- `DEPLOYMENT.md` — Old deployment docs
- `README.md` — Old README (root level — **REVIEW**: May want to keep as legacy entry point)

**Commands**:
```bash
mkdir -p archive/2025-11-16/legacy_code
mv bear_detector.py archive/2025-11-16/legacy_code/
mv trading_engine.py archive/2025-11-16/legacy_code/
mv swarm_system.py archive/2025-11-16/legacy_code/
mv data_fetcher.py archive/2025-11-16/legacy_code/
mv dashboard.py archive/2025-11-16/legacy_code/
mv real_time_monte_carlo.py archive/2025-11-16/legacy_code/
mv monte_carlo_backtest.py archive/2025-11-16/legacy_code/
mv config.py archive/2025-11-16/legacy_code/
mv test_bear_bull_data.py archive/2025-11-16/legacy_code/
mv run.sh archive/2025-11-16/legacy_code/
mv requirements.txt archive/2025-11-16/legacy_code/
mv Dockerfile archive/2025-11-16/legacy_code/
mv docker-compose.yml archive/2025-11-16/legacy_code/
mv DEPLOYMENT.md archive/2025-11-16/legacy_code/
# README.md — REVIEW before moving
```

---

### Category 3: Experimental Code (testing_area/)

**Action**: **ARCHIVE** entire `testing_area/` directory

**Rationale**: 305MB of experimental code, duplicate implementations, and large data files. Not part of production system.

**Directory to Archive**:
- `testing_area/` — Entire directory (305MB)

**Commands**:
```bash
mkdir -p archive/2025-11-16/experimental
mv testing_area archive/2025-11-16/experimental/
```

---

### Category 4: Old Backtest Results

**Action**: **ARCHIVE** to `archive/2025-11-16/backtest_results/`

**Rationale**: Historical backtest results are not needed for production but may be useful for reference.

**Files/Directories to Archive**:
- `backtests/` — Entire directory (old backtest outputs)
- `backtest_report_*.json` — All root-level backtest reports
- `BACKTEST_RESULTS.md` — Backtest results summary
- `monte_carlo_live/` — Old Monte Carlo live results

**Commands**:
```bash
mkdir -p archive/2025-11-16/backtest_results
mv backtests archive/2025-11-16/backtest_results/
mv backtest_report_*.json archive/2025-11-16/backtest_results/
mv BACKTEST_RESULTS.md archive/2025-11-16/backtest_results/
mv monte_carlo_live archive/2025-11-16/backtest_results/ 2>/dev/null || true
```

---

### Category 5: Large Bloat Files

**Action**: **DELETE** (not needed, too large to archive)

**Rationale**: Log files and OS metadata are bloat. No historical value.

**Files to Delete**:
- `backtest_output.log` (1.9MB)
- `backtest_output_corrected.log` (1.9MB)
- `.DS_Store` files (OS metadata)
- `4` (92KB — unclear what this is, **REVIEW** first)

**Commands**:
```bash
rm -f backtest_output.log
rm -f backtest_output_corrected.log
find . -name ".DS_Store" -type f -delete
# 4 — REVIEW before deleting
```

---

### Category 6: Historical Data (Large)

**Action**: **ARCHIVE** or **DELETE** (depending on need)

**Rationale**: 65MB of historical data. May be needed for validation, but not for production deployment.

**Directories**:
- `Historical Data/` (65MB)
- `testing_area/Historical Data/` (included in testing_area archive)

**Commands**:
```bash
mkdir -p archive/2025-11-16/data
mv "Historical Data" archive/2025-11-16/data/ 2>/dev/null || true
```

---

### Category 7: Phase Documentation (Historical)

**Action**: **ARCHIVE** to `archive/2025-11-16/phase_docs/`

**Rationale**: Phase status documents are historical records of development. Not needed for production but useful for reference.

**Files to Archive**:
- All `PHASE*_STATUS.md` files in root
- All `PHASE*_PROGRESS.md` files in root
- `PHASE4_DAY*_STATUS.md` files in root
- `QUICK_STATUS.md`
- `SYSTEM_AUDIT_REPORT.md` (may be useful — **REVIEW**)

**Note**: Phase docs in `boonmindx_capital_shield/` should **KEEP** (they're part of the Capital Shield documentation).

**Commands**:
```bash
mkdir -p archive/2025-11-16/phase_docs
mv PHASE4_DAY*_STATUS.md archive/2025-11-16/phase_docs/ 2>/dev/null || true
mv QUICK_STATUS.md archive/2025-11-16/phase_docs/ 2>/dev/null || true
# SYSTEM_AUDIT_REPORT.md — REVIEW
```

---

### Category 8: Template Files (Root Level)

**Action**: **REVIEW** — May want to keep or move to `boonmindx_capital_shield/docs/`

**Rationale**: Some template files are in root but may belong with Capital Shield docs.

**Files to Review**:
- `API_PRODUCTIZATION_PLAN.md` — Product plan (may be useful)
- `MULTI_PRODUCT_ROADMAP.md` — Roadmap (may be useful)
- `RETAIL_PRICING_TIERS.md` — Pricing (may be useful)
- `COMMERCIAL_MODELS_TEMPLATE.md` — Template (may belong in Capital Shield)
- `PARTNER_MODELS_TEMPLATE.md` — Template (may belong in Capital Shield)
- `ENTERPRISE_REQUIREMENTS_CHECKLIST_TEMPLATE.md` — Template (may belong in Capital Shield)
- `LICENSING_FAQ_TEMPLATE.md` — Template (may belong in Capital Shield)
- `TECHNICAL_DD_*.md` — Technical DD templates (may belong in Capital Shield)

**Recommendation**: Move templates to `boonmindx_capital_shield/docs/` or archive if not needed.

---

### Category 9: Old Templates/Directories

**Action**: **ARCHIVE** or **DELETE**

**Rationale**: Old template directories that may be superseded.

**Directories**:
- `templates/` — Old Flask templates (superseded by Capital Shield dashboard)
- `static/` — Old static files (superseded by Capital Shield dashboard)
- `tests/` (root level) — Old tests (superseded by Capital Shield tests)
- `logs/` — Old logs directory (should be empty, verify)

**Commands**:
```bash
mkdir -p archive/2025-11-16/legacy_web
mv templates archive/2025-11-16/legacy_web/ 2>/dev/null || true
mv static archive/2025-11-16/legacy_web/ 2>/dev/null || true
mv tests archive/2025-11-16/legacy_code/ 2>/dev/null || true
# logs/ — Verify empty, then delete or archive
```

---

### Category 10: Unclear Files

**Action**: **REVIEW** before action

**Files**:
- `🐻⚔️ BEAR HUNTER TRADING SYSTEM (1).txt` — Large text file (110KB), unclear content
- `4 Trading Bots (1).txt` — Unclear content
- `4` (92KB) — Unclear what this is
- `MontyCarloTest15Nov.txt` — Test dataset (may be needed for Capital Shield)

**Recommendation**: Review contents, then decide ARCHIVE/DELETE/KEEP.

---

## Summary of Actions

| Category | Action | Count | Size Impact |
|----------|--------|-------|-------------|
| Financial Forecasts | ARCHIVE | ~12 files | ~100KB |
| Legacy Code | ARCHIVE | ~15 files | ~100KB |
| Experimental Code | ARCHIVE | 1 directory | 305MB |
| Backtest Results | ARCHIVE | 1 directory + files | ~10MB |
| Large Bloat | DELETE | ~4 files | ~4MB |
| Historical Data | ARCHIVE | 1 directory | 65MB |
| Phase Docs | ARCHIVE | ~10 files | ~50KB |
| Templates | REVIEW | ~10 files | ~50KB |
| Legacy Web | ARCHIVE | 3 directories | ~100KB |
| Unclear Files | REVIEW | 4 files | ~200KB |

**Total Size Reduction**: ~384MB (mostly from testing_area/ and Historical Data/)

---

## Safety Checks Before Execution

1. ✅ **Backup**: Ensure git repository is backed up
2. ✅ **Verify**: No uncommitted changes
3. ✅ **Review**: All REVIEW items decided
4. ✅ **Secrets**: Verify no secrets in files to be archived
5. ✅ **Dependencies**: Verify no broken imports after cleanup

---

## Execution Order

1. Create archive structure
2. Archive investor docs (Category 1)
3. Archive legacy code (Category 2)
4. Archive experimental code (Category 3)
5. Archive backtest results (Category 4)
6. Delete bloat files (Category 5)
7. Archive historical data (Category 6)
8. Archive phase docs (Category 7)
9. Review and handle templates (Category 8)
10. Archive legacy web (Category 9)
11. Review unclear files (Category 10)
12. Final verification

---

## Post-Cleanup Verification

After cleanup, verify:
- ✅ `boonmindx_capital_shield/` is intact
- ✅ All tests still pass
- ✅ README.md points to correct locations
- ✅ No broken imports
- ✅ `.gitignore` is still correct
- ✅ No secrets in archived files

---

## Rollback Plan

If cleanup causes issues:
1. All archived files are in `archive/2025-11-16/`
2. Can restore with: `mv archive/2025-11-16/* .`
3. Deleted files (logs) can be regenerated if needed

---

**Status**: ⚠️ **AWAITING APPROVAL**  
**Next Step**: Review `FILE_ACTIONS.csv` for complete file-by-file classification, then approve this plan.
