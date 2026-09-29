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
test_rmti.py -- automated reproducibility suite for the RMTI reference
implementation.

Run with either:
    python -m unittest tests.test_rmti -v
    python -m pytest tests/ -v

Every assertion here reproduces a number printed in a published source:
the Natural Hazards manuscript (Bamako/Lagos/Lilongwe/Nairobi/Dar es
Salaam/Lusaka), the HCC surveillance-triage manuscript (six published
cohorts, six Pearl-protocol aetiologies, the within-tier EAL worked
example), the RMTI Calculator workbook (IEI column), and the multi-hazard
Lagos illustration (Eq. 3/5). If any of these fail, do not publish --
that is precisely the class of silent mismatch v1.1.0 was cut to fix.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.rmti_core import (
    score, assess, rank_cohort, e_log, tier, pct_reduction,
    investment_efficiency, score_multi, assess_multi, check_weights,
)
from disaster_climate.rmti_ssa import COHORT, _scoreable_cohort
from oncology.rmti_hcc import (
    PUBLISHED_COHORTS, PEARL_COHORTS, _scoreable, rank_cohort_hcc,
    score_patient, albi_cohort_v, C_LADDER,
    HCC_TIER_POSTURE, hcc_posture, assess_patient, exposure_from_population,
    N_MIN_HCC, N_MAX_HCC,
)
from core.rmti_core import TIER_POSTURE, posture, TIER


class TestCoreArithmetic(unittest.TestCase):
    """The bug this whole release exists to fix."""

    def test_decimal_rounding_boundary(self):
        # 0.30 * 0.65 * 0.60 * (1 - 0.50) is exactly 0.0585 in decimal and
        # must round HALF_UP to 0.059. In binary float this product is
        # 0.058499999999999996, so a naive round(x, 3) silently gives 0.058
        # -- the archived v1.0.0 core produced 0.058 here.
        result = score(L=0.30, E_sel=0.65, V=0.60, rho=0.50, C=3)
        self.assertEqual(result["R"], 0.059)

    def test_tier_thresholds(self):
        self.assertEqual(tier(0.049), "Tier 1 - Low")
        self.assertEqual(tier(0.05), "Tier 2 - Moderate")
        self.assertEqual(tier(0.149), "Tier 2 - Moderate")
        self.assertEqual(tier(0.15), "Tier 3 - High")
        self.assertEqual(tier(0.349), "Tier 3 - High")
        self.assertEqual(tier(0.35), "Tier 4 - Severe")
        self.assertEqual(tier(0.599), "Tier 4 - Severe")
        self.assertEqual(tier(0.60), "Tier 5 - Critical")

    def test_e_log_worked_example(self):
        # Lilongwe walkthrough: N = 1.1M -> E_log = 0.800
        self.assertAlmostEqual(e_log(1_100_000), 0.800, places=3)

    def test_e_log_clamped(self):
        self.assertEqual(e_log(1), 0.0)          # below N_MIN
        self.assertEqual(e_log(50_000_000), 1.0)  # above N_MAX

    def test_weights_must_sum_to_one(self):
        with self.assertRaises(ValueError):
            check_weights({"social": 0.5, "economic": 0.3, "environmental": 0.1})


