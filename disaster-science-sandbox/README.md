# RMTI Sandbox — Disaster Science

**v2.1.0.** Interactive, self-contained reference implementation of the
Risk Mechanism Theory Index (RMTI) for urban, infrastructure and
disaster-risk assessment. A single HTML file — no build step, no server,
no external dependencies. Open `index.html` in any browser, or use the
live page: **https://drmarolla.github.io/rmti-disaster-science-sandbox/**

## What it does

Implements the two RMTI equations —

- **R = L · E · V · (1 − ρ)** — the core risk score, bounded 0–1
- **EAL = L · C · (1 − ρ)** — the Expected Annual Loss severity layer

— plus a fixed five-tier scale (Low / Moderate / High / Severe / Critical)
and a log-normalized population-exposure helper. Includes eight worked
examples (the original six-city Sub-Saharan Africa portfolio, plus the
January 2025 Pacific Palisades and Altadena, California wildfires) and a
**Custom / Your Field** mode where you name and score your own case,
save it, and export/import saved cases as JSON to move them between
browsers or archive them outside localStorage.

## Companion artifacts

- **Oncology sandbox** (same framework, applied to HCC surveillance triage):
  https://github.com/drmarolla/rmti-oncology-sandbox
- **Python reference implementation** (the same equations, as a tested
  Python package — use this for batch scoring, not the interactive UI):
  https://github.com/drmarolla/Risk-Mechanism-Theory-Index-RMTI-
- **RMTI Calculator** — an Excel workbook version of this same tool

## Citation

See `CITATION.cff`. Concept DOI (always resolves to the latest version):
https://doi.org/10.5281/zenodo.22909081

## License

Apache License 2.0 — see `LICENSE` and `NOTICE`. Covers everything in
this repository: code, rubric text, tier descriptions, and worked
examples alike, with no exceptions.

## Intended use and limitations

Educational and research use only. Scores are relative, rubric-based
indices, not forecasts, engineering assessments, or actuarial figures,
and the worked examples are teaching illustrations rather than official
assessments. Not a substitute for professionally validated hazard and
risk assessments. An independent academic tool; not an official product
of the World Bank Group or any other institution.
