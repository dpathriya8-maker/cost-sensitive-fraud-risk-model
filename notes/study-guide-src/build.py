"""Build the Fraud Risk Model study guide PDF (A4, Text-to-SQL guide style)."""
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
                                KeepTogether, PageBreak, CondPageBreak)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", FONT_DIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVI", FONT_DIR + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DVBI", FONT_DIR + "DejaVuSans-BoldOblique.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("DV", normal="DV", bold="DVB", italic="DVI", boldItalic="DVBI")

M = json.load(open("/tmp/kres/out/reports/metrics.json"))

INK = colors.HexColor("#333331"); MUTED = colors.HexColor("#767673")
PURPLE = "#534ab7"; PURPLE_L = "#eeedfe"; DPURPLE = "#3c3489"
GREEN = "#0f6e56"; GREEN_L = "#e1f5ee"
AMBER = "#854f0b"; AMBER_L = "#faeeda"
BLUE = "#185fa5"; BLUE_L = "#e6f1fb"
RED = "#993c1d"; RED_L = "#faece7"
GRAY = "#5f5e5a"; GRAY_L = "#f1efe8"
ALT = colors.HexColor("#f6f5f0"); LINE = colors.HexColor("#dddcd5")

PAGE_W, PAGE_H = A4
LM = RM = 15 * mm
CONTENT_W = PAGE_W - LM - RM

body = ParagraphStyle("body", fontName="DV", fontSize=8.5, leading=11.4, textColor=INK, alignment=TA_LEFT)
small = ParagraphStyle("small", parent=body, fontSize=7.8, leading=10.2)
cell = ParagraphStyle("cell", parent=body, fontSize=7.8, leading=10.0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="DVB")
headcell = ParagraphStyle("headcell", parent=cell, fontName="DVB", textColor=colors.white)
qstyle = ParagraphStyle("q", parent=body, fontName="DVB", fontSize=8.8, leading=11.6, spaceBefore=3)
really = ParagraphStyle("really", parent=body, fontName="DVI", fontSize=7.9, leading=10.2, textColor=MUTED, leftIndent=9)
ans = ParagraphStyle("ans", parent=body, leftIndent=9, spaceAfter=3.5)
band_style = ParagraphStyle("band", fontName="DVB", fontSize=13, leading=16, textColor=colors.white)
box_title = ParagraphStyle("boxt", parent=body, fontName="DVB", fontSize=8.6, leading=11)


def amber(text):
    return f'<font color="{AMBER}"><b>{text}</b></font>'


def green(text):
    return f'<font color="{GREEN}"><b>{text}</b></font>'


def red(text):
    return f'<font color="{RED}"><b>{text}</b></font>'


def link(text, url):
    return f'<a href="{url}" color="{BLUE}"><u>{text}</u></a>'


def band(title, color):
    t = Table([[Paragraph(title, band_style)]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(color)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def callout(title, text, color, fill):
    t = Table([[Paragraph(f'<font color="{color}"><b>{title}</b></font> ' + text, body)]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(fill)),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(color)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def cv_box(title, text, color, fill):
    t = Table([[Paragraph(f'<font color="{color}"><b>{title}</b></font>', box_title)],
               [Paragraph(text, ParagraphStyle("cvb", parent=body, fontSize=8.8, leading=12))]],
              colWidths=[CONTENT_W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(fill)),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(color)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (0, 0), 6), ("TOPPADDING", (0, 1), (0, 1), 1),
                           ("BOTTOMPADDING", (0, -1), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (0, 0), 1)]))
    return t


def table(rows, widths, head_color, bold_first=False):
    data = [[Paragraph(h, headcell) for h in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(str(c), cellb if (bold_first and i == 0) else cell) for i, c in enumerate(r)])
    t = Table(data, colWidths=[w * CONTENT_W for w in widths], repeatRows=1)
    style = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(head_color)),
             ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
             ("TOPPADDING", (0, 0), (-1, -1), 3.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.6),
             ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE)]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ALT))
    t.setStyle(TableStyle(style))
    return t


def qa(question, asking, answer):
    return KeepTogether([Paragraph(f'<font color="{BLUE}">Q.</font> {question}', qstyle),
                         Paragraph(f"Really asking: {asking}", really),
                         Paragraph(answer, ans)])


def image(path, width):
    from PIL import Image as PILImage
    w, h = PILImage.open(path).size
    return Image(path, width=width, height=width * h / w)


