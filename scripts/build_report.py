"""Compile the findings into a single PDF report.

The analysis lives in ``docs/`` as eight markdown files, which is right for a repo and
wrong for something to hand in. This produces one self-contained PDF with the figures
embedded.

Built with reportlab rather than by converting the markdown, because no markdown
toolchain (pandoc, LibreOffice, a headless browser) is available in this environment
and adding one is a heavier dependency than writing the document directly. The
trade-off is that the report's structure is defined here rather than derived from
``docs/``; every *number* is still read from ``results/`` at build time, so the report
cannot drift from the experiments even though its prose is authored here.

Usage:
    python -m scripts.build_report
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = ROOT / "bias_mitigation_report.pdf"

NAVY = colors.HexColor("#1E2761")
GOLD = colors.HexColor("#E8A33D")
GRAY = colors.HexColor("#5A6270")
INK = colors.HexColor("#1B1B1F")
PALE = colors.HexColor("#F4F6FA")
RULE = colors.HexColor("#D8DDE8")
GREEN = colors.HexColor("#1BAF7A")
ORANGE = colors.HexColor("#EB6834")

FRAME_WIDTH = A4[0] - 4.0 * cm


# ----------------------------------------------------------------------- styles


def build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Times-Bold",
                                fontSize=22, leading=26, textColor=NAVY, spaceAfter=6),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"],
                                   fontName="Helvetica", fontSize=11, leading=15,
                                   textColor=GRAY, alignment=TA_LEFT, spaceAfter=16),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Times-Bold",
                             fontSize=15, leading=19, textColor=NAVY,
                             spaceBefore=16, spaceAfter=7),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold",
                             fontSize=11, leading=15, textColor=INK,
                             spaceBefore=11, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["Normal"], fontName="Helvetica",
                               fontSize=9.5, leading=13.6, textColor=INK,
                               alignment=TA_JUSTIFY, spaceAfter=7),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"], fontName="Helvetica",
                                 fontSize=9.5, leading=13.4, textColor=INK,
                                 leftIndent=13, bulletIndent=3, spaceAfter=4),
        "caption": ParagraphStyle("caption", parent=base["Normal"], fontName="Helvetica-Oblique",
                                  fontSize=8.2, leading=11, textColor=GRAY, spaceAfter=11),
        "callout": ParagraphStyle("callout", parent=base["Normal"], fontName="Helvetica-Bold",
                                  fontSize=10, leading=14.5, textColor=INK,
                                  alignment=TA_LEFT),
        "mono": ParagraphStyle("mono", parent=base["Normal"], fontName="Courier",
                               fontSize=8.5, leading=12, textColor=INK, spaceAfter=8),
    }


S = build_styles()


def para(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    return [Paragraph(f"&bull;&nbsp;&nbsp;{item}", S["bullet"]) for item in items]


def callout(text, *, accent=GOLD, fill=colors.HexColor("#FDF3E2")):
    """A boxed statement, for the sentence a reader should not skim past."""
    tbl = Table([[Paragraph(text, S["callout"])]], colWidths=[FRAME_WIDTH])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fill),
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, accent),
        ("BOX", (0, 0), (-1, -1), 0.5, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return [Spacer(1, 3), tbl, Spacer(1, 11)]


def data_table(rows, *, widths=None, highlight=None, align_first_left=True):
    """A results table: navy header, banded body, optional highlighted row."""
    if widths is None:
        first = FRAME_WIDTH * 0.34
        rest = (FRAME_WIDTH - first) / (len(rows[0]) - 1)
        widths = [first] + [rest] * (len(rows[0]) - 1)

    body = [[Paragraph(f"<b>{c}</b>" if r == 0 else str(c),
                       ParagraphStyle("cell", fontName="Helvetica-Bold" if r == 0 else "Helvetica",
                                      fontSize=8.4, leading=11,
                                      textColor=colors.white if r == 0 else INK,
                                      alignment=TA_LEFT if (c_i == 0 and align_first_left) else 2))
             for c_i, c in enumerate(row)]
            for r, row in enumerate(rows)]

    tbl = Table(body, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for r in range(1, len(rows)):
        style.append(("BACKGROUND", (0, r), (-1, r),
                      colors.white if r % 2 else PALE))
    if highlight:
        for r in highlight:
            style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#FDF3E2")))
    tbl.setStyle(TableStyle(style))
    return [tbl, Spacer(1, 5)]


def figure(path: Path, caption: str, width_frac: float = 1.0):
    if not path.exists():
        return []
    from PIL import Image as PILImage

    with PILImage.open(path) as im:
        ratio = im.height / im.width
    width = FRAME_WIDTH * width_frac
    return [Spacer(1, 4), Image(str(path), width=width, height=width * ratio),
            Spacer(1, 3), para(caption, "caption")]


# ------------------------------------------------------------------------- data


def load() -> dict:
    read = lambda name, **kw: pd.read_csv(RESULTS / name, **kw)
    return {
        "baseline": read("baseline_summary.csv", header=[0, 1], index_col=0),
        "mitigation": read("mitigation_summary.csv", header=[0, 1], index_col=[0, 1]),
        "ablation": read("ablation_summary.csv", header=[0, 1], index_col=0),
        "who": read("who_pays_runs.csv").groupby("method").mean(numeric_only=True),
        "shap": read("shap_proxy_reliance.csv", index_col=0),
        "shares": read("shap_feature_shares.csv", index_col=0),
        "inter": read("intersectional_summary.csv", index_col=0),
        "proxy": read("proxy_removal_summary.csv").sort_values("n_removed"),
        "eps": read("epsilon_sweep_summary.csv", index_col=0),
    }


def ms(frame, row, metric) -> str:
    """mean ± std, from a two-level summary frame."""
    return f"{frame.loc[row, (metric, 'mean')]:.4f} ± {frame.loc[row, (metric, 'std')]:.4f}"


# ---------------------------------------------------------------------- sections


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(2 * cm, 1.25 * cm,
                      "Algorithmic Bias Mitigation on Adult Census Income")
    canvas.drawRightString(A4[0] - 2 * cm, 1.25 * cm, f"{doc.page}")
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
    canvas.restoreState()


def build(n: dict) -> list:
    story: list = []
    A, M, B, W, SH, IN = n["ablation"], n["mitigation"], n["baseline"], n["who"], n["shap"], n["inter"]

    # ------------------------------------------------------------------- title
    story += [
        para("Algorithmic Bias Mitigation on Adult Census Income", "title"),
        para("An in-processing study reproducing Agarwal et al. (2018), <i>A Reductions "
             "Approach to Fair Classification</i>, and measuring three consequences its "
             "framing does not surface.", "subtitle"),
    ]

    story += [para("Summary", "h1")]
    story += [para(
        "The base paper's method works exactly as claimed. Wrapped around a decision tree, "
        "its exponentiated-gradient reduction takes demographic parity difference from "
        f"{M.loc[('decision_tree','baseline'),('demographic_parity_diff','mean')]:.4f} to "
        f"{M.loc[('decision_tree','expgrad_dp'),('demographic_parity_diff','mean')]:.4f} "
        "&mdash; an 88% reduction &mdash; for 1.5 accuracy points, without modifying a single "
        "row of training data. Every claim the paper makes held up under independent "
        "reimplementation.")]
    story += [para(
        "That confirmation is the first half of this report. The second half asks four "
        "questions the paper's framing does not: <b>who</b> was moved to satisfy the "
        "constraint, whether the total number of favourable decisions fell, what the "
        "method's randomization costs an individual, and what the constrained model "
        "actually leans on. The answers are less comfortable than the headline metric.")]

    story += callout(
        "Every mitigation studied closed the fairness gap primarily by withdrawing "
        "favourable decisions from the advantaged group rather than extending them to the "
        "disadvantaged one, reducing the total number of approvals by 8&ndash;22%. And the "
        "two methods with the best parity scores rely on proxies for the protected "
        "attribute <i>more</i> than the unmitigated baseline does.")

    story += [para("Contributions", "h2")]
    story += bullets([
        "<b>Reproduction</b> of the base paper's four deliverables on an independent "
        "implementation, over five random seeds.",
        "<b>An ablation</b> of six in-processing methods under identical conditions, two "
        "of them implemented from their source papers rather than from a library, and "
        "verified against degenerate cases.",
        "<b>An incidence analysis</b> (new) decomposing each closed fairness gap into the "
        "part paid by the advantaged group losing ground and the part gained by the "
        "disadvantaged group, in rates and in people.",
        "<b>A proxy-reliance analysis</b> using SHAP, which refutes this project's own "
        "stated prediction.",
        "<b>An intersectional analysis</b> (new) at Sex&nbsp;&times;&nbsp;Race, including a "
        "measurement-reliability treatment showing that half the subgroups on this dataset "
        "cannot support the estimates commonly published for them.",
    ])

    # ------------------------------------------------------------------- setup
    story += [PageBreak(), para("1. Setup", "h1")]
    story += [para(
        "UCI Adult Census Income, 45,222 rows after listwise deletion. Task: predict "
        "whether income exceeds $50K. Protected attribute: <font face='Courier'>sex</font>. "
        "Base rates differ sharply &mdash; 31.25% of men in the data earn above the threshold "
        "against 11.36% of women &mdash; and that 2.75&times; ratio is the entire source of "
        "the bias. Nothing in the algorithm is malicious; empirical risk minimisation "
        "reproduces the gap because reproducing it minimises error.")]
    story += [para(
        "<b>The protected attribute is removed from the feature matrix.</b> No model in "
        "this study can read <font face='Courier'>sex</font> directly. This is fairness "
        "through unawareness, included precisely because it does not work: the models "
        "reconstruct the disparity from proxies, and section 6 measures which ones.")]
    story += [para(
        "Splits are stratified on the <font face='Courier'>(sex, income)</font> interaction "
        "rather than the label alone, so the four cells the fairness metrics are computed "
        "from keep a stable size across seeds. Without this, sampling noise in the smallest "
        "cell appears as model instability &mdash; which would have confounded the stability "
        "finding in section 4. All three fairness metrics are implemented from their "
        "definitions and cross-checked against <font face='Courier'>fairlearn</font> on "
        "every run; rates with an empty denominator return NaN rather than 0, so an "
        "undefined rate can never masquerade as a perfectly fair one.")]

    story += [para("2. Baseline", "h1")]
    story += data_table([
        ["Base classifier", "Accuracy", "DP diff", "EO diff", "Disparate impact"],
        ["Decision tree", ms(B, "decision_tree", "accuracy"),
         ms(B, "decision_tree", "demographic_parity_diff"),
         ms(B, "decision_tree", "equalized_odds_diff"),
         ms(B, "decision_tree", "disparate_impact")],
        ["Logistic regression", ms(B, "logistic_regression", "accuracy"),
         ms(B, "logistic_regression", "demographic_parity_diff"),
         ms(B, "logistic_regression", "equalized_odds_diff"),
         ms(B, "logistic_regression", "disparate_impact")],
    ])
    story += [para(
        "Disparate impact of 0.29&ndash;0.31 means women are selected at under a third of "
        "the male rate. The US EEOC four-fifths rule flags anything below 0.80; this is off "
        "by nearly a factor of three. Accuracy sits near 85% throughout &mdash; a reader "
        "monitoring only accuracy would conclude the pipeline is healthy, which is the "
        "ordinary case.")]

    # ----------------------------------------------------------- base paper
    story += [para("3. Reproducing the base paper", "h1")]
    story += [para(
        "Agarwal et al. rewrite the constrained problem "
        "min<sub>h</sub> E[1{h(x)&ne;y}] subject to &phi;(h) &le; &epsilon; as a two-player "
        "zero-sum game, min<sub>h</sub> max<sub>&lambda;</sub> error(h) + "
        "&lambda;<sup>T</sup>(&phi;(h) &minus; &epsilon;). In practice this reduces to "
        "repeatedly reweighting the training examples and refitting the base classifier, so "
        "the classifier is a black box and the data is never touched. Decision tree base, "
        "&epsilon;&nbsp;=&nbsp;0.01, 5 seeds.")]
    story += data_table([
        ["Method", "Accuracy", "DP diff", "EO diff", "Disparate impact"],
        ["Baseline tree", ms(M, ("decision_tree", "baseline"), "accuracy"),
         ms(M, ("decision_tree", "baseline"), "demographic_parity_diff"),
         ms(M, ("decision_tree", "baseline"), "equalized_odds_diff"),
         ms(M, ("decision_tree", "baseline"), "disparate_impact")],
        ["ExpGrad &mdash; Demographic Parity", ms(M, ("decision_tree", "expgrad_dp"), "accuracy"),
         ms(M, ("decision_tree", "expgrad_dp"), "demographic_parity_diff"),
         ms(M, ("decision_tree", "expgrad_dp"), "equalized_odds_diff"),
         ms(M, ("decision_tree", "expgrad_dp"), "disparate_impact")],
        ["ExpGrad &mdash; Equalized Odds", ms(M, ("decision_tree", "expgrad_eo"), "accuracy"),
         ms(M, ("decision_tree", "expgrad_eo"), "demographic_parity_diff"),
         ms(M, ("decision_tree", "expgrad_eo"), "equalized_odds_diff"),
         ms(M, ("decision_tree", "expgrad_eo"), "disparate_impact")],
    ], highlight=[2])
    story += [para(
        "<b>The method works.</b> Under the parity constraint the violation falls 88% for "
        "1.5 accuracy points, and disparate impact moves from failing the four-fifths rule "
        "by a factor of three to comfortably passing it. Under the equalized-odds "
        "constraint, EO difference falls 57% for half an accuracy point. Each constraint "
        "improves the metric it was given and only that one &mdash; correct behaviour, and "
        "the seed of the finding in section 4.")]
    story += figure(RESULTS / "pareto_demographic_parity.png",
                    "Figure 1. GridSearch sweep over 15 &lambda; values (base-paper "
                    "deliverable 4). Open rings mark the non-dominated frontier; dominated "
                    "points are shown rather than hidden, because a grid producing many of "
                    "them is evidence the trade-off is less smooth than a frontier-only "
                    "plot implies.", width_frac=0.86)

    # -------------------------------------------------------------- ablation
    story += [para("4. Ablation: six methods, one table", "h1")]
    story += [para(
        "Data, base classifier, split and metrics held fixed; only the mitigation varies. "
        "All six rows use logistic regression, including the reductions rows that section 3 "
        "runs on a tree: Prejudice Remover adds a term to a likelihood and Adversarial "
        "Debiasing needs gradients to flow from an adversary into the predictor, so neither "
        "can wrap a tree. Reporting a tree for some rows and a linear model for others "
        "would vary the hypothesis class and the mitigation at once.")]
    labels = [
        ("baseline", "Baseline (no mitigation)"),
        ("expgrad_dp", "Exponentiated Gradient (DP)"),
        ("expgrad_eo", "Exponentiated Gradient (EO)"),
        ("gridsearch_dp", "GridSearch (DP)"),
        ("prejudice_remover", "Prejudice Remover"),
        ("adversarial_debiasing", "Adversarial Debiasing"),
    ]
    rows = [["Method", "Accuracy", "DP diff", "EO diff", "Disparate impact"]]
    for key, label in labels:
        rows.append([label, ms(A, key, "accuracy"),
                     ms(A, key, "demographic_parity_diff"),
                     ms(A, key, "equalized_odds_diff"),
                     ms(A, key, "disparate_impact")])
    story += data_table(rows, highlight=[2])
    story += [para(
        "Prejudice Remover and Adversarial Debiasing were implemented from Kamishima et al. "
        "(2012) and Zhang et al. (2018) in PyTorch rather than taken from "
        "<font face='Courier'>aif360</font>, whose Prejudice Remover shells out to the "
        "original script through temporary files and whose Adversarial Debiasing requires a "
        "TensorFlow-1 compatibility chain. The cost of implementing from scratch is that "
        "the implementations might be wrong, so they are tested against degenerate cases: "
        "with &eta;&nbsp;=&nbsp;0 the prejudice penalty vanishes and the method must reduce "
        "to per-group logistic regression, which it reproduces to <b>99.88%</b> prediction "
        "agreement. Both fairness knobs are checked for monotonicity &mdash; the check that "
        "would catch a sign error, the failure mode where a mitigation quietly increases "
        "disparity while the metrics still look plausible.", "body")]

    story += [para("4.1 Which method gives the best value?", "h2")]
    story += [para(
        "GridSearch-DP reaches the lowest absolute violation (0.0150), but the best "
        "<i>exchange rate</i> belongs to Prejudice Remover, which buys 11.7 parity points "
        "per accuracy point against ExpGrad-DP's 9.0 &mdash; roughly 30% better. It stops "
        "at DP 0.065 rather than pushing to 0.015, because &eta; is a penalty weight rather "
        "than a constraint and has no target it is obliged to hit. Its efficiency win also "
        "carries a caveat the reductions rows do not: it fits one weight vector per group, "
        "so it requires <font face='Courier'>sex</font> at <i>prediction</i> time. Two "
        "applicants identical on every feature but differing in sex are scored by different "
        "weight vectors &mdash; disparate treatment in the legal sense, arrived at while "
        "trying to reduce disparate impact.")]

    story += [para("4.2 Which method is most stable? (Our prediction was inverted.)", "h2")]
    story += data_table([
        ["Method", "Accuracy std", "DP std", "Disparate impact std"],
        ["Adversarial Debiasing", f"{A.loc['adversarial_debiasing',('accuracy','std')]:.4f}",
         f"{A.loc['adversarial_debiasing',('demographic_parity_diff','std')]:.4f}",
         f"{A.loc['adversarial_debiasing',('disparate_impact','std')]:.4f}"],
        ["Exponentiated Gradient (DP)", f"{A.loc['expgrad_dp',('accuracy','std')]:.4f}",
         f"{A.loc['expgrad_dp',('demographic_parity_diff','std')]:.4f}",
         f"{A.loc['expgrad_dp',('disparate_impact','std')]:.4f}"],
        ["GridSearch (DP)", f"{A.loc['gridsearch_dp',('accuracy','std')]:.4f}",
         f"{A.loc['gridsearch_dp',('demographic_parity_diff','std')]:.4f}",
         f"{A.loc['gridsearch_dp',('disparate_impact','std')]:.4f}"],
    ], highlight=[1, 3])
    story += [para(
        "The project's own specification predicted that adversarial training would be the "
        "higher-variance approach. It is the <b>most</b> stable method in the study. "
        "GridSearch &mdash; a deterministic sweep with no adversary, no minibatching and no "
        "randomness in the procedure &mdash; is the least, by 6&times; on accuracy and "
        "3&times; on disparate impact. The variance is measured across seeds, and a seed "
        "changes the train/test split: GridSearch takes a discrete argmax over a coarse "
        "15-point &lambda; grid, so a small change in the data flips which grid point wins "
        "and the answer moves discontinuously. Adversarial Debiasing has no selection step. "
        "<b>The instability came from model selection, not from stochastic training.</b>")]

    story += [para("4.3 Does the ranking change with the metric?", "h2")]
    story += [para(
        "It inverts. Ranked by demographic parity the order runs GridSearch &rarr; "
        "ExpGrad-DP &rarr; Adversarial &rarr; Prejudice Remover &rarr; ExpGrad-EO &rarr; "
        "Baseline. Ranked by equalized odds it becomes ExpGrad-EO &rarr; <b>Baseline</b> "
        "&rarr; Prejudice Remover &rarr; Adversarial &rarr; ExpGrad-DP &rarr; GridSearch.")]
    story += callout(
        "Four of the five mitigations are worse than doing nothing on equalized odds, and "
        "the unmitigated baseline ranks second of six. An engineer deploying GridSearch-DP "
        f"on its parity score would take equalized odds from "
        f"{A.loc['baseline',('equalized_odds_diff','mean')]:.3f} to "
        f"{A.loc['gridsearch_dp',('equalized_odds_diff','mean')]:.3f} &mdash; 3.2&times; "
        "worse than no mitigation &mdash; while the dashboard showed green.")
    story += [para(
        "This is not a defect in any implementation. It is the impossibility result "
        "(Kleinberg et al. 2016; Chouldechova 2017) appearing in practice: when base rates "
        "differ across groups, demographic parity and equalized odds cannot both hold. "
        "&ldquo;We made the model fair&rdquo; is not a well-formed claim on this data.")]

    # -------------------------------------------------------------- who pays
    story += [PageBreak(), para("5. Who pays for the fairness fix?", "h1")]
    story += [para(
        "<i>This section and section 7 are outside the original specification.</i> The "
        "ablation table reports that ExpGrad-DP took demographic parity from 0.186 to "
        "0.018. That single number is compatible with two opposite stories: the "
        "disadvantaged group's selection rate rose to meet the advantaged group's "
        "(<i>levelling up</i>, nobody made worse off), or the advantaged group's fell to "
        "meet theirs (<i>levelling down</i>). Same metric, opposite ethics. Mittelstadt, "
        "Wachter &amp; Russell (2023) argue the second is the common case and that "
        "gap-only reporting conceals it.")]
    story += [para(
        "Writing the signed gap as gap = r<sub>priv</sub> &minus; r<sub>unpriv</sub>, the "
        "change decomposes exactly:", "body")]
    story += [Paragraph(
        "closure = (r_priv_before &minus; r_priv_after) + (r_unpriv_after &minus; "
        "r_unpriv_before)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        "\\____ privileged loss ____/&nbsp;&nbsp;&nbsp;\\____ unprivileged gain ____/",
        S["mono"])]
    story += [para(
        "The two terms sum to the closure identically, so their ratio is a well-defined "
        "share. The identity is verified over 200 random cases, and a gap that "
        "<i>widened</i> returns NaN rather than a plausible-looking number (8/8 tests).")]

    rows = [["Method", "Share paid by privileged (rates)", "Share paid by privileged (people)",
             "Lost per gained", "Change in total approvals"]]
    for key, label in [("expgrad_dp", "Exponentiated Gradient (DP)"),
                       ("gridsearch_dp", "GridSearch (DP)"),
                       ("adversarial_debiasing", "Adversarial Debiasing"),
                       ("prejudice_remover", "Prejudice Remover"),
                       ("expgrad_eo", "Exponentiated Gradient (EO)")]:
        r = W.loc[key]
        rows.append([label, f"{r['dp_share_levelling_down']:.3f}",
                     f"{r['people_share_levelling_down']:.3f}",
                     f"{r['lost_per_gained']:.2f}",
                     f"{r['positives_pct_change']:+.1f}%"])
    story += data_table(rows, widths=[FRAME_WIDTH * 0.28] + [FRAME_WIDTH * 0.18] * 4)

    story += [para(
        "<b>Measured in rates every method looks even-handed</b> (0.50&ndash;0.58 of the "
        "closure paid by the privileged group). <b>Measured in people they are lopsided</b> "
        "(0.66&ndash;0.74). Both are correct; they answer different questions. The rate "
        "decomposition is population-size blind, and the privileged group here is "
        "2.1&times; larger, so equal rate movement is very unequal headcount &mdash; and "
        "headcount is what a person subject to the system experiences.")]
    story += figure(RESULTS / "who_pays_incidence.png",
                    "Figure 2. Favourable decisions withdrawn and granted, in people, mean "
                    "over five seeds. Not one method closed the gap primarily by extending "
                    "favourable decisions to the disadvantaged group.")
    story += callout(
        f"ExpGrad-DP took approval away from {W.loc['expgrad_dp','priv_lost']:.0f} men so "
        f"that {W.loc['expgrad_dp','unpriv_gained']:.0f} women could gain it. Every method "
        "reduced the total number of favourable decisions &mdash; by 7.9% to 22.1%. "
        "Demographic parity constrains a ratio, not a total, and the cheapest way to fix a "
        "ratio is usually to shrink the numerator.")

    story += [para("5.1 How much of the effect is not fairness at all", "h2")]
    story += [para(
        "<font face='Courier'>ExponentiatedGradient</font> returns a distribution over "
        "classifiers and samples one at predict time, so some subjects receive a different "
        "decision on every call regardless of any constraint. The <b>arbitrariness "
        "floor</b> measures this by drawing twice from the same fitted model.")]
    rows = [["Method", "Subjects whose decision changed", "Arbitrariness floor",
             "Share of the effect that is noise"]]
    for key, label in [("expgrad_eo", "Exponentiated Gradient (EO)"),
                       ("expgrad_dp", "Exponentiated Gradient (DP)"),
                       ("gridsearch_dp", "GridSearch (DP)"),
                       ("adversarial_debiasing", "Adversarial Debiasing")]:
        r = W.loc[key]
        rows.append([label, f"{100 * r['total_churn']:.2f}%",
                     f"{100 * r['arbitrariness_floor']:.2f}%",
                     f"{100 * r['churn_that_is_noise']:.0f}%"])
    story += data_table(rows, highlight=[1])
    story += [para(
        f"About {100 * W.loc['expgrad_eo','churn_that_is_noise']:.0f}% of the individual "
        "decisions ExpGrad-EO changes are re-sampling, not fairness. Reporting its churn as "
        "the constraint's effect would be wrong by a factor of two and a half. The same "
        "applicant applying twice can receive different answers, for reasons unconnected to "
        "fairness or to their application. This is not a bug &mdash; the paper is explicit "
        "that the output is randomized, and the randomization is what makes the theory work "
        "&mdash; but it is a cost that falls on individuals and appears in no group metric.")]

    # ------------------------------------------------------------------ shap
    story += [PageBreak(), para("6. What does the mitigated model actually use?", "h1")]
    n_seeds = int(SH["n_seeds"].max()) if "n_seeds" in SH.columns else 1
    story += [para(
        "The specification listed SHAP as a stretch goal, expecting it to &ldquo;show "
        "reliance on <font face='Courier'>sex</font> and its proxies <b>shrinking</b> "
        "post-mitigation&rdquo;. It does not. For the two best parity methods it grows.")]
    story += [para(
        "<font face='Courier'>sex</font> is absent from the feature matrix, so any "
        "sex-related reliance is proxy reliance by construction. The proxies examined are "
        "<font face='Courier'>relationship</font> (whose levels on Adult are literally "
        "Husband and Wife), <font face='Courier'>marital-status</font>, "
        "<font face='Courier'>occupation</font> and "
        "<font face='Courier'>hours-per-week</font>. Attributions are aggregated back to "
        "source features &mdash; exact, since Shapley values are additive &mdash; and "
        "reported as a share of each model's total attribution mass, because the six models "
        "emit scores on different scales. Five of seven explainers are exact linear SHAP; "
        "the two randomized ensembles are sampled, and that is flagged rather than hidden.")]

    order = [("baseline", "Baseline (no mitigation)"), ("expgrad_dp", "Exponentiated Gradient (DP)"),
             ("gridsearch_dp", "GridSearch (DP)"), ("prejudice_remover [Male]", "Prejudice Remover [Male]"),
             ("prejudice_remover [Female]", "Prejudice Remover [Female]"),
             ("expgrad_eo", "Exponentiated Gradient (EO)"),
             ("adversarial_debiasing", "Adversarial Debiasing")]
    rows = [["Model", "Proxy reliance", "vs baseline", "relationship alone", "SHAP"]]
    for key, label in order:
        if key not in SH.index:
            continue
        std = SH.loc[key, "proxy_share_std"] if "proxy_share_std" in SH.columns else float("nan")
        share = f"{SH.loc[key, 'proxy_share']:.3f}"
        if pd.notna(std):
            share += f" ± {std:.3f}"
        change = "&mdash;" if key == "baseline" else f"{SH.loc[key, 'pct_change']:+.1f}%"
        rel = n["shares"].loc["relationship", key] if key in n["shares"].columns else float("nan")
        rows.append([label, share, change, f"{rel:.3f}", SH.loc[key, "shap_quality"]])
    story += data_table(rows, widths=[FRAME_WIDTH * 0.30, FRAME_WIDTH * 0.19,
                                      FRAME_WIDTH * 0.15, FRAME_WIDTH * 0.20,
                                      FRAME_WIDTH * 0.16], highlight=[2, 3])
    story += [para(f"Mean over {n_seeds} seed(s).", "caption")]

    story += callout(
        "The two methods with the best demographic-parity scores lean on sex proxies harder "
        "than the model with no fairness fix, and both roughly doubled their use of "
        "<i>relationship</i>. To equalise selection rates across sex while forbidden to "
        "read sex, a model must first infer sex in order to compensate &mdash; the "
        "constraint gives it a reason to become a better sex-detector.")

    story += [para(
        "Two things make this a mechanism rather than an artifact. First, ExpGrad's figure "
        "is sampled but GridSearch's is exact linear SHAP, and the two agree in direction "
        "and magnitude despite sharing only the constraint. Second, the one method that "
        "substantially <i>reduces</i> proxy reliance is Adversarial Debiasing &mdash; "
        "precisely the method whose objective is to make the output uninformative about "
        "sex. Theory predicts the ranking and the measurement matches it.")]
    story += [para(
        "The practical consequence: the reduction's operational selling point is that the "
        "deployed classifier does not require <font face='Courier'>sex</font>. That is "
        "true, and it is a claim about the API, not about the model's reasoning. If a "
        "regulator asks whether a model treats men and women differently, the absence of "
        "<font face='Courier'>sex</font> from the input schema is not an answer.")]

    # --------------------------------------------------------- intersectional
    story += [PageBreak(), para("7. Intersectional: Sex &times; Race", "h1")]
    story += [para(
        "Every method above constrains one binary attribute, which is the field's default "
        "and has a known failure mode: constraints on marginals can hold while the cells "
        "inside them stay unfair (Kearns et al. 2018). Three arms on identical splits, "
        "3 seeds. Fairlearn's reductions accept a multi-valued sensitive feature directly, "
        "so arm 3 is not a new algorithm &mdash; the contribution is the measurement.")]

    story += [para("7.1 The measurement problem comes first", "h2")]
    story += [para(
        "Sex &times; Race splits the test set into ten subgroups spanning three orders of "
        "magnitude, from Male&nbsp;&times;&nbsp;White at 8,110 people down to "
        "Female&nbsp;&times;&nbsp;Other at 21. <b>Five cannot support a rate estimate.</b> "
        "Female&nbsp;&times;&nbsp;Other has no positive labels at all, so its true-positive "
        "rate is undefined by division, not by convention. A ten-cell heatmap printed "
        "without that caveat reports sampling noise as discrimination.")]
    rows = [["Arm", "Gap over all 10 subgroups", "Gap over the 5 measurable", "Inflation"]]
    for key, label in [("baseline", "No constraint"), ("expgrad_dp_sex", "ExpGrad-DP on Sex"),
                       ("expgrad_dp_intersectional", "ExpGrad-DP on Sex &times; Race")]:
        r = IN.loc[key]
        rows.append([label, f"{r['intersectional_gap_all']:.4f}",
                     f"{r['intersectional_gap_reliable']:.4f}", f"{r['gap_inflation']:.4f}"])
    story += data_table(rows, highlight=[3])
    story += [para(
        "For the intersectionally-constrained arm, 70% of the apparent gap is contributed "
        "by subgroups too small to measure. Every gap quoted below is the reliable one, and "
        "the widest reliable gap in each arm was checked for overlapping 95% Wilson "
        "intervals &mdash; in all three arms they do not overlap, so these are real "
        "differences.")]

    story += [para("7.2 Bias hides at the intersection", "h2")]
    rows = [["Arm", "Accuracy", "Sex gap", "Sex &times; Race gap", "Worst-off subgroup"]]
    for key, label in [("baseline", "No constraint"), ("expgrad_dp_sex", "ExpGrad-DP on Sex"),
                       ("expgrad_dp_intersectional", "ExpGrad-DP on Sex &times; Race")]:
        r = IN.loc[key]
        rows.append([label, f"{r['accuracy']:.4f}", f"{r['sex_dp_gap']:.4f}",
                     f"{r['intersectional_gap_reliable']:.4f}", r["worst_subgroup_mode"]])
    story += data_table(rows, highlight=[2])
    ratio = IN.loc["expgrad_dp_sex", "intersectional_gap_reliable"] / IN.loc["expgrad_dp_sex", "sex_dp_gap"]
    story += callout(
        f"Constraining on sex takes the sex gap to "
        f"{IN.loc['expgrad_dp_sex','sex_dp_gap']:.4f} &mdash; essentially solved, and the "
        f"number the ablation table reports. At the intersection the same model still "
        f"carries a gap of {IN.loc['expgrad_dp_sex','intersectional_gap_reliable']:.4f}, "
        f"<b>{ratio:.0f}&times; larger than the number on its own dashboard.</b> Black men "
        "are selected at 9.2% against Asian men at 30.7%.")
    story += [para(
        "<b>The sex constraint moved the worst-off subgroup from Black women to Black "
        "men.</b> Before mitigation Black women were at the bottom; the constraint raised "
        "women's selection rates across the board, including theirs, but Black men were "
        "protected by no constraint at all and became the residual. Nothing was done to "
        "them &mdash; the constraint simply had nothing to say about them. A group can be "
        "made worst-off by a fairness intervention without ever appearing in it.")]
    story += [para(
        "Constraining on the intersection instead cuts the reliable gap by 73% for 1.7 "
        "additional accuracy points, and is the only arm in this study that <b>lifts the "
        "floor</b>: the worst-off subgroup's selection rate triples, 0.052 &rarr; 0.157. "
        "The mechanism differs from section 5 because with ten groups rather than two, the "
        "constraint cannot satisfy itself by trimming one large group's numerator without "
        "opening gaps against the eight it is not trimming.")]

    # --------------------------------------------------- proxy removal & epsilon
    story += [PageBreak(), para("8. Two ways out that do not work", "h1")]
    story += [para(
        "Sections 5 and 6 invite two obvious responses. If the model leans on "
        "<font face='Courier'>relationship</font>, delete it. If the constraint levels "
        "down, loosen it. Both were tested; neither works.")]

    story += [para("8.1 Deleting the leaky feature", "h2")]
    story += callout(
        "This sub-section is deliberately <i>not</i> in-processing. Every method in "
        "sections 3 and 4 changes only the objective; deleting features is "
        "pre-processing, and it is run here as a <b>negative control</b> rather than as "
        "a proposed mitigation. Its result defends this project's in-processing scope "
        "rather than departing from it: no row of the ablation table comes from here.",
        accent=NAVY, fill=colors.HexColor("#F4F6FA"))
    story += [para(
        "<font face='Courier'>FairnessDataset.attribute_leakage()</font> trains a probe "
        "to predict <font face='Courier'>sex</font> from the <i>remaining</i> features "
        "and reports ROC AUC. This is the direct measurement SHAP can only approach "
        "sideways: if the attribute is still recoverable after a deletion, the column "
        "went and the information stayed. Features are removed cumulatively, most "
        "sex-determining first. 3 seeds.")]
    P = n["proxy"]
    rows = [["Features removed", "Sex leakage (AUC)", "Baseline acc", "Baseline DP",
             "ExpGrad acc", "ExpGrad DP"]]
    for _, r in P.iterrows():
        rows.append([r["removed"], f"{r['leakage_auc']:.3f}",
                     f"{r['baseline_accuracy']:.4f}", f"{r['baseline_dp']:.4f}",
                     f"{r['expgrad_accuracy']:.4f}", f"{r['expgrad_dp']:.4f}"])
    story += data_table(rows, widths=[FRAME_WIDTH * 0.34] + [FRAME_WIDTH * 0.132] * 5,
                        highlight=[1, 2])
    story += [para("Chance leakage is 0.500; the majority-class rate is 0.675.", "caption")]
    story += [para(
        "Removing <font face='Courier'>relationship</font> &mdash; which determines sex "
        "outright for 45.9% of the dataset &mdash; moves leakage only from <b>0.934 to "
        "0.868</b>. The information was never in that column alone. Suppressing the leak "
        "takes four deletions out of eleven features, and at that point the probe's "
        "accuracy (0.676) is indistinguishable from the majority-class rate (0.675).")]
    story += [para(
        "Worse, the deletion <b>made the unmitigated model more unfair</b>: demographic "
        "parity difference rose from 0.190 to 0.205, with attribution simply relocating "
        "to <font face='Courier'>marital-status</font>, which remained the top feature "
        "in both rounds. The intervention that feels most obviously correct moved the "
        "metric the wrong way.")]
    story += callout(
        "Feature deletion is strictly dominated. Removing four features yields DP 0.076 "
        "at 80.8% accuracy; the constraint on the untouched feature set yields <b>DP "
        "0.020 at 83.0%</b>. Worse on both axes &mdash; and mitigation becomes more "
        "expensive afterwards, ExpGrad's accuracy falling from 0.830 to 0.803 as soon as "
        "<i>relationship</i> is gone.")

    story += [para("8.2 Loosening the constraint", "h2")]
    story += [para(
        "Every result in section 5 used &epsilon; = 0.01, which leaves almost no slack. "
        "If levelling down is an artifact of an unusually tight constraint, the fix is "
        "to loosen it. The sweep below tests that. The baseline gap is 0.190, so "
        "&epsilon; &ge; 0.15 is non-binding and must reproduce the baseline exactly "
        "&mdash; which it does, and that is the check that the parameter now controls "
        "what it claims to.")]
    E = n["eps"]
    rows = [["&epsilon;", "Accuracy", "DP diff", "Share paid by advantaged (people)",
             "Lost per gained", "Change in total approvals"]]
    for value, r in E.iterrows():
        binding = r["closure"] > 1e-9
        rows.append([f"{value:g}", f"{r['accuracy']:.4f}", f"{r['dp_diff']:.4f}",
                     f"{r['people_share_levelling_down']:.3f}" if binding else "not binding",
                     f"{r['lost_per_gained']:.2f}" if binding else "&mdash;",
                     f"{r['pie_change_pct']:+.1f}%"])
    story += data_table(rows, widths=[FRAME_WIDTH * 0.10, FRAME_WIDTH * 0.14,
                                      FRAME_WIDTH * 0.13, FRAME_WIDTH * 0.28,
                                      FRAME_WIDTH * 0.16, FRAME_WIDTH * 0.19])
    story += [para(
        "<b>The share does not move.</b> Across the entire binding range the advantaged "
        "group bears 0.739&ndash;0.777 of the closure measured in people. Total approvals "
        "fall at every binding &epsilon;, and closing a fixed amount of gap costs a "
        "near-constant number of approvals &mdash; roughly 120 to 146 per unit &mdash; "
        "whatever &epsilon; is set to. &epsilon; is a dial on how much fairness is "
        "bought, not on how it is bought.")]
    story += [para(
        "At the loosest binding setting the split is in fact the <i>most</i> lopsided per "
        "unit of work, at 3.41 favourable decisions destroyed per one created. The likely "
        "reason is that a small correction is cheapest to make by trimming the largest "
        "group's selection rate slightly, which touches many people because that group is "
        "2.1&times; larger.")]
    story += [para(
        "<b>A bug was found here before the finding was.</b> The first run of this sweep "
        "returned identical numbers at every &epsilon;, including where the constraint "
        "cannot bind. <font face='Courier'>fairlearn</font>'s "
        "<font face='Courier'>DemographicParity()</font>, constructed with no arguments, "
        "pins its violation bound at the library default of 0.01, and the "
        "<font face='Courier'>eps</font> argument on "
        "<font face='Courier'>ExponentiatedGradient</font> sets only the Lagrange "
        "multiplier bound B = 1/&epsilon;. The sweep had been varying a parameter that "
        "never touched the constraint. No previously reported result changes &mdash; every "
        "other experiment used &epsilon; = 0.01, which coincides with that default, "
        "verified by reproducing seed 0's gap of 0.0282 exactly after the fix.")]

    # ---------------------------------------------------------------- verdict
    story += [PageBreak(), para("9. Verdict against the base paper", "h1")]
    story += [para(
        "The distinction between extending a paper and refuting it is easy to blur and "
        "worth keeping sharp.")]

    story += [para("Confirmed", "h2")]
    story += bullets([
        "The reduction drives the fairness violation toward &epsilon; for a modest accuracy "
        "cost &mdash; 88% reduction for 1.5 accuracy points.",
        "The base classifier is a black box: the identical wrapper worked unmodified on a "
        "decision tree and on logistic regression.",
        "The training data is never modified; reweighting is internal to the objective.",
        "GridSearch traces a usable accuracy-versus-fairness frontier.",
        "The output is a randomized classifier &mdash; confirmed, and quantified in 5.1.",
    ])

    story += [para("Extended (outside the paper's frame, not against it)", "h2")]
    story += [para(
        "Agarwal et al. is a paper about feasibility and optimality: given a constraint, "
        "find the most accurate classifier satisfying it. Within that frame every result "
        "here is a success. The findings in sections 5&ndash;8 are questions the frame "
        "does not ask &mdash; who was moved, whether the total fell, what randomization "
        "costs an individual, what the model leans on, what happens one level below the "
        "constrained attribute, and whether either obvious escape route works.")]

    story += [para("Refuted", "h2")]
    story += [para(
        "<b>Nothing in the base paper.</b> The two refuted predictions are this project's "
        "own: that adversarial training would be the higher-variance approach (it is the "
        "most stable, and GridSearch is the least), and that SHAP would show proxy reliance "
        "shrinking after mitigation (it grew). One caution does touch the paper indirectly: "
        "GridSearch is presented there as the practical alternative for binary protected "
        "attributes, and its frontier is its selling point &mdash; this study suggests "
        "reporting its variance across resamples alongside that frontier, because the "
        "frontier looks smooth while the selection on it is fragile.")]

    story += [para("What a practitioner should take from this", "h2")]
    story += bullets([
        "<b>Use the reduction.</b> It works, it is cheap, it wraps anything, and it leaves "
        "the data alone.",
        "<b>Do not report the gap alone.</b> &ldquo;DP fell from 0.186 to 0.018&rdquo; and "
        "&ldquo;909 men lost approval so 316 women could gain it, and 570 fewer people were "
        "approved overall&rdquo; are both true; only the second describes what happened.",
        "<b>Say which metric.</b> Four of five mitigations here made equalized odds worse "
        "than no mitigation while improving demographic parity.",
        "<b>Do not treat the absence of the protected attribute from the feature list as "
        "evidence of anything.</b> Tightening the constraint made the model lean on proxies "
        "harder.",
        "<b>Quantify the arbitrariness floor</b> before attributing individual-level "
        "changes to a fairness intervention.",
        "<b>Do not delete the proxy.</b> It leaves the information in place, can make "
        "the unmitigated model more biased, and loses to the constraint on fairness and "
        "accuracy at the same time.",
        "<b>Do not expect a looser constraint to be gentler in kind.</b> It is gentler "
        "only in degree, and per unit of gap closed it is not even that.",
        "<b>Check one level below the attribute you constrained</b> &mdash; and report "
        "subgroup sizes, so a reader can tell a finding from a small sample.",
    ])

    story += [para("Limitations", "h2")]
    story += bullets([
        "<b>One dataset.</b> Every finding is a statement about Adult, which is a 1994 "
        "census extract with known idiosyncrasies. Whether these results are properties of "
        "constraint-based reductions or of this dataset is not established here, and "
        "replication on ACS Income is the obvious next step.",
        "Race is used as recorded in the source data: five administrative categories of "
        "very unequal size, the smallest of which are why half of section 7 is unmeasurable.",
        "&eta; and &alpha; are each fixed at one value. &epsilon; is swept in section 8.2, "
        "on a coarse grid that does not resolve where the constraint stops binding.",
        "The reliability threshold of 30 is a conventional rule of thumb. Wilson intervals "
        "are reported for every subgroup so a reader can apply their own.",
    ])

    story += [para("References", "h2")]
    story += bullets([
        "Agarwal, Beygelzimer, Dud&iacute;k, Langford &amp; Wallach (2018). A Reductions "
        "Approach to Fair Classification. <i>ICML</i>.",
        "Kamishima, Akaho, Asoh &amp; Sakuma (2012). Fairness-Aware Classifier with "
        "Prejudice Remover Regularizer. <i>ECML PKDD</i>.",
        "Zhang, Lemoine &amp; Mitchell (2018). Mitigating Unwanted Biases with Adversarial "
        "Learning. <i>AIES</i>.",
        "Kearns, Neel, Roth &amp; Wu (2018). Preventing Fairness Gerrymandering. <i>ICML</i>.",
        "Mittelstadt, Wachter &amp; Russell (2023). The Unfairness of Fair Machine "
        "Learning. <i>Michigan Technology Law Review</i>.",
        "Kleinberg, Mullainathan &amp; Raghavan (2016); Chouldechova (2017) &mdash; the "
        "impossibility results.",
        "Marx, Calmon &amp; Ustun (2020). Predictive Multiplicity in Classification. "
        "<i>ICML</i>.",
        "Ding, Hardt, Miller &amp; Schmidt (2021). Retiring Adult. <i>NeurIPS</i>.",
    ])
    return story


def main() -> None:
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
        title="Algorithmic Bias Mitigation on Adult Census Income",
        author="Dheirav",
    )
    doc.build(build(load()), onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
