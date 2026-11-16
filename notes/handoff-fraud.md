# Handoff card: Cost-Sensitive Fraud Risk Model (Chat 2)

**Status (17 Nov 2026):** build complete, Steps 1–11. All code tested end-to-end on DEMO/fake data only.
**Real Kaggle run: PENDING**, so there are no real numbers yet. Never quote `metrics_DEMO.json`.
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

## Key numbers
- **Real:** pending. Fill them in from `reports/metrics.json` after the Kaggle "Save & Run All".
- **DEMO only (not quotable), but they matched the theory:**
  - random-split AUC > time-split AUC
  - recall at 0.5 was ~0.12
  - isotonic won on check Brier but overfit slightly on 3K rows
  - cost-rule test loss ≈ 43% of "flag nothing" (vs max-F1 ≈ 81%, 0.5 ≈ 88%)

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
1. Kaggle run → metrics.json → README "My real results" + the numbers in this card.
2. 10-question mock OA (posted in Chat 2, unanswered).
3. 5 mock-interview questions.
4. Build the Docker image once (it was untested: Docker Hub was blocked in the build sandbox).

## Notes for future chats
- Jupyter autosave overwrote appended notebook sections 3 times. Tell DP to click **Revert** (or File → Reload from Disk) before running.
- Sync: stage → append → commit with an mtime guard → verify cell count.
