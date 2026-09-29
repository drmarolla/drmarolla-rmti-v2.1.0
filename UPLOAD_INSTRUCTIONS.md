# Deployment & Upload Instructions (v2.1.0 Release Workflow)

This document outlines the step-by-step workflow for deploying version **v2.1.0** from this staging workspace across your three public GitHub repositories and updating their associated Zenodo records.

---

## 🛠️ Step 1: Deploy to `rmti-disaster-science-sandbox`

### 1.1 Local Workspace Preparation
Open your terminal and navigate to the directory containing your local clone of the disaster sandbox:
```bash
cd /path/to/rmti-disaster-science-sandbox
```

### 1.2 Sync Staging Changes
Copy the updated files from your staging folder `disaster-science-sandbox/` into this repository. Ensure the following version updates are reflected:
* `index.html` (Version bumped to 2.1.0, Apache 2.0 footer verified)
* `README.md` (Citation updated with the corrected disaster DOI: `10.5281/zenodo.22909081`)
* `CITATION.cff` and `.zenodo.json` (Bumped to 2.1.0)
* Root `LICENSE` and `NOTICE` files present.

### 1.3 Push to GitHub
```bash
git add .
git commit -m "Release v2.1.0: Bump version, correct citation DOI, and enforce Apache 2.0"
git branch -M main
git push origin main
```

### 1.4 Tag the Release
```bash
git tag -a v2.1.0 -m "Disaster Sandbox Oncology Release v2.1.0"
git push origin v2.1.0
```

---

## 🔬 Step 2: Deploy to `rmti-oncology-sandbox`

### 2.1 Local Workspace Preparation
```bash
cd /path/to/rmti-oncology-sandbox
```

### 2.2 Sync Staging Changes
Copy the updated files from the staging folder `oncology-sandbox/` into this repository. Ensure:
* `index.html` reflects the new vocabulary terms (`HCC_TIER_POSTURE`, "planned surveillance improvement").
* Unified population bounds (N from 100 to 5,000,000) and EAL per 1,000,000 metrics are implemented.
* `CITATION.cff` and `.zenodo.json` are updated to 2.1.0.

### 2.3 Push and Tag
```bash
git add .
git commit -m "Release v2.1.0: Standardize oncology vocabulary, population bounds, and metrics"
git branch -M main
git push origin main

git tag -a v2.1.0 -m "Oncology Sandbox Release v2.1.0"
git push origin v2.1.0
```

---

## 🐍 Step 3: Deploy to `Risk-Mechanism-Theory-Index-RMTI-` (Python Package)

### 3.1 Local Workspace Preparation
```bash
cd /path/to/Risk-Mechanism-Theory-Index-RMTI-
```

### 3.2 Sync Staging Changes
Copy the files from the staging folder `rmti-python/` into this repository. Double-check that:
* The test suite contains all 37 passing assertions (29 baseline + 8 new oncology module assertions).
* All updated `.py` source files include the Apache 2.0 copyright header.
* `CHANGELOG.md` accurately documents the floating-point rounding fixes, sorting bug corrections, and the wildfire case data synchronization.

### 3.3 Verify Tests Locally
Always run your test runner before pushing to guarantee nothing broke during the file migration:
```bash
pytest
```

### 3.4 Push and Tag
```bash
git add .
git commit -m "Release v2.1.0: Implement HCC module, expand test suite to 37, and fix edge-case bugs"
git branch -M main
git push origin main

git tag -a v2.1.0 -m "Python Reference Implementation Release v2.1.0"
git push origin v2.1.0
```

---

## 📜 Step 4: Publish GitHub Releases & Sync Zenodo

For each of the three repositories above, complete the final publishing steps on the web interface:

1. **Navigate to the Repository on GitHub.**
2. **Open the Releases Sidebar:** On the right side of the main page, click **Releases** -> **Draft a new release**.
3. **Select the Tag:** Choose the `v2.1.0` tag you just pushed via the command line.
4. **Generate Release Notes:** Click the **Generate release notes** button to automatically pull commit headlines.
5. **Publish:** Click **Publish release**.
6. **Zenodo Automation:** If your GitHub account is linked to Zenodo, publishing these releases will automatically trigger a webhook to mint your permanent v2.1.0 DOIs using the metadata provided in your `.zenodo.json` files.

---

## 📊 External Assets Note
The contents of **`RMTI_Calculator/`** (`RMTI_HCC_Calculator_v2.1.0.xlsx`) and **`docs/`** are intended for your self-hosted landing page or external documentation hub. Ensure these are uploaded alongside your release notifications so users can download the verified Excel tools.