# ------------------------------------------------------------------ page decorations
def on_first(canvas, doc):
    canvas.saveState()
    band_h = 50 * mm
    canvas.setFillColor(colors.HexColor(PURPLE))
    canvas.rect(0, PAGE_H - band_h, PAGE_W, band_h, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("DVB", 22)
    canvas.drawString(LM, PAGE_H - 19 * mm, "Cost-Sensitive Fraud Risk Model")
    canvas.setFont("DV", 10)
    canvas.drawString(LM, PAGE_H - 27 * mm,
                      "Interview study guide · LightGBM, XGBoost, CatBoost · isotonic calibration · SHAP · FastAPI + Docker")
    canvas.drawString(LM, PAGE_H - 33 * mm, "Deepanshu (DP) · IIT Delhi · real Kaggle run 17 Nov 2026 · guide 19 Nov 2026")
    canvas.setFillColor(colors.HexColor("#f6c35b"))
    headline = "Final result: test cost $161K vs $332K at the 0.5 threshold (−51%) on 88,581 unseen payments"
    size = 10.5
    while pdfmetrics.stringWidth(headline, "DVB", size) > CONTENT_W and size > 7:
        size -= 0.25
    canvas.setFont("DVB", size)
    canvas.drawString(LM, PAGE_H - 42 * mm, headline)
    footer(canvas, doc)
    canvas.restoreState()


def footer(canvas, doc):
    canvas.setFont("DV", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(LM, 9 * mm, "Fraud risk model · study guide · real numbers from reports/metrics.json (Kaggle run, 17 Nov 2026)")
    canvas.drawRightString(PAGE_W - RM, 9 * mm, str(doc.page))


def on_later(canvas, doc):
    canvas.saveState(); footer(canvas, doc); canvas.restoreState()


story = []

# ------------------------------------------------------------------ 1. cover
story.append(Spacer(1, 42 * mm))
story.append(Paragraph(
    "On your CVs (portal slot, CV inside, position): Analytics (Data Analyst) #2 · Finance (SDE-Backend = software development engineer) #5 · "
    "Consulting (AI Engineer, AI = artificial intelligence) #6 · Information Technology (GenAI-LLM = generative AI, large language models) #6 · "
    "Teaching &amp; Research (ML Research = machine learning) #6. Not on Core Chemical. "
    f"Colour key: {green('green = why / win')} · {red('red = trap / problem')} · {amber('amber = number')} · "
    f'<font color="{BLUE}"><b>blue = question / link</b></font>.', small))
story.append(Spacer(1, 6))
story.append(cv_box("CV bullet 1", "Optuna-tuned LightGBM, XGBoost and CatBoost on 590K+ transactions with 390+ features under class imbalance", PURPLE, PURPLE_L))
story.append(Spacer(1, 5))
story.append(cv_box("CV bullet 2", "Calibrated outputs via isotonic regression, scored on PR-AUC and Brier, setting thresholds by expected monetary cost", GREEN, GREEN_L))
story.append(Spacer(1, 5))
story.append(cv_box("CV bullet 3", "Deployed PSI/KS drift detection and SHAP explainability as a containerised FastAPI scoring service on Docker"
                    '<br/><font size="7.6" color="#767673">(Data Analyst CV wording: "PSI/KS drift monitoring" instead of "drift detection".)</font>', AMBER, AMBER_L))
story.append(Spacer(1, 6))
story.append(callout("30-second pitch:",
    "A card company must decide in milliseconds whether to stop a payment. I trained three gradient-boosted tree models on "
    "590K real transactions with a time-based split, tuned the best one (LightGBM) with Optuna, and calibrated its scores with "
    "isotonic regression so that 20% really means 20%. Instead of a fixed 0.5 cut-off, a payment is flagged when its expected "
    "fraud loss is bigger than the $10 cost of a review. On later, unseen months that cut total cost from $332K to $161K. "
    "SHAP gives the top reasons for each decision, PSI and KS watch for drift, and it all runs as a FastAPI service in Docker.",
    GREEN, GREEN_L))
story.append(Spacer(1, 7))
story.append(table([
    ["word", "plain meaning"],
    ["IEEE-CIS data", "Kaggle fraud data from the IEEE Computational Intelligence Society (Institute of Electrical and Electronics Engineers) and Vesta: 590,540 card payments, 3.5% fraud"],
    ["GBDT (gradient-boosted decision trees)", "many small trees added one after another, each one fixing the mistakes of the trees before it; LightGBM, XGBoost and CatBoost are three libraries for this"],
    ["PR-AUC (precision–recall area under the curve)", "how well fraud is ranked above legit, judged on the rare fraud class; a random guess scores the fraud rate (0.035)"],
    ["ROC-AUC (receiver operating characteristic AUC)", "chance that a random fraud gets a higher score than a random legit payment; looks high when legit rows are plentiful"],
    ["calibration · isotonic regression", "making scores match real frequencies; isotonic = a non-decreasing step function fitted on held-out data"],
    ["Brier score", "average of (p − y)² over all rows, where y = 1 for fraud; lower is better"],
    ["SHAP (SHapley Additive exPlanations)", "splits one prediction into pushes per feature that add up exactly to the model's output"],
    ["PSI · KS (Population Stability Index · Kolmogorov–Smirnov)", "drift checks: PSI compares binned shares old vs new; KS = biggest gap between two cumulative curves"],
    ["Optuna · TPE (Tree-structured Parzen Estimator)", "a library for smart hyper-parameter search; TPE tries new settings where good past trials were"],
    ["FastAPI · Docker", "Python framework for web APIs (application programming interfaces) · a container that packs code, libraries and model so they run the same anywhere"],
], [0.33, 0.67], PURPLE, bold_first=False))
story.append(PageBreak())

# ------------------------------------------------------------------ 2. Q&A
story.append(band("Bullet 1 · three boosters, 590K transactions, class imbalance", PURPLE))
story.append(Spacer(1, 3))
b1 = [
    ("Walk me through the data.", "do you know your data and its traps?",
     f"IEEE-CIS: {amber('590,540')} card payments over {amber('182 days')}. A transaction table is left-joined to an identity table "
     f"on TransactionID; only {amber('24.4%')} of rows have identity data. {amber('431')} features, {amber('214')} columns more than half "
     f"missing, {amber('3.50%')} fraud. So \"always legit\" already gets {amber('96.5%')} accuracy, which is why I never report accuracy."),
    ("Why split by time and not randomly?", "do you understand leakage?",
     "A live model always scores the future. A random split puts later payments of the same cards into training, so the model "
     f"\"remembers\" them. I sorted by TransactionDT and split 70/15/15. My leakage demo: random-split AUC {amber('0.9525')} vs time-split "
     f"{amber('0.9204')}, so the random split overstates performance by about 0.03."),
    ("Why boosted trees and not a neural network or logistic regression?", "can you pick a model for tabular data?",
     "The data is a table of mixed numbers and text codes, full of missing values and interactions (card × amount × device). "
     "Boosted trees handle NaN (Not a Number, i.e. missing) values themselves, need no scaling and usually beat neural networks on "
     "tables. Logistic regression would need a lot of manual feature work to capture the interactions."),
    ("Why three libraries, and which won?", "was the comparison fair, and do you know how they differ?",
     f"Same split, same early stopping, natural class ratio. {green('LightGBM')} (leaf-wise growth, histogram bins) won: valid PR-AUC "
     f"{amber('0.656')} in {amber('350 s')}. XGBoost (level-wise growth) {amber('0.599')} in {amber('954 s')}; CatBoost (symmetric trees, "
     f"ordered boosting) {amber('0.595')} in {amber('2,346 s')}. Honest caveat: FAST_MODE (my quick-run switch) capped trees at 1,000; LightGBM used 965 and "
     "CatBoost 986, so both were still improving."),
    ("How did you handle the imbalance? Why not SMOTE?", "do you know the options and their side effects?",
     f"About {amber('1 fraud per 27')} legit payments. I kept the natural ratio and compared models by PR-AUC. SMOTE (Synthetic Minority "
     "Over-sampling Technique) invents fake frauds between real neighbours, which is shaky with 431 half-missing, mixed columns. "
     f"{red('Both SMOTE and class weights shift the predicted probabilities')}, and my cost rule needs honest ones. Costs come in at "
     "decision time instead."),
    ("How does Optuna's TPE work, and how much did it help?", "real understanding, and honest numbers.",
     "After 10 random start-up trials, TPE splits past trials into \"good\" (top ~10%) and \"bad\", fits a density to each, l(x) and "
     "g(x), and tries settings where l(x)/g(x) is high. Objective = valid PR-AUC with early stopping. "
     f"{amber('20')} trials moved LightGBM from {amber('0.656 to 0.660')}: small, because the defaults were already strong."),
    ("Early stopping vs Optuna pruning: what's the difference?", "two ideas people often mix up.",
     "Early stopping ends ONE training run when the valid score stops improving for N rounds, which picks the number of trees. "
     "Pruning kills a whole bad Optuna trial before it finishes. Both look only at the validation set; the test set stays locked "
     "until the final numbers."),
]
for q in b1:
    story.append(qa(*q))
story.append(callout("Say it in interview:", "On a time split of 590K payments, LightGBM beat XGBoost and CatBoost on PR-AUC "
                     "(0.656 vs about 0.60) and trained 3–7× faster. Optuna added a little; the big wins came after the model.", PURPLE, PURPLE_L))
story.append(Spacer(1, 8))

story.append(band("Bullet 2 · calibration, PR-AUC + Brier, thresholds by money", GREEN))
story.append(Spacer(1, 3))
b2 = [
    ("Why PR-AUC and not ROC-AUC or accuracy?", "can you choose a metric under imbalance?",
     f"ROC uses the false-positive rate, which stays tiny because there are 85K legit rows, so ROC-AUC {amber('0.928')} looks great. "
     f"PR-AUC uses precision, which drops fast when false alarms pile up. Random PR-AUC = fraud rate {amber('0.034')}; mine "
     f"{amber('0.656')}, about {amber('19×')} better."),
    ("Why calibrate a boosted model at all?", "do you know a score is not automatically a probability?",
     "The cost rule multiplies p by the amount, so p must mean what it says. My raw model under-predicted on later months: in the "
     f"reliability diagram a bin it called about {amber('12%')} was really about {amber('24%')} fraud, and the default LightGBM's mean "
     f"prediction was {amber('1.5%')} against a true {amber('3.4%')}. Calibration fixes the scale without retraining."),
    ("Isotonic or Platt? Why isotonic?", "do you know the trade-off?",
     "Platt scaling fits one S-shaped (sigmoid) curve: 2 numbers, smooth, needs little data. Isotonic fits any non-decreasing step "
     f"function: flexible, but needs lots of data. I had {amber('44,290')} held-out rows, enough. Test Brier: raw {amber('0.0236')}, "
     f"Platt {amber('0.0236')} (no help), isotonic {green('0.0215')}."),
    ("What is the Brier score, and how do you read 0.0215?", "can you work with the numbers?",
     f"Brier = mean of (p − y)². Always saying the base rate scores {amber('0.0336')}. Brier skill = 1 − 0.0215 / 0.0336 = "
     f"{amber('0.36')}, i.e. 36% better than only knowing the fraud rate (raw model: 0.30)."),
    ("Why did PR-AUC drop after isotonic (0.562 → 0.542)?", "do you separate ranking from calibration?",
     "Isotonic is a step function, so many different raw scores land on the same calibrated value (ties), and ranking loses a "
     "little detail. Platt is strictly increasing, so its PR-AUC is identical to raw. I accept the small loss because the "
     "decision depends on honest p."),
    ("Where did you fit the calibrator, and why not on training data?", "leakage awareness.",
     f"On the earlier half of the validation set ({amber('44,290')} rows), checked on the later half ({amber('44,291')}). On training rows "
     f"the model has seen the answers, {red('so its scores there are too confident')} and the calibrator would learn the wrong mapping. "
     "The test set was never touched."),
    ("How did you choose the threshold? Derive it.", "expected value, step by step.",
     "Flag when the expected loss of letting it through beats the expected cost of a review: p × amount > (1 − p) × $10, so "
     f"p > 10 / (10 + amount). A $500 payment → cut-off 10 / 510 = {amber('1.96%')}; the average fraud amount $173.53 → "
     f"{amber('0.0545')}, and my brute-force scan agreed ({amber('0.055')}). The $10 review cost is an assumption; with $25 the "
     "cut-off becomes 25 / (25 + amount)."),
    ("What did it save?", "business impact, in real numbers.",
     f"On 88,581 test payments: cost rule {green('$161,369')} vs threshold 0.5 {amber('$332,344')} (−51%), max-F1 {amber('$283,650')} "
     f"(−43%; F1 = harmonic mean of precision and recall), flag nothing {amber('$469,608')} (−66%). The same rule with uncalibrated p costs {amber('$309,568')}, so calibration "
     f"alone roughly halved the cost. It caught {amber('2,011')} of about 3,080 frauds (65% by count, about 76% of fraud dollars)."),
]
for q in b2:
    story.append(qa(*q))
story.append(callout("Say it in interview:", "Isotonic calibration made the probabilities honest, and the per-payment rule "
                     "p × amount > (1 − p) × $10 cut test cost from $332K at the 0.5 threshold to $161K. With raw scores the same rule cost "
                     "$310K, so calibration was half of the win.", GREEN, GREEN_L))
story.append(Spacer(1, 8))

story.append(band("Bullet 3 · drift, SHAP, FastAPI, Docker", AMBER))
story.append(Spacer(1, 3))
b3 = [
    ("What is SHAP and why TreeSHAP?", "explanation theory.",
     "SHAP splits one prediction fairly among the features, using Shapley values from game theory. The pushes add up exactly: "
     "base value + all pushes = the model's log-odds. TreeSHAP computes this exactly and fast for tree models. My additivity check: "
     f"largest error {amber('0.0003')}."),
    ("SHAP vs LightGBM's built-in feature importance?", "global vs local, and the bias of split counts.",
     "Split importance counts how often a feature is used: no direction, no per-payment view, and biased toward features with many "
     "values. SHAP gives size and direction for each payment, and the mean |SHAP| gives a global ranking. My top features: "
     f"{amber('C13, TransactionAmt, C1, card1, card2, addr1, D1')}."),
    ("Is SHAP causal? Can you tell a customer \"blocked because of X\"?", "do you know the limits?",
     f"{red('No.')} SHAP explains the model, not the world, and correlated features share credit. It is great for reason codes and "
     "debugging, but \"C13 caused the fraud\" is not a valid claim."),
    ("What are PSI and KS, and what do your numbers say?", "drift numbers.",
     "PSI = Σ (new% − old%) × ln(new% / old%) over bins. Rule of thumb: < 0.10 stable, 0.10–0.25 watch, > 0.25 big shift. KS = "
     f"biggest gap between two cumulative curves. Valid → test: every PSI < {amber('0.03')} (largest C13 {amber('0.025')}, D1 "
     f"{amber('0.023')}), model-score PSI {amber('0.011')}, so everything is stable."),
    ("KS p-values are about 0, yet you say \"stable\". Contradiction?", "statistics with a huge n.",
     f"With 88K rows even a tiny shift is \"significant\". The KS statistic itself is small (D1 {amber('0.086')}). I judge drift by "
     "the size of the effect (PSI, KS value), not by the p-value alone."),
    ("Walk me through the API.", "can you design a serving layer?",
     "FastAPI loads the model, calibrator, feature list and drift bins once at startup. Pydantic checks the input: amount ≤ 0 → 422 "
     "error. POST /score returns calibrated p, FLAG/PASS, this amount's cut-off and the top-3 SHAP reasons. POST /drift takes ≥ 50 "
     "recent rows and returns PSI per feature; GET /health is for monitoring. In my test run a prediction took about 25 ms and "
     f"SHAP about 300 ms, {red('so SHAP dominates latency')}."),
    ("Why Docker, and how is it reproducible?", "deployment basics.",
     "Docker packs Python, libraries and model so it runs the same everywhere. The image uses python:3.13-slim (the Python the "
     "Kaggle run trained with), exact versions pinned in requirements-serve.txt (lightgbm 4.6.0, scikit-learn 1.6.1 …), a "
     "non-root user, and copies requirements before code so the pip layer is cached. A container shares the host's kernel, so it "
     "starts in seconds, unlike a virtual machine."),
    ("Next month the score PSI jumps to 0.3. What do you do?", "what-if: monitoring in production.",
     "First check the data pipeline for bugs, then per-feature PSI to see what moved. Fraud labels arrive late, so watch "
     "labelled PR-AUC and cost once they come in. Cheap fix: re-fit the calibrator on recent data; bigger fix: retrain on recent "
     "months, keeping the old model as a fallback."),
]
for q in b3:
    story.append(qa(*q))
story.append(callout("Say it in interview:", "Every decision comes with its top-3 SHAP reasons. PSI and KS on the top-10 features "
                     "and on the score showed everything stable (PSI < 0.03). It runs as a FastAPI service in a Docker image with pinned versions.",
                     AMBER, AMBER_L))
story.append(Spacer(1, 9))
story.append(KeepTogether([
    Paragraph(f'<font color="{AMBER}"><b>Numbers to memorise before any interview</b></font>', body),
    Spacer(1, 3),
    table([
        ["number", "what it is"],
        ["590,540 · 431 · 3.5%", "payments · features · fraud rate (1 fraud per 27 legit)"],
        ["0.9525 vs 0.9204", "AUC with a random split vs a time split (leakage demo)"],
        ["0.656 / 0.928", "LightGBM valid PR-AUC / ROC-AUC (XGBoost 0.599, CatBoost 0.595 PR-AUC)"],
        ["0.656 → 0.660", "Optuna gain from 20 trials"],
        ["0.0236 → 0.0215", "test Brier score, raw → isotonic (always-base-rate 0.0336)"],
        ["10 / (10 + amount)", "per-payment cut-off; 0.0545 at the average fraud amount $173.53"],
        ["$161K vs $332K", "test cost: cost rule vs threshold 0.5 (−51%); same rule on raw p $310K"],
        ["2,011 of ~3,080", "frauds caught on test (65% by count, ~76% by dollars)"],
        ["< 0.03 · 0.011", "PSI of every monitored feature · PSI of the model score (stable)"],
        ["~25 ms + ~300 ms", "prediction + SHAP per API call (measured in a test run)"],
    ], [0.26, 0.74], AMBER, bold_first=True)]))
story.append(PageBreak())

# ------------------------------------------------------------------ 3. pipeline
story.append(band("How it works · the whole pipeline", BLUE))
story.append(Spacer(1, 6))
story.append(image("/tmp/sg/pipeline.png", CONTENT_W))
story.append(Spacer(1, 6))
story.append(Paragraph("No LLM (large language model) calls in this project: every piece is our own Python code or a library.", small))
story.append(Spacer(1, 4))
story.append(table([
    ["piece", "what it is", "takes in", "gives out"],
    ["load + merge", "our code: pandas read_csv + merge(how=\"left\")", "2 CSV (comma-separated values) files", "one table, 590,540 × 434"],
    ["time split", "our code: sort by TransactionDT, slice 70/15/15", "the table", "train 413,378 · valid 88,581 · test 88,581"],
    ["3 boosters", "libraries: LightGBM, XGBoost, CatBoost (.fit with early stopping)", "train + valid", "3 models + valid PR-AUC"],
    ["tuning", "library: Optuna TPESampler, 20 trials", "objective function (valid PR-AUC)", "best LightGBM settings"],
    ["calibration", "library: scikit-learn IsotonicRegression(out_of_bounds=\"clip\")", "raw scores + labels (early valid half)", "step function raw → honest p"],
    ["cost rule", "our function (FraudScorer.score)", "p, amount, $10 review cost", "FLAG / PASS + cut-off"],
    ["SHAP reasons", "library: shap.TreeExplainer", "model + one feature row", "431 pushes → top 3 reasons"],
    ["drift", "our psi functions + scipy ks_2samp", "saved training bins + new rows", "PSI / KS per feature + verdict"],
    ["API", "FastAPI + Pydantic + uvicorn (api/main.py)", "JSON (JavaScript Object Notation) payment", "JSON score, decision, reasons"],
    ["container", "Docker (python:3.13-slim, pinned libraries)", "code + 4 model files", "an image that runs anywhere"],
], [0.14, 0.38, 0.24, 0.24], BLUE, bold_first=True))
story.append(PageBreak())

# ------------------------------------------------------------------ 4. example
story.append(band("One real payment through the pipeline", GRAY))
story.append(Spacer(1, 6))
story.append(image("/tmp/sg/example.png", CONTENT_W))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Values come from your real Kaggle-trained model, run on a real test-month payment from data/sample (the Kaggle output). "
    "How to read box C: SHAP works in log-odds, where 0 means 50% and every −2.3 divides the odds by about 10. "
    "The base value −13.93 is the average log-odds over training rows; the 428 smaller pushes together add +4.65.", small))