class TestDisasterClimateCohort(unittest.TestCase):
    """Six-city Sub-Saharan Africa cohort + wildfire cases, Tables 4-6."""

    @classmethod
    def setUpClass(cls):
        cls.ranked = {r["name"]: r for r in rank_cohort(_scoreable_cohort(COHORT))}

    def test_bamako(self):
        r = self.ranked["Bamako"]
        self.assertEqual(r["IR"], 0.510)
        self.assertEqual(r["R_now"], 0.408)
        self.assertEqual(r["tier_now"], "Tier 4 - Severe")
        self.assertEqual(r["R_after"], 0.214)
        self.assertEqual(r["tier_after"], "Tier 3 - High")
        self.assertAlmostEqual(r["risk_reduction_pct"], 47.5, places=1)
        self.assertEqual(r["EAL_now"], 0.480)

    def test_lagos(self):
        r = self.ranked["Lagos"]
        self.assertEqual(r["R_now"], 0.374)
        self.assertEqual(r["R_after"], 0.211)
        self.assertAlmostEqual(r["risk_reduction_pct"], 43.8, places=1)
        self.assertEqual(r["EAL_now"], 0.720)

    def test_lilongwe(self):
        r = self.ranked["Lilongwe"]
        self.assertEqual(r["E_log"], 0.800)
        self.assertEqual(r["R_now"], 0.420)
        self.assertEqual(r["R_after"], 0.291)
        self.assertAlmostEqual(r["risk_reduction_pct"], 30.7, places=1)
        self.assertAlmostEqual(r["equity_now_per_1M"], 0.4474, places=4)

    def test_nairobi(self):
        # R_after = 0.4356 * 0.35 = 0.15246 -> 0.152 (the published
        # Explanation PDF prints 0.153; 0.152 is the correct ROUND_HALF_UP
        # result and is what this reference implementation reproduces --
        # see AUDIT.md item B1).
        r = self.ranked["Nairobi"]
        self.assertEqual(r["R_now"], 0.196)
        self.assertEqual(r["R_after"], 0.152)

    def test_dar_es_salaam_investment_efficiency(self):
        r = self.ranked["Dar es Salaam"]
        self.assertEqual(r["R_now"], 0.277)
        self.assertEqual(r["R_after"], 0.185)
        self.assertAlmostEqual(r["IEI"], 1.111, places=3)

    def test_lusaka(self):
        r = self.ranked["Lusaka"]
        self.assertEqual(r["R_now"], 0.269)
        self.assertEqual(r["R_after"], 0.196)

    def test_pacific_palisades(self):
        # Palisades Fire, Jan 7 2025. N/L/rho corrected against LAEDC (2025)
        # and the SSRN Palisades policy-gap report (2026) -- see the RMTI
        # Calculator workbook and sandbox for the full per-field sourcing.
        # Note R_now/R_after land in the SAME tier: the resilience gain
        # (rho 0.20 -> 0.35) is real but partial, per the policy report's
        # own status matrix (most enacted fixes are financial/claims-layer,
        # not the physical/operational fire-monitoring and water-
        # infrastructure gaps).
        r = self.ranked["Pacific Palisades"]
        self.assertEqual(r["IR"], 0.144)
        self.assertEqual(r["R_now"], 0.115)
        self.assertEqual(r["tier_now"], "Tier 2 - Moderate")
        self.assertEqual(r["R_after"], 0.094)
        self.assertEqual(r["tier_after"], "Tier 2 - Moderate")
        self.assertEqual(r["EAL_now"], 0.240)

    def test_altadena(self):
        # Eaton Fire, Jan 7 2025. L and rho are unified with Palisades
        # (same Very High Fire Hazard Severity Zone classification, same
        # regional Santa Ana wind event, same shared statewide policy
        # response) -- the two cases are differentiated through N, E and V
        # instead, i.e. their genuinely different local exposure and
        # vulnerability profiles. Unlike Palisades, Altadena's higher V
        # (lower household income/homeownership per LAEDC) is enough to
        # cross a full tier boundary: High -> Moderate post-resilience.
        r = self.ranked["Altadena"]
        self.assertEqual(r["IR"], 0.192)
        self.assertEqual(r["R_now"], 0.154)
        self.assertEqual(r["tier_now"], "Tier 3 - High")
        self.assertEqual(r["R_after"], 0.125)
        self.assertEqual(r["tier_after"], "Tier 2 - Moderate")
        self.assertEqual(r["EAL_now"], 0.240)

    def test_priority_resets_within_tier(self):
        # Regression test for the v1.0.0 global-numbering bug: at least
        # two different tiers must each contain a priority == 1.
        ranked_list = list(self.ranked.values())
        priorities_by_tier = {}
        for r in ranked_list:
            priorities_by_tier.setdefault(r["tier_now"], []).append(r["priority_in_tier"])
        for tier_label, priorities in priorities_by_tier.items():
            self.assertEqual(min(priorities), 1,
                              f"{tier_label} does not reset to priority 1")


