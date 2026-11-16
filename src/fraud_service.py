"""Fraud scoring logic used by the API (api/main.py).

Loads the 4 trained files ONCE, then:
  score(transaction)  -> honest fraud probability + FLAG/PASS decision + top-3 SHAP reasons
  drift(transactions) -> PSI per monitored feature against the training distribution
"""
import json                                    # read the .json files made in the notebook
from pathlib import Path                       # file paths that work on Windows and Linux

import joblib                                  # load the saved model / calibrator
import numpy as np                             # number arrays
import pandas as pd                            # tables (the model expects a DataFrame)
import shap                                    # TreeSHAP explanations


def psi_verdict(psi_value):
    """Rule of thumb: < 0.10 stable, 0.10-0.25 watch, > 0.25 major shift."""
    if psi_value < 0.10:
        return "stable"
    if psi_value <= 0.25:
        return "watch"
    return "MAJOR"


def to_json_value(value):
    """Turn NumPy / pandas values into plain Python values that JSON can carry."""
    if value is None or (isinstance(value, float) and np.isnan(value)) or pd.isna(value):
        return None
    if isinstance(value, (np.floating, float)):
        return float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    return str(value)


class FraudScorer:
    """Everything the service needs, loaded once and kept in memory."""

    def __init__(self, model_dir):
        model_dir = Path(model_dir)
        self.model = joblib.load(model_dir / "final_lightgbm_tuned.joblib")        # tuned LightGBM (notebook §5)
        self.calibrator = joblib.load(model_dir / "isotonic_calibrator.joblib")    # isotonic translator (§6)
        info = json.loads((model_dir / "feature_info.json").read_text())           # column order etc. (§10)
        self.feature_columns = info["feature_columns"]
        self.text_columns = set(info["text_columns"])
        self.false_alarm_cost = float(info["false_alarm_cost"])
        self.model_version = info["model_version"]
        reference = json.loads((model_dir / "drift_reference.json").read_text())   # train bins (§9)
        self.drift_reference = {}
        for feature, value in reference.items():
            if isinstance(value, list):                    # older §9 format: a plain list of 11 decile edges
                n_bins = len(value) - 1
                value = {"inner_edges": value[1:-1], "expected_share": [1 / n_bins] * n_bins}
            self.drift_reference[feature] = value
        self.explainer = shap.TreeExplainer(self.model)                             # built once, reused per request

    def to_table(self, transactions):
        """List of dicts -> DataFrame with the EXACT training columns and types."""
        table = pd.DataFrame(transactions).reindex(columns=self.feature_columns)  # missing columns -> NaN, extra ones dropped
        for column in self.feature_columns:
            if column in self.text_columns:
                table[column] = table[column].astype("category")      # LightGBM maps these to its training categories
            else:
                table[column] = pd.to_numeric(table[column], errors="coerce").astype("float32")  # text like "abc" -> NaN
        return table

    def score(self, transaction):
        """One transaction (dict) -> decision dict."""
        table = self.to_table([transaction])
        raw_score = float(self.model.predict_proba(table)[:, 1][0])          # LightGBM's raw P(fraud)
        probability = float(self.calibrator.predict([raw_score])[0])         # honest P(fraud) after isotonic
        amount = float(transaction.get("TransactionAmt") or 0.0)
        flag = probability * amount > (1 - probability) * self.false_alarm_cost  # expected-cost rule from §7

        explanation = self.explainer(table)                                  # TreeSHAP for this one row
        pushes = np.asarray(explanation.values)[0]
        if pushes.ndim == 2:                                                 # some shap versions: one column per class
            pushes = pushes[:, 1]
        top_positions = np.argsort(-np.abs(pushes))[:3]                     # 3 biggest pushes (either direction)
        reasons = [{"feature": self.feature_columns[i],
                    "value": to_json_value(table.iloc[0, i]),
                    "shap": round(float(pushes[i]), 4),
                    "direction": "toward fraud" if pushes[i] > 0 else "toward legit"}
                   for i in top_positions]

        return {"fraud_probability": round(probability, 4),
                "raw_score": round(raw_score, 4),
                "decision": "FLAG" if flag else "PASS",
                "threshold_for_this_amount": round(self.false_alarm_cost / (self.false_alarm_cost + amount), 4) if amount > 0 else 1.0,
                "top_reasons": reasons,
                "model_version": self.model_version}

    def drift(self, transactions):
        """A batch of recent transactions -> PSI per monitored feature."""
        table = self.to_table(transactions)
        features = {}
        for feature, reference in self.drift_reference.items():
            values = table[feature].to_numpy(dtype=float)
            values = values[~np.isnan(values)]                               # ignore missing values
            if len(values) == 0:
                continue
            edges = np.concatenate([[-np.inf], reference["inner_edges"], [np.inf]])  # same bins as training
            actual_share = np.clip(np.histogram(values, bins=edges)[0] / len(values), 1e-4, None)
            expected_share = np.clip(np.array(reference["expected_share"]), 1e-4, None)
            psi_value = float(np.sum((actual_share - expected_share) * np.log(actual_share / expected_share)))
            features[feature] = {"psi": round(psi_value, 4), "status": psi_verdict(psi_value), "rows_used": int(len(values))}
        return {"rows_received": len(transactions),
                "features": features,
                "alarm": any(item["status"] == "MAJOR" for item in features.values())}
