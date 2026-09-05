"""Single entry point: generate the dataset, run the analysis, print the
report. Stdlib only — no pip install required to run this."""

import random
import sqlite3

import generate
import report

if __name__ == "__main__":
    generate.build_database(random.Random(generate.SEED))

    connection = sqlite3.connect(generate.DB_PATH)
    text = report.render(connection)
    connection.close()

    print()
    print(text)
    report.REPORT_PATH.parent.mkdir(exist_ok=True)
    report.REPORT_PATH.write_text(text)
    print(f"\nReport written to {report.REPORT_PATH}")