story.append(Spacer(1, 6))
story.append(table([
    ["step", "the maths, written out"],
    ["raw p from log-odds", "p = 1 / (1 + e^5.27) = 1 / (1 + 194.4) = 0.0051 = 0.51%"],
    ["cut-off for this amount", "p* = 10 / (10 + 500) = 0.0196 = 1.96%; calibrated 22.6% > 1.96% → FLAG"],
    ["expected money, calibrated", "PASS: 0.2258 × $500 = $112.90 expected loss · FLAG: (1 − 0.2258) × $10 = $7.74 → flag is cheaper"],
    ["expected money, raw", "PASS: 0.0051 × $500 = $2.56 · FLAG: 0.9949 × $10 = $9.95 → would PASS a real fraud"],
], [0.26, 0.74], GRAY, bold_first=True))
story.append(Spacer(1, 7))
story.append(callout("Say it in interview:", "Take a real $500 payment from the test months. The raw model said 0.5%, so both the "
                     "raw-score rule and the 0.5 threshold would let it through. Calibrated, it is 22.6%, the expected loss is $113 against a "
                     "$7.74 review, so we flag it, and it really was fraud.", GREEN, GREEN_L))
story.append(PageBreak())

# ------------------------------------------------------------------ 5. results
cal = {r["version"]: r for r in M["step06_calibration"]["table"]}
story.append(band("Results · only your real numbers (reports/metrics.json)", GREEN))
story.append(Spacer(1, 6))
story.append(image("/tmp/sg/results.png", CONTENT_W))
story.append(Spacer(1, 6))
s2 = M["step02_split"]; s4 = M["step04_metrics"]["at_threshold_0_5"]
story.append(table([
    ["metric", "your value", "compare with", "set"],
    ["PR-AUC, LightGBM (default)", "0.656", "random 0.034 · XGBoost 0.599 · CatBoost 0.595", "valid"],
    ["ROC-AUC, LightGBM (default)", "0.928", "random 0.5 · XGBoost 0.915 · CatBoost 0.909", "valid"],
    ["recall at 50% precision", "0.675", "XGBoost 0.602 · CatBoost 0.595", "valid"],
    ["at threshold 0.5", f"precision {s4['precision']:.2f} · recall {s4['recall']:.2f}", f"TP {s4['tp']:,} · FP {s4['fp']:,} · FN {s4['fn']:,}", "valid"],
    ["leakage demo AUC", f"time split {s2['leakage_demo_time_split_auc']}", f"random split {s2['leakage_demo_random_split_auc']}", "valid"],
    ["Optuna (20 trials)", "0.660", "untuned 0.656", "valid"],
    ["Brier score", f"isotonic {cal['isotonic']['test_brier']:.4f}", f"raw {cal['raw']['test_brier']:.4f} · Platt {cal['platt']['test_brier']:.4f} · base rate {cal['always say base rate']['test_brier']:.4f}", "test"],
    ["PR-AUC after calibration", f"isotonic {cal['isotonic']['test_pr_auc']:.3f}", f"raw {cal['raw']['test_pr_auc']:.3f}", "test"],
    ["total cost, cost rule", "$161,369", "0.5: $332,344 · max-F1: $283,650 · raw p: $309,568 · none: $469,608", "test"],
    ["drift (PSI)", "all < 0.03", "score PSI 0.011 · largest feature C13 0.025", "valid → test"],
], [0.27, 0.2, 0.43, 0.1], GREEN, bold_first=True))
story.append(Spacer(1, 7))
story.append(KeepTogether([table([
    ["metric", "what it means", "good / bad (rule of thumb)"],
    ["PR-AUC", "ranking quality on the rare class", "random = fraud rate; 0.5+ is strong for raw-feature fraud models; compare models on the same split"],
    ["ROC-AUC", "P(random fraud scores above random legit)", "0.5 = coin flip; 0.9+ looks great but flatters under imbalance"],
    ["precision / recall", "of flagged, share real fraud / of frauds, share caught", "trade off by moving the threshold; never judge one alone"],
    ["Brier score", "mean (p − y)², honesty + sharpness", "lower is better; beat the base rate (0.0336 here); skill = 1 − Brier / base"],
    ["PSI", "how much a distribution moved", "< 0.10 stable · 0.10–0.25 watch · > 0.25 act"],
    ["total cost ($)", "money lost to missed fraud + reviews", "the business metric; lower is better; compare rules on the same test set"],
], [0.17, 0.35, 0.48], GREEN, bold_first=True)]))
story.append(Spacer(1, 6))
rel_img = image("/tmp/kres/out/reports/figures/06_reliability_diagram.png", 0.27 * CONTENT_W)
rel_text = Paragraph(
    f'<font color="{GREEN}"><b>Your real reliability diagram</b></font> (reports/figures/06_reliability_diagram.png), drawn on the '
    "check half of the validation set (44,291 rows). Each dot is a bin of payments: x = average predicted fraud chance, "
    "y = real fraud rate in that bin. The diagonal is perfect honesty.<br/><br/>"
    f"{red('Raw (blue) dots sit ABOVE the diagonal')}: a bin predicted at about 12% was really about 24% fraud, so the raw model "
    f"under-predicts. {green('Isotonic (orange) dots sit on the diagonal')}: after calibration, 25% means about 25%. "
    "That is why the cost rule only works on calibrated p.", small)
