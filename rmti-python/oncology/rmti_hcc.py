# Copyright 2026 Cesar Marolla
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
rmti_hcc.py -- Reference implementation of the Risk Mechanism Theory Index
(RMTI) for hepatocellular-carcinoma (HCC) surveillance triage.

RMTI-Py computes the same bounded, fixed-tier score as the open spreadsheet
calculator, in a form that can be embedded in registries, electronic health
records, and reproducible research pipelines.

    IR  = L * E * V                     Eq. (1)
    R   = IR * (1 - rho)                Eq. (2) -- residual decision score
    EAL = L * C * (1 - rho)             Eq. (6) -- expected-annual-loss index

All terms are bounded on [0, 1]. Tiers and anchor tables are pre-registered
and identical for every patient and every run.

CHANGELOG (v2.1.0)
-------------------------------------------------------------------------
Changed -- oncology vocabulary. assess_patient() and rank_cohort_hcc() used
to report the shared infrastructure posture text ("Structured mitigation;
fund soon", "Priority capital; act now"), which is wrong for a clinical
cohort. They now use HCC_TIER_POSTURE, a surveillance-programme vocabulary
(usual-care surveillance, adherence, navigation, specialist follow-up).
Only the wording changes; tier thresholds and every number are identical.
Consistent with the rest of this module: per-capita equity is reported per
1,000,000 at-risk patients (core.assess), and the advisory E_log helper uses
N_MIN_HCC = 100 / N_MAX_HCC = 5,000,000; the companion workbook and sandbox
now use the same units and bounds.

CHANGELOG (v1.1.0, relative to the archived v1.0.0 release)
-------------------------------------------------------------------------
Fixed -- forked tier logic. The archived module redefined its own
TIER_BANDS and tier() purely to get "1 Low" instead of core's
"Tier 1 - Low", in direct violation of core.rmti_core's own "do not fork
these functions per domain" instruction, and flagged in the framework
README as a known inconsistency to resolve before publication. Tier
thresholds now come from core.rmti_core.TIER exclusively; only the label
*text* is reformatted for this module's published output style.

Fixed -- inconsistent consequence encoding. The archived module took C as
a raw float looked up in a local C_LADDER (e.g. C=0.30), while the
corrected core-based score() expects the Table 2 integer index C in
{1..5}. C_LADDER now maps each BCLC stage name to that integer index, so
both domains use exactly one consequence table (core.C_INFRA).

Fixed -- rounding. score_patient() previously used core's *unfixed*
score(), a binary-float round(). Now calls the Decimal-exact score() in
core.rmti_core (see that module's changelog for the 0.0585 -> 0.059
worked example).

Fixed -- missing post-treatment state. The archived score_patient()/
rank_cohort() computed only a single (baseline) state: there was no way
to represent "R after a surveillance-improvement package" in code at all,
even though that is exactly what the manuscript's Table 2 reports (R_now
vs R_after for six published cohorts). assess_patient() below wraps
core.assess() to add rho_after, risk_reduction_pct, and per-patient
equity, matching the manuscript's full table, not just its first column.

Fixed -- global priority numbering. rank_cohort() previously assigned a
flat 1..n sequence across the whole cohort. Priority is now assigned
WITHIN each tier (resets at every tier boundary), matching this module's
own docstring ("orders by tier, then by EAL -- within-tier priority") and
the RMTI Calculator workbook's COUNTIFS priority columns. This fix lives
in core.rank_cohort(), which this module now calls instead of forking.
-------------------------------------------------------------------------

