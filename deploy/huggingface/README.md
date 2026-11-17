---
title: Fraud Risk Scoring API
emoji: 💳
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
pinned: false
short_description: Cost-aware fraud scoring with LightGBM, isotonic and SHAP
---

# Fraud risk scoring API

FastAPI service in a Docker container. It scores one card transaction and returns:

- a **calibrated fraud probability** (LightGBM + isotonic regression),
- a **FLAG / PASS** decision from the expected-cost rule: flag if p × amount > (1 − p) × $10,
- the **top 3 SHAP reasons** behind the score.

Open the Space for a phone-friendly form, or `/docs` to call every endpoint (`/score`, `/drift`, `/health`).

**Model:** LightGBM tuned with Optuna on the IEEE-CIS Fraud Detection data (590,540 transactions, 431 features, time-based split).
On the held-out test months, the cost rule cut total cost from $332K (threshold 0.5) to $161K.

Code, notebook and full results: https://github.com/dpathriya8-maker/cost-sensitive-fraud-risk-model
The training data is not included here, only the trained model files.
