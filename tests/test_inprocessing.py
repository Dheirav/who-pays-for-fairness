"""Correctness checks for the from-scratch in-processing implementations.

Both methods are written from the papers rather than taken from a library, so they
need evidence they are right. The strategy is degenerate cases: each method has a
setting where its fairness mechanism switches off, and it must then reproduce a
known reference model.

* Prejudice Remover with ``eta=0`` is per-group logistic regression -- the penalty
  term vanishes and nothing couples the groups.
* Adversarial Debiasing with ``adversary_weight=0`` still applies the gradient
  *projection*, so it is not plain logistic regression; what it must do is stay
  close in accuracy while not being systematically worse.
* Raising the fairness knob must move fairness monotonically in the right direction.
  This is the check that would catch a sign error -- the failure mode where a
  "mitigation" quietly increases disparity while the metrics still look plausible.

Run:  python -m tests.test_inprocessing
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression

from src.datasets.adult import AdultLoader
from src.inprocessing import AdversarialDebiasing, PrejudiceRemover
from src.metrics import demographic_parity_difference
from src.preprocessing import prepare

SUBSAMPLE = 8000


def _fixture():
    dataset = AdultLoader().load()
    split = prepare(dataset, random_state=0)
    n = min(SUBSAMPLE, len(split.y_train))
    return dataset, split, n


# The tests take (dataset, split, n) positionally so ``main()`` below can drive them
# without a test runner; these fixtures hand pytest the same values. Module scope,
# because the Adult load-and-split is identical for all four and dwarfs the assertions.
import pytest


@pytest.fixture(scope="module", name="_shared")
def _shared_fixture():
    return _fixture()


@pytest.fixture(name="dataset")
def _dataset(_shared):
    return _shared[0]


@pytest.fixture(name="split")
def _split(_shared):
    return _shared[1]


@pytest.fixture(name="n")
def _n(_shared):
    return _shared[2]


def test_prejudice_remover_eta_zero_matches_per_group_logistic(dataset, split, n) -> None:
    """eta=0 removes the penalty, leaving independent per-group logistic regressions."""
    pr = PrejudiceRemover(eta=0.0, l2=1e-4, max_iter=800, lr=0.05, random_state=0)
    pr.fit(split.X_train[:n], split.y_train[:n], split.a_train[:n])
    ours = pr.predict(split.X_test, split.a_test)

    reference = np.zeros(len(split.y_test), dtype=int)
    for group in np.unique(split.a_train[:n]):
        train_mask = split.a_train[:n] == group
        test_mask = split.a_test == group
        lr = LogisticRegression(max_iter=2000, C=1 / 1e-4).fit(
            split.X_train[:n][train_mask], split.y_train[:n][train_mask]
        )
        reference[test_mask] = lr.predict(split.X_test[test_mask])

    agreement = float(np.mean(ours == reference))
    print(f"  eta=0 vs per-group logistic: {agreement:.3%} prediction agreement")
    assert agreement > 0.95, f"eta=0 should recover per-group logistic regression, got {agreement:.3f}"


def test_prejudice_remover_eta_monotone(dataset, split, n) -> None:
    """Raising eta must reduce demographic parity difference, not raise it."""
    kw = {"privileged": dataset.privileged_value, "unprivileged": dataset.unprivileged_value}
    gaps = []
    for eta in (0.0, 5.0, 30.0):
        pr = PrejudiceRemover(eta=eta, max_iter=400, random_state=0)
        pr.fit(split.X_train[:n], split.y_train[:n], split.a_train[:n])
        gap = demographic_parity_difference(
            pr.predict(split.X_test, split.a_test), split.a_test, **kw
        )
        gaps.append(gap)
        print(f"  eta={eta:>5}: DP diff = {gap:.4f}")

    assert gaps[-1] < gaps[0], f"increasing eta should reduce DP difference, got {gaps}"


def test_adversarial_debiasing_alpha_monotone(dataset, split, n) -> None:
    """Raising the adversary weight must reduce demographic parity difference."""
    kw = {"privileged": dataset.privileged_value, "unprivileged": dataset.unprivileged_value}
    gaps = []
    for alpha in (0.0, 1.0, 4.0):
        ad = AdversarialDebiasing(adversary_weight=alpha, epochs=12, random_state=0)
        ad.fit(split.X_train[:n], split.y_train[:n], split.a_train[:n])
        gap = demographic_parity_difference(ad.predict(split.X_test), split.a_test, **kw)
        gaps.append(gap)
        print(f"  alpha={alpha:>4}: DP diff = {gap:.4f}")

    assert gaps[-1] < gaps[0], f"increasing alpha should reduce DP difference, got {gaps}"


def test_adversarial_debiasing_accuracy_sane(dataset, split, n) -> None:
    """The predictor must stay a real classifier, not collapse to one class.

    Adversarial training can degenerate: predicting a constant trivially defeats the
    adversary and would score ~76% accuracy on Adult's class imbalance while being
    useless. Checking the positive-prediction rate catches that; accuracy alone
    would not.
    """
    ad = AdversarialDebiasing(adversary_weight=1.0, epochs=12, random_state=0)
    ad.fit(split.X_train[:n], split.y_train[:n], split.a_train[:n])
    y_pred = ad.predict(split.X_test)

    positive_rate = float(np.mean(y_pred))
    accuracy = float(np.mean(y_pred == split.y_test))
    print(f"  accuracy={accuracy:.4f}  positive rate={positive_rate:.4f}")

    assert 0.02 < positive_rate < 0.6, f"predictor collapsed to near-constant: {positive_rate:.3f}"
    assert accuracy > 0.78, f"accuracy {accuracy:.3f} below the majority-class floor"


def main() -> None:
    dataset, split, n = _fixture()
    tests = [
        test_prejudice_remover_eta_zero_matches_per_group_logistic,
        test_prejudice_remover_eta_monotone,
        test_adversarial_debiasing_alpha_monotone,
        test_adversarial_debiasing_accuracy_sane,
    ]
    failures = 0
    for test in tests:
        print(f"\n{test.__name__}")
        try:
            test(dataset, split, n)
            print("  PASS")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL: {exc}")

    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
