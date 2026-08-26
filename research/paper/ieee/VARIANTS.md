# Shorter builds of the paper

`paper.tex` is the source of truth. `paper-10p.tex` and `paper-8p.tex` are **generated** —
do not edit them, the next run overwrites them.

```
python research/paper/ieee/make_variants.py
```

| build | pages | body type | margins | leading | overfull |
|---|---|---|---|---|---|
| `paper` | 18 | 10pt | 0.62in | 1.00 | 0 |
| `paper-10p` | 10 | 8.0pt | 0.45in | 0.95 | 0 |
| `paper-8p` | 8 | 7.5pt | 0.35in | 0.90 | 0 |

## Nothing is left out, and that is checked

Both variants contain **every** section, subsection, table, figure, algorithm, ledger row,
label, cross-reference, citation and word of `paper.tex`. Not summarised, not pointed at —
present. `make_variants.py` asserts it on every run by censusing both files and refusing to
write a variant whose counts differ:

```
paper.tex   18 pages   sections 14  subsections 15  tables 11  figures 2
                       algorithms 1  labels 27  refs 51  bibitems 20
                       citations 36  words 16077
```

A silently dropped float is the characteristic failure of a page-limit edit, so it is
asserted rather than trusted.

## How the pages are found

Only density changes: type size, margins, leading, column separation, float and caption
separation, `microtype`, tightened section headings and list spacing. The two full-width
figures are scaled to 0.84 of the text width; their content is unchanged.

The type size is the only real dial, and the settings above are the **largest** that fit
each limit — measured across a grid, not guessed. 8.5pt gives 11 pages, 8.0pt gives 10,
7.8pt gives 9, 7.5pt gives 8. There is nothing to gain by going smaller than the table
says.

Two implementation notes worth keeping. The class is switched to `9pt` because IEEEtran
supports 9/10/11/12 only — passing `8pt` is **silently ignored** and the build comes back
*longer*, which cost an hour to notice. And the size is set with the `fontsize` package
rather than a bare `\fontsize`, because the latter rescales body text without rescaling
`\small`, `\footnotesize` and the tables with it, which leaves table text larger than the
prose around it.

## What these are, and are not

They are for reading the whole argument in fewer pages — a supervisor, a reviewer, a
printout that fits a stapler.

**They are not submissible to a venue that specifies the IEEE format.** IEEE conference
templates require 10pt body text and set the margins; these set 8pt and 7.5pt at reduced
margins, and a format check would reject them on sight. A real page-limited submission has
to lose content, and [`../COMPRESSION-PLAN.md`](../COMPRESSION-PLAN.md) is where that
decision is already worked out — Pass 3's rulings, and the list of what may never be cut.
