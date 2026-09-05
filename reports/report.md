# Cold Outreach Reply Funnel — Analysis Report

Generated from 700 synthetic sends across a deterministic dataset (seed = 42, see `generate.py`).

## 1. Overall funnel

| Sends | Opened | Open rate | Replied (of opened) | Reply rate |
|---|---|---|---|---|
| 700 | 314 | 44.9% | 39 | 12.4% |

## 2. Reply rate by seniority

| Seniority | Opened sends | Replies | Reply rate |
|---|---|---|---|
| Decision-maker | 89 | 25 | 28.1% |
| Individual contributor | 225 | 14 | 6.2% |

**Finding:** decision-makers replied 4.5x more often than individual contributors (28.1% vs 6.2%).

## 3. Reply rate by touch number

| Touch # | Opened sends | Replies | Reply rate |
|---|---|---|---|
| 1 | 54 | 14 | 25.9% |
| 2 | 61 | 11 | 18.0% |
| 3 | 59 | 7 | 11.9% |
| 4 | 68 | 4 | 5.9% |
| 5 | 72 | 3 | 4.2% |

**Finding:** reply rate fell 6.2x from touch 1 (25.9%) to touch 5 (4.2%) — later follow-ups are seeing sharply diminishing returns.
