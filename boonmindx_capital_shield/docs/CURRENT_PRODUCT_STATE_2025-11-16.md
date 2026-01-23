# Current Product State — 16 November 2025

This document answers key reality-vs-narrative questions with the most accurate “now” status. Where unknown or undecided, it says so explicitly.

---

## 1) Reality vs Narrative

- Canonical status source (current truth): `TECH_OVERVIEW_MASTER.md`, `PHASE4_COMPLETE_SUMMARY.md`, `PHASE4_PROGRESS.md`, `SCALABILITY_BENCHMARKS.md`, `BENCHMARK_EXECUTION_NOTES.md`.
- Aspirational narratives: investor-facing placeholders (deck/FAQ templates) and any BearHunter Prime Q&A that references future-state items (AWS fleet, FCA timelines, 30+ year team).
- Action: Treat Capital Shield docs as the true current status. Any BearHunter Q&A claims that exceed these should be marked “target state”.

Team reality:
- Named advisors (e.g., “Dr. Sarah Chen”, “Brevan CRO”, “LSE professor”): status unknown. They appear as placeholders unless explicitly confirmed.
- Action: Decide which names are real, whether approvals exist, and remove or mark placeholders until confirmed.

Regulation / FCA:
- Capital Shield (now): analytics layer, no regulatory filings; not an RIA/broker. That is the truthful, compliant position today.
- BearHunter Prime (future): any FCA review/licensing statements are target-state unless there is active engagement (unknown).
- Action: Keep “no regulatory filings yet” for Shield; decide BearHunter regulatory claims after legal consultation.

Infra stack:
- Current: FastAPI app + scripts; staging/deploy templates ready; no evidence of a live AWS cluster in repo. Actual running host/provider not declared in git.
- Investor framing: Present AWS stack as planned reference architecture; do not claim migration is complete.
- Action: Declare the real current host/provider (VPS/cloud), or keep redacted and state “staging server live; provider redacted”.

---

## 2) BearHunter Engine — Shape & Status

Detectors:
- Six conceptual detectors listed: volatility_shock, momentum_crisis, correlation_breakdown, liquidity_stress, entropy_spike, institutional_panic.
- Implementation status: not inventoried in code here (unknown). Likely conceptual/pseudocode unless stated elsewhere.
- Action: Inventory implemented vs conceptual and note data inputs.

“Independence” math (<1e-27 FN):
- Formal derivation not present in repo (unknown).
- Recommendation: move to “hypothetical upper bound” language for DD until a derivation is documented.

Detection windows:
- Not codified here (unknown). Time horizons (30m/1D/5D) and cross-asset inputs need specification.
- Action: Define canonical horizons and whether cross-asset signals are mandatory.

Alpha vs risk:
- Shield positioned as pure risk rail; BearHunter as alpha layer.
- Current truth: alpha side unspecified here; likely extinction-only at present.
- Action: Confirm alpha scope/timeline; keep Shield presented as analytics-only in v1.

---

## 3) Capital Shield Core — Positioning

Observer-coupled narrative:
- External (investors): keep deterministic, “boringly engineering” terminology; omit Ω/BUE physics.
- Internal: free to align with Ω/BUE concepts for design, but do not surface externally unless agreed.

Asset universe:
- Current runs appear crypto-heavy; indices/equities referenced in narratives as targets.
- Truthful phrasing: “Validated on synthetic + crypto/equity OHLCV; expanding to indices/FX/commodities.”

Guardrail presets:
- Presets exist (CONSERVATIVE/BALANCED/AGGRESSIVE).
- Decision needed: default preset for first integrations; whether presets are documented publicly or client-configured privately.

Role boundaries:
- Shield does not execute or hold funds; analytics-only is the v1 truth.
- Future execution product: TBD. Keep Shield boundary firm for now.

---

## 4) Quant & Validation

FP / OC / Execution:
- Scripts exist and have been run in this environment previously with reports regenerated. Exact trusted datasets need listing.
- Action: Identify which specific runs are investor-appendix-ready.

Monte Carlo Round 2 (30m, 5%, 10K):
- Status: sandbox experiment for harness verification; dataset currently includes 4 synthetic assets; results exist under `reports/monte_carlo_round2/`.
- Recommendation: Treat as “non-canonical, illustrative”; do not lean on for investor performance claims.

RSA formula (A/B/C/D):
- Preferred variant not declared (unknown).
- Guidance: choose a definition that blends terminal equity with max drawdown (survival-aware), then lock for consistency.

Black swan tests:
- Policy not fixed. Decide extremes (halts, haircuts) and whether to include at least one failure case for honesty.

---

## 5) Product & GTM

Business model wedge:
- Not chosen yet (unknown). Options: SaaS per engine; enterprise on-prem; % AUM; hybrid.

First 3 customer archetypes:
- Not specified. Choose concrete targets (e.g., crypto quant, prop, multi-asset funds).

GTM constraints:
- Regions and disallowed deal types not defined. Recommend defining upfront (e.g., avoid US retail initially).

Pricing:
- Prior anchors referenced (£50k/yr) in BearHunter narrative. Shield SaaS could support lower entry tiers (£1–5k/m) for early logos; decision pending.

---

## 6) Architecture & Integration

BearHunter–Shield integration:
- Present state: adapters exist; mock fallbacks used when BearHunter absent.
- Decision: separate service calls Shield vs same-process library vs multi-engine calling a central Shield API.

Broker/exchange target:
- Not specified. Pick first pilot venue (IBKR vs regulated crypto exchange).

Health rail in production:
- Decide extra signals (broker connectivity, exchange status, cloud region health, data vendor status).
- Format: single `health_score` vs structured flags.

---

## 7) Story, IP, Brand

Ω/BUE in product story:
- External: keep minimal; mention only design philosophy if desired.
- Internal: maintain alignment for coherence.

Patent vs open-source:
- Decide what to keep proprietary (multi-axis extinction math, RSA) vs open-source (API skeleton, load harness).

Brand alignment:
- Choose: standalone “Capital Shield / BearHunter” vs “BoonMindX Capital Shield (by BoonMind)”.

---

## 8) Immediate TODOs (Decisions Required)

See `TODO_CURRENT_PRODUCT_STATE_2025-11-16.md` for an actionable list mirroring the open decisions above. 

