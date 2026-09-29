# Marolla's RMTI — Disaster Science and Oncology. 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23031912.svg)](https://doi.org/10.5281/zenodo.23031912)
## How to cite
Marolla, Cesar. (2026). *Marolla's RMTI Framework v2.1.0*. Zenodo. https://doi.org/10.5281/zenodo.23031912
**Version 2.1.0 (revised package).** The Risk Mechanism Theory Index (RMTI) provides a single, decision-ready risk score:

R = L x E x V x (1 - p)

It features an Expected Annual Loss severity layer:

EAL = L x C x (1 - p)

The index is implemented four ways: two interactive web sandboxes, one Python reference package, and one Excel workbook.

* **Author:** Cesar Marolla 
* **ORCID:** [0000-0001-8498-7380](https://orcid.org)

---

## 📂 Repository Mapping & Architecture

This repository serves as the central staging directory to push v2.1.0 live across all three specialized GitHub repositories and their linked Zenodo records. Please reference `UPLOAD_INSTRUCTIONS.md` for deployment workflows.

| Folder | Target Deployment | Component Description |
| :--- | :--- | :--- |
| **`disaster-science-sandbox/`** | `github.com/drmarolla/rmti-disaster-science-sandbox` | Interactive HTML sandbox for urban, infrastructure, and disaster risk. Includes 8 worked examples (6-city Sub-Saharan Africa portfolio + Jan 2025 Pacific Palisades and Altadena wildfires). |
| **`oncology-sandbox/`** | `github.com/drmarolla/rmti-oncology-sandbox` | Interactive HTML sandbox tailored for hepatocellular carcinoma (HCC) and public-health surveillance triage. |
| **`rmti-python/`** | `github.com/drmarolla/Risk-Mechanism-Theory-Index-RMTI-` | Core Python reference implementation (37 passing tests). Serves as the mathematical baseline for both sandboxes. |
| **`RMTI_Calculator/`** | *Self-Hosted / External Archive* | Excel workbooks: `RMTI_Calculator_v2.0.0.xlsx` (urban/climate) and `RMTI_HCC_Calculator_v2.1.0.xlsx` (oncology — **new**). |
| **`docs/`** | *Documentation Repository* | Contains `RMTI_Calculator_Explainer_v2.1.0.docx` (a column-by-column explainer and worked patient profile for the HCC calculator). |
| **`LICENSE`, `NOTICE`** | *Reference Copies* | Global Apache 2.0 reference files shipping within every component folder. |

---

## 🔄 Version History & Core Updates

### What changed in v2.1.0 (Oncology Release)
No foundational equations, tier thresholds, or anchor values were modified; all v2.0.0 numbers reproduce identically. 
* **Oncology Vocabulary:** The HCC module now reports localized surveillance-programme vocabulary (`HCC_TIER_POSTURE`) via a new optional `postures` argument instead of infrastructure text.
* **Standardized Population Bounds:** Universal bounds (N from 100 to 5,000,000) and an EAL unit per 1,000,000 at-risk patients are now shared across all three oncology tools to match the Python package.
* **New Verification Workbook:** Added `RMTI_HCC_Calculator_v2.1.0.xlsx`, row-for-row verified against the Python package. 
* **Sandbox Adjustments:** Refined terminology ("planned surveillance improvement" replaces "planned resilience investment").
* **Test Suite Expansion:** Total tests expanded to 37 (29 baseline + 8 new oncology assertions).

### What changed in v2.0.0 (Baseline Consolidation)
* **Unified Licensing:** Migrated completely to **Apache License 2.0**. This supersedes the original MIT limits and removes proprietary carve-outs on text elements.
* **Data Harmonization:** Synchronized stale draft figures from the Pacific Palisades and Altadena wildfire test cases to match the calculator tool.
* **Sandbox Standalone Capabilities:** Added offline capabilities (no external font dependencies), JSON export/import for custom configuration states, and dynamic metadata footers linked directly to authentic DOIs.
* **Python Optimization:** Fixed a floating-point rounding issue, corrected within-tier priority ranking sorting bugs, and abstracted duplicate logic.

---

## ⚖️ Framework Interoperability & Math Continuity

The two web sandboxes are built using vanilla JavaScript, whereas `rmti-python/` is an independently-tested engine. Both platforms are cross-verified to emit identical data outputs for identical inputs. 

> [!IMPORTANT]
> Because math engines are isolated to optimize native performance across environments, changing equations in one module will not automatically cascade to the others. Math updates must be applied manually to JavaScript, Python, and Excel engines uniformly.

---

## 🆔 Provenance & Authorship Verification

Project ownership and identity verification depend on five explicit repository markers:
1. **`NOTICE`**: Located in every folder, identifying the author and ORCID as mandated under Apache 2.0 §4(d).
2. **`CITATION.cff`**: Standardized semantic file parsed natively by GitHub's citation block and Zenodo metadata indexing.
3. **Zenodo ORCID Integration**: Cryptographically links project deposits directly to a verified author record.
4. **Git Commit Timestamps**: Linear, cryptographic proof of structural development history.
5. **Per-File Boilerplate Headers**: Embedded directly into Python source components to guarantee identity integrity when extracted.

---

## 📜 License

This master package and all secondary modules are licensed under the **Apache License 2.0**. Refer to the root `LICENSE` and `NOTICE` files for details.
