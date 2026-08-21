# The whole thing, in plain words

No jargon in this document. Every technical term used in the other documents is defined at
the end.

## The situation

A bank uses a computer program to decide who gets a mortgage. The program looks at income,
loan size, property value and so on, and says yes or no.

Someone checks the results and finds a problem: the program approves **79%** of one group of
applicants and only **57%** of another. Same kind of applications, very different outcomes.

That is the thing people call "algorithmic bias", and there are well-known tools for fixing
it. You tell the program: *approve both groups at the same rate.*

## The catch, and it is a known one

There are two completely different ways for the program to obey that instruction.

**Way one:** approve more people from the group that was being turned down.

**Way two:** turn down more people from the group that was getting through.

Both make the rates equal. Both count as "fixed". **And the score that certifies the fix
cannot tell them apart** — it only measures whether the two rates match, not how they came
to match.

Way one helps people. Way two helps nobody — it just spreads the disadvantage around. There
is a name for it in the ethics literature: *levelling down*.

## What was already known

A well-known 2023 paper from Oxford showed that these tools mostly do **way two**. They put
it in their title: levelling down happens "by default".

**And that the score cannot tell way one from way two was known too.** A 2023 paper on
fairness across combinations of groups says as much in plain words — this "often goes
unnoticed in the overall performance of the model" — and a separate 2023 auditing tool
exists because a fairness score does not say how many people were affected or in which
direction. So the catch above is where this work starts, not something it found.

That paper is also the closest competitor — because it not only identified the problem, it
proposed the fix. This project originally believed it had invented that fix independently.
It had not. Found by reading their paper properly, and corrected.

**The way of measuring it is not mine either.** A 2023 paper set out how to audit what one
of these fixes does to individuals: how many people it moves, which way it moves them, and
what happens to the overall approval rate. Those are the three things counted here. What is
mine is what the counts say once you run them on 26 datasets instead of one — the direction
turns out to depend on the data, which their framework was never used to ask.

**And there is a second one.** A March 2026 paper proves mathematically that when the
program cannot see which group someone belongs to — which is the situation studied here —
the effect **can go either way** depending on the data. So the *idea* that it is not always
harmful was published, in theory, five months before this work reached it independently.

That paper has no experiments in it at all. Not one dataset. It proves the possibility and
gives conditions written in terms of the shape of the program's internal scores.

## What this work found

**It is not "by default". It depends on how generous the system is to begin with.**

Count what fraction of *everyone* gets approved, across both groups. Call that the approval
rate of the system as a whole.

- If the system approves **few** people overall — say under 30% — then forcing equality
  takes approvals **away**. Way two. The harmful one.
- If the system approves **most** people — say over 60% — then forcing equality **hands
  approvals out**. Way one. The good one.
- Somewhere in between, it flips.

Same tool. Same instruction. Opposite effect on real people, depending on nothing more than
how generous the system already was.

## How it was proven, and why the proof is trustworthy

The obvious worry is that two datasets differ in a hundred ways, so you can never tell which
difference caused what.

So the test used **one** dataset and changed exactly **one** thing.

The dataset predicts whether a person earns more than \$50,000. That \$50,000 is an
arbitrary number someone picked. Move it to \$70,000 and fewer people qualify. Move it to
\$20,000 and most people do.

Same people. Same information about them. Same groups. **Only the finish line moved.**

And the effect flipped, exactly as described. There is automated test code that checks the
people, the information and the groups really are identical between runs, so this is not a
matter of trust.

It then held up in:

- a second population,
- a second way of dividing people into groups,
- **real mortgage data**, where there is no arbitrary cutoff at all — the answer is a real
  lender's real decision,
- and **fourteen further runs — four new populations, each measured at several income
  cutoffs — carried out *after* the prediction was written down**, so they could not have
  influenced it. Four is the number that matters: runs on the same population share their
  people and differ only in where the cutoff was put.

## How this sits with the theory

Three things came out of checking this work against that 2026 paper:

1. **Their conditions never actually hold.** Applied to all 26 real datasets here, the
   mathematical conditions in their theorem are satisfied **zero times**. The quantity they
   are written over blows up on real data. So their result, as stated, cannot be used on
   anything.
2. **Their direction is still right.** Loosened into a comparison rather than a strict
   requirement, it predicts correctly in 24 of 26 cases.
3. **And it matches the approval-rate rule almost exactly** — the two agree on 25 of 26
   datasets, and the numbers behind them correlate at **0.93**.

