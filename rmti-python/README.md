# Risk Mechanism Theory Index (RMTI)

**v2.1.0.** v2.1.0 changes only the wording of the HCC module's posture text
(now oncology vocabulary) and adds an optional `postures` argument; no number
changes. See `CHANGELOG.md` for exactly what changed since the archived 1.0.0
release and why. If you have code depending on 1.0.0, read it before
upgrading: this release changes at least one computed output value (a
binary-float rounding bug fix), corrects two case-study inputs, and
unifies licensing across the whole RMTI project under Apache 2.0.

Reference implementation of the Risk Mechanism Theory Index (RMTI), Marolla
(2025), "RMTI: A Systemic Risk Mechanism Design and Theory Framework." This
repository holds the shared mathematical core once, and applies it across
domains: urban infrastructure/climate risk and hepatocellular carcinoma
(HCC) surveillance triage, with a generalized multi-hazard extension shared
by both.

## Framework

RMTI scores residual risk for an asset, patient, or cohort using a fixed
indicator backbone (Table 9.4):

| Symbol | Meaning | Effect on R |
|---|---|---|
| E | Exposure (RMTre) | raises R |
| V | Vulnerability (RMTseen) | raises R |
| ρ | Resilience / treatment capacity (RMTrl) | lowers R, via (1 − ρ) |

Core equations:

- Eq. (1)/(2): `IR = L * E * V`, `R = IR * (1 - rho)`
- Eq. (3): `R = sum_h,c  w_c * L_h * E_h,c * V_h,c * (1 - rho_h,c)` — multi-factor/multi-category generalization
- Eq. (4): advisory log-normalized exposure baseline from population/cohort size N
- Eq. (5)/(6): Expected Annual Loss, `EAL = L * C * (1 - rho)`, and its multi-factor generalization
- Eq. (7): per-capita / per-patient equity rate

Risk scores map to five fixed, pre-registered tiers (Table 3: Low, Moderate,
High, Severe, Critical) and consequence severity uses a fixed five-level
scale (Table 2). These tables are never re-derived per sample — that fixity
is what lets an R score mean the same thing across every application.

## Repository structure

```
rmti-framework/
├── core/
│   └── rmti_core.py         # shared equations, tables, validated core, multi-factor extension
├── disaster_climate/
│   └── rmti_ssa.py          # disaster/climate application: eight-asset cohort
├── oncology/
│   └── rmti_hcc.py          # HCC surveillance-triage application
├── tests/
│   └── test_rmti.py         # automated reproducibility suite, 37 assertions
├── docs/
│   └── LICENSE-DOCS.md      # code vs. teaching-material licensing scope
├── CHANGELOG.md
├── CITATION.cff
├── NOTICE                   # attribution notice (Apache 2.0 §4(d))
├── LICENSE                  # Apache 2.0 — governs everything in this repo
└── README.md
```

Domain modules import shared logic from `core.rmti_core` rather than
duplicating it, so a validated fix or extension to the equations propagates
to every application automatically. (This was not true of the archived
1.0.0 release — see `CHANGELOG.md`.)

## Quick start

```bash
git clone https://github.com/drmarolla/Risk-Mechanism-Theory-Index-RMTI-.git
cd Risk-Mechanism-Theory-Index-RMTI-
python -m unittest tests.test_rmti -v          # 37 tests, expect 0 failures
python disaster_climate/rmti_ssa.py            # eight-asset cohort + multi-hazard demo
python oncology/rmti_hcc.py                    # six published cohorts + Pearl protocol
```

```python
from core.rmti_core import assess

result = assess(N=1_100_000, L=0.875, E_sel=0.800, V=0.800,
                 rho_now=0.25, rho_after=0.48, C=4)
print(result["R_now"], result["tier_now"])   # 0.42 Tier 4 - Severe
print(result["R_after"], result["tier_after"])  # 0.291 Tier 3 - High
print(result["IEI"])                          # investment efficiency index
```

## Applications in this repository

- **`disaster_climate/`** — validated against an eight-asset cohort: the
  six-city Sub-Saharan Africa portfolio (Bamako, Lagos, Lilongwe, Nairobi,
  Dar es Salaam, Lusaka; World Bank AFRI-RES compendium, 2023) plus the
  January 2025 California wildfire cases (Pacific Palisades, Altadena),
  with a multi-hazard/multi-category extension (Eq. 3/5). Companion
  manuscript: "From Narrative to Algorithm: A Risk Mechanism Theory Index
  for Urban Infrastructure Investment in Sub-Saharan Africa" (Marolla,
  submitted to Natural Hazards, manuscript NHAZ-D-26-03050).
- **`oncology/`** — hepatocellular carcinoma (HCC) surveillance-triage
  application of the same framework: six published cohorts and six
  Pearl-protocol aetiologies, ALBI-derived cohort vulnerability, and the
  within-tier EAL priority-reversal worked example.

## License

Apache License 2.0, covering everything in this repository **and** the
companion RMTI Calculator workbook and both interactive sandboxes
(oncology/public-health surveillance and disaster/climate) — code, rubric
text, tier descriptions, and worked examples alike, with no exceptions.
See `LICENSE` for the full text and `NOTICE` for attribution. Earlier
internal drafts (never published to Zenodo) split code from teaching
materials under different terms; that split was retired in v2.0.0 — see
`docs/LICENSE-DOCS.md` for that history if you're reconciling an old
citation against this one.

## Related registrations

- Zenodo archive (this repository, concept DOI, always resolves to latest):
  https://doi.org/10.5281/zenodo.21445892
- OSF registration (oncology application): link
- OSF registration (disaster/climate application): link

## Citation

See `CITATION.cff`. If you use this framework or its data, please cite both
the source paper and this software record.
