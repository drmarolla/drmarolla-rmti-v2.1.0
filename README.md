# Marolla's RMTI — Disaster Science and Oncology

**Version 2.1.0 (revised package).** The Risk Mechanism Theory Index (RMTI) — a single,
decision-ready risk score, R = L·E·V·(1−ρ), with an Expected Annual Loss
severity layer, EAL = L·C·(1−ρ) — implemented four ways: two interactive
web sandboxes, one Python reference package, and one Excel workbook.
Author: Cesar Marolla (ORCID: 0000-0001-8498-7380).

This folder is everything needed to push v2.1.0 live across all three
GitHub repositories and their linked Zenodo records. See
`UPLOAD_INSTRUCTIONS.md` for the exact steps.

## What's in this folder

| Folder | Goes to | What it is |
|---|---|---|
| `disaster-science-sandbox/` | `github.com/drmarolla/rmti-disaster-science-sandbox` | Interactive HTML sandbox — urban, infrastructure and disaster risk. Eight worked examples (six-city Sub-Saharan Africa portfolio + Jan 2025 Pacific Palisades and Altadena wildfires). |
| `oncology-sandbox/` | `github.com/drmarolla/rmti-oncology-sandbox` | Interactive HTML sandbox — hepatocellular carcinoma (HCC) and public-health surveillance triage. |
| `rmti-python/` | `github.com/drmarolla/Risk-Mechanism-Theory-Index-RMTI-` | Tested Python reference implementation (37 passing tests) both sandboxes' math is built to mirror. Also delivered as a standalone zip. |
| `RMTI_Calculator/` | Wherever you currently host it (not on GitHub) | Excel versions of the same tool: `RMTI_Calculator_v2.0.0.xlsx` (urban / climate, unchanged) and **`RMTI_HCC_Calculator_v2.1.0.xlsx` (oncology — new)**. |
| `docs/` | Wherever you keep documentation | `RMTI_Calculator_Explainer_v2.1.0.docx` — column-by-column explainer and worked patient example for the HCC calculator. |
| `LICENSE`, `NOTICE` | (reference copies) | The same Apache 2.0 grant that ships inside every component folder above. |

## What changed in v2.1.0 (oncology release)

No equation, tier threshold or anchor value changed, and every v2.0.0 number
is reproduced exactly. What changed:

- **Oncology vocabulary.** The HCC module reported the shared infrastructure
  posture text ("Structured mitigation; fund soon"). It now reports an HCC
  surveillance-programme vocabulary (`HCC_TIER_POSTURE`), via a new optional
  `postures` argument in the shared core; the disaster module is unaffected.
- **One set of population bounds and one per-capita unit across all three
  oncology tools:** N from 100 to 5,000,000 (advisory E-log helper) and EAL per
  1,000,000 at-risk patients — the Python values. The sandbox and the new
  workbook previously used 10 to 650,000 and (workbook) per 100,000.
- **New oncology workbook** `RMTI_HCC_Calculator_v2.1.0.xlsx`, verified
  row-for-row against the Python package (R, tier, EAL, per-capita, priority,
  posture, E-log, Δ risk, IEI); the HCC ALBI cohort counts are corrected
  to 10/18/1.
- **Sandbox wording:** "planned surveillance improvement" replaces
  "planned resilience investment" in the oncology domain.
- **Tests:** 37 (29 + 8 new).

## What changed in v2.0.0 (the short version)

- **One license, everywhere, no exceptions: Apache License 2.0.** This
  supersedes MIT (both sandboxes' original license) and a proprietary
  carve-out that an earlier internal draft of the Python repo had applied
  to rubric wording and sandbox UI content. Every component now carries
  the same `LICENSE` and a `NOTICE` file naming you as the author.
- **Two real data corrections, not just polish:** the Python package's
  Pacific Palisades/Altadena wildfire cases were syncing stale draft
  figures from before they were corrected in the Calculator and sandboxes
  — now consistent everywhere. See `rmti-python/CHANGELOG.md` for the
  full, sourced explanation.
- **Both sandboxes:** JSON export/import for saved custom cases, no
  external font dependency (fully self-contained offline), and a footer
  that actually shows accurate version, license, DOI, and citation
  information — it was previously showing a hardcoded placeholder.
- **The Python package:** fixes a real floating-point rounding bug that
  affected a published table value, a within-tier priority-ranking bug,
  and de-duplicates logic that three modules had each copy-pasted
  independently. Full details, each independently verifiable by running
  the test suite, in `rmti-python/CHANGELOG.md`.

## How the pieces relate

The two sandboxes are hand-written JavaScript; `rmti-python/` is the
independently-tested Python implementation of the same equations. Both
were checked against each other during this release (identical outputs
for the same inputs, including the Palisades/Altadena cases and a known
floating-point edge case), but they are not generated from shared source
— if you change the math in one, the others do not update automatically.
The Calculator workbook is the same equations again, in Excel formulas.

## Establishing authorship

This is intentionally redundant, because provenance for open work rests
on several independent signals adding up, not one document:

1. **`NOTICE`** in every folder names you, with your ORCID, per the
   mechanism Apache 2.0 §4(d) requires redistributors to preserve.
2. **`CITATION.cff`** in every folder is what GitHub's own "Cite this
   repository" button reads, and what Zenodo uses to pre-fill author
   metadata — both already carry your ORCID.
3. **Zenodo's ORCID verification**: when you connect your ORCID to your
   Zenodo account, each deposit is cryptographically tied to your
   identity, not just a free-text name field.
4. **Git commit history** under your own GitHub account is itself
   timestamped evidence of authorship — nothing extra needed there.
5. **A per-file copyright header** (in every `.py` source file) so
   authorship travels with the file even if it's copied out of its
   repository.

None of this is exclusive to Apache 2.0 — MIT would have offered the same
CITATION.cff/NOTICE/ORCID/git-history stack. What Apache 2.0 adds on top
is the explicit patent grant and more detailed liability language
discussed earlier in this conversation.

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.

## Revision notes

- Disaster sandbox version bumped 2.0.0 → 2.1.0 in `CITATION.cff`, `.zenodo.json`, `index.html` and README; its README citation DOI corrected to `10.5281/zenodo.22909081` (it pointed to the oncology DOI).
- Python and oncology `.zenodo.json` descriptions now describe v2.1.0; Python README test counts corrected to 37.
- All repository URLs use the `drmarolla` GitHub account.