So: their maths explains *why* it happens. This work shows *how you can tell in advance* —
using a number any organisation already has, rather than one requiring the model's internals.
Two independent routes to the same place, which is better evidence than either alone.

## Why it matters

Loans. Job applications. University admissions. These are the places these tools actually
get used — and I checked where each one sits.

| what is being decided | share who get a "yes" | which way the fix goes |
|---|---|---|
| Sifting job applications | **2–3%** | takes opportunities away |
| Getting into a top university | 4–10% | takes opportunities away |
| Getting into university generally | 66–73% | hands opportunities out |
| Getting a mortgage | **~84%** | hands opportunities out |

They are at **opposite ends**. So:

**Two organisations can use exactly the same fairness tool, in good faith, and get opposite
effects on how many people get helped.** That the fairness report looks identical either way
is not my observation — it is why Maheshwari et al. and Ferry et al. wrote their papers. What
is new is that the *direction* differs between them, and that you can tell in advance which
one you are about to get.

A bank fixing its mortgage model will end up approving more people. A company fixing its
CV-screening will end up interviewing fewer. Same tool. Same score. Opposite result.

That is why knowing which side you are on matters, and why it is worth being able to check.

## What could not be worked out

**Why** the flip happens.

There was an attempt: derive it from theory, write the prediction down in advance, then test
it on new data. It passed the test that was set for it — and then a much stupider rule
("more than half get approved? then it's the good kind") did *better*.

So the honest position is: we know **when** it flips. We do not know **why**. That failure is
written into the paper rather than left out.

## The one number that is worth remembering

**About 0.3.** Below roughly a 30% approval rate, these fairness tools take opportunities
away. Above it, they hand them out.

And you can check which side you are on before building anything, using a number you
already have.

---

# Glossary

Terms used in the other documents in this folder.

**Algorithmic bias.** A program producing systematically different outcomes for different
groups of people, usually because it learned from data in which that difference already
existed.

**Protected attribute.** The characteristic the fairness rule is about — sex, race, and so
on. In this work the programs are never allowed to see it directly.

**Proxy.** A piece of information that stands in for the protected attribute without being
it. If almost everybody labelled "husband" is male, then that label is a proxy for sex, and
removing "sex" from the data does not remove the information.

**Demographic parity.** The rule "approve both groups at the same rate". The main fairness
rule studied here.

**Constraint.** The instruction given to the program. "Approve both groups at the same rate"
is a constraint.

**Mitigation.** Any method for reducing bias. This work studies methods that change the
program's *instructions* rather than editing the data.

**Selection rate.** The fraction of everyone who gets the good outcome. If a bank approves
8,000 of 10,000 applications, the selection rate is 0.8. **This is the central quantity in
this work.**

**Base rate.** How often the good outcome genuinely occurs in a group — as opposed to how
often the program predicts it.

**Levelling down.** Making two groups equal by making the better-off group worse, rather
than the worse-off group better.

**Levelling up.** The opposite, and the desirable version.

**"The pie."** Informal shorthand for the total number of approvals. Levelling down shrinks
the pie; levelling up grows it.

**Exchange rate.** How many approvals were destroyed for each one created. Below 1.0 means
more were created than destroyed — good. On one dataset here it reached 46.7, meaning 46
people lost an approval for every one who gained one.

**Baseline.** The ordinary program, before any fairness fix, used as the comparison point.

**Seed.** A random number that decides how data is split for testing. Everything here is run
five times with five different seeds, so that a result cannot be an accident of one split.

**Held out.** Data deliberately not looked at until after a prediction is written down, so
the prediction cannot have been shaped by it.

**Pre-registration.** Writing down what you expect to find, and what would count as being
wrong, *before* running the experiment. The commit history proves the order.

**Feature attribution / SHAP.** A tool that claims to show which pieces of information a
program relied on. This work finds it can move dramatically without the program's actual
behaviour changing much.

**Intersectional.** Looking at combinations — not just "women" and "Black applicants" but
"Black women" specifically. A fix can look fine for each group separately while a
combination is treated badly.

**Correlation (r).** A number from −1 to +1 for how strongly two things move together. +0.9
is a strong positive relationship; 0 is none.

**Partial correlation.** The same, but with a third factor held fixed, to check the
relationship is not really caused by that third thing.

**Adult / ACS / HMDA.** The three data sources. *Adult* is a 1994 US census extract, the
standard benchmark. *ACS* is its modern replacement, available per state. *HMDA* is a
public record of real US mortgage applications and the lender's actual decision.

**Population.** One dataset, with one choice of protected attribute. Twenty-six were used
here.
