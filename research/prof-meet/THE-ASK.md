# The decision I need

> **Update, 23 August.** This document's argument stands, but its numbers are from an
> earlier stage; `06-status-report.pdf` carries the current ones. Since this was written:
> the population count went from 18 to 47; the direction rule passed a sealed test
> committed before the data existed (**9 of 10** never-measured states, best constant 6);
> the theory's own regime prediction was confirmed 27 of 27, nine pre-registered; and a
> second sealed campaign then showed the fixed 0.54 tipping point is population-dependent
> (located values 0.28–0.65), which narrowed the claim honestly rather than breaking it.
> The fork below is unchanged — if anything, the sealed pass strengthens the "stands on
> its own" branch.

## The question

**A 2026 theory paper proves the effect can go either way, with no experiments in it. I have
the experiments, a rule you can apply, and — since I last wrote this — a result that says the
theory is right about one half of its claim and wrong about the other. Is that an empirical
paper worth publishing, or does it read as a follow-up to someone else's result?**

## Why it is a genuine fork

**If the empirical half stands on its own**, the paper is close to ready. Their paper proves
the possibility and contains zero experiments. Mine has 18 independent populations across five
domains, two countries and two decades; a controlled design that separates the rate from the
difficulty of the task; and a rule computable from a historical approval rate.

**The strongest thing I have is a two-sided result about their theory.** They split the world
into two regimes — whether the protected attribute is available when the decision is made.

* Their **conditions**, the ordering relations their theorem is stated over, **cannot be
  evaluated on any of my 26 arms** — the quantity diverges on real data, so the two regions'
  ranges always overlap. They are *sufficient, not necessary*, so this says their theorem is
  **silent** on real populations, not that it is wrong. A relaxed form of the same ordering
  tracks the direction on 24 of 26.
* Their **regime distinction** holds on **18 of 18**. In the attribute-aware regime they predict
  the direction is determined rather than variable, and it is: the advantaged group loses and
  the disadvantaged gains in every population, with no exceptions.

So I am not applying their theory and not simply refuting it. I am showing which half survives
contact with data. That is what an empirical paper can settle and a population-level argument
cannot.

**If it now reads as derivative**, that is a problem of framing rather than content, but it
is still a problem. I reached this before knowing their paper existed — provable from dates
— but a reader encountering both will see theirs first.

## What I would argue

The "when" is the contribution, and it stands on its own:

1. **Theory says it *can* go either way. Only measurement says *when*.** That is the gap,
   and it is the gap a practitioner is standing in.
2. **Their conditions do not work on data.** Zero of 26. That is a finding only someone with
   the experiments could have produced, and it is a contribution against the theory rather
   than an application of it.
3. **My rule is computable and theirs is not.** Theirs needs the joint distribution of the
   model's scores and group membership. Mine needs last year's approval rate.
4. **The practical reading is sharper than I first thought, and less comfortable.** I
   originally claimed loans, hiring and admissions are nearly all stingy systems, so the
   harmful direction is the usual one. **I measured it, and that was wrong** — they span the
   whole range and sit on both sides of the switch. The real practical claim is better: two
   products in the *same* mortgage market, run through the *same* fairness constraint, move
   in opposite directions, and the fairness report says success in both cases.

## The objection I expect

That this is now the empirical appendix to someone else's theory paper.

My answer: their conditions fail on every dataset I have, so this is not an application of
their result — it is a demonstration that their result cannot be applied, plus a substitute
that can. But I would rather be told now if that is too fine a distinction to carry a paper.

## Other questions, if there is time

1. **Which venue, and when?** The deadline decides the page limit, which decides how much of
   **34 research documents** survives into the paper. My default is FAccT or AIES; there is no
   new algorithm here and the theory content is thin, which is a description of the work rather
   than a complaint about it.
2. ~~One missing comparison.~~ **Done, and it failed.** I ran the post-processing version
   across 17 populations: the rule vanishes, r = −0.024 against +0.585 for my own method. That
   is the regime boundary above rather than fragility — post-processing reads the protected
   attribute, which is the regime where the theory says nothing varies. But it means **every
   claim in the paper is now explicitly about attribute-blind in-processing**, which is where
   almost every deployed system sits, because per-group thresholds are disparate treatment on
   their face. Is narrowing it that way a strength or a weakness in your reading?
3. **AI assistance.** I used an AI assistant substantially — for writing code, running
   analyses and drafting. What does the department expect me to disclose, and how?

## What is not in question

The measurements. Every headline number is regenerated from stored results by an automated
check that fails if a document and its data disagree — 28 such checks at the time of writing.

## What I would want you to press me on

**I withdrew two headline results this week.** My strongest correlations, +0.979 and +0.968,
came from arms where the model was worse than always predicting the majority label. I found it
because a dataset where 89% of people pass forced the issue, and the same fix then rescued the
mortgage result that had been failing. The method that caught it — pre-registering every
prediction with the naive alternative it has to beat — is the part of this work I would most
like judged, because it is also the part that keeps producing results I did not want.

Three of my own predictions failed and are written up as failures. Two of my own claims were
withdrawn. I would rather be told the framing is wrong now than find out in review — which
is exactly what happened with the remedy, and why I no longer claim it as new.
