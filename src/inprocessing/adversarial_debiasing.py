"""Adversarial Debiasing (Zhang, Lemoine & Mitchell, 2018).

"Mitigating Unwanted Biases with Adversarial Learning", AIES 2018.

Two networks trained against each other:

* **Predictor** -- maps ``x`` to a logit for ``y``. Linear here, matching the
  logistic-regression base used across the ablation.
* **Adversary** -- tries to recover the protected attribute ``a`` from the
  predictor's *output*. It never sees ``x``.

If the adversary cannot predict ``a`` from the prediction, the prediction carries no
information about ``a`` -- which is exactly demographic parity. Feeding the adversary
the true label as well relaxes this to equalized odds, since it may then use whatever
information about ``a`` is already explained by ``y``.

Following the paper, the adversary sees ``s = σ((1 + |c|) · logit)`` for a learnable
scalar ``c``, and additionally ``[s·y, s·(1-y)]`` under the equalized-odds variant.

**The gradient surgery is the method.** The predictor's update is not simply
"minimise my loss and the negative of theirs":

    ∇_W L_P  -  proj_{∇_W L_A}(∇_W L_P)  -  α ∇_W L_A
                ^^^^^^^^^^^^^^^^^^^^^^^^     ^^^^^^^^^^
                remove the component of      actively
                the predictor's gradient     damage the
                that also helps the          adversary
                adversary

Without the projection term the predictor can improve accuracy in a direction that
happens to help the adversary, and the two objectives fight to a standstill instead of
converging. It is implemented explicitly below (over the flattened predictor
gradient, as in the paper) rather than approximated by a weighted sum of losses,
because the weighted-sum version is a different and weaker algorithm.

Unlike :mod:`~src.inprocessing.prejudice_remover`, the protected attribute is used
only during **training** -- ``predict`` takes ``X`` alone, like the reductions
methods.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

EPS = 1e-8


class AdversarialDebiasing:
    """Linear predictor trained against an adversary that predicts ``a``.

    Args:
        constraint: ``"demographic_parity"`` (adversary sees the prediction only) or
            ``"equalized_odds"`` (adversary also sees the true label).
        adversary_weight: α, how hard the predictor works to defeat the adversary.
        epochs / batch_size / lr: standard optimisation controls.
        random_state: seed for initialisation and batch shuffling.
    """

    def __init__(
        self,
        *,
        constraint: str = "demographic_parity",
        adversary_weight: float = 1.0,
        epochs: int = 30,
        batch_size: int = 256,
        lr: float = 0.01,
        adversary_hidden: int = 16,
        random_state: int = 0,
        verbose: bool = False,
    ) -> None:
        if constraint not in ("demographic_parity", "equalized_odds"):
            raise ValueError(f"unknown constraint '{constraint}'")
        self.constraint = constraint
        self.adversary_weight = adversary_weight
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.adversary_hidden = adversary_hidden
        self.random_state = random_state
        self.verbose = verbose

    def _adversary_input(self, logits: torch.Tensor, y: torch.Tensor, c: torch.Tensor) -> torch.Tensor:
        s = torch.sigmoid((1.0 + c.abs()) * logits).unsqueeze(1)
        if self.constraint == "demographic_parity":
            return s
        return torch.cat([s, s * y.unsqueeze(1), s * (1 - y).unsqueeze(1)], dim=1)

    def fit(self, X: np.ndarray, y: np.ndarray, a: np.ndarray) -> "AdversarialDebiasing":
        torch.manual_seed(self.random_state)
        rng = np.random.default_rng(self.random_state)

        Xt = torch.as_tensor(np.array(X, dtype=np.float32))
        yt = torch.as_tensor(np.array(y, dtype=np.float32))

        self.groups_ = np.unique(np.asarray(a))
        if len(self.groups_) != 2:
            raise ValueError("binary protected attribute required")
        at = torch.as_tensor(np.array(np.asarray(a) == self.groups_[1], dtype=np.float32))

        n, n_features = Xt.shape
        predictor = nn.Linear(n_features, 1)
        c = torch.zeros(1, requires_grad=True)
        adversary_in = 1 if self.constraint == "demographic_parity" else 3
        adversary = nn.Sequential(
            nn.Linear(adversary_in, self.adversary_hidden),
            nn.ReLU(),
            nn.Linear(self.adversary_hidden, 1),
        )

        opt_p = torch.optim.Adam(predictor.parameters(), lr=self.lr)
        opt_a = torch.optim.Adam([*adversary.parameters(), c], lr=self.lr)
        bce = nn.BCEWithLogitsLoss()
        p_params = list(predictor.parameters())

        for epoch in range(self.epochs):
            order = rng.permutation(n)
            # Paper's 1/t decay: the predictor's steps must shrink faster than the
            # adversary's for the minimax game to settle rather than oscillate.
            decay = 1.0 / (1.0 + epoch)
            for group in opt_p.param_groups:
                group["lr"] = self.lr * decay

            for start in range(0, n, self.batch_size):
                idx = order[start : start + self.batch_size]
                xb, yb, ab = Xt[idx], yt[idx], at[idx]

                # --- adversary step: get as good as possible at recovering `a` ---
                opt_a.zero_grad()
                logits = predictor(xb).squeeze(1)
                loss_a = bce(adversary(self._adversary_input(logits.detach(), yb, c)).squeeze(1), ab)
                loss_a.backward()
                opt_a.step()

                # --- predictor step with gradient surgery ---
                opt_p.zero_grad()
                logits = predictor(xb).squeeze(1)
                loss_p = bce(logits, yb)
                loss_a = bce(adversary(self._adversary_input(logits, yb, c)).squeeze(1), ab)

                grad_p = torch.autograd.grad(loss_p, p_params, retain_graph=True)
                grad_a = torch.autograd.grad(loss_a, p_params, retain_graph=False)

                flat_p = torch.cat([g.reshape(-1) for g in grad_p])
                flat_a = torch.cat([g.reshape(-1) for g in grad_a])
                unit_a = flat_a / (flat_a.norm() + EPS)
                combined = flat_p - (flat_p @ unit_a) * unit_a - self.adversary_weight * flat_a

                offset = 0
                for param in p_params:
                    size = param.numel()
                    param.grad = combined[offset : offset + size].view_as(param).clone()
                    offset += size
                opt_p.step()

            if self.verbose:
                print(f"  epoch {epoch:3d}  loss_p={loss_p.item():.4f}  loss_a={loss_a.item():.4f}")

        self.predictor_ = predictor
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            logits = self.predictor_(torch.as_tensor(np.asarray(X), dtype=torch.float32)).squeeze(1)
            return torch.sigmoid(logits).numpy()

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict labels. The protected attribute is not needed at inference."""
        return (self.predict_proba(X) >= 0.5).astype(int)
