"""Run the analysis queries and render a Markdown report.

The interpretation lines below the tables are built from the actual query
results, not typed by hand. That's a small thing, but it's the point: the
prose can't say something the data doesn't show, because it's generated
from the same numbers that produced the table above it.
"""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "funnel.db"
REPORT_PATH = ROOT / "reports" / "report.md"

QUERIES = {
    "funnel": (ROOT / "sql" / "analysis_1_funnel.sql").read_text(),
    "seniority": (ROOT / "sql" / "analysis_2_seniority.sql").read_text(),
    "touch": (ROOT / "sql" / "analysis_3_touch_fatigue.sql").read_text(),
}


def _rows(conn: sqlite3.Connection, sql: str) -> list[sqlite3.Row]:
    return conn.execute(sql).fetchall()


def render(conn: sqlite3.Connection) -> str:
    conn.row_factory = sqlite3.Row

    funnel = _rows(conn, QUERIES["funnel"])[0]
    seniority = {row["seniority"]: row for row in _rows(conn, QUERIES["seniority"])}
    touch = {row["touch_number"]: row for row in _rows(conn, QUERIES["touch"])}

    dm = seniority["decision_maker"]
    ic = seniority["individual_contributor"]
    seniority_ratio = dm["reply_rate_pct"] / ic["reply_rate_pct"]

    first_touch = touch[min(touch)]
    last_touch = touch[max(touch)]
    fatigue_ratio = first_touch["reply_rate_pct"] / last_touch["reply_rate_pct"]

    lines = [
        "# Cold Outreach Reply Funnel — Analysis Report",
        "",
        f"Generated from {funnel['total_sends']} synthetic sends "
        f"across a deterministic dataset (seed = 42, see `generate.py`).",
        "",
        "## 1. Overall funnel",
        "",
        "| Sends | Opened | Open rate | Replied (of opened) | Reply rate |",
        "|---|---|---|---|---|",
        f"| {funnel['total_sends']} | {funnel['total_opened']} | "
        f"{funnel['open_rate_pct']}% | {funnel['total_replied']} | "
        f"{funnel['reply_rate_given_open_pct']}% |",
        "",
        "## 2. Reply rate by seniority",
        "",
        "| Seniority | Opened sends | Replies | Reply rate |",
        "|---|---|---|---|",
        f"| Decision-maker | {dm['opened_sends']} | {dm['replies']} | {dm['reply_rate_pct']}% |",
        f"| Individual contributor | {ic['opened_sends']} | {ic['replies']} | {ic['reply_rate_pct']}% |",
        "",
        _seniority_finding(seniority_ratio, dm, ic),
        "",
        "## 3. Reply rate by touch number",
        "",
        "| Touch # | Opened sends | Replies | Reply rate |",
        "|---|---|---|---|",
    ]
    for number in sorted(touch):
        row = touch[number]
        lines.append(
            f"| {number} | {row['opened_sends']} | {row['replies']} | "
            f"{row['reply_rate_pct']}% |"
        )
    lines += [
        "",
        _fatigue_finding(fatigue_ratio, first_touch, last_touch),
        "",
    ]
    return "\n".join(lines)


def _seniority_finding(ratio: float, dm, ic) -> str:
    # Threshold, not a hand-picked adjective: only call it a "strong"
    # effect if it clears 2x, so this line can't overstate a fluke.
    if ratio >= 2:
        return (
            f"**Finding:** decision-makers replied {ratio:.1f}x more often than "
            f"individual contributors ({dm['reply_rate_pct']}% vs {ic['reply_rate_pct']}%)."
        )
    return f"**Finding:** no strong seniority effect observed (ratio {ratio:.1f}x)."


def _fatigue_finding(ratio: float, first, last) -> str:
    if ratio >= 2:
        return (
            f"**Finding:** reply rate fell {ratio:.1f}x from touch "
            f"{first['touch_number']} ({first['reply_rate_pct']}%) to touch "
            f"{last['touch_number']} ({last['reply_rate_pct']}%) — later "
            f"follow-ups are seeing sharply diminishing returns."
        )
    return f"**Finding:** no strong touch-fatigue effect observed (ratio {ratio:.1f}x)."


if __name__ == "__main__":
    connection = sqlite3.connect(DB_PATH)
    report = render(connection)
    connection.close()

    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(report)
    print(report)
