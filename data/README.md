# Data: IEEE-CIS Fraud Detection (Kaggle competition)

Link: https://www.kaggle.com/competitions/ieee-fraud-detection

## One-time setup (5 min)
1. Log in to Kaggle → open the link above → click **Join Competition / Late Submission** and accept the rules.
   (Without this, Kaggle won't let you attach the data to a notebook.)
2. Settings → verify your phone number (Kaggle needs it for internet/GPU in notebooks).

## Files we use
| File | What it is |
|---|---|
| train_transaction.csv | ~590K rows, one per transaction: amount, card, email domain, C/D/M/V columns, `isFraud` label |
| train_identity.csv | ~144K rows: device and browser info. Only some transactions have it |
| test_transaction.csv / test_identity.csv | Kaggle's unlabelled test set (we DON'T use it: no labels, so we can't measure anything) |

Join key: `TransactionID`. Time column: `TransactionDT` (seconds from a hidden start date).

## Where files live
- **Kaggle:** somewhere under `/kaggle/input/` once attached. Our notebooks search for the file, so the exact sub-path does not matter
- **Laptop:** `data/raw/` if you ever download the full CSVs (optional), `data/sample/` for the small sample we export from Kaggle in Step 1
