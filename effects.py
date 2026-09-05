"""The ground truth the generator plants and the analysis has to recover.

This file is the answer key. `generate.py` reads it to build synthetic data.
Nothing under `sql/` or `report.py` may import it — an analysis that knows
the planted answer in advance proves nothing about whether the SQL actually
finds it. `tests/test_ground_truth.py` is the only test allowed to import
this module, because its whole job is comparing what was planted against
what the SQL recovered.

Two effects are planted, deliberately not more. Each is small enough to
explain in one sentence and verify in one query.
"""

# Baseline probability of replying, given the email was opened at all.
BASE_REPLY_GIVEN_OPEN = 0.15

# Effect 1: seniority. Decision-makers reply more per open than individual
# contributors do — multiplies the base rate.
SENIORITY_MULTIPLIER = {
    "decision_maker": 2.2,
    "individual_contributor": 0.7,
}

# Effect 2: touch fatigue. Reply probability per open declines with each
# additional follow-up in the sequence.
TOUCH_MULTIPLIER = {
    1: 1.3,
    2: 1.1,
    3: 0.8,
    4: 0.4,
    5: 0.2,
}

# Open rate is constant across every group. The two effects above live
# entirely in the reply-given-open step, not in whether the email gets
# opened — that keeps each effect isolated to one stage of the funnel.
OPEN_RATE = 0.45


def reply_probability(seniority: str, touch_number: int) -> float:
    """The planted reply-given-open probability for one send."""
    rate = BASE_REPLY_GIVEN_OPEN * SENIORITY_MULTIPLIER[seniority] * TOUCH_MULTIPLIER[touch_number]
    return min(rate, 0.95)
