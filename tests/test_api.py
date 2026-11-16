"""Quick API tests. Run from the project folder:  pytest -q
Needs the 4 trained files in models/ (notebook §10); otherwise the tests are skipped."""
from pathlib import Path

import pytest

MODEL_FILES = ["final_lightgbm_tuned.joblib", "isotonic_calibrator.joblib", "drift_reference.json", "feature_info.json"]
if not all((Path("models") / name).exists() for name in MODEL_FILES):
    pytest.skip("models/ is not filled yet: run the notebook up to §10 first", allow_module_level=True)

from fastapi.testclient import TestClient   # noqa: E402  (import after the skip check)
from api.main import app                    # noqa: E402

GOOD_TRANSACTION = {"TransactionAmt": 480.0, "ProductCD": "C", "P_emaildomain": "anonymous.com", "DeviceType": "mobile"}


def test_health():
    with TestClient(app) as client:          # "with" runs the startup (model loading) first
        reply = client.get("/health")
    assert reply.status_code == 200 and reply.json()["model_loaded"] is True


def test_score_good_transaction():
    with TestClient(app) as client:
        reply = client.post("/score", json=GOOD_TRANSACTION)
    body = reply.json()
    assert reply.status_code == 200
    assert 0.0 <= body["fraud_probability"] <= 1.0
    assert body["decision"] in {"FLAG", "PASS"}
    assert len(body["top_reasons"]) == 3


def test_score_rejects_bad_amount():
    with TestClient(app) as client:
        reply = client.post("/score", json={**GOOD_TRANSACTION, "TransactionAmt": "abc"})
    assert reply.status_code == 422          # Pydantic stops bad input before the model runs


def test_drift_needs_50_rows_and_returns_psi():
    with TestClient(app) as client:
        too_few = client.post("/drift", json={"transactions": [GOOD_TRANSACTION] * 10})
        enough = client.post("/drift", json={"transactions": [GOOD_TRANSACTION] * 60})
    assert too_few.status_code == 422
    assert enough.status_code == 200 and "features" in enough.json()