class TestOncologyCohorts(unittest.TestCase):
    """Six published HCC cohorts + six Pearl-protocol aetiologies, Tables 2-3."""

    @classmethod
    def setUpClass(cls):
        cls.published = rank_cohort_hcc(_scoreable(PUBLISHED_COHORTS))
        cls.pearl = rank_cohort_hcc(_scoreable(PEARL_COHORTS))
        cls.by_name_pub = {r["name"]: r for r in cls.published}
        cls.by_name_pearl = {r["name"]: r for r in cls.pearl}

    def test_untreated_hbv(self):
        r = self.by_name_pub["Untreated HBV"]
        self.assertEqual(r["R_now"], 0.312)
        self.assertEqual(r["R_after"], 0.191)

    def test_active_viral_cirrhosis(self):
        r = self.by_name_pub["Active viral cirrhosis"]
        self.assertEqual(r["R_now"], 0.102)
        self.assertEqual(r["R_after"], 0.071)

    def test_alcohol_cirrhosis_is_the_rounding_regression_case(self):
        # This is the published-table cell that the archived v1.0.0
        # binary-float round() got wrong (see TestCoreArithmetic).
        r = self.by_name_pub["Alcohol cirrhosis"]
        self.assertEqual(r["R_now"], 0.094)
        self.assertEqual(r["R_after"], 0.059)

    def test_cured_hcv_cirrhosis(self):
        r = self.by_name_pub["Cured-HCV cirrhosis"]
        self.assertEqual(r["R_now"], 0.058)
        self.assertEqual(r["R_after"], 0.032)

    def test_suppressed_hbv(self):
        r = self.by_name_pub["Suppressed-HBV"]
        self.assertEqual(r["R_now"], 0.040)
        self.assertEqual(r["R_after"], 0.022)

    def test_nafld_cirrhosis(self):
        r = self.by_name_pub["NAFLD cirrhosis"]
        self.assertEqual(r["R_now"], 0.038)
        self.assertEqual(r["R_after"], 0.024)

    def test_pearl_protocol_uniform_56pct_reduction(self):
        for name, r in self.by_name_pearl.items():
            self.assertAlmostEqual(r["risk_reduction_pct"], 56.3, delta=0.15,
                                    msg=f"{name} did not show the uniform "
                                        f"56% reduction from rho 0.20->0.65")

    def test_pearl_high_burden_masld(self):
        r = self.by_name_pearl["High-burden MASLD"]
        self.assertEqual(r["R_now"], 0.156)
        self.assertEqual(r["R_after"], 0.068)

    def test_within_tier_eal_priority_reversal(self):
        # Section 2.6 worked example: A outranks B on R alone, but EAL
        # reverses the within-tier priority because B is far more
        # consequential if a tumour is missed.
        A = score_patient(L=0.30, E=0.60, V=0.50, rho=0.20, C=C_LADDER["BCLC_A"])
        B = score_patient(L=0.25, E=0.60, V=0.55, rho=0.20, C=C_LADDER["BCLC_CD"])
        self.assertGreater(A.R, B.R)
        self.assertGreater(B.EAL, A.EAL)

    def test_albi_cohort_vulnerability(self):
        hcc_v = albi_cohort_v({1: 10, 2: 18, 3: 1})
        cirr_v = albi_cohort_v({1: 12, 2: 13, 3: 0})
        self.assertAlmostEqual(hcc_v, 0.52, places=2)
        self.assertAlmostEqual(cirr_v, 0.48, places=2)

    def test_priority_resets_within_tier(self):
        priorities_by_tier = {}
        for r in self.published:
            priorities_by_tier.setdefault(r["tier_now"], []).append(r["priority_in_tier"])
        for tier_label, priorities in priorities_by_tier.items():
            self.assertEqual(min(priorities), 1,
                              f"{tier_label} does not reset to priority 1")


