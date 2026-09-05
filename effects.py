"""The answer key.

Everything the synthetic data "knows" is written here, and nowhere else.
generate.py reads this module to build the data. test_recovery.py reads it to
check the analysis found what was planted.

The SQL never reads it. That separation is the point of the project: an
analysis query that already knows the answer proves nothing about whether the
query is right.

Two effects, deliberately. More would make the data harder to reason about
without making the argument any stronger.
"""

# Everyone starts here. A 6% chance of replying once you've actually opened
# the email is roughly what I saw on real campaigns.
BASE_REPLY_RATE_PER_OPEN = 0.06

# Effect 1: seniority.
# Decision-makers reply about 3x as often as individual contributors, measured
# per open rather than per send. Per open is the honest denominator: if one
# group simply opens more email, a per-send rate would credit that to seniority.
SENIORITY_REPLY_MULTIPLIER = {
    "decision_maker": 3.0,
    "individual_contributor": 1.0,
}

# Effect 2: follow-up fatigue.
# Each additional touch in a sequence gets a worse response than the one
# before. By touch 5 the reply rate is a small fraction of touch 1.
TOUCH_REPLY_MULTIPLIER = {
    1: 1.00,
    2: 0.62,
    3: 0.38,
    4: 0.23,
    5: 0.14,
}

# Not an effect under test — just the mechanics of the funnel. Open rate is
# flat across both groups on purpose, so the only thing separating them in the
# reply numbers is the seniority multiplier above.
OPEN_RATE = 0.34

# Share of contacts who are decision-makers.
DECISION_MAKER_SHARE = 0.40

# Sized so that even touch 5 — the smallest cell, and the one the follow-up
# effect makes rarest — carries enough replies to measure a rate against.
N_COMPANIES = 3000
N_CONTACTS = 40000

# Fixed so that every run produces byte-identical data.
SEED = 20260904
