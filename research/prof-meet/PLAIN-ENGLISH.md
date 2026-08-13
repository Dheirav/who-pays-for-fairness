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

## The catch nobody looks at

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

That paper is the starting point for this work, and it is also the closest competitor —
because it not only identified the problem, it proposed the fix. This project originally
believed it had invented that fix independently. It had not. That was found by reading their
paper properly, and corrected.

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
- and **fourteen further populations that were run *after* the prediction was written down**,
  so they could not have influenced it.

## Why it matters

Loans. Job applications. University admissions.

These are the places these fairness tools actually get used — and they are almost all the
**stingy** kind. Few applicants get approved.

**So the normal case, in real deployments, is the harmful one. And the fairness score never
says so.**

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