class TestMultiHazardExtension(unittest.TestCase):
    """Eq. 3/5 generalized multi-hazard, multi-category form -- the
    illustrative Lagos two-hazard example."""

    @classmethod
    def setUpClass(cls):
        cls.hazards = [
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
        cls.weights = {"social": 0.40, "economic": 0.30, "environmental": 0.30}
        cls.result = assess_multi(N=16_000_000, hazards=cls.hazards, weights=cls.weights)

    def test_aggregate_R_and_EAL(self):
        self.assertEqual(self.result["R"], 0.578)
        self.assertEqual(self.result["EAL"], 1.179)
        self.assertAlmostEqual(self.result["equity_per_1M"], 0.0737, places=4)

    def test_e_log_advisory(self):
        self.assertAlmostEqual(self.result["E_log_advisory"], 0.985, places=3)

    def test_per_hazard_category_terms(self):
        expected = {
            ("coastal flood", "social"): 0.1613,
            ("coastal flood", "economic"): 0.0911,
            ("coastal flood", "environmental"): 0.0983,
            ("pluvial (drainage) flood", "social"): 0.0916,
            ("pluvial (drainage) flood", "economic"): 0.0580,
            ("pluvial (drainage) flood", "environmental"): 0.0780,
        }
        for row in self.result["breakdown"]:
            key = (row["hazard"], row["category"])
            self.assertAlmostEqual(row["term"], expected[key], places=4)

    def test_weights_enforced(self):
        with self.assertRaises(ValueError):
            score_multi(self.hazards, {"social": 0.5, "economic": 0.3, "environmental": 0.3})


class TestOncologyVocabularyAndUnits(unittest.TestCase):
    """v2.1.0: the HCC module reports in oncology vocabulary, per-capita in
    per-1,000,000 units, with the HCC population bounds -- and none of this
    changes any number or any other domain."""

    INFRA_WORDS = ("fund", "capital", "mitigation", "infrastructure",
                   "invest", "construction", "asset")

    def test_one_posture_per_fixed_tier(self):
        self.assertEqual(list(HCC_TIER_POSTURE), [lbl for _, lbl in TIER])
        self.assertEqual(len(set(HCC_TIER_POSTURE.values())), 5)   # all distinct

    def test_no_infrastructure_wording_in_hcc_posture(self):
        for text in HCC_TIER_POSTURE.values():
            for w in self.INFRA_WORDS:
                self.assertNotIn(w, text.lower())

    def test_default_posture_unchanged_for_other_domains(self):
        self.assertEqual(posture(0.20), TIER_POSTURE["Tier 3 - High"])
        self.assertEqual(posture(0.20, None), "Structured mitigation; fund soon")

    def test_assess_patient_uses_hcc_posture(self):
        r = assess_patient(N=100_000, L=0.65, E=0.60, V=0.50,
                           rho_now=0.20, rho_after=0.65, C=5)
        self.assertEqual(r["R_now"], 0.156)
        self.assertEqual(r["posture_now"], HCC_TIER_POSTURE["Tier 3 - High"])
        self.assertEqual(r["posture_after"], HCC_TIER_POSTURE["Tier 2 - Moderate"])
        self.assertEqual(hcc_posture(0.156), r["posture_now"])

    def test_rank_cohort_hcc_uses_hcc_posture(self):
        ranked = rank_cohort_hcc(_scoreable(PUBLISHED_COHORTS))
        for r in ranked:
            self.assertIn(r["posture_now"], HCC_TIER_POSTURE.values())

    def test_hcc_population_bounds(self):
        self.assertEqual((N_MIN_HCC, N_MAX_HCC), (100, 5_000_000))
        self.assertEqual(exposure_from_population(100), 0.0)
        self.assertEqual(exposure_from_population(5_000_000), 1.0)
        self.assertAlmostEqual(exposure_from_population(100_000), 0.6384, places=4)
        r = assess_patient(N=100_000, L=0.65, E=0.60, V=0.50, rho_now=0.20, C=5)
        self.assertEqual(r["E_log"], 0.638)

    def test_per_capita_is_per_million(self):
        # EAL_raw = 0.65 * 1.00 * 0.80 = 0.52 ; N = 100,000 -> 0.52 / 0.1 = 5.2
        r = assess_patient(N=100_000, L=0.65, E=0.60, V=0.50, rho_now=0.20, C=5)
        self.assertAlmostEqual(r["equity_now_per_1M"], 5.2, places=4)

    def test_within_tier_eal_reversal_worked_example(self):
        ranked = rank_cohort_hcc({
            "A": dict(N=100_000, L=0.30, E=0.60, V=0.50, rho_now=0.20, C=2),
            "B": dict(N=100_000, L=0.25, E=0.60, V=0.55, rho_now=0.20, C=5),
        })
        self.assertEqual([r["name"] for r in ranked], ["B", "A"])
        by = {r["name"]: r for r in ranked}
        self.assertEqual((by["A"]["R_now"], by["B"]["R_now"]), (0.072, 0.066))
        self.assertEqual((by["A"]["EAL_now"], by["B"]["EAL_now"]), (0.072, 0.200))
        self.assertEqual(by["B"]["priority_in_tier"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
