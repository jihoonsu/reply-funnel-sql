"""The argument that the SQL can be trusted.

Two effects were planted in the data by generate.py. These tests run the real
analysis queries and check that the numbers alone recover both — the queries
are never told what to look for.

This is the only file besides generate.py that is allowed to import effects.

Run with: python3 -m unittest test_recovery -v
"""

import unittest

import effects
from db import run_query_file

# Generous on magnitude, because these are sampled rates and not exact
# arithmetic. Ordering is asserted separately and is the sharper check: noise
# moves a ratio by a few percent, but a broken query breaks the ordering.
TOLERANCE = 0.30

# Matches the reporting threshold in report.py: below this many replies, a
# rate is too thin to assert anything about.
MIN_REPLIES = 25


class GroundTruthRecovery(unittest.TestCase):
    """Each test states the planted value and the recovered one on failure."""

    @classmethod
    def setUpClass(cls):
        cls.seniority = {r["seniority"]: r for r in run_query_file("02_reply_by_seniority.sql")}
        cls.touch = {r["touch_number"]: r for r in run_query_file("03_reply_by_touch.sql")}
        cls.funnel = {r["stage"]: r for r in run_query_file("01_funnel_overall.sql")}

    # ---------------------------------------------------------------- effect 1

    def test_decision_makers_reply_more(self):
        """Direction, before magnitude. This fails on any sign error."""
        dm = self.seniority["decision_maker"]["reply_rate_per_open_pct"]
        ic = self.seniority["individual_contributor"]["reply_rate_per_open_pct"]
        self.assertGreater(
            dm, ic,
            f"decision-makers should reply more per open; got dm={dm}%, ic={ic}%",
        )

    def test_seniority_multiplier_is_recovered(self):
        dm = self.seniority["decision_maker"]
        ic = self.seniority["individual_contributor"]
        for row in (dm, ic):
            self.assertGreaterEqual(
                row["replies"], MIN_REPLIES,
                f"{row['seniority']} has only {row['replies']} replies — too few to assert on",
            )

        planted = (
            effects.SENIORITY_REPLY_MULTIPLIER["decision_maker"]
            / effects.SENIORITY_REPLY_MULTIPLIER["individual_contributor"]
        )
        recovered = dm["reply_rate_per_open_pct"] / ic["reply_rate_per_open_pct"]
        self.assertAlmostEqual(
            recovered, planted, delta=planted * TOLERANCE,
            msg=(
                f"planted {planted:.2f}x, recovered {recovered:.2f}x "
                f"(dm {dm['reply_rate_per_open_pct']}% on {dm['replies']} replies, "
                f"ic {ic['reply_rate_per_open_pct']}% on {ic['replies']} replies)"
            ),
        )

    # ---------------------------------------------------------------- effect 2

    def test_reply_rate_declines_across_touches(self):
        """The sharper of the two follow-up checks: every step must go down."""
        rates = [
            self.touch[t]["reply_rate_per_open_pct"]
            for t in sorted(self.touch)
            if self.touch[t]["replies"] >= MIN_REPLIES
        ]
        self.assertGreater(len(rates), 1, "not enough touch levels clear the reply threshold")
        self.assertEqual(
            rates, sorted(rates, reverse=True),
            f"reply rate per open should fall at every touch; got {rates}",
        )

    def test_last_touch_is_far_worse_than_first(self):
        first = self.touch[min(self.touch)]
        last_number = max(t for t in self.touch if self.touch[t]["replies"] >= MIN_REPLIES)
        last = self.touch[last_number]

        planted = (
            effects.TOUCH_REPLY_MULTIPLIER[last_number]
            / effects.TOUCH_REPLY_MULTIPLIER[min(self.touch)]
        )
        recovered = last["reply_rate_per_open_pct"] / first["reply_rate_per_open_pct"]
        self.assertAlmostEqual(
            recovered, planted, delta=planted * TOLERANCE,
            msg=(
                f"touch {last_number} vs touch {min(self.touch)}: planted {planted:.3f}x, "
                f"recovered {recovered:.3f}x "
                f"(touch 1 {first['reply_rate_per_open_pct']}% on {first['replies']} replies, "
                f"touch {last_number} {last['reply_rate_per_open_pct']}% on "
                f"{last['replies']} replies)"
            ),
        )

    def test_every_touch_step_matches_its_planted_multiplier(self):
        """Checks the whole decay curve, not just its endpoints."""
        first_number = min(self.touch)
        first_rate = self.touch[first_number]["reply_rate_per_open_pct"]
        for number in sorted(self.touch):
            row = self.touch[number]
            if row["replies"] < MIN_REPLIES:
                continue
            planted = (
                effects.TOUCH_REPLY_MULTIPLIER[number]
                / effects.TOUCH_REPLY_MULTIPLIER[first_number]
            )
            recovered = row["reply_rate_per_open_pct"] / first_rate
            with self.subTest(touch=number):
                self.assertAlmostEqual(
                    recovered, planted, delta=planted * TOLERANCE,
                    msg=(
                        f"touch {number}: planted {planted:.3f}x, recovered {recovered:.3f}x "
                        f"({row['reply_rate_per_open_pct']}% on {row['replies']} replies)"
                    ),
                )

    # ------------------------------------------------------- funnel sanity

    def test_funnel_narrows_at_every_stage(self):
        counts = [self.funnel[s]["n"] for s in ("sent", "opened", "replied")]
        self.assertEqual(
            counts, sorted(counts, reverse=True),
            f"the funnel cannot widen: {counts}",
        )

    def test_open_rate_is_recovered(self):
        """Not one of the two effects, but if this drifts the per-open rates
        that both effects are measured on are suspect."""
        opened = self.funnel["opened"]["n"]
        sent = self.funnel["sent"]["n"]
        recovered = opened / sent
        self.assertAlmostEqual(
            recovered, effects.OPEN_RATE, delta=effects.OPEN_RATE * 0.10,
            msg=f"planted open rate {effects.OPEN_RATE}, recovered {recovered:.4f}",
        )


if __name__ == "__main__":
    unittest.main()
