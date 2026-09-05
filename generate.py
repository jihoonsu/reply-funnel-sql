"""Build funnel.db from the parameters in effects.py.

Standard library only, and seeded, so the same command always produces the
same database. Nothing here comes from a real campaign — every company, person
and address below is invented, and all domains end in .test, a TLD reserved by
RFC 2606 so it can never resolve to a real site.
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import effects

ROOT = Path(__file__).parent
DB_PATH = ROOT / "funnel.db"
SCHEMA = ROOT / "sql" / "schema.sql"

INDUSTRIES = ["logistics", "healthcare", "manufacturing", "retail", "finance"]

COMPANY_HEAD = [
    "Northwind", "Brightpath", "Cindershore", "Draycott", "Evermoor", "Fernwald",
    "Glasshouse", "Harrowgate", "Ironvale", "Junipero", "Kestrelton", "Lowbridge",
    "Marrowfield", "Norhaven", "Oakcliff", "Pemberton", "Quarrystone", "Redhollow",
]
COMPANY_TAIL = ["Logistics", "Systems", "Holdings", "Labs", "Partners", "Group", "Supply"]

FIRST_NAMES = [
    "Aisha", "Bao", "Camila", "Dmitri", "Elif", "Farhan", "Grete", "Hyun",
    "Ines", "Jarrah", "Kofi", "Lucia", "Mateo", "Nadia", "Oskar", "Priya",
    "Rania", "Souta", "Tomas", "Viktor", "Wren", "Yusuf", "Zofia",
]
LAST_NAMES = [
    "Achterberg", "Baptiste", "Cavalcante", "Drummond", "Eberhardt", "Fontaine",
    "Halvorsen", "Ibarra", "Jorgensen", "Kowalczyk", "Lindqvist", "Moreau",
    "Nakagawa", "Oyelaran", "Petrosyan", "Quiroga", "Sandoval", "Thackeray",
    "Vasquez", "Whitlock", "Yamashita", "Zielinski",
]

CAMPAIGN_START = date(2026, 6, 1)


def build(db_path: Path = DB_PATH, seed: int = effects.SEED) -> dict[str, int]:
    """Create the database and fill it. Returns row counts."""
    rng = random.Random(seed)

    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA.read_text())

    companies = [
        (
            i,
            f"{rng.choice(COMPANY_HEAD)} {rng.choice(COMPANY_TAIL)}",
            rng.choice(INDUSTRIES),
        )
        for i in range(1, effects.N_COMPANIES + 1)
    ]
    conn.executemany("INSERT INTO companies (id, name, industry) VALUES (?, ?, ?)", companies)

    contacts = []
    for i in range(1, effects.N_CONTACTS + 1):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        seniority = (
            "decision_maker"
            if rng.random() < effects.DECISION_MAKER_SHARE
            else "individual_contributor"
        )
        contacts.append((
            i,
            rng.randint(1, effects.N_COMPANIES),
            f"{first.lower()}.{last.lower()}{i}@company{i % effects.N_COMPANIES}.test",
            seniority,
        ))
    conn.executemany(
        "INSERT INTO contacts (id, company_id, email, seniority) VALUES (?, ?, ?, ?)",
        contacts,
    )

    sends = []
    send_id = 1
    for contact_id, _company_id, _email, seniority in contacts:
        # How far into the sequence this contact got. Most sequences stop early,
        # which is why later touches have fewer sends behind them.
        n_touches = rng.choices([1, 2, 3, 4, 5], weights=[18, 24, 24, 20, 14])[0]
        first_day = rng.randint(0, 45)
        for touch in range(1, n_touches + 1):
            sent_on = CAMPAIGN_START + timedelta(days=first_day + (touch - 1) * 4)

            opened = 1 if rng.random() < effects.OPEN_RATE else 0

            replied = 0
            if opened:
                # The two planted effects, and nothing else, decide this.
                p_reply = (
                    effects.BASE_REPLY_RATE_PER_OPEN
                    * effects.SENIORITY_REPLY_MULTIPLIER[seniority]
                    * effects.TOUCH_REPLY_MULTIPLIER[touch]
                )
                replied = 1 if rng.random() < p_reply else 0

            sends.append((send_id, contact_id, touch, sent_on.isoformat(), opened, replied))
            send_id += 1

    conn.executemany(
        "INSERT INTO sends (id, contact_id, touch_number, sent_on, opened, replied) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        sends,
    )

    conn.commit()
    counts = {"companies": len(companies), "contacts": len(contacts), "sends": len(sends)}
    conn.close()
    return counts


def main() -> None:
    for entity, n in build().items():
        print(f"  {entity:<10} {n:>7,}")


if __name__ == "__main__":
    main()
