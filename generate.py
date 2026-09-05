"""Generate a synthetic cold-outreach dataset with two planted effects.

Deterministic: seeded once, at the top, so the same run always produces the
same database and the same report. That matters here for a specific reason
— a reviewer (or an interviewer) can regenerate the exact numbers in this
README themselves, rather than trusting a screenshot.

This is the only file that imports effects.py besides the ground-truth
test. The analysis SQL never sees it.
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import effects

SEED = 42
N_COMPANIES = 40
ROOT = Path(__file__).parent
DB_PATH = ROOT / "funnel.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

INDUSTRIES = [
    "Healthcare", "Manufacturing", "Logistics", "Retail",
    "Financial Services", "Technology", "Construction", "Education",
]
NAME_PREFIXES = [
    "North", "Blue", "Summit", "Cedar", "Harbor", "Iron", "Silver",
    "Bright", "Union", "Crown", "River", "Stone", "Maple", "West",
]
NAME_SUFFIXES = [
    "Ridge", "Peak", "Field", "Works", "Labs", "Group", "Systems",
    "Partners", "Logistics", "Analytics", "Solutions", "Holdings",
]
FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Sam",
    "Jamie", "Drew", "Cameron", "Quinn", "Avery", "Reese", "Skyler",
]
LAST_NAMES = [
    "Kim", "Patel", "Garcia", "Nguyen", "Smith", "Johnson", "Lee",
    "Brown", "Davis", "Martinez", "Chen", "Wilson", "Moore", "Clark",
]
DECISION_MAKER_TITLES = [
    "VP of Operations", "Director of Procurement", "Chief Financial Officer",
    "VP of Engineering", "Head of Supply Chain", "Director of IT",
]
IC_TITLES = [
    "Operations Analyst", "Procurement Specialist", "Financial Analyst",
    "Software Engineer", "Supply Chain Coordinator", "IT Support Specialist",
]

TOUCHES_PER_CONTACT = 5
DAYS_BETWEEN_TOUCHES = 4
START_DATE = date(2026, 1, 5)


def build_database(rng: random.Random) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())

    company_id = 0
    contact_id = 0
    send_id = 0

    for _ in range(N_COMPANIES):
        company_id += 1
        name = f"{rng.choice(NAME_PREFIXES)} {rng.choice(NAME_SUFFIXES)}"
        industry = rng.choice(INDUSTRIES)
        conn.execute(
            "INSERT INTO companies (id, name, industry) VALUES (?, ?, ?)",
            (company_id, name, industry),
        )

        for _ in range(rng.randint(2, 5)):
            contact_id += 1
            seniority = (
                "decision_maker" if rng.random() < 0.30 else "individual_contributor"
            )
            titles = DECISION_MAKER_TITLES if seniority == "decision_maker" else IC_TITLES
            full_name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            title = rng.choice(titles)
            conn.execute(
                "INSERT INTO contacts (id, company_id, name, title, seniority) "
                "VALUES (?, ?, ?, ?, ?)",
                (contact_id, company_id, full_name, title, seniority),
            )

            for touch_number in range(1, TOUCHES_PER_CONTACT + 1):
                send_id += 1
                sent_at = START_DATE + timedelta(
                    days=(touch_number - 1) * DAYS_BETWEEN_TOUCHES
                )
                opened = rng.random() < effects.OPEN_RATE
                replied = opened and rng.random() < effects.reply_probability(
                    seniority, touch_number
                )
                conn.execute(
                    "INSERT INTO sends "
                    "(id, contact_id, touch_number, sent_at, opened, replied) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (send_id, contact_id, touch_number, sent_at.isoformat(),
                     int(opened), int(replied)),
                )

    conn.commit()
    conn.close()
    print(
        f"Generated {company_id} companies, {contact_id} contacts, "
        f"{send_id} sends -> {DB_PATH}"
    )


if __name__ == "__main__":
    build_database(random.Random(SEED))
