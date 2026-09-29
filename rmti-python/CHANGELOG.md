# Changelog

## [2.1.0] — 2026-09-28

Oncology-vocabulary and unit-consistency release. **No equation, tier
threshold, anchor value, or published number changes.** Only the wording of
the posture text reported by the HCC module changes, plus one new optional
parameter in the shared core. Every v2.0.0 numeric output is reproduced
exactly (the original 29 tests pass unchanged; 8 new tests were added).

### Changed

- **`oncology/rmti_hcc.py` — HCC surveillance vocabulary.** `assess_patient()`
  and `rank_cohort_hcc()` previously reported the shared infrastructure
  posture text ("Structured mitigation; fund soon", "Priority capital; act
  now"), which is wrong for a clinical cohort. They now report
  `HCC_TIER_POSTURE` (usual-care surveillance, adherence and recall,
  navigation, specialist hepatology follow-up, case management). Tier 1 and
  Tier 2 are now worded differently (both previously read "usual-care
  biannual surveillance appropriate" in the workbook). New helper:
  `hcc_posture(R)`. These are decision-support readings, not treatment
  recommendations; the HCC application is not validated against prospective
  incident HCC.

### Added

- **`core/rmti_core.py` — optional `postures` argument** on `posture()` and
  `assess()`, so a domain can report the fixed tier in its own vocabulary
  without forking `tier()` or the thresholds. Default is unchanged
  (`TIER_POSTURE`), so the disaster/climate module is unaffected.
- **Companion files aligned to this module:** the HCC workbook
  (`RMTI_HCC_Calculator_v2.1.0.xlsx`) and the oncology sandbox now use the
  same HCC population bounds (`N_MIN_HCC = 100`, `N_MAX_HCC = 5,000,000`),
  the same per-capita unit (EAL per 1,000,000 at-risk patients), and the same
  HCC posture text. Previously the workbook used 10 / 650,000 and per 100,000,
  and the sandbox used 10 / 650,000.

### Tests

- 37 tests (29 + 8): HCC posture table has one distinct entry per fixed tier
  and no infrastructure wording; default posture unchanged for other domains;
  HCC bounds and per-1,000,000 unit; within-tier EAL reversal worked example
  (Patient A 0.072 vs Patient B 0.200).

## [2.0.0] — 2026-09-26

Corrected, relicensed release. Consolidates the fixes originally prepared
for an internal "1.1.0" that was never separately published to Zenodo —
so this changelog entry covers everything from that unpublished draft
plus the two changes below it (the license unification and the Pacific
Palisades/Altadena data correction), all shipping together as one
release. Fixes a reproducibility bug that affects published table values,
a real ranking bug, an architectural violation the repository's own
README already flagged as needing resolution before publication, and
retires an earlier code-vs-teaching-materials license split in favor of
one uniform Apache 2.0 grant across the whole RMTI project. No equations
changed beyond the rounding-correctness fix below. Every fix is
independently verifiable by running `python -m unittest tests.test_rmti -v`
or the `__main__` block in any module.

### Fixed

- **`core/rmti_core.py` — binary-float rounding at exact decimal boundaries.**
  `score()` previously rounded `IR`/`R`/`EAL` with Python's built-in
  `round()` on binary floats. `0.30 * 0.65 * 0.60 * (1 - 0.50)` is exactly
  `0.0585` in decimal and must round `HALF_UP` to `0.059` — matching Excel
  and Table 2 of the HCC surveillance manuscript — but evaluates to
  `0.058499999999999996` in IEEE-754 float, so `round(x, 3)` silently
  returned `0.058`. `score()` now builds each product from the `Decimal`
  string representation of its inputs and rounds via `ROUND_HALF_UP`.
  This is the single change with the widest blast radius: any published
  figure landing on a `...5` boundary in the third decimal place was at
  risk, and the Alcohol cirrhosis `R_after` cell in the manuscript's
  own Table 2 is exactly such a case.

- **`oncology/rmti_hcc.py` — global priority numbering instead of
  within-tier.** `rank_cohort()` assigned a flat `1..n` sequence across
  the whole cohort. The module's own docstring, the manuscript's stated
  method, and the RMTI Calculator workbook's `COUNTIFS` priority columns
  all specify that priority resets at every tier boundary. Fixed by
  centralizing `rank_cohort()` in `core` (see below) with the reset logic
  implemented once.

- **`oncology/rmti_hcc.py` — forked tier logic.** The archived module
  redefined its own `TIER_BANDS` and `tier()` purely to change label
  *text* ("1 Low" vs. core's "Tier 1 - Low"). `core/rmti_core.py`'s own
  docstring says: "Do not fork these functions per domain — if a domain
  needs different behavior, extend via parameters, not copy-paste." This
  is also the "known tier-label inconsistency between the two
  applications" the repository README already flagged as needing
  resolution before final publication. Fixed: tier *thresholds* now come
  from `core.rmti_core.TIER` exclusively; a new `short_tier()` wrapper
  reformats only the label text for this module's published output style,
  so both applications provably share one set of thresholds.

- **`disaster_climate/rmti_ssa.py` — duplicated, not imported, core
  logic.** This module carried byte-for-byte copies of `score()`,
  `assess()`, `rank_cohort()`, `score_multi()`, and `assess_multi()`,
  independently inheriting the same rounding bug and unable to receive a
  fix to `core` without manual re-duplication. Fixed: this module now
  imports all scoring functions from `core.rmti_core` and retains only
  the domain-specific cohort data (`COHORT`) and the illustrative
  multi-hazard example.

- **`oncology/rmti_hcc.py` — no representation of a post-treatment
  state.** `score_patient()`/`rank_cohort()` computed a single point in
  time only; there was no `rho_after` parameter anywhere in the module,
  even though the manuscript's Table 2 reports paired `R_now`/`R_after`
  values for all six published cohorts and six Pearl-protocol
  aetiologies. Added `assess_patient()` and `rank_cohort_hcc()`, thin
  HCC-bounded wrappers around `core.assess()`/`core.rank_cohort()`, so
  the module can now reproduce Table 2 and Table 3 of the manuscript in
  full, not just their baseline columns.

- **`oncology/rmti_hcc.py` — inconsistent consequence encoding.** The
  archived `score_patient()` took `C` as a raw float from a local
  `C_LADDER` (e.g. `C=0.30`), incompatible with `core.score()`'s integer
  `1..5` Table 2 index. `C_LADDER` now maps each BCLC stage name to that
  integer index, so both domains share exactly one consequence table
  (`core.C_INFRA`).

- **ALBI-derived cohort Vulnerability worked example.** The `__main__`
  illustration used ALBI grade counts (`{1: 9, 2: 19, 3: 1}`) that do not
  correspond to the manuscript's stated 35% / 62% / 4% split of n = 29 and
  produced V = 0.531 rather than the published 0.52. Corrected to
  `{1: 10, 2: 18, 3: 1}` (35% / 62% / 4% exactly), which reproduces 0.522
  → 0.52.

- **`disaster_climate/rmti_ssa.py` — Pacific Palisades and Altadena carried
  unverified draft figures.** The two wildfire cases added below were
  copied from an early, uncorrected draft of the RMTI Calculator workbook.
  Two problems: (1) Altadena's `N=42,846` was that community's total
  census population, not the population within the Eaton Fire's hazard
  footprint — inconsistent with how `N` is defined everywhere else in this
  cohort, and with how Pacific Palisades' own `N` was derived; (2) `L=0.90`
  / `L=0.88` scored both fires as a near-annual-certainty hazard, which is
  inconsistent with `L`'s own definition (*annual* probability the hazard
  materially strikes the asset) — Very High Fire Hazard Severity Zone
  classification and a worsening drought/Santa Ana trend support an
  elevated `L`, not a value in the range this cohort otherwise reserves
  for near-certain seasonal monsoon flooding. Corrected against LAEDC
  Institute for Applied Economics (2025), Casey et al., *JAMA Health
  Forum* (2025), and a 2026 SSRN policy report on the Palisades Fire's
  institutional-failure record (`N`: 21,300 / 23,000 from each fire's own
  demographic-profile area; `L`: 0.40 for both, unified since both sit in
  the same Very High FHSZ classification and were driven by the same
  regional wind event; `rho_after`: 0.35 for both, down from 0.50/0.45,
  reflecting that only 2-3 of 7 identified structural policy gaps are
  actually enacted into law per that report's own status matrix). `E`, `V`
  and `C` were reviewed and left unchanged — see `test_pacific_palisades`
  and `test_altadena` for the resulting reference values, added below.

### Added

- `core.investment_efficiency()` — IEI = Δ risk ÷ (1 − ρ_after), matching
  the RMTI Calculator workbook's column Z. Uses the unrounded Δ fraction,
  not the displayed, rounded percentage (verified against Dar es Salaam:
  IEI = 1.111, not 1.11).
- `core.posture()` — returns the Table 3 recommended-action text for a
  given tier, so downstream applications don't need their own copy of
  the posture strings.
- `tests/test_rmti.py` — an automated suite (29 assertions) reproducing
  every published figure this changelog references, runnable via
  `python -m unittest` or `pytest`. Includes an explicit regression test
  for the 0.0585 → 0.059 rounding boundary and for within-tier priority
  reset, so these two bug classes cannot silently reappear.
- Two additional disaster/climate cases in `COHORT`: Pacific Palisades
  and Altadena (January 2025 California wildfires), present in the RMTI
  Calculator workbook but absent from the archived module.
- `NOTICE` — Apache 2.0 §4(d) attribution file naming Cesar Marolla as
  author (with ORCID), the source manuscripts, and the concept DOI.
  Every `.py` source file also now carries a standard Apache 2.0
  copyright/license header comment.

### License

- **Unified the entire RMTI project under Apache License 2.0, with no
  exceptions.** An internal draft of this repository previously split
  licensing: code under Apache 2.0, but rubric wording, tier descriptions,
  and any interactive sandbox built on the code marked all-rights-reserved
  (documented in `docs/LICENSE-DOCS.md`). That split is retired as of
  this release — the decision was to make the whole project, including
  the RMTI Calculator workbook and both interactive sandboxes, uniformly
  and permissively licensed. `docs/LICENSE-DOCS.md` is rewritten to
  record this history rather than to define an active boundary; `LICENSE`
  is now the single, complete grant for everything in this repository.

### Changed

- `e_log()` now clamps its result to `[0, 1]` internally (previously the
  clamp was left to callers in some code paths; the RMTI Calculator
  workbook's `MIN(1, MAX(0, ...))` behavior is now guaranteed by the
  function itself, regardless of caller).
- Version pin: `__version__ = "2.0.0"` set in all three modules.

### Verification

Every fix above is covered by an assertion in `tests/test_rmti.py`, and
every module's own `__main__` block re-prints and re-checks its published
table against the source manuscripts. Run:

```
python -m unittest tests.test_rmti -v
```

Expected: 29 tests, 0 failures.

## [1.0.0] — 2026-07-19

Initial Zenodo archive (10.5281/zenodo.21445893). Reference implementation
of the two-stage risk computation, EAL severity layer, log-normalized
exposure transform, and multi-hazard extension, applied to urban
infrastructure/climate risk and HCC surveillance triage.
