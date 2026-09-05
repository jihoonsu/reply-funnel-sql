# Reply Funnel SQL

A small SQL analysis project on a synthetic cold-outreach dataset: does contact seniority affect reply rate, and does a follow-up sequence lose effectiveness over time? The interesting part isn't the questions — it's how the project proves its own answers are correct.

> **All data is synthetic.** Nothing here is real company, contact, or campaign data. See [Why synthetic data](#why-synthetic-data-and-why-it-has-to-be) below.

## The idea

I did cold email outreach as a Data Analyst Intern at GAO Tek — building lead lists, running them through Apollo and Mailmeteor, tracking who opened and who replied. Two questions kept coming up that I never got to answer properly: does it matter who you're emailing (a VP versus an analyst), and does emailing someone a fifth time actually help or just annoy them?

I couldn't use the real campaign data to explore this — it's a client's confidential business data, not mine to publish. So I built a small synthetic version I could freely analyze, and used it to ask both questions properly.

## Why synthetic data (and why it has to be)

Any project like this has to answer a basic question: how do you know your SQL query is actually correct, rather than just running without an error and producing a number that looks plausible?

The answer here is that I don't have to trust it. Before generating a single row, [`effects.py`](effects.py) plants two exact effects — decision-makers reply about 3x more per open than individual contributors, and reply rate drops sharply with each additional follow-up. The generator ([`generate.py`](generate.py)) then builds 700 synthetic sends around those planted rules, using a fixed random seed so the same run always produces the same data.

The analysis SQL never sees `effects.py`. It has to find both effects cold, from the data alone — the same way it would have to find a real effect in real data. [`tests/test_ground_truth.py`](tests/test_ground_truth.py) checks that it does.

I didn't just write that test and assume it works. I copied the project to a scratch directory, set both planted effects to zero, and reran the tests — they failed, with the actual numbers in the message (`0.94 not greater than 2.0`, `got 7.9% vs 8.4%`). That's the proof the test is checking something real, not just checking that the code runs.

## What the analysis found

A real run, committed at [`reports/report.md`](reports/report.md):

```
## 2. Reply rate by seniority

| Seniority               | Opened sends | Replies | Reply rate |
|--------------------------|--------------|---------|-------------|
| Decision-maker           | 89           | 25      | 28.1%       |
| Individual contributor   | 225          | 14      | 6.2%        |

Finding: decision-makers replied 4.5x more often than individual
contributors (28.1% vs 6.2%).

## 3. Reply rate by touch number

| Touch # | Opened sends | Replies | Reply rate |
|---------|--------------|---------|-------------|
| 1       | 54           | 14      | 25.9%       |
| 2       | 61           | 11      | 18.0%       |
| 3       | 59           | 7       | 11.9%       |
| 4       | 68           | 4       | 5.9%        |
| 5       | 72           | 3       | 4.2%        |

Finding: reply rate fell 6.2x from touch 1 (25.9%) to touch 5 (4.2%) —
later follow-ups are seeing sharply diminishing returns.
```

Both "Finding" lines are generated from the query results at runtime ([`report.py`](report.py)), not typed by hand — they're built from thresholds against the actual numbers, so the report can't claim an effect that isn't there.

## How I used AI on this

I designed the funnel model, picked which two effects to plant and why (they're the two real questions from my internship, above), and decided on the ground-truth-recovery approach as the way to prove correctness. I used Claude Code to implement the generator, schema, and analysis queries from that design, and to write the report renderer.

The verification was mine to check, not to assume: I ran the recovery test, then deliberately broke each planted effect in a scratch copy to confirm the test actually fails when the effect disappears — described above, and it's the reason I trust the numbers in this README enough to publish them.

## Running it

Pure Python 3 standard library. No pip install, no external services.

```bash
python3 run.py
```

Generates the database, runs all three analyses, prints the report, and writes it to `reports/report.md`.

```bash
python3 -m unittest discover tests -v
```

Runs the ground-truth recovery test.

## Project layout

| Path | Holds |
|---|---|
| `effects.py` | The planted ground truth. Only `generate.py` and the test import it. |
| `generate.py` | Builds the synthetic SQLite database, deterministically. |
| `sql/schema.sql` | Three tables: `companies`, `contacts`, `sends`. |
| `sql/analysis_*.sql` | The three analysis queries — plain SQL, no Python logic mixed in. |
| `report.py` | Runs the queries, generates the findings text, renders the report. |
| `tests/test_ground_truth.py` | Proves the SQL recovers both planted effects. |

## What I'd add next

- A third planted effect (industry) once the two-effect version has been reviewed — kept to two on purpose so the whole project stays easy to hold in your head and explain.
- Real Postgres features (window functions, materialized views) once the SQLite version has proven the design is right. SQLite was the deliberate choice here: zero setup, and anyone can run this in ten seconds with nothing installed.

## License

MIT — see [LICENSE](LICENSE).
