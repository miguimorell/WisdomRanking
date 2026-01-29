from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from typing import Dict, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POP_CSV = REPO_ROOT / "assets" / "data" / "population-by-age-group.csv"
DEFAULT_DEATHS_CSV = REPO_ROOT / "assets" / "data" / "deaths-by-age-group.csv"
DEFAULT_OUTPUT = REPO_ROOT / "assets" / "data" / "age_distribution.json"

AGE_GROUP_COLUMNS: Dict[str, Tuple[int, int]] = {
    "Population - Sex: all - Age: 0-4 - Variant: estimates": (0, 4),
    "Population - Sex: all - Age: 5-14 - Variant: estimates": (5, 14),
    "Population - Sex: all - Age: 15-24 - Variant: estimates": (15, 24),
    "Population - Sex: all - Age: 25-64 - Variant: estimates": (25, 64),
    "Population - Sex: all - Age: 65+ - Variant: estimates": (65, 110),
}

DEATH_GROUP_COLUMNS: Dict[str, Tuple[int, int]] = {
    "Deaths - Sex: all - Age: 0-9 - Variant: estimates": (0, 9),
    "Deaths - Sex: all - Age: 10-19 - Variant: estimates": (10, 19),
    "Deaths - Sex: all - Age: 20-29 - Variant: estimates": (20, 29),
    "Deaths - Sex: all - Age: 30-39 - Variant: estimates": (30, 39),
    "Deaths - Sex: all - Age: 40-49 - Variant: estimates": (40, 49),
    "Deaths - Sex: all - Age: 50-59 - Variant: estimates": (50, 59),
    "Deaths - Sex: all - Age: 60-69 - Variant: estimates": (60, 69),
    "Deaths - Sex: all - Age: 70-79 - Variant: estimates": (70, 79),
    "Deaths - Sex: all - Age: 80-89 - Variant: estimates": (80, 89),
    "Deaths - Sex: all - Age: 90-99 - Variant: estimates": (90, 99),
    "Deaths - Sex: all - Age: 100+ - Variant: estimates": (100, 110),
}


def _pick_latest_year(rows: list[dict], year: int | None) -> int:
    if year is not None:
        return year
    years = [int(row["Year"]) for row in rows]
    return max(years)


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


def build_from_population_csv(
    pop_csv: Path,
    deaths_csv: Path | None,
    entity: str,
    year: int | None,
    births_per_year: float | None,
) -> dict:
    rows = _load_rows(pop_csv, entity)

    target_year = _pick_latest_year(rows, year)
    row = next((r for r in rows if int(r["Year"]) == target_year), None)
    if row is None:
        raise ValueError(f"Year {target_year} not found for entity '{entity}'")

    buckets = []
    for column_name, (min_age, max_age) in AGE_GROUP_COLUMNS.items():
        raw_value = row.get(column_name)
        if raw_value is None:
            raise ValueError(f"Missing column '{column_name}' in CSV")
        buckets.append(
            {
                "min": min_age,
                "max": max_age,
                "count": int(float(raw_value)),
            }
        )

    payload = {
        "updated_at": date.today().isoformat(),
        "buckets": buckets,
    }

    if births_per_year is not None:
        payload["births_per_year"] = int(births_per_year)

    if deaths_csv is not None and deaths_csv.exists():
        death_rows = _load_rows(deaths_csv, entity)
        death_row = next(
            (r for r in death_rows if int(r["Year"]) == target_year),
            None,
        )
        if death_row is None:
            raise ValueError(
                f"Year {target_year} not found for entity '{entity}' in {deaths_csv}"
            )

        deaths_by_age = []
        for column_name, (min_age, max_age) in DEATH_GROUP_COLUMNS.items():
            raw_value = death_row.get(column_name)
            if raw_value is None:
                raise ValueError(f"Missing column '{column_name}' in deaths CSV")
            deaths_by_age.append(
                {
                    "min": min_age,
                    "max": max_age,
                    "deaths_per_year": int(float(raw_value)),
                }
            )
        payload["deaths_by_age"] = deaths_by_age

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build age_distribution.json from population-by-age-group.csv",
    )
    parser.add_argument(
        "--population-csv",
        type=Path,
        default=DEFAULT_POP_CSV,
        help="Path to population-by-age-group.csv",
    )
    parser.add_argument(
        "--deaths-csv",
        type=Path,
        default=DEFAULT_DEATHS_CSV,
        help="Path to deaths-by-age-group.csv",
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
    parser.add_argument(
        "--births-per-year",
        type=float,
        default=None,
        help="Optional births per year (number)",
    )

    args = parser.parse_args()

    payload = build_from_population_csv(
        pop_csv=args.population_csv,
        deaths_csv=args.deaths_csv,
        entity=args.entity,
        year=args.year,
        births_per_year=args.births_per_year,
    )

    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
