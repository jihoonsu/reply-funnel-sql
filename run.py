"""Run the whole thing: build the database, then write the report.

One command, no setup beyond Python 3 — sqlite3 is in the standard library.
"""

import generate
import report


def main() -> None:
    print("generating synthetic data...")
    for entity, n in generate.build().items():
        print(f"  {entity:<10} {n:>7,}")
    print("writing report...")
    report.main()


if __name__ == "__main__":
    main()
