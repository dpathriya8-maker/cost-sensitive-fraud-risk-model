# Notebooks

- `fraud_pipeline.ipynb`: the real project. One section per step (§0 setup, §1 EDA, §2 split, ...). Run on Kaggle.
- `concepts_playground.ipynb`: tiny by-hand demos (Gini, bagging, boosting) on 10-row toy data. Runs on the laptop.

The setup cell (§0) detects Kaggle vs laptop and finds the data. Every section ends by saving its numbers
to `reports/metrics.json` with `save_metrics(...)`, so your interview numbers come from code.