(c) 2025 Cesar Marolla. Developed for ENVR E-241 / RMTI-HCC.
"""
from __future__ import annotations
from dataclasses import dataclass

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.rmti_core import (  # noqa: E402
    e_log, tier as _core_tier, posture, score, assess, rank_cohort, C_INFRA,
    TIER,
)

__version__ = "2.1.0"

# ---- Pre-registered anchor tables (HCC-specific) -----------------------------
# Consequence C: stage at which a missed tumour would be detected (BCLC),
# mapped to the Table 2 integer index so it composes with core.C_INFRA
# exactly like the infrastructure domain's C in {1..5}. C_INFRA[index] gives
# the same 0-1 severity value the manuscript's Table 2 / Eq. 6 uses:
#   1 -> 0.10  BCLC 0          (very early, curable)
#   2 -> 0.30  BCLC A          (early, curative)
#   3 -> 0.50  early-intermediate (constrained)
#   4 -> 0.75  BCLC B          (intermediate, TACE)
#   5 -> 1.00  BCLC C-D        (advanced, fatal)
C_LADDER = {"BCLC0": 1, "BCLC_A": 2, "EARLY_INT": 3, "BCLC_B": 4, "BCLC_CD": 5}

# Vulnerability V from liver reserve (ALBI grade). ALBI is computed directly
# from measured serum albumin and total bilirubin (manuscript Sec. 3.2).
ALBI_V = {1: 0.35, 2: 0.60, 3: 0.85}

# Resilience rho: published surveillance-effectiveness ladder (manuscript
# Table 5 / Extended Data). Advisory reference points, not a categorical
# lookup -- practitioners enter a continuous rho per their own assessment.
RHO_ANCHORS = {"none": 0.15, "usual": 0.20, "outreach": 0.45,
               "specialist": 0.50, "optimised": 0.65}

# Posture text by fixed tier, in HCC-surveillance vocabulary. Keys are core's
# tier labels so thresholds are never forked. These describe how intensively
# the surveillance programme is engaged for a patient or cohort at that tier;
# they are a decision-support reading, not a treatment recommendation, and
# the RMTI-HCC application is not validated against prospective incident HCC.
HCC_TIER_POSTURE = {
    "Tier 1 - Low":      "Monitor; usual-care biannual surveillance appropriate",
    "Tier 2 - Moderate": "Usual-care biannual surveillance appropriate; confirm adherence and recall",
    "Tier 3 - High":     "Prioritise for surveillance; fixed-interval adherence essential",
    "Tier 4 - Severe":   "Structured navigation; close specialist hepatology follow-up",
    "Tier 5 - Critical": "Immediate, resourced pathway; case management",
}
assert list(HCC_TIER_POSTURE) == [lbl for _, lbl in TIER]   # one entry per fixed tier


def hcc_posture(R: float) -> str:
    """Surveillance-posture text for the tier containing R (HCC vocabulary)."""
    return posture(R, HCC_TIER_POSTURE)


N_MIN_HCC = 100          # smallest plausible at-risk cohort
N_MAX_HCC = 5_000_000    # national-scale cirrhosis population ceiling


def short_tier(R: float) -> str:
    """Map residual score R to this module's published label format
    ("1 Low" rather than core's "Tier 1 - Low"), without forking the
    underlying thresholds -- both come from core.rmti_core.TIER."""
    label = _core_tier(R)                      # e.g. "Tier 3 - High"
    n, _, rest = label.partition(" - ")
    return f"{n.replace('Tier ', '')} {rest}"  # "3 High"


def exposure_from_population(n: float) -> float:
    """Log-normalised at-risk population -> bounded exposure helper E in
    [0, 1]. Uses HCC-appropriate bounds (a national at-risk cirrhosis
    population, not a city) via core.e_log's n_min/n_max override, so the
    disaster/climate module's N_MIN=10 / N_MAX=20,000,000 city anchors are
    not silently reused for a clinical cohort size."""
    return e_log(n, n_min=N_MIN_HCC, n_max=N_MAX_HCC)


def albi_to_v(grade: int) -> float:
    """ALBI grade (1-3) -> Vulnerability V."""
    return ALBI_V[grade]


def albi_cohort_v(grade_counts: dict) -> float:
    """Cohort-mean Vulnerability from a distribution of ALBI grades:
    V = sum(p_g * anchor_g). grade_counts e.g. {1: 9, 2: 19, 3: 1}."""
    n = sum(grade_counts.values())
    if n == 0:
        raise ValueError("grade_counts must contain at least one patient")
    return round(sum(ALBI_V[g] * c for g, c in grade_counts.items()) / n, 4)


@dataclass
class RMTIResult:
    inherent: float      # L * E * V
    R: float             # residual decision score
    tier: str
    EAL: float           # expected-annual-loss index

    def __repr__(self):
        return (f"R={self.R:.3f} ({self.tier})  "
                f"inherent={self.inherent:.3f}  EAL={self.EAL:.3f}")


def score_patient(L: float, E: float, V: float, rho: float, C: int = 5) -> RMTIResult:
    """Score one patient at a single point in time (baseline OR
    post-treatment -- call twice to get both, or use assess_patient()
    for the paired before/after form the manuscript reports).

    L   - annual HCC incidence from a validated score (aMAP/THRI/hccrisk.com)
    E   - share of the at-risk population reached by surveillance, or the
          population helper from exposure_from_population()
    V   - liver-reserve vulnerability; use albi_to_v() or albi_cohort_v()
    rho - surveillance adequacy; use RHO_ANCHORS as reference points
    C   - Table 2 integer index 1-5 (use C_LADDER for the BCLC stage name);
          default 5 (BCLC C-D / advanced) matches the archived module's
          "severe by default" behaviour for an unspecified stage
    """
    for name, x in dict(L=L, E=E, V=V, rho=rho).items():
        if not 0.0 <= x <= 1.0:
            raise ValueError(f"{name}={x} is outside [0, 1]")
    if C not in C_INFRA:
        raise ValueError(f"C={C} must be a Table 2 index in {{1,2,3,4,5}}; "
                          f"use C_LADDER to map a BCLC stage name to this index")
    result = score(L, E, V, rho, C)
    return RMTIResult(result["IR"], result["R"], short_tier(result["R"]), result["EAL"])


def assess_patient(N, L, E, V, rho_now, rho_after=None, C=5):
    """Full patient/cohort assessment: baseline state, optional
    post-surveillance-improvement state, risk-reduction %, investment
    (treatment) efficiency, and per-patient equity rate -- the paired
    before/after form the manuscript's Table 2 reports for six published
    cohorts. Thin, HCC-appropriately-bounded wrapper around core.assess();
    see that function for the field list.

    New in v1.1.0 -- the archived score_patient()/rank_cohort() had no way
    to represent rho_after at all. New in v2.1.0 -- posture_now/posture_after
    are worded for HCC surveillance (HCC_TIER_POSTURE), and equity is per
    1,000,000 at-risk patients.
    """
    out = assess(N, L, E, V, rho_now, rho_after, C,
                 n_min=N_MIN_HCC, n_max=N_MAX_HCC, postures=HCC_TIER_POSTURE)
    out["tier_now"] = short_tier(out["R_now"])
    if "R_after" in out:
        out["tier_after"] = short_tier(out["R_after"])
    return out


def rank_cohort_hcc(patients: dict) -> list:
    """Score and rank a cohort/registry of patients: primary sort by tier
    severity, secondary sort by EAL descending, with priority reset within
    each tier (core.rank_cohort -- see that function's v1.1.0 changelog
    for the global-numbering bug this replaces).

    patients: dict of name -> kwargs accepted by assess_patient(), e.g.
        {"Patient A": dict(N=100_000, L=0.30, E=0.60, V=0.50,
                            rho_now=0.20, C=2), ...}
    """
    clean = {}
    for name, kwargs in patients.items():
        row = {**kwargs, "n_min": N_MIN_HCC, "n_max": N_MAX_HCC,
               "postures": HCC_TIER_POSTURE}
        if "E" in row:
            row["E_sel"] = row.pop("E")
        clean[name] = row
    ranked = rank_cohort(clean)
    for r in ranked:
        r["tier_now"] = short_tier(r["R_now"])
        if "R_after" in r:
            r["tier_after"] = short_tier(r["R_after"])
    return ranked


# ---------------------------------------------------------------------------
# REAL DATA -- six published cohorts (manuscript Table 2) and six
# Pearl-protocol aetiologies (manuscript Table 3).
# ---------------------------------------------------------------------------
PUBLISHED_COHORTS = {
    "Untreated HBV":          dict(N=100_000, L=0.90, E=0.70, V=0.55,
                                    rho_now=0.10, rho_after=0.45, C=5,
                                    incidence="~12.8%/yr (historical)"),
    "Active viral cirrhosis": dict(N=100_000, L=0.55, E=0.70, V=0.53,
                                    rho_now=0.50, rho_after=0.65, C=5,
                                    incidence="2-7%/yr"),
    "Alcohol cirrhosis":      dict(N=100_000, L=0.30, E=0.65, V=0.60,
                                    rho_now=0.20, rho_after=0.50, C=5,
                                    incidence="1-2.5%/yr"),
    "Cured-HCV cirrhosis":    dict(N=100_000, L=0.25, E=0.60, V=0.48,
                                    rho_now=0.20, rho_after=0.55, C=5,
                                    incidence="~1.8%/yr"),
    "Suppressed-HBV":         dict(N=100_000, L=0.20, E=0.55, V=0.45,
                                    rho_now=0.20, rho_after=0.55, C=5,
                                    incidence="~1.25%/yr"),
    "NAFLD cirrhosis":        dict(N=100_000, L=0.15, E=0.60, V=0.53,
                                    rho_now=0.20, rho_after=0.50, C=5,
                                    incidence="~1.06%/yr"),
}

# Pearl-protocol aetiologies, compensated-cirrhosis Exposure (0.60) and
# Vulnerability (0.50) held fixed; only surveillance adequacy varies.
PEARL_COHORTS = {
    "MASLD cirrhosis (compensated)": dict(N=100_000, L=0.15, E=0.60, V=0.50,
                                           rho_now=0.20, rho_after=0.65, C=5,
                                           incidence="~1.0%/yr"),
    "Suppressed HBV":                dict(N=100_000, L=0.20, E=0.60, V=0.50,
                                           rho_now=0.20, rho_after=0.65, C=5,
                                           incidence="~1.25%/yr"),
    "HCV post-SVR":                  dict(N=100_000, L=0.25, E=0.60, V=0.50,
                                           rho_now=0.20, rho_after=0.65, C=5,
                                           incidence="~1.8%/yr"),
    "Alcohol cirrhosis (Pearl)":     dict(N=100_000, L=0.30, E=0.60, V=0.50,
                                           rho_now=0.20, rho_after=0.65, C=5,
                                           incidence="~2%/yr"),
    "Active viral (Pearl)":          dict(N=100_000, L=0.55, E=0.60, V=0.50,
                                           rho_now=0.20, rho_after=0.65, C=5,
                                           incidence="2-7%/yr"),
    "High-burden MASLD":             dict(N=100_000, L=0.65, E=0.60, V=0.50,
                                           rho_now=0.20, rho_after=0.65, C=5,
                                           incidence="~5%/yr"),
}


def _scoreable(cohort):
    out = {}
    for name, row in cohort.items():
        clean = {k: v for k, v in row.items() if k != "incidence"}
        out[name] = clean
    return out


if __name__ == "__main__":
    print("=" * 70)
    print("PART 1 -- six published cohorts (manuscript Table 2)")
    print("=" * 70)
    ranked = rank_cohort_hcc(_scoreable(PUBLISHED_COHORTS))
    for r in ranked:
        print(f"{r['priority_in_tier']}. {r['name']:<24} R_now={r['R_now']:.3f} "
              f"[{r['tier_now']}]  R_after={r.get('R_after','--')} "
              f"[{r.get('tier_after','--')}]  reduction={r.get('risk_reduction_pct','--')}%  "
              f"EAL_now={r['EAL_now']:.3f}")

    print()
    print("=" * 70)
    print("SELF-CHECK -- reproduce the manuscript's own Table 2 exactly")
    print("=" * 70)
    checks = [
        ("Untreated HBV", "R_now", 0.312), ("Untreated HBV", "R_after", 0.191),
        ("Active viral cirrhosis", "R_now", 0.102), ("Active viral cirrhosis", "R_after", 0.071),
        ("Alcohol cirrhosis", "R_now", 0.094), ("Alcohol cirrhosis", "R_after", 0.059),
        ("Cured-HCV cirrhosis", "R_now", 0.058), ("Cured-HCV cirrhosis", "R_after", 0.032),
        ("Suppressed-HBV", "R_now", 0.040), ("Suppressed-HBV", "R_after", 0.022),
        ("NAFLD cirrhosis", "R_now", 0.038), ("NAFLD cirrhosis", "R_after", 0.024),
    ]
    by_name = {r["name"]: r for r in ranked}
    all_ok = True
    for name, field, expected in checks:
        got = by_name[name][field]
        ok = abs(got - expected) < 0.001
        all_ok &= ok
        print(f"  {name:<24} {field:<8} expected={expected:<6} got={got:<6} "
              f"{'OK' if ok else 'MISMATCH'}")
    print(f"\nAll checks passed: {all_ok}")
    print("(This is the case that the archived v1.0.0 float-round() bug got "
          "wrong: Alcohol cirrhosis R_after is exactly 0.0585 in decimal, "
          "which must round to 0.059, not 0.058.)")

    print()
    print("=" * 70)
    print("PART 2 -- six Pearl-protocol aetiologies (manuscript Table 3)")
    print("=" * 70)
    ranked_pearl = rank_cohort_hcc(_scoreable(PEARL_COHORTS))
    for r in ranked_pearl:
        print(f"{r['priority_in_tier']}. {r['name']:<32} R_usual={r['R_now']:.3f} "
              f"[{r['tier_now']}]  R_optimised={r.get('R_after','--')} "
              f"[{r.get('tier_after','--')}]  reduction={r.get('risk_reduction_pct','--')}%")

    print()
    print("=" * 70)
    print("PART 3 -- within-tier EAL priority worked example (Sec. 2.6)")
    print("=" * 70)
    A = score_patient(L=0.30, E=0.60, V=0.50, rho=0.20, C=C_LADDER["BCLC_A"])   # post-SVR, curable if missed
    B = score_patient(L=0.25, E=0.60, V=0.55, rho=0.20, C=C_LADDER["BCLC_CD"])  # marginal reserve, fatal if missed
    print(f"Patient A (post-SVR, curable if missed):    {A}")
    print(f"Patient B (marginal reserve, fatal if missed): {B}")
    r_order = ">" if A.R > B.R else "<"
    eal_order = ">" if B.EAL > A.EAL else "<"
    print(f"R ranks A{r_order}B ; EAL ranks B{eal_order}A  -> EAL reverses within-tier priority")

    print()
    print("=" * 70)
    print("PART 4 -- ALBI cohort-mean Vulnerability (Faria et al. dataset)")
    print("=" * 70)
    hcc_grades = {1: 10, 2: 18, 3: 1}      # 35% / 62% / 4% of n=29
    cirr_grades = {1: 12, 2: 13, 3: 0}     # 48% / 52% / 0% of n=25
    V_hcc = albi_cohort_v(hcc_grades)
    V_cirr = albi_cohort_v(cirr_grades)
    print(f"  HCC cohort (n=29)       mean V = {V_hcc}  (manuscript reports 0.52)")
    print(f"  Cirrhosis cohort (n=25) mean V = {V_cirr}  (manuscript reports 0.48)")
