"""Prejudice Remover (Kamishima et al., 2012).

"Fairness-Aware Classifier with Prejudice Remover Regularizer", ECML PKDD 2012.

Adds a fairness penalty directly to the training loss rather than reducing to a
constrained game:

    L(W) = -Σ ln M[y_i | x_i, a_i]  +  η · PI(W)  +  (λ/2) ||W||²
           ^^^^^^^^^^^^^^^^^^^^^^^     ^^^^^^^^^^     ^^^^^^^^^^^^
           log loss                    prejudice      L2
                                       index

The prejudice index is a sample estimate of the mutual information I(Ŷ; A) between
the model's *predicted distribution* and the protected attribute:

    PI = Σ_i Σ_{y∈{0,1}} M[y|x_i,a_i] · ln( P̂[y|a_i] / P̂[y] )

    P̂[y|a] = mean of M[y|x_i,a_i] over samples with a_i = a
    P̂[y]   = mean of M[y|x_i,a_i] over all samples

PI is zero exactly when the predicted label distribution is independent of the
protected attribute, so η trades log-likelihood against that independence. The
training data is untouched; only the objective changes.

**Implementation note that matters for the writeup.** Kamishima parameterises the
model *per protected group* -- ``M[y=1|x,a] = σ(w_a · x + b_a)`` -- so unlike the
reductions approach, this method requires the protected attribute at **prediction**
time, not just during training. Two applicants identical on every feature but
differing in ``sex`` are scored by different weight vectors. That is disparate
treatment in the legal sense even though the intent is to reduce disparate impact,
and it is a genuine qualitative difference between this row of the ablation table and
the ExponentiatedGradient rows, not an implementation detail. ``predict`` therefore
takes ``a`` as a required argument -- the signature makes the dependency impossible
to overlook.

Implemented directly rather than via ``aif360`` so the objective above is visible and
so the project avoids that package's TensorFlow-1-compat dependency chain.
"""

from __future__ import annotations

import numpy as np
import torch

EPS = 1e-8


class PrejudiceRemover:
    """Logistic regression with a mutual-information fairness regulariser.

    Args:
        eta: Strength of the prejudice-index penalty. 0 reduces to per-group
            logistic regression; larger values buy independence at the cost of
            log-likelihood.
        l2: L2 coefficient (Kamishima's λ).
        lr: Adam learning rate.
        max_iter: Full-batch gradient steps.
        random_state: Seed for weight initialisation.
    """

    def __init__(
        self,
        *,
        eta: float = 1.0,
        l2: float = 1e-4,
        lr: float = 0.05,
        max_iter: int = 600,
        random_state: int = 0,
        verbose: bool = False,
    ) -> None:
        self.eta = eta
        self.l2 = l2
        self.lr = lr
        self.max_iter = max_iter
        self.random_state = random_state
        self.verbose = verbose

    def _group_index(self, a: np.ndarray) -> torch.Tensor:
        codes = np.searchsorted(self.groups_, np.asarray(a))
        return torch.as_tensor(codes, dtype=torch.long)

    def fit(self, X: np.ndarray, y: np.ndarray, a: np.ndarray) -> "PrejudiceRemover":
        torch.manual_seed(self.random_state)

        self.groups_ = np.unique(np.asarray(a))
        n_groups, n_features = len(self.groups_), X.shape[1]

        Xt = torch.as_tensor(np.array(X, dtype=np.float32))
        yt = torch.as_tensor(np.array(y, dtype=np.float32))
        gt = self._group_index(a)

        # One weight vector and bias per protected group -- Kamishima's parameterisation.
        W = torch.zeros(n_groups, n_features, requires_grad=True)
        b = torch.zeros(n_groups, requires_grad=True)
        torch.nn.init.normal_(W, std=0.01)

        optimiser = torch.optim.Adam([W, b], lr=self.lr)
        group_masks = [(gt == k) for k in range(n_groups)]

        for step in range(self.max_iter):
            optimiser.zero_grad()

            logits = (Xt * W[gt]).sum(dim=1) + b[gt]
            p1 = torch.sigmoid(logits)

            nll = torch.nn.functional.binary_cross_entropy(p1.clamp(EPS, 1 - EPS), yt, reduction="sum")

            # Prejudice index: mutual information between the predicted label
            # distribution and the protected attribute.
            p_marginal = torch.stack([(1 - p1).mean(), p1.mean()])
            pi = torch.zeros((), dtype=torch.float32)
            for mask in group_masks:
                if not bool(mask.any()):
                    continue
                p_group = torch.stack([(1 - p1[mask]).mean(), p1[mask].mean()])
                probs = torch.stack([1 - p1[mask], p1[mask]], dim=1)
                log_ratio = torch.log(p_group.clamp_min(EPS) / p_marginal.clamp_min(EPS))
                pi = pi + (probs * log_ratio).sum()

            loss = nll + self.eta * pi + 0.5 * self.l2 * (W * W).sum()
            loss.backward()
            optimiser.step()

            if self.verbose and step % 100 == 0:
                print(f"  step {step:4d}  loss={loss.item():.1f}  nll={nll.item():.1f}  pi={pi.item():.3f}")

        self.W_ = W.detach().numpy()
        self.b_ = b.detach().numpy()
        return self

    def predict_proba(self, X: np.ndarray, a: np.ndarray) -> np.ndarray:
        codes = np.searchsorted(self.groups_, np.asarray(a))
        logits = (np.asarray(X) * self.W_[codes]).sum(axis=1) + self.b_[codes]
        return 1.0 / (1.0 + np.exp(-logits))

    def predict(self, X: np.ndarray, a: np.ndarray) -> np.ndarray:
        """Predict labels. ``a`` is required -- see the module docstring."""
        return (self.predict_proba(X, a) >= 0.5).astype(int)
