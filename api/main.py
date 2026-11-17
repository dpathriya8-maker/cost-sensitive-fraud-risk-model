"""Fraud risk scoring API.

Run on your laptop (from the project folder, in Anaconda Prompt):
    pip install -r requirements-serve.txt
    uvicorn api.main:app --reload --port 8000
Then open http://127.0.0.1:8000 for the phone-friendly demo page,
or http://127.0.0.1:8000/docs to try every endpoint.
"""
import os                                              # read environment variables (MODEL_DIR)
from contextlib import asynccontextmanager             # lets us run code at server start and stop
from pathlib import Path                               # find demo.html next to this file

from fastapi import FastAPI                            # the web framework
from fastapi.responses import HTMLResponse             # send a web page instead of JSON
from pydantic import BaseModel, ConfigDict, Field      # input/output schemas with automatic checking

from src.fraud_service import FraudScorer              # our scoring logic (src/fraud_service.py)

MODEL_DIR = os.getenv("MODEL_DIR", "models")           # folder with the 4 trained files; Docker sets it to /app/models
DEMO_PAGE = Path(__file__).parent / "demo.html"        # the small web form (api/demo.html)
state = {}                                             # holds the loaded scorer while the server runs


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["scorer"] = FraudScorer(MODEL_DIR)           # load ONCE at startup (not on every request)
    yield                                              # the server runs and answers requests here
    state.clear()                                      # tidy up when the server stops


app = FastAPI(title="Fraud risk scoring API", version="1.0", lifespan=lifespan)


class Transaction(BaseModel):
    """One transaction. Named fields are checked; any other IEEE-CIS column is also accepted."""
    model_config = ConfigDict(extra="allow")           # accept the other ~390 columns too
    TransactionAmt: float = Field(gt=0, description="amount in dollars, must be > 0")
    ProductCD: str | None = None
    card1: float | None = None
    P_emaildomain: str | None = None
    DeviceType: str | None = None


class Reason(BaseModel):
    feature: str
    value: float | str | None
    shap: float
    direction: str


class ScoreResponse(BaseModel):
    fraud_probability: float
    raw_score: float
    decision: str
    threshold_for_this_amount: float
    top_reasons: list[Reason]
    model_version: str


class DriftRequest(BaseModel):
    transactions: list[Transaction] = Field(min_length=50, description="at least 50 recent transactions")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def demo_page():
    """Phone-friendly form that calls POST /score (open the server's address in any browser)."""
    return DEMO_PAGE.read_text(encoding="utf-8")


@app.get("/health")
def health():
    """Monitoring check: is the server up and the model loaded?"""
    return {"status": "ok", "model_loaded": "scorer" in state}


@app.post("/score", response_model=ScoreResponse)
def score(transaction: Transaction):
    """Score ONE transaction: honest probability, FLAG/PASS by expected cost, top-3 SHAP reasons."""
    return state["scorer"].score(transaction.model_dump())


@app.post("/drift")
def drift(request: DriftRequest):
    """PSI of recent transactions vs training, per monitored feature."""
    return state["scorer"].drift([item.model_dump() for item in request.transactions])
