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
rmti_ssa.py -- RMTI-Py v1.1: disaster/climate application of the Risk
Mechanism Theory Index (RMTI), Marolla (2025), "RMTI: A Systemic Risk
Mechanism Design and Theory Framework" and the companion RMTI Calculator
(ENVR E-241, Risk by Design).

This module holds ONLY the domain-specific parts: the six-city
Sub-Saharan Africa cohort (World Bank AFRI-RES compendium) plus the
January 2025 California wildfire cases, and the illustrative multi-hazard
Lagos example. All scoring math (score, assess, rank_cohort, score_multi,
assess_multi, e_log, tier) is imported from core.rmti_core rather than
duplicated here.

CHANGELOG (v1.1.0, relative to the archived v1.0.0 release)
-------------------------------------------------------------------------
Fixed: this module previously carried its own copies of score()/assess()/
rank_cohort()/score_multi()/assess_multi(), byte-for-byte duplicating
core.rmti_core -- in violation of that module's own "do not fork, extend
via parameters" instruction, and independently inheriting the same
binary-float rounding bug (see core.rmti_core changelog). Those functions
are now imported directly, so a fix to core propagates here automatically
and cannot silently drift out of sync again.
-------------------------------------------------------------------------

Table 9.4 indicator backbone (fixed categories, Marolla 2018 pp.158-183):
    RMTre  (Risk Exposure)                         -> E   (raises R)
    RMTseen (Socio-Economic & Environmental Vuln.)  -> V   (raises R)
    RMTrl  (Resilience Level Capacity)              -> rho (lowers R, via 1-rho)

