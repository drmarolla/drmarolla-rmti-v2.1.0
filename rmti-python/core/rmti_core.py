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
rmti_core.py -- Shared RMTI framework core.

This module holds everything that is common across ALL domain applications
of the Risk Mechanism Theory Index (RMTI), Marolla (2018, 2025), "RMTI: A
Systemic Risk Mechanism Design and Theory Framework":

    - Eq. (1)/(2): IR = L * E_sel * V ; R = IR * (1 - rho)
    - Eq. (3)/(5): generalized multi-hazard/multi-category extension
    - Eq. (4): advisory log-normalized exposure baseline
    - Eq. (6): EAL = L * C * (1 - rho)
    - Eq. (7): per-capita/per-patient equity rate
    - Table 2: consequence scale (C_INFRA)
    - Table 3: fixed, pre-registered risk tiers
    - Table 9.4: indicator backbone (RMTre -> E, RMTseen -> V, RMTrl -> rho)

Domain-specific modules (oncology/, disaster_climate/) import from here so
the underlying math stays in exactly one place. Do not fork these functions
per domain -- if a domain needs different behavior, extend via parameters,
not copy-paste, so a fix or validation update here propagates everywhere.

CHANGELOG (v1.1.0, relative to the archived v1.0.0 release)
-------------------------------------------------------------------------
Fixed: score() previously rounded IR/R/EAL with Python's binary-float
round(), which silently disagrees with decimal arithmetic at exact
half-way boundaries. Example: 0.30 * 0.65 * 0.60 * (1 - 0.50) is exactly
0.0585 in decimal and must round to 0.059 (ROUND_HALF_UP, matching Excel
and the manuscript's Table 2), but evaluates to 0.058499999999999996 in
IEEE-754 binary float, so round(x, 3) silently returned 0.058. score() now
builds the products from the Decimal string representation of each input
and rounds via ROUND_HALF_UP, eliminating this class of error. tier()
still compares against the plain float R, which is safe because the fixed
Table 3 thresholds are not near this kind of boundary.

Domain modules (rmti_ssa.py, rmti_hcc.py) previously duplicated score()/
assess()/rank_cohort() with their own copies (in violation of this
module's own "do not fork" instruction, and inheriting the same rounding
bug independently). Both now import these functions from here.
-------------------------------------------------------------------------
"""
import math
from decimal import Decimal, ROUND_HALF_UP

__version__ = "2.1.0"

# ---------------------------------------------------------------------------
# FIXED, PRE-REGISTERED LOOKUP TABLES (Table 3 / Table 2 -- never re-derived
# per-sample; that is what makes a score of 0.30 mean the same thing in every
# application of the framework, per Sec. 3.5).
# ---------------------------------------------------------------------------
TIER = [(0.05, "Tier 1 - Low"), (0.15, "Tier 2 - Moderate"),
        (0.35, "Tier 3 - High"), (0.60, "Tier 4 - Severe"),
        (1e9,  "Tier 5 - Critical")]

TIER_POSTURE = {
    "Tier 1 - Low":      "Monitor; maintain baseline",
    "Tier 2 - Moderate":  "Low-regret preventive measures",
    "Tier 3 - High":      "Structured mitigation; fund soon",
    "Tier 4 - Severe":    "Priority capital; act now",
    "Tier 5 - Critical":  "Immediate, system-level response",
}

# RMTrl typology anchors -- advisory reference points for rho (Table 9.4
# resilience-capacity ladder), NOT a categorical lookup; practitioners
# enter a continuous rho per their own Table 9.4 assessment.
RHO_TYPOLOGY_ANCHORS = {"none": 0.10, "ad_hoc": 0.20,
                         "monitoring_enforcement": 0.25, "structured": 0.45,
                         "structured_to_funded": 0.55, "funded": 0.58,
                         "optimised": 0.70}

C_INFRA = {1: 0.10, 2: 0.30, 3: 0.50, 4: 0.75, 5: 1.00}   # Table 2
N_MIN, N_MAX = 10, 20_000_000                              # Sec. 3.3 anchors


def e_log(N, n_min=None, n_max=None):
    """Eq. (4): advisory log-normalized exposure baseline from population N.

    n_min/n_max default to the module-level N_MIN/N_MAX (the disaster/climate
    "smallest viable scheme" / "largest metro" anchors). Domain applications
    with a different natural population ceiling -- e.g. HCC surveillance,
    where the relevant denominator is a national at-risk cirrhosis population
    rather than a city -- may pass their own bounds here without altering
    the shared defaults used elsewhere. Result is clamped to [0, 1]."""
    lo = N_MIN if n_min is None else n_min
    hi = N_MAX if n_max is None else n_max
    N = max(lo, min(hi, N))
    val = (math.log10(N) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
    return max(0.0, min(1.0, val))


def tier(R):
    """Map a residual risk score R to its fixed Table 3 tier label."""
    for threshold, label in TIER:
        if R < threshold:
            return label
    return TIER[-1][1]


def posture(R, postures=None):
    """Recommended posture text for the tier containing R (Table 3).

    postures -- optional {tier label: text} table, keyed exactly like
    TIER_POSTURE. Added in v2.1.0 so that a domain module can report the
    fixed tier in its own vocabulary (e.g. oncology.rmti_hcc.HCC_TIER_POSTURE
    for HCC surveillance) without forking tier() or the thresholds. Defaults
    to the shared infrastructure-domain TIER_POSTURE, so existing callers
    are unchanged."""
    table = TIER_POSTURE if postures is None else postures
    return table[tier(R)]


def pct_reduction(rho_now, rho_after):
    """Percent cut in R from a resilience/treatment investment, holding IR
    fixed: 1 - R_after/R_now = 1 - (1-rho_after)/(1-rho_now). Excel-style
    rounding (round-half-away-from-zero)."""
    a, b = Decimal(str(rho_now)), Decimal(str(rho_after))
    pct = (1 - (1 - b) / (1 - a)) * 100
    return float(pct.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def investment_efficiency(rho_now, rho_after):
    """IEI = Delta risk (unrounded fraction) / (1 - rho_after). > 1 means
    the intervention removes more risk than the exposure it leaves behind.
    Matches the RMTI Calculator workbook's column Z exactly, which uses the
    unrounded delta rather than the displayed, rounded percentage."""
    a, b = Decimal(str(rho_now)), Decimal(str(rho_after))
    if b >= 1:
        return None
    delta_fraction = 1 - (1 - b) / (1 - a)
    iei = delta_fraction / (1 - b)
    return float(iei.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


# ---------------------------------------------------------------------------
# VALIDATED CORE -- Eq. (1)/(2)/(6): single hazard/insult, single blended
# (E, V, rho) per asset or patient. Domain modules call these directly.
# ---------------------------------------------------------------------------
def score(L, E_sel, V, rho, C=5):
    """Core two-stage computation for one resilience/treatment state.
        IR  = L * E_sel * V                    Eq. (1)
        R   = IR * (1 - rho)                   Eq. (2)
        EAL = L * C_INFRA[C] * (1 - rho)       Eq. (6)

    Display rounding uses exact Decimal arithmetic built from the string
    representation of each input (ROUND_HALF_UP to 3 dp), not from the
    binary-float products, so 0.30*0.65*0.60*0.50 rounds to 0.059 and not
    0.058 -- see module changelog above. tier() compares the unrounded
    float R, which is safe: the fixed Table 3 thresholds are not near this
    kind of boundary.
    """
    q3 = Decimal("0.001")
    L_d, E_d, V_d, rho_d = (Decimal(str(x)) for x in (L, E_sel, V, rho))
    IR_d = L_d * E_d * V_d
    R_d = IR_d * (1 - rho_d)
    EAL_d = L_d * Decimal(str(C_INFRA[C])) * (1 - rho_d)

    IR, R, EAL_raw = float(IR_d), float(R_d), float(EAL_d)
    return {"IR": float(IR_d.quantize(q3, rounding=ROUND_HALF_UP)),
            "R": float(R_d.quantize(q3, rounding=ROUND_HALF_UP)),
            "tier": tier(R),
            "EAL": float(EAL_d.quantize(q3, rounding=ROUND_HALF_UP)),
            "EAL_raw": EAL_raw}


def assess(N, L, E_sel, V, rho_now, rho_after=None, C=5, n_min=None, n_max=None,
           postures=None):
    """Full asset/patient-level assessment: baseline + optional
    post-investment/post-treatment state, risk-reduction %, investment
    efficiency, and per-capita equity rate (Eq. 7). n_min/n_max optionally
    override the population bounds used only by the advisory E_log helper
    (see e_log); they do not affect R, tier, or EAL. postures optionally
    replaces the posture-text table (see posture); it does not affect any
    number."""
    now = score(L, E_sel, V, rho_now, C)
    out = {"N": N, "E_log": round(e_log(N, n_min, n_max), 3), "rho_now": rho_now,
           "IR": now["IR"], "R_now": now["R"], "tier_now": now["tier"],
           "posture_now": posture(now["R"], postures),
           "EAL_now": now["EAL"], "equity_now_per_1M": round(now["EAL_raw"] / (N / 1e6), 4)}
    if rho_after is not None:
        after = score(L, E_sel, V, rho_after, C)
        out.update({"rho_after": rho_after, "R_after": after["R"],
                     "tier_after": after["tier"], "posture_after": posture(after["R"], postures),
                     "EAL_after": after["EAL"],
                     "equity_after_per_1M": round(after["EAL_raw"] / (N / 1e6), 4),
                     "risk_reduction_pct": pct_reduction(rho_now, rho_after),
                     "IEI": investment_efficiency(rho_now, rho_after)})
    return out


def rank_cohort(rows):
    """Batch-score a cohort/portfolio and rank for prioritization: primary
    sort by tier severity, secondary sort by EAL_now descending. Priority
    is assigned WITHIN each tier group (resets at every tier boundary),
    matching the RMTI Calculator workbook's COUNTIFS priority columns.

    Fixed in v1.1.0: the archived v1.0.0 oncology module (rmti_hcc.py)
    assigned a single global 1..n sequence here instead of resetting per
    tier; that bug is fixed by centralizing this function in core and
    having every domain module call it instead of forking its own copy.
    """
    tier_rank = {lbl: i for i, (_, lbl) in enumerate(TIER)}
    results = []
    for name, kwargs in rows.items():
        r = assess(**kwargs); r["name"] = name; results.append(r)
    results.sort(key=lambda r: (-tier_rank[r["tier_now"]], -r["EAL_now"]))
    last_tier, k = None, 0
    for r in results:
        k = 1 if r["tier_now"] != last_tier else k + 1
        r["priority_in_tier"] = k
        last_tier = r["tier_now"]
    return results


# ---------------------------------------------------------------------------
# GENERALIZED "UNIVERSAL ALGORITHM" -- Eq. (3)/(5): multi-factor,
# multi-category extension shared across domains.
# ---------------------------------------------------------------------------
CATEGORIES = ("social", "economic", "environmental")


def check_weights(weights, categories=CATEGORIES):
    total = sum(weights.get(c, 0.0) for c in categories)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(
            f"Category weights must sum to 1 (Table 1, w_c); got {total:.4f} "
            f"for {weights}. This is enforced, not assumed.")


def score_multi(hazards, weights, categories=CATEGORIES):
    """Generalized multi-hazard/multi-factor scoring, Eq. (3) and (5).

    hazards: list of dicts, one per hazard/factor h, each shaped as:
        {
          "name": "coastal flood",
          "L": 0.90,
          "categories": {
              "social":        {"E": 0.70, "V": 0.80, "rho": 0.30},
              "economic":      {"E": 0.55, "V": 0.60, "rho": 0.40},
              "environmental": {"E": 0.65, "V": 0.75, "rho": 0.35},
          },
          "rho_hazard": 0.35,
          "C": 5,
        }
    weights: dict of category -> w_c, must sum to 1.

    Returns dict with R (Eq. 3), EAL (Eq. 5), tier, and a per-hazard
    breakdown for auditability (Sec. 3.2). Eq. 1/2 are the single-hazard,
    single-category reduction of this equation.
    """
    check_weights(weights, categories)
    R_total = 0.0
    EAL_total = 0.0
    breakdown = []
    for h in hazards:
        L_h = h["L"]
        hazard_contribution = 0.0
        for c in categories:
            cat = h["categories"][c]
            w_c = weights[c]
            term = w_c * L_h * cat["E"] * cat["V"] * (1 - cat["rho"])
            hazard_contribution += term
            breakdown.append({
                "hazard": h["name"], "category": c, "w_c": w_c,
                "L": L_h, "E": cat["E"], "V": cat["V"], "rho": cat["rho"],
                "term": round(term, 4),
            })
        R_total += hazard_contribution
        EAL_total += L_h * C_INFRA[h["C"]] * (1 - h["rho_hazard"])

    return {
        "R": round(R_total, 3), "tier": tier(R_total), "posture": posture(R_total),
        "EAL": round(EAL_total, 3),
        "breakdown": breakdown,
    }


def assess_multi(N, hazards, weights, categories=CATEGORIES):
    """Multi-factor equivalent of assess(): adds population/cohort-derived
    E_log (Eq. 4, advisory only) and per-capita equity rate (Eq. 7)."""
    result = score_multi(hazards, weights, categories)
    result["N"] = N
    result["E_log_advisory"] = round(e_log(N), 3)
    result["equity_per_1M"] = round(result["EAL"] / (N / 1e6), 4)
    return result
