# Cost-Sensitive Fraud Risk Model

**On CVs:** GenAI-LLM, AI-Engineer, ML-Research, Data-Analyst, SDE-Backend (5 of 6)
**Dataset:** Kaggle IEEE-CIS Fraud Detection, about 590K card transactions, about 3.5% fraud

## What it does (plain words)
Predicts whether a card transaction is fraud. It doesn't stop at a score:
1. It makes the predicted probabilities honest (calibration), so "0.3" really means a 30% chance.
2. It picks the block/allow cut-off that loses the least money (expected cost), not a default 0.5.
3. It explains each decision (SHAP) and raises an alarm when new data drifts (PSI/KS).
4. It runs as an API (FastAPI) inside a Docker container.

## Pipeline
```
transaction.csv + identity.csv ──merge on TransactionID──► one table
  ▼
EDA (imbalance, missing values)  ──►  time-based split: train | valid | test
  ▼
LightGBM | XGBoost | CatBoost  ◄── Optuna tunes settings (scored on valid only)
  ▼
isotonic calibration (fit on held-out data)  ──►  PR-AUC + Brier
  ▼
threshold = lowest expected $ cost  ──►  SHAP explanations + PSI/KS drift
  ▼
FastAPI /score endpoint  ──►  Docker container
```

## CV bullets → where each one is built

| CV bullet | Files | Step |
|---|---|---|
| B1: Optuna-tuned LightGBM, XGBoost, CatBoost on 590K+ transactions, 390+ features, class imbalance | pipeline §1–§3, §5 + playground | 1–6, 8 |
| B2: isotonic calibration, PR-AUC + Brier, thresholds by expected monetary cost | pipeline §4, §6, §7 + playground §F | 7, 9 |
| B3: PSI/KS drift detection + SHAP explainability, containerised FastAPI service on Docker | pipeline §8–§9 + src/, api/, Dockerfile | 10–11 |

## Folder map

| Folder | What goes in it | Why |
|---|---|---|
| data/raw | the original Kaggle CSVs (laptop only, optional) | never edit raw data, so you can always restart |
| data/sample | a small sample made on Kaggle (e.g. 50K rows) | lets the laptop run things without 1.3 GB of RAM |
| data/processed | cleaned or merged data saved by notebooks | saves re-running slow steps |
| notebooks | fraud_pipeline.ipynb (grows each step) + concepts_playground.ipynb | learning + experiments |
| src | `fraud_service.py`: loads the 4 trained files once; `score()` + `drift()` | the API imports it (Step 11) |
| models | saved model + calibrator files | the API loads them |
| reports | figures + metrics.json | your REAL numbers for interviews |
| api | `main.py`: FastAPI app with GET /health, POST /score, POST /drift | Step 11 |
| tests | `test_api.py`: 4 quick API tests (`pytest -q`) | Step 11 |
| notes | step notes, interview lines, handoff card | revision before interviews |

## Step checklist
Files: ONE growing notebook `notebooks/fraud_pipeline.ipynb` (each step adds a section §n)
+ `notebooks/concepts_playground.ipynb` (tiny by-hand demos on toy data, runs on the laptop in seconds).

- [x] 01 Data + merge + EDA + why accuracy lies → pipeline §0–§1
- [x] 02 Time-based split + leakage → pipeline §2 (+ leakage demo: random vs time split AUC)
- [x] 03 Decision tree from zero (Gini/entropy by hand) → playground §A
- [x] 04 Random forest = bagging + feature randomness → playground §B
- [x] 05 Boosting: AdaBoost idea → gradient boosting → playground §C
- [x] 06 LightGBM vs XGBoost vs CatBoost + imbalance → pipeline §3
- [x] 07 Metrics: precision/recall/F1, ROC-AUC vs PR-AUC → pipeline §4 + playground §D
- [x] 08 Optuna tuning → pipeline §5 + playground §E
- [x] 08b Re-teach: TPE by hand → playground §E2
- [x] 09 Calibration + expected-cost threshold (merged, one-day mode) → pipeline §6–§7 + playground §F
- [x] 10 SHAP + PSI/KS drift → pipeline §8–§9 (needs `pip install shap` on the laptop)
- [x] 11 FastAPI + Docker → pipeline §10 (export) + `src/fraud_service.py`, `api/main.py`, `Dockerfile`, `requirements-serve.txt`, `tests/test_api.py`
- [ ] 12 Wrap-up: mock OA + mock interview + handoff card → `notes/handoff-fraud.md`

Kaggle checkpoint: ✅ done 17 Nov 2026 (full data). Real numbers below; the Kaggle output zip is kept on the laptop in `kaggle_run/results.zip`.

