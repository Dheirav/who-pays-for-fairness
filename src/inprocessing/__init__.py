"""From-scratch in-processing methods (Kamishima 2012; Zhang et al. 2018)."""

from .adversarial_debiasing import AdversarialDebiasing
from .prejudice_remover import PrejudiceRemover

__all__ = ["AdversarialDebiasing", "PrejudiceRemover"]
