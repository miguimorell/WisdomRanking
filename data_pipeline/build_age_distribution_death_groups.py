from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POP_CSV = REPO_ROOT / "assets" / "data" / "population-by-age-group.csv"
DEFAULT_OUTPUT = REPO_ROOT / "assets" / "data" / "age_distribution_death_groups.json"

POP_COLUMNS = {
    "Population - Sex: all - Age: 0-4 - Variant: estimates": "0-4",
    "Population - Sex: all - Age: 5-14 - Variant: estimates": "5-14",
    "Population - Sex: all - Age: 15-24 - Variant: estimates": "15-24",
    "Population - Sex: all - Age: 25-64 - Variant: estimates": "25-64",
    "Population - Sex: all - Age: 65+ - Variant: estimates": "65+",
}

POP_GROUP_SPANS = {
    "0-4": 5,
    "5-14": 10,
    "15-24": 10,
    "25-64": 40,
    "65+": 46,
}


def _load_rows(csv_path: Path, entity: str) -> list[dict]:
    rows: list[dict] = []
    with csv_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("Entity") == entity:
                rows.append(row)
    if not rows:
        raise ValueError(f"Entity '{entity}' not found in {csv_path}")
    return rows


def _aligned_population(pop_values: dict[str, float]) -> list[dict]:
    pop_0_4 = pop_values["0-4"]
    pop_5_14 = pop_values["5-14"]
    pop_15_24 = pop_values["15-24"]
    pop_25_64 = pop_values["25-64"]
    pop_65_plus = pop_values["65+"]

    pop_5_9 = pop_5_14 * (5 / POP_GROUP_SPANS["5-14"])
    pop_10_14 = pop_5_14 * (5 / POP_GROUP_SPANS["5-14"])

    pop_15_19 = pop_15_24 * (5 / POP_GROUP_SPANS["15-24"])
    pop_20_24 = pop_15_24 * (5 / POP_GROUP_SPANS["15-24"])

    pop_25_29 = pop_25_64 * (5 / POP_GROUP_SPANS["25-64"])
    pop_30_39 = pop_25_64 * (10 / POP_GROUP_SPANS["25-64"])
    pop_40_49 = pop_25_64 * (10 / POP_GROUP_SPANS["25-64"])
    pop_50_59 = pop_25_64 * (10 / POP_GROUP_SPANS["25-64"])
    pop_60_64 = pop_25_64 * (5 / POP_GROUP_SPANS["25-64"])

    pop_65_69 = pop_65_plus * (5 / POP_GROUP_SPANS["65+"])
    pop_70_79 = pop_65_plus * (10 / POP_GROUP_SPANS["65+"])
    pop_80_89 = pop_65_plus * (10 / POP_GROUP_SPANS["65+"])
    pop_90_99 = pop_65_plus * (10 / POP_GROUP_SPANS["65+"])
    pop_100_110 = pop_65_plus * (11 / POP_GROUP_SPANS["65+"])

    return [
        {"min": 0, "max": 9, "count": int(pop_0_4 + pop_5_9)},
        {"min": 10, "max": 19, "count": int(pop_10_14 + pop_15_19)},
        {"min": 20, "max": 29, "count": int(pop_20_24 + pop_25_29)},
        {"min": 30, "max": 39, "count": int(pop_30_39)},
        {"min": 40, "max": 49, "count": int(pop_40_49)},
        {"min": 50, "max": 59, "count": int(pop_50_59)},
        {"min": 60, "max": 69, "count": int(pop_60_64 + pop_65_69)},
        {"min": 70, "max": 79, "count": int(pop_70_79)},
        {"min": 80, "max": 89, "count": int(pop_80_89)},
        {"min": 90, "max": 99, "count": int(pop_90_99)},
        {"min": 100, "max": 110, "count": int(pop_100_110)},
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build age_distribution with death-group ranges from population CSV",
    )
    parser.add_argument(
        "--population-csv",
        type=Path,
        default=DEFAULT_POP_CSV,
        help="Path to population-by-age-group.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON path",
    )
    parser.add_argument(
        "--entity",
        default="World",
        help="Entity name (e.g. 'World' or 'Spain')",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Target year (default: latest available)",
    )

    args = parser.parse_args()

    rows = _load_rows(args.population_csv, args.entity)
    if args.year is None:
        args.year = max(int(row["Year"]) for row in rows)

    row = next((r for r in rows if int(r["Year"]) == args.year), None)
    if row is None:
        raise ValueError(f"Year {args.year} not found for entity '{args.entity}'")

    pop_values = {label: float(row[col]) for col, label in POP_COLUMNS.items()}
    buckets = _aligned_population(pop_values)

    payload = {
        "updated_at": date.today().isoformat(),
        "buckets": buckets,
    }

    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