## My real results (Kaggle run, 17 Nov 2026)
Source: `reports/metrics.json`, from the full Kaggle "Save & Run All" (FAST_MODE = True: learning rate 0.1, max 1,000 trees, 20 Optuna trials).
Data: 590,540 transactions, 434 columns after the merge → 431 features, 3.50% fraud. Time split: train 413,378 | valid 88,581 | test 88,581.

**1. Three boosters, default settings (validation set)**

| Model | PR-AUC | ROC-AUC | Recall at 50% precision | Trees used (cap 1,000) | Train time |
|---|---|---|---|---|---|
| LightGBM | **0.656** | **0.928** | **0.675** | 965 | 350 s |
| XGBoost | 0.599 | 0.915 | 0.602 | 775 | 954 s |
| CatBoost | 0.595 | 0.909 | 0.595 | 986 | 2,346 s |

Random baseline PR-AUC = fraud rate ≈ 0.034. Leakage demo: random split AUC 0.9525 vs time split 0.9204.

**2. Final model = Optuna-tuned LightGBM:** valid PR-AUC 0.656 → 0.660 (20 trials; small gain).

**3. Calibration (test set; fit on the earlier half of valid)**

| Version | Brier (lower = better) | PR-AUC |
|---|---|---|
| raw | 0.0236 | 0.562 |
| Platt | 0.0236 | 0.562 |
| **isotonic** | **0.0215** | 0.542 |
| always say the base rate | 0.0336 | — |

**4. Decision rule on the test set** (88,581 transactions, about 3,080 frauds, $10 per false alarm)

| Rule | Total cost | Flagged | Fraud caught |
|---|---|---|---|
| **flag if p × amount > (1 − p) × $10, isotonic p** | **$161,369** | 7,008 | 2,011 |
| max-F1 threshold (0.26) | $283,650 | 2,699 | 1,589 |
| same cost rule, raw p (not calibrated) | $309,568 | 1,684 | 1,251 |
| threshold 0.5 | $332,344 | 1,758 | 1,301 |
| flag nothing | $469,608 | 0 | 0 |

**5. SHAP top features:** C13, TransactionAmt, C1, card1, card2, addr1, D1, C5, C14, C2 (additivity error 0.0003).
**6. Drift (valid → test):** every PSI < 0.03 (largest: C13 0.025, D1 0.023); model score PSI 0.011 → all stable.
**7. API with the real model:** pytest 4/4 pass; /score ≈ 25 ms for the prediction + ≈ 300 ms for SHAP reasons (887 trees × 375 leaves, on a test machine).

## How to run
- **Kaggle (heavy steps):** New Notebook → File → Import Notebook → pick the `.ipynb` from `notebooks/` → Add Input → Competition "IEEE-CIS Fraud Detection" → Run All. Download outputs from the right panel (Output) into `reports/` and `models/`.
- **Laptop (light steps):** see the main `cv-projects/README.md` for how to open Jupyter. Install libraries once: `pip install -r requirements.txt`
- **Laptop with no data = DEMO mode:** the notebook makes a small FAKE fraud-like table so every cell runs in ~1 min (for practising the code). Demo numbers go to `reports/metrics_DEMO.json` and must never be quoted as results.

## Run the API (Step 11)
`models/` now holds the REAL Kaggle-trained files (`final_lightgbm_tuned.joblib`, `isotonic_calibrator.joblib`, `drift_reference.json`, `feature_info.json`), and `requirements-serve.txt` has the exact versions Kaggle trained them with.
⚠️ Don't "Run All" the laptop notebook in DEMO mode: it would overwrite `models/` and `reports/figures/` with fake-data versions. If that happens, unzip `kaggle_run/results.zip` again.

**A. Laptop, no Docker (Anaconda Prompt, inside the project folder):**
```
pip install -r requirements-serve.txt
uvicorn api.main:app --reload --port 8000
```
Open http://127.0.0.1:8000/docs → POST /score → "Try it out" → paste `{"TransactionAmt": 480, "ProductCD": "C", "P_emaildomain": "anonymous.com", "DeviceType": "mobile"}` → Execute.
If your laptop's library versions differ from the pins, sklearn may print an `InconsistentVersionWarning`. That is a warning, not an error: it was tested and gives the same scores. Docker uses the exact pins.
Tests: `pytest -q` (4 tests: health, score, bad input → 422, drift).

**B. Docker (needs Docker Desktop on Windows):**
```
docker build -t fraud-api .
docker run -p 8000:8000 fraud-api
```
Then the same http://127.0.0.1:8000/docs page.
