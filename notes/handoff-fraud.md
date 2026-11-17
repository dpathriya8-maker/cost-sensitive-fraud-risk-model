# Handoff card: Cost-Sensitive Fraud Risk Model (Chat 2)

**Status (17 Nov 2026):** build complete, Steps 1–11. **Real Kaggle run DONE** (full 590,540 rows, FAST_MODE). The API was tested with the real model (pytest 4/4).
Quote only `reports/metrics.json`. Never quote `metrics_DEMO.json`.
Repo: https://github.com/dpathriya8-maker/cost-sensitive-fraud-risk-model ·
Study guide (every step, mistakes, video links): https://claude.ai/artifact/XTgY72uizbDEQByGGNGP1P

## Pipeline in 5 lines
1. IEEE-CIS: ~590K transactions, transaction ⟕ identity (left join), ~3.5% fraud. Accuracy is useless here.
2. Time split 70/15/15 by TransactionDT. The leakage demo showed a random split inflates AUC.
3. LightGBM / XGBoost / CatBoost with early stopping at the natural ratio, judged by PR-AUC. LightGBM was Optuna (TPE) tuned.
4. Isotonic calibration (fit on the earlier half of valid, checked on the later half; Brier + reliability diagram) → expected-cost rule: flag if p × amount > (1 − p) × $10.
5. TreeSHAP reason codes + PSI/KS drift on the top-10 SHAP features and the score → FastAPI (/health, /score, /drift) + Dockerfile (pinned versions).

## CV bullets (SDE-Backend wording)
- **Optuna-tuned LightGBM, XGBoost, CatBoost on 590K+ transactions, 390+ features, class imbalance:** three boosters on a time split, natural class ratio, PR-AUC, TPE tuning on valid PR-AUC, test kept locked. Note: §5 tunes LightGBM fully; the XGBoost/CatBoost objectives are behind `TUNE_ALL_THREE`.
- **Isotonic calibration, PR-AUC + Brier, thresholds by expected monetary cost:** PR-AUC checks ranking; the cost rule needs honest p values, so isotonic was fit on held-out data. The threshold is per transaction: p* = C_FP / (C_FP + amount).
- **PSI/KS drift + SHAP as a containerised FastAPI service on Docker:** artifacts are loaded once at startup, inputs are validated by Pydantic (422), and /score returns p, FLAG/PASS and the top-3 SHAP reasons. /drift computes PSI against the train bins.

## Top interview Q&As
These are in the study guide, "Top 12 interview questions": why not accuracy · why a time split · bagging vs boosting · why 3 libraries · imbalance (no SMOTE) · PR-AUC vs ROC-AUC · how TPE works · why calibrate · how the threshold was chosen · PSI > 0.25 · SHAP vs feature importance · FastAPI/Docker + throughput.

## Key numbers (real, from reports/metrics.json)
- **Data:** 590,540 rows, 431 features, 3.50% fraud. Time split 413,378 / 88,581 / 88,581.
- **Leakage demo:** random-split AUC 0.9525 vs time-split 0.9204, so a random split inflates AUC by about 0.03.
- **Boosters (valid PR-AUC / ROC-AUC):**
  - LightGBM 0.656 / 0.928, trained in 350 s
  - XGBoost 0.599 / 0.915, 954 s
  - CatBoost 0.595 / 0.909, 2,346 s
  - Baseline PR-AUC is 0.034, so LightGBM is about 19× better than random.
  - LightGBM catches 67.5% of fraud at 50% precision.
- **Optuna (20 trials):** 0.656 → 0.660, a small gain. Defaults were already strong.
- **At 0.5:** precision 0.90 but recall only 0.39. That is why 0.5 is the wrong cut-off.
- **Calibration:** the raw model under-predicted on future data (a 0.12 bin was really 0.24; mean p 0.015 vs a true 0.034).
  - Isotonic test Brier: 0.0236 → 0.0215 (−9%). Brier skill vs the base rate: 0.30 → 0.36.
  - Platt did not help.
  - Isotonic costs a little PR-AUC (0.562 → 0.542) because it creates tied scores.
- **Cost (test):**
  - The cost rule with isotonic p costs $161K, against $332K at 0.5 (−51%), $284K at max-F1 (−43%) and $470K for flag nothing (−66%).
  - The same rule with raw p costs $310K, so calibration alone halves the cost.
  - It catches 2,011 of ~3,080 frauds (65% by count, ~76% by dollars).
  - Formula threshold p* = 10 / (10 + 173.53) = 0.0545, and the threshold scan agrees (0.055).
- **SHAP top features:** C13, TransactionAmt, C1, card1, card2, addr1, D1.
- **Drift:** all PSI < 0.03 (stable), score PSI 0.011.
  - KS p-values ≈ 0 only because n is huge (effect size matters, not the p-value).
- **Honest gaps:**
  - Valid → test PR-AUC drops 0.66 → 0.56: the valid set was used for early stopping and tuning, and later data has more unseen cards.
  - LightGBM and CatBoost used 965 and 986 of 1,000 trees, so they were still improving (FAST_MODE).
  - There is no feature engineering. The Kaggle winners built user-ID aggregates.
- **Latency:** prediction ≈ 25 ms and SHAP ≈ 300 ms per request. SHAP dominates.

## Weak spots / Revisit list
- **Code reading is the weakest area:** function vs variable vs library, so use the under-line, tagged explanation format.
- PSI arithmetic.
- axis=0/1.
- Brier is a mean, not a sum.
- `^` vs `**`.
- Duplicate function names.
- Optuna objective blanks (S-M-R).
- TPE models densities, not the score curve.
- Pruning vs early stopping (fixed in the re-test).
- Calibration feel: fixed with the visualizer.
- Running max: fixed.

## Pending
1. ✅ Kaggle run done (17 Nov).
2. 10-question mock OA (posted in Chat 2, unanswered).
3. 5 mock-interview questions.
4. Build the Docker image once (it was untested: Docker Hub was blocked in the build sandbox).
5. Laptop sync: copy the real `models/`, `reports/` and the updated README/pins into `Desktop\cv-projects\02-fraud-risk-model` (the desktop bridge was offline on 17 Nov). The GitHub repo already has everything except the models.

## Notes for future chats
- Jupyter autosave overwrote appended notebook sections 3 times. Tell DP to click **Revert** (or File → Reload from Disk) before running.
- Sync: stage → append → commit with an mtime guard → verify cell count.