rel = Table([[rel_img, rel_text]], colWidths=[0.29 * CONTENT_W, 0.71 * CONTENT_W])
rel.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                         ("BACKGROUND", (1, 0), (1, 0), colors.HexColor(GREEN_L)), ("LEFTPADDING", (1, 0), (1, 0), 9),
                         ("RIGHTPADDING", (1, 0), (1, 0), 9), ("TOPPADDING", (1, 0), (1, 0), 7), ("BOTTOMPADDING", (1, 0), (1, 0), 7)]))
story.append(KeepTogether([rel]))
story.append(PageBreak())

# ------------------------------------------------------------------ 6. why
story.append(band("Why it worked, where it's weak, what I'd try next", RED))
story.append(Spacer(1, 6))
story.append(table([
    ["fix", "why it worked", "evidence"],
    ["time split, not random", "the model can't peek at later payments of the same cards", "random AUC 0.9525 vs time 0.9204: the random split overstates by 0.03"],
    ["PR-AUC as the main metric", "ROC hides false alarms when legit rows are 27× more common", "ROC-AUC 0.928 while 0.5 catches only 39% of fraud"],
    ["LightGBM over XGBoost / CatBoost", "leaf-wise trees + histograms: better splits, faster", "0.656 vs 0.599 / 0.595; 350 s vs 954 / 2,346 s"],
    ["isotonic on held-out data", "raw scores under-predicted later months", "bin ~12% was ~24% real; test Brier 0.0236 → 0.0215; Platt no help"],
    ["calibrate BEFORE the cost rule", "the rule multiplies p by the amount", "same rule: raw p $309,568 vs isotonic p $161,369"],
    ["per-payment cut-off", "a $500 and a $5 payment deserve different thresholds", "$161K vs max-F1 $284K vs 0.5 $332K; formula 0.0545 = scan 0.055"],
], [0.24, 0.38, 0.38], RED, bold_first=True))
story.append(Spacer(1, 7))
story.append(table([
    ["weak spot", "evidence", "what I'd say"],
    ["valid → test drop", "PR-AUC 0.66 (valid) → 0.574 (late valid half) → 0.562 (test)", "valid was reused for early stopping + tuning, and later months bring more unseen cards; quote the test number"],
    ["under-trained (FAST_MODE)", "LightGBM 965 and CatBoost 986 of 1,000 trees", "more trees at a lower learning rate would likely help"],
    ["small Optuna gain", "+0.004 PR-AUC from 20 trials", "defaults were strong; the money came from calibration + cost rule"],
    ["isotonic ties", "test PR-AUC 0.562 → 0.542", "accepted: decisions need honest p more than fine ranking"],
    ["no feature engineering", "raw IEEE-CIS columns only", "top Kaggle teams built user-ID aggregates"],
    ["PSI sees inputs only", "all PSI stable, yet test < valid", "concept drift needs labelled monitoring (labels arrive late)"],
    ["not yet built end-to-end", "Docker image and Hugging Face Space not run yet", "build + run the image once before interviews"],
], [0.22, 0.36, 0.42], RED, bold_first=True))
story.append(Spacer(1, 7))
story.append(Paragraph(f'<font color="{RED}"><b>Next steps I would try</b></font>', body))
nexts = [
    "FAST_MODE off (learning rate 0.03, up to 5,000 trees) and 60+ Optuna trials; also tune XGBoost and CatBoost.",
    "User-ID features: combine card1 + addr1 + a first-seen date from D1, then group statistics (mean amount, count per user).",
    "Several time folds (forward-chaining validation) for a less optimistic score than one valid block.",
    "Compute SHAP only for flagged payments, or asynchronously, to cut the ~300 ms latency.",
    "Monitor labelled cost each month, re-fit the calibrator monthly, alert when score PSI > 0.10.",
    "Build and run the Docker image, deploy the Hugging Face Space, add a small load test.",
]
for i, n in enumerate(nexts, 1):
    story.append(Paragraph(f"{i}. {n}", ParagraphStyle("nx", parent=body, leftIndent=10, spaceAfter=1.5)))
