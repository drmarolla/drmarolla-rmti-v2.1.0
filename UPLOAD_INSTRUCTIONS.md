# Upload checklist — v2.1.0 (oncology release, revised)

**Revised:** all three components are now v2.1.0 (the disaster sandbox was bumped from 2.0.0), the
Python repository is expected under the `drmarolla` GitHub account, and the Zenodo
descriptions match the 37-test suite.

Three separate GitHub repos, three separate Zenodo records. Do them in
any order; none depend on each other. ~10 minutes each if you're just
replacing files through the GitHub web UI; faster with git.

For each repo: **delete the old file and upload the new one with the same
name** (don't rename), so git shows a clean diff instead of an add+delete.

---

## 1. Disaster-science sandbox
`github.com/drmarolla/rmti-disaster-science-sandbox`

**Copy in, replacing the existing file of the same name:**
- `disaster-science-sandbox/index.html`
- `disaster-science-sandbox/LICENSE`
- `disaster-science-sandbox/.zenodo.json`
- `disaster-science-sandbox/CITATION.cff`

**Add as new files:**
- `disaster-science-sandbox/NOTICE`

**Review before committing (I wrote these from scratch, not from your
current file — merge in anything of yours you want to keep, like
screenshots):**
- `disaster-science-sandbox/README.md`

**Leave alone:** anything else already in the repo I haven't mentioned.

**Then:** commit → tag `v2.1.0` (the disaster sandbox metadata now says 2.1.0 too) → push → create a GitHub Release from that
tag. If the Zenodo webhook is already connected, it archives automatically
as a new version under concept DOI `10.5281/zenodo.22909081`. **Check the
Zenodo draft before publishing** — the `.zenodo.json` should have primed
the license as Apache-2.0, but confirm the dropdown actually shows
"Apache License 2.0" and not the old MIT before you hit Publish.

---

## 2. Oncology sandbox
`github.com/drmarolla/rmti-oncology-sandbox`

Same steps as above, using the `oncology-sandbox/` folder instead. Concept
DOI: `10.5281/zenodo.22909090`.

One thing specific to this repo: **`DISCLAIMER.md` already exists there
and I haven't touched it** — I don't have its current content, so I
didn't try to guess and overwrite it. Leave it as-is; the in-app modal
already links to it.

---

## 3. Python reference implementation
`github.com/drmarolla/Risk-Mechanism-Theory-Index-RMTI-`

**Account move.** The repo previously lived under a different GitHub account. Zenodo's
GitHub link only sees repos of the account you connect (`drmarolla`), so either
(a) on the old repo go to Settings → Danger Zone → *Transfer ownership* → `drmarolla`
(keep the name; GitHub redirects the old URL), or (b) create the repo under `drmarolla`
and push the files there. Then switch it ON at zenodo.org → Account → GitHub → Sync now.
If you would rather not use the webhook, upload the release by hand: open the Zenodo record
(concept DOI `10.5281/zenodo.21445892`) → *New version* → upload `rmti-framework-v2.1.0.zip`.
On the new version set **Access = Open**, confirm license = Apache License 2.0, and check the
resource type (the v1.0.0 record is 'Software documentation'; `.zenodo.json` says 'software').

Replace the **entire repository contents** with everything in
`rmti-python/` (or use the standalone `rmti-framework-v2.1.0.zip` I gave
you separately — same contents). Then: commit → tag `v2.1.0` → push →
GitHub Release → Zenodo new version under concept DOI
`10.5281/zenodo.21445892`.

Run the test suite once before you push, just to see it pass on your own
machine, not just mine:
```
cd rmti-python
python -m unittest tests.test_rmti -v
```
Expect: `Ran 37 tests ... OK`.

---

## 4. RMTI Calculator

Not on GitHub/Zenodo — just replace wherever you currently host or share
the urban workbook with `RMTI_Calculator/RMTI_Calculator_v2.0.0.xlsx` (unchanged), and
share the new oncology workbook `RMTI_Calculator/RMTI_HCC_Calculator_v2.1.0.xlsx`
alongside it. The Word explainer is `docs/RMTI_Calculator_Explainer_v2.1.0.docx`.
If you'd like this archived with its own DOI too (as a Zenodo "software"
or "dataset" upload, or as a supplementary file attached to one of the
two sandbox records), that's a separate, new decision — say the word and
I'll help you set it up, but I didn't do it here since nothing in this
conversation established an existing repo or DOI for it.

---

## Note on versions

If v2.0.0 has **not** been uploaded yet, publish this folder as the release
instead (skip v2.0.0). If v2.0.0 is already live, v2.1.0 is a new version under
the same concept DOIs. Also: the archived Zenodo record 21445893 is v1.0.0;
the preprint's "version 1.1.0" was never published, so update the manuscript's
Code availability to cite the concept DOI 10.5281/zenodo.21445892 (or the
v2.1.0 version DOI once Zenodo assigns it).

---

## After all three are live: one loose end

Both sandboxes' `index.html` currently ship with an **empty**
`versionDoi` field (search for `TODO` in the `<script>` block). Zenodo
assigns that number at upload time, so it couldn't be known in advance.
Once each Zenodo upload finishes:

1. Copy the new version-specific DOI Zenodo gives you (something like
   `10.5281/zenodo.229090XX`).
2. Paste it into `RMTI_RELEASE.versionDoi` in that sandbox's `index.html`.
3. Commit that one-line change (no new release/tag needed for this — it's
   just filling in a number the file was already built to display).

Until you do this, the footer will just show the concept DOI without a
"this version:" line — not wrong, just incomplete.
