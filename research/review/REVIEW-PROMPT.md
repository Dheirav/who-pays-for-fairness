# Prompt for an external review

Paste the block below, then attach `research/paper/ieee/paper.pdf` — or paste
`research/review/paper-plaintext.txt` if the tool will not take a file.

**Deliberately withheld:** our own list of weaknesses. If the reviewer independently finds
what we already know, that is a signal the list is right. If it finds something else, that
is worth more than a confirmation. Do not paste our self-assessment alongside this.

---

You are reviewing a submission for a machine-learning venue that publishes empirical work on
fairness — think FAccT, AIES, or the ML-and-society track of a general conference. Review it
as a knowledgeable, sceptical referee who will have to justify the recommendation to an area
chair.

The paper is empirical. It claims that the direction in which a demographic-parity constraint
moves the total pool of favourable decisions — whether it extends decisions to more people or
withdraws them from people who had them — is predictable in advance from the rate at which
the deployed model currently returns a favourable decision. It reports a large multi-dataset
study, a set of pre-registered and externally timestamped predictions including several that
failed, and an audit procedure intended for deployment.

I want a hostile-but-fair review, not encouragement. Specifically:

**1. The strongest objections.** Give me the three or four arguments most likely to sink this
at review, ranked. For each, say what would answer it and whether the paper could answer it
with the evidence it already has, or would need new experiments.

**2. Claim-by-claim support.** Go through the paper's substantive claims and mark each as
well-supported, thinly supported, or unsupported. Quote the specific evidence you are judging
against. Where a claim rests on a small sample or a single dataset, say so with the number.

**3. Statistical audit.** Check every inferential statement you can. Correlations reported
without a sample size, significance claimed on small n, confidence intervals that do or do
not exclude the null, multiple comparisons, any place a pass/fail threshold could have been
chosen after seeing data. Recompute where you can and tell me if a number does not follow.

**4. Denominator audit.** This paper counts populations, arms, markets and tests, and those
counts appear in several places. Check they agree with each other and that nothing is counted
twice or under two different definitions. Flag any count you cannot verify from the text.

**5. Novelty.** Separate what is genuinely new from what replicates existing work. The paper
disclaims several things as not-novel; check whether it disclaims enough, and whether
anything it does claim is in fact already known. Name the prior work you have in mind.

**6. The failure ledger.** The paper reports many pre-registered tests that failed. Tell me
honestly whether this reads as unusual rigour or as a fishing expedition that found little,
and what would tip a reader either way.

**7. What to cut, what to add.** If it must lose two pages, what goes? If one new experiment
would most improve it, what is it?

**8. Verdict.** Accept / minor revision / major revision / reject, with the single change
that would most move your recommendation.

Constraints on your review:

* If you cannot verify something from the text, say "cannot verify from the text" rather than
  assuming it holds or that it fails.
* Do not soften. If a central claim is weakly supported, lead with that.
* Do not praise the writing unless it materially affects whether the science is checkable.
* Where you assert a number is wrong, show the arithmetic.
* Distinguish "this is not supported" from "I disagree with this framing" and label which
  you are doing.
