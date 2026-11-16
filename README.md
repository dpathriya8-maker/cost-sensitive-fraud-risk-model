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
| src | clean .py code: features, predict, drift | the API imports it (Step 11) |
| models | saved model + calibrator files | the API loads them |
| reports | figures + metrics.json | your REAL numbers for interviews |
| api | FastAPI app | Step 11 |
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
- [ ] 10 SHAP + PSI/KS drift → pipeline §8–§9
- [ ] 11 FastAPI + Docker → `src/`, `api/main.py`, `Dockerfile`
- [ ] 12 Wrap-up: mock OA + mock interview + handoff card → `notes/handoff-fraud.md`

Kaggle checkpoints (Run All, optional but gives your real numbers): now (after Step 9), and after Step 10.

## My real results
Fill ONLY from `reports/metrics.json` after running on Kaggle. Never type a number here that you didn't produce.

| Model | PR-AUC (test) | ROC-AUC (test) | Brier before → after calibration | Chosen threshold | Expected cost |
|---|---|---|---|---|---|
| LightGBM | | | | | |
| XGBoost | | | | | |
| CatBoost | | | | | |

## How to run
- **Kaggle (heavy steps):** New Notebook → File → Import Notebook → pick the `.ipynb` from `notebooks/` → Add Input → Competition "IEEE-CIS Fraud Detection" → Run All. Download outputs from the right panel (Output) into `reports/` and `models/`.
- **Laptop (light steps):** see the main `cv-projects/README.md` for how to open Jupyter. Install libraries once: `pip install -r requirements.txt`
- **Laptop with no data = DEMO mode:** the notebook makes a small FAKE fraud-like table so every cell runs in ~1 min (for practising the code). Demo numbers go to `reports/metrics_DEMO.json` and must never be quoted as results.
