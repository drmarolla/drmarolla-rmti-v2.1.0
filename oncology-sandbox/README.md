# RMTI Sandbox — Oncology and Public Health Surveillance

**v2.1.0.** Interactive, self-contained reference implementation of the
Risk Mechanism Theory Index (RMTI) for hepatocellular carcinoma (HCC)
surveillance and public-health surveillance settings. A single HTML file —
no build step, no server, no external dependencies. Open `index.html` in
any browser, or use the live page:
**https://drmarolla.github.io/rmti-oncology-sandbox/**

## What changed in v2.1.0

Aligned to RMTI-Py 2.1.0 and the RMTI–HCC Calculator v2.1.0. No equation, tier
threshold or anchor changed. The advisory "Estimate E from N" helper now uses
the same population bounds as the Python HCC module (N from 100 to 5,000,000,
previously 10 to 650,000); the per-capita line is reported per 1,000,000
at-risk patients (the Python unit); and the comparison block is worded for
surveillance ("planned surveillance improvement") instead of "resilience
investment".

## What it does

Implements the two RMTI equations —

- **R = L · E · V · (1 − ρ)** — the core risk score, bounded 0–1
- **EAL = L · C · (1 − ρ)** — the Expected Annual Loss severity layer

— plus a fixed five-tier scale (Low / Moderate / High / Severe / Critical)
and a log-normalized population-exposure helper. Likelihood is grounded in
a validated risk score (aMAP, THRI); vulnerability in hepatic reserve
(ALBI); resilience in surveillance-delivery adequacy. Includes a
**Custom / Your Field** mode where you name and score your own case,
save it, and export/import saved cases as JSON to move them between
browsers or archive them outside localStorage.

## Companion artifacts

- **Disaster-science sandbox** (same framework, applied to urban and
  climate risk): https://github.com/drmarolla/rmti-disaster-science-sandbox
- **Python reference implementation** (the same equations, as a tested
  Python package, validated against six published HCC cohorts and six
  Pearl-protocol aetiologies — use this for batch scoring, not the
  interactive UI): https://github.com/drmarolla/Risk-Mechanism-Theory-Index-RMTI-
- **RMTI Calculator** — an Excel workbook version of this same tool

## Citation

See `CITATION.cff`. Concept DOI (always resolves to the latest version):
https://doi.org/10.5281/zenodo.22909090

## License

Apache License 2.0 — see `LICENSE` and `NOTICE`. Covers everything in
this repository: code, rubric text, tier descriptions, and worked
examples alike, with no exceptions.

## Intended use and limitations

Educational and research use only. This is not a medical device, has not
been clinically validated, and is not a substitute for clinical judgment
or current clinical guidelines. It does not diagnose, predict outcomes for
individual patients, or prescribe treatment, and its on-screen readings
are not recommendations for any patient. Decisions about patient care
remain with the treating clinicians. Do not enter patient-identifiable
information. See the in-app notice and `DISCLAIMER.md` for the full
statement.