story.append(Spacer(1, 6))
story.append(callout("Say it in interview:", "My biggest lesson: the model was the easy part. A time split kept the numbers honest, and "
                     "calibration plus a money-based threshold halved the cost. Next I'd add user-level features and forward-chaining validation.",
                     GREEN, GREEN_L))
story.append(PageBreak())

# ------------------------------------------------------------------ 7. cheat sheet
YT = "https://www.youtube.com/watch?v="
story.append(band("Cheat sheet · concepts, links, files, Revisit list", BLUE))
story.append(Spacer(1, 6))
rows = [["concept", "one line", "learn more"]]
rows += [
    ["decision tree", "splits that make groups purer (Gini or entropy)", link("StatQuest", YT + "_L39rN6gz7Y")],
    ["random forest · bagging", "many trees on bootstrap samples, averaged", link("StatQuest forest", YT + "J4Wdy0Wc_xQ") + " · " + link("bootstrap", YT + "Xz0x-8-cgaQ")],
    ["bias vs variance", "too simple vs too wiggly; boosting cuts bias, bagging cuts variance", link("StatQuest", YT + "EuBBz3bI-aA")],
    ["AdaBoost → gradient boosting", "each new tree fixes the previous errors (residuals / gradients)", link("AdaBoost", YT + "LsK-xG1cLYA") + " · " + link("gradient boost", YT + "3CC4N4z3GJc")],
    ["XGBoost", "regularised boosting; split gain uses G² / (H + λ)", link("StatQuest 1", YT + "OtD8wVaFm6E") + " · " + link("2", YT + "8b1JEDvenQU") + " · " + link("paper", "https://arxiv.org/abs/1603.02754")],
    ["LightGBM", "leaf-wise growth; GOSS (Gradient-based One-Side Sampling) keeps big-gradient rows, EFB (Exclusive Feature Bundling) merges sparse columns", link("video", YT + "K_nI-oGAQiE") + " · " + link("LightGBM paper", "https://proceedings.neurips.cc/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf")],
    ["CatBoost", "symmetric trees, ordered boosting for categories", link("StatQuest", YT + "KXOTSkPL2X4") + " · " + link("paper", "https://arxiv.org/abs/1706.09516")],
    ["imbalance · SMOTE", "rare class; resample, re-weight or move the threshold", link("CampusX", YT + "yh2AKoJCV3k") + " · " + link("SMOTE video", YT + "qgnrtl1TzMA")],
    ["confusion matrix · ROC/AUC", "TP/FP/FN/TN (true/false positives/negatives) and the ROC curve", link("matrix", YT + "Kdsp6soqA7o") + " · " + link("ROC", YT + "4jRBRDbJemM")],
    ["data leakage", "training sees information it won't have live", link("Kaggle Learn", "https://www.kaggle.com/dansbecker/data-leakage")],
    ["Optuna · TPE", "smart search; samples where l(x)/g(x) is high", link("docs", "https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html") + " · " + link("paper", "https://arxiv.org/abs/1907.10902") + " · " + link("video", YT + "bcy6A57jAwI")],
    ["calibration", "make p match reality; Platt vs isotonic", link("scikit-learn guide", "https://scikit-learn.org/stable/modules/calibration.html") + " · " + link("Niculescu-Mizil &amp; Caruana 2005", "https://mlanthology.org/icml/2005/niculescumizil2005icml-predicting")],
    ["cost-sensitive threshold", "flag if p × amount > (1 − p) × review cost", link("scikit-learn example", "https://scikit-learn.org/stable/auto_examples/model_selection/plot_cost_sensitive_learning.html")],
    ["Shapley · SHAP", "fair split of one prediction among features", link("paper", "https://arxiv.org/abs/1705.07874") + " · " + link("article", "https://www.aidancooper.co.uk/how-shapley-values-work/") + " · " + link("video", YT + "UJeu29wq7d0")],
    ["PSI · KS · p-value", "drift size · max gap of cumulative curves · chance of a gap this big by luck", link("PSI", "https://arize.com/glossary/population-stability-index-psi/") + " · " + link("KS", YT + "VpQ6MLoRSfY") + " · " + link("p-values", YT + "vemZtEM63GY")],
    ["FastAPI · Docker", "Python web API · container image", link("FastAPI video", YT + "BPRKBQwEHe0") + " · " + link("Docker in 100 s", YT + "Gjnup-PuquQ")],
    ["dataset", "IEEE-CIS Fraud Detection competition", link("Kaggle page", "https://www.kaggle.com/competitions/ieee-fraud-detection")],
]
story.append(table(rows, [0.22, 0.44, 0.34], BLUE, bold_first=True))
story.append(Spacer(1, 7))
story.append(KeepTogether([table([
    ["file (in 02-fraud-risk-model)", "what's inside"],
    ["notebooks/fraud_pipeline.ipynb", "§0 setup → §10 export, one growing notebook (run on Kaggle for real numbers)"],
    ["notebooks/concepts_playground.ipynb", "by-hand demos: Gini, bootstrap, AdaBoost, TPE, Brier, PAVA (pool-adjacent-violators, the isotonic fit), reliability diagram"],
    ["src/fraud_service.py", "FraudScorer: load the 4 files once, score(), drift()"],
    ["api/main.py · api/demo.html", "FastAPI app (/score, /drift, /health) + phone-friendly page"],
    ["tests/test_api.py", "4 pytest checks (health, score, 422 on bad amount, drift needs ≥ 50 rows)"],
    ["Dockerfile · requirements-serve.txt", "container recipe + exact library versions"],
    ["reports/metrics.json · reports/figures/", "REAL Kaggle results; never quote metrics_DEMO.json"],
    ["notes/handoff-fraud.md", "handoff card for future chats"],
], [0.38, 0.62], GRAY, bold_first=True)]))
story.append(Spacer(1, 7))
story.append(callout("Revisit list:", "telling a function from a variable from a library when reading code · PSI arithmetic · axis=0 vs "
                     "axis=1 · Brier is a mean, not a sum · ^ is XOR (exclusive or) in Python, ** is power · duplicate function names overwrite each other · "
                     "the 3 parts of an Optuna objective (suggest → train → return the score) · TPE models densities, not the score curve. "
                     f'Still pending: the 10-question mock OA (online assessment) and 5 mock-interview questions. Code: {link("GitHub repo", "https://github.com/dpathriya8-maker/cost-sensitive-fraud-risk-model")}.',
                     RED, RED_L))

doc = SimpleDocTemplate("/tmp/sg/fraud-risk-model-study-guide.pdf", pagesize=A4, leftMargin=LM, rightMargin=RM,
                        topMargin=14 * mm, bottomMargin=16 * mm, title="Cost-Sensitive Fraud Risk Model · study guide",
                        author="Deepanshu (DP)")
doc.build(story, onFirstPage=on_first, onLaterPages=on_later)
print("built")
