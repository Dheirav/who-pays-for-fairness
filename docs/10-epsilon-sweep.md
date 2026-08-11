# 10 — Does levelling down depend on how tight the constraint is?

**Not in the initiation document.** This closes the most serious objection to
document 05.

## The objection

Document 05 found that every mitigation closed the fairness gap mostly by withdrawing
favourable decisions from the advantaged group, and that all five shrank the total
number of approvals. Every one of those runs used **ε = 0.01** — almost no slack at
all.

That invites a good objection: **at ε = 0.01 the model may have no room to do anything
else.** If levelling down is an artifact of an unusually tight constraint, then the
honest recommendation is simply "loosen it", and document 05's finding is far narrower
than it appears. If the behaviour persists across the whole range, it is a property of
optimising a ratio, and loosening only buys a smaller dose of the same thing.

## A bug found first

The first run of this sweep returned **identical numbers at every ε**, including at
ε = 0.20 where the constraint cannot possibly bind — the unmitigated gap is 0.19, so
ε = 0.20 imposes no constraint at all and the reduction should return the baseline. It
returned a demographic parity difference of 0.0196.

The cause was in this project's own code. `fairlearn`'s `DemographicParity()`,
constructed with no arguments, pins its violation bound at the library default of 0.01
and **nothing passed to `ExponentiatedGradient` changes it**. The `eps` argument on the
reduction sets only `B = 1/eps`, the bound on the Lagrange multipliers the regulator
may play. So the sweep had been varying a parameter that never touched the constraint.

`src/mitigation.py` now passes ε to both the moment and the reduction, and
`build_constraint` takes the bound explicitly so it cannot be left implicit again.

**No previously reported result changes.** Every other experiment used ε = 0.01, which
coincides with the library default, so the fitted objects were identical — confirmed by
reproducing seed 0's ExpGrad-DP gap of 0.0282 exactly after the fix. The numbers were
right; the docstring explaining *why* was wrong.

The sanity check that caught it is worth recording: **a sweep whose extreme value must
reproduce a known answer, and does not, is a broken sweep** — the flat result was not a
finding, it was a symptom.

## Results

Logistic regression, 3 seeds. The baseline gap is 0.1897, so ε ≥ 0.15 is non-binding.

| ε | accuracy | DP diff | closure | share paid by privileged (rates) | share paid (people) | lost per gained | change in total approvals |
|---|---|---|---|---|---|---|---|
| 0.005 | 0.8284 | 0.0122 | 0.1776 | 0.580 | 0.746 | 2.74 | **−22.0%** |
| 0.010 | 0.8295 | 0.0197 | 0.1700 | 0.580 | 0.746 | 2.74 | −21.1% |
| 0.020 | 0.8324 | 0.0342 | 0.1555 | 0.578 | 0.744 | 2.73 | −19.1% |
| 0.050 | 0.8388 | 0.0762 | 0.1135 | 0.572 | 0.739 | 2.69 | −13.6% |
| 0.100 | 0.8457 | 0.1557 | 0.0341 | **0.625** | **0.777** | **3.41** | −5.0% |
| 0.150 | 0.8465 | 0.1897 | 0.0000 | — | — | — | 0.0% |
| 0.200 | 0.8465 | 0.1897 | 0.0000 | — | — | — | 0.0% |

The two non-binding rows return the baseline exactly, which is the check that the
corrected parameter now does what it claims.

## Finding 1 — the objection does not survive. Levelling down is not a tight-constraint artifact.

Across the entire binding range, the share of the closure paid by the privileged group
is **flat**: 0.572–0.625 in rates, **0.739–0.777 in people**. It does not decline as
the constraint loosens. There is no setting of ε at which the reduction closes the gap
mainly by lifting the disadvantaged group.

The total number of approvals falls at every binding ε. It falls *less* at loose ε —
but only because the constraint is doing less work overall, not because it is doing
different work.

## Finding 2 — the exchange rate is nearly constant

Dividing the shrinkage in approvals by the gap actually closed isolates the mechanism
from the dose:

| ε | pie change per unit of gap closed |
|---|---|
| 0.005 | −124 |
| 0.010 | −124 |
| 0.020 | −123 |
| 0.050 | −120 |
| 0.100 | −146 |

Within noise, **closing a fixed amount of gap costs a fixed number of approvals,
whatever ε you set.** ε is a dial on how much fairness you buy; it is not a dial on
*how* the method buys it.

## Finding 3 — the loosest binding constraint is the most lopsided per unit of work

At ε = 0.100 the people-level share rises to 0.777 and the ratio to **3.41 lost per 1
gained**, the highest in the sweep. A practitioner choosing a gentle constraint to
avoid harming anyone gets the opposite of what they intended per unit of gap closed.

The likely reason is that at loose ε the reduction only needs a small correction, and
the cheapest small correction is to trim the largest group's selection rate slightly —
which touches many people, because that group is 2.1× larger. Tighter constraints force
larger structural changes that necessarily move the smaller group too.

## What this means

The recommendation "if levelling down bothers you, loosen the constraint" **does not
work**. Loosening reduces how much the method does; it does not change what the method
does. If the gap should close by lifting the disadvantaged group, that has to be
expressed in the objective — no setting of ε expresses it.

This strengthens document 05 rather than qualifying it. The behaviour there is not a
corner case of an aggressive setting; it is what constraint-based parity optimisation
does across its whole operating range.

## Relation to the base paper

Agarwal et al. present ε as the knob that traces the accuracy–fairness trade-off, and
it does exactly that: accuracy rises monotonically from 0.828 to 0.847 as ε loosens,
and the violation tracks the bound. That claim is confirmed here in the cleanest form
this project has produced.

What the sweep adds is that the trade-off curve is **one-dimensional in the wrong
way**. Moving along it changes how much fairness you buy and what you pay in accuracy,
and changes nothing about who pays. The curve the paper draws is real; the axis it does
not have is the one document 05 measures.

## Limits

* 3 seeds, one dataset, one base classifier, demographic parity only. The equalized-odds
  constraint may behave differently, since it conditions on the true label and
  therefore cannot be satisfied by trimming a selection rate alone.
* ε is swept on a coarse grid; the transition between binding and non-binding falls
  somewhere between 0.100 and 0.150 and is not resolved.
