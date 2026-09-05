"""The one test that matters: does the SQL find effects we know are there?

Anyone can write a SQL query that runs without errors and produces a
plausible-looking number. That doesn't mean the query is correct. This
project's answer to "how do you know the analysis is right" is that the
data isn't real — two effects were planted deliberately (see effects.py),
and this test checks that the analysis queries actually recover them.

This is the only test file allowed to import effects.py, alongside
generate.py itself. sql/*.sql never does, and neither does report.py —
an analysis that already knows the answer proves nothing.
"""

import random
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import effects  # noqa: E402  (see module docstring for why this import is allowed here)
import generate  # noqa: E402


class GroundTruthRecovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate.build_database(random.Random(generate.SEED))
        cls.conn = sqlite3.connect(generate.DB_PATH)
        cls.conn.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def _rows(self, path: str):
        sql = (Path(__file__).parent.parent / path).read_text()
        return self.conn.execute(sql).fetchall()

    def test_seniority_effect_is_recovered(self):
        """Planted: decision-makers reply ~3x more per open than ICs.

        Asserting >= 2x rather than the exact planted ratio (~3.1x) is
        deliberate — the generator uses randomness, so the observed ratio
        moves run to run even at a fixed seed if the effect sizes above
        ever change. The test should fail if the *effect* disappears, not
        if the exact multiplier drifts within a wide, still-obviously-real
        margin.
        """
        rows = {r["seniority"]: r for r in self._rows("sql/analysis_2_seniority.sql")}
        dm_rate = rows["decision_maker"]["reply_rate_pct"]
        ic_rate = rows["individual_contributor"]["reply_rate_pct"]

        self.assertGreater(
            dm_rate / ic_rate, 2.0,
            f"expected decision-makers to reply at least 2x as often as ICs, "
            f"got {dm_rate}% vs {ic_rate}%",
        )

    def test_touch_fatigue_effect_is_recovered(self):
        """Planted: reply rate drops sharply from touch 1 to touch 5."""
        rows = {r["touch_number"]: r for r in self._rows("sql/analysis_3_touch_fatigue.sql")}
        first = rows[1]["reply_rate_pct"]
        last = rows[5]["reply_rate_pct"]

        self.assertGreater(
            first / last, 2.0,
            f"expected touch 1 reply rate to be at least 2x touch 5's, "
            f"got {first}% vs {last}%",
        )

    def test_open_rate_matches_the_planted_constant_within_sampling_noise(self):
        """Open rate isn't where either effect lives, so it should sit close
        to the flat constant in effects.py regardless of seniority or touch."""
        row = self._rows("sql/analysis_1_funnel.sql")[0]
        observed = row["open_rate_pct"] / 100
        planted = effects.OPEN_RATE

        self.assertLess(
            abs(observed - planted), 0.05,
            f"open rate drifted too far from the planted {planted:.0%}: got {observed:.1%}",
        )


if __name__ == "__main__":
    unittest.main()