Table 3 (fixed, pre-registered risk tiers -- never re-derived from a
sample's own min/max):
    Tier 1 - Low       R < 0.05   Monitor
    Tier 2 - Moderate  0.05-0.15  Prevent
    Tier 3 - High      0.15-0.35  Mitigate
    Tier 4 - Severe    0.35-0.60  Intervene
    Tier 5 - Critical  R >= 0.60  Emergency

Table 2 (consequence scale C for the EAL severity layer):
    1  Insignificant  0.10   <50 people affected
    2  Minor          0.30   50-500
    3  Moderate       0.50   500-50,000
    4  Major          0.75   50,000-1,000,000
    5  Severe         1.00   >1,000,000
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.rmti_core import (  # noqa: E402
    e_log, tier, posture, score, assess, rank_cohort,
    score_multi, assess_multi, TIER, C_INFRA, RHO_TYPOLOGY_ANCHORS,
)

__version__ = "2.1.0"

# ---------------------------------------------------------------------------
# REAL DATA -- the six-city Sub-Saharan Africa cohort exactly as reported
# in Tables 4-6 (World Bank AFRI-RES compendium, World Bank 2023), plus the
# January 2025 California wildfire cases from the RMTI Calculator workbook.
# ---------------------------------------------------------------------------
COHORT = {
    "Bamako":        dict(N=4_500_000,  L=0.800, E_sel=0.850, V=0.750,
                           rho_now=0.20, rho_after=0.58, C=4,
                           country="Mali", hazard="Drought / seasonal Niger River flood / heatwave"),
    "Lagos":         dict(N=16_000_000, L=0.900, E_sel=0.650, V=0.800,
                           rho_now=0.20, rho_after=0.55, C=5,
                           country="Nigeria", hazard="Coastal & pluvial flood (transit corridors)"),
    "Lilongwe":      dict(N=1_100_000,  L=0.875, E_sel=0.800, V=0.800,
                           rho_now=0.25, rho_after=0.48, C=4,
                           country="Malawi", hazard="Pluvial / riverine flood"),
    "Nairobi":       dict(N=4_700_000,  L=0.900, E_sel=0.880, V=0.550,
                           rho_now=0.55, rho_after=0.65, C=4,
                           country="Kenya", hazard="Pluvial flood"),
    "Dar es Salaam": dict(N=7_400_000,  L=0.850, E_sel=0.930, V=0.780,
                           rho_now=0.55, rho_after=0.70, C=4,
                           country="Tanzania", hazard="Coastal flood"),
    "Lusaka":        dict(N=3_360_000,  L=0.800, E_sel=0.850, V=0.720,
                           rho_now=0.45, rho_after=0.60, C=3,
                           country="Zambia", hazard="Flood / cholera"),
    "Pacific Palisades": dict(N=21_300, L=0.400, E_sel=0.900, V=0.400,
                           rho_now=0.20, rho_after=0.35, C=4,
                           country="USA", hazard="Wildfire (WUI) -- Palisades Fire, Jan 2025"),
    "Altadena":      dict(N=23_000,     L=0.400, E_sel=0.800, V=0.600,
                           rho_now=0.20, rho_after=0.35, C=4,
                           country="USA", hazard="Wildfire (WUI) -- Eaton Fire, Jan 2025"),
}


def _scoreable_cohort(cohort):
    """Strip the metadata-only fields (country, hazard) before passing
    each row into assess(), which only accepts its named parameters."""
    clean = {}
    for name, row in cohort.items():
        clean[name] = {k: v for k, v in row.items() if k not in ("country", "hazard")}
    return clean


if __name__ == "__main__":
    import json

    print("=" * 70)
    print("PART 1 -- VALIDATED CORE: eight-asset cohort, ranked for capital "
          "sequencing")
    print("=" * 70)
    ranked = rank_cohort(_scoreable_cohort(COHORT))
    for r in ranked:
        meta = COHORT[r["name"]]
        print(f"{r['name']:<18} ({meta['country']:<10}) priority={r['priority_in_tier']}  "
              f"IR={r['IR']:.3f}  R_now={r['R_now']:.3f} [{r['tier_now']}]  "
              f"R_after={r.get('R_after', '--')}  "
              f"reduction={r.get('risk_reduction_pct', '--')}%  IEI={r.get('IEI', '--')}  "
              f"EAL_now={r['EAL_now']:.3f}  equity/1M={r['equity_now_per_1M']:.4f}")

    print()
    print("=" * 70)
    print("SELF-CHECK -- reproduce the paper's own reported figures exactly "
          "(Tables 4-6) and the RMTI Calculator workbook")
    print("=" * 70)
    checks = [
        ("Bamako",        "R_now", 0.408), ("Bamako",        "R_after", 0.214),
        ("Lagos",         "R_now", 0.374), ("Lagos",         "R_after", 0.211),
        ("Lilongwe",      "R_now", 0.420), ("Lilongwe",      "R_after", 0.291),
        ("Nairobi",       "R_now", 0.196), ("Nairobi",       "R_after", 0.152),
        ("Dar es Salaam", "R_now", 0.277), ("Dar es Salaam", "R_after", 0.185),
        ("Dar es Salaam", "IEI",   1.111),
        ("Lusaka",        "R_now", 0.269), ("Lusaka",        "R_after", 0.196),
        ("Pacific Palisades", "R_now", 0.115), ("Pacific Palisades", "R_after", 0.094),
        ("Altadena",          "R_now", 0.154), ("Altadena",          "R_after", 0.125),
    ]
    by_name = {r["name"]: r for r in ranked}
    all_ok = True
    for name, field, expected in checks:
        got = by_name[name][field]
        ok = abs(got - expected) < 0.001
        all_ok &= ok
        print(f"  {name:<15} {field:<8} expected={expected:<6} got={got:<6} "
              f"{'OK' if ok else 'MISMATCH'}")
    print(f"\nAll checks passed: {all_ok}")

    print()
    print("=" * 70)
    print("PART 2 -- GENERALIZED MULTI-HAZARD / MULTI-CATEGORY EXTENSION "
          "(Eq. 3 & 5)")
    print("=" * 70)
    lagos_hazards = [
        {
            "name": "coastal flood", "L": 0.90,
            "categories": {
                "social":        {"E": 0.70, "V": 0.80, "rho": 0.20},
                "economic":      {"E": 0.60, "V": 0.75, "rho": 0.25},
                "environmental": {"E": 0.65, "V": 0.70, "rho": 0.20},
            },
            "rho_hazard": 0.20, "C": 5,
        },
        {
            "name": "pluvial (drainage) flood", "L": 0.85,
            "categories": {
                "social":        {"E": 0.55, "V": 0.70, "rho": 0.30},
                "economic":      {"E": 0.50, "V": 0.65, "rho": 0.30},
                "environmental": {"E": 0.60, "V": 0.68, "rho": 0.25},
            },
            "rho_hazard": 0.28, "C": 4,
        },
    ]
    weights = {"social": 0.40, "economic": 0.30, "environmental": 0.30}
    multi_result = assess_multi(N=16_000_000, hazards=lagos_hazards, weights=weights)
    print(json.dumps({k: v for k, v in multi_result.items() if k != "breakdown"}, indent=2))
    print("\nPer hazard x category breakdown:")
    for row in multi_result["breakdown"]:
        print(f"  {row['hazard']:<24} {row['category']:<14} "
              f"w={row['w_c']:.2f} term={row['term']:.4f}")

    exp_multi = {"R": 0.578, "EAL": 1.179, "equity_per_1M": 0.0737}
    multi_ok = all(abs(multi_result[k] - v) < 0.001 for k, v in exp_multi.items())
    print(f"\nMulti-hazard self-check passed: {multi_ok}")
