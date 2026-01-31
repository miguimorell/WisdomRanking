from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POP_CSV = REPO_ROOT / "assets" / "data" / "population-by-age-group.csv"
DEFAULT_DEATHS_CSV = REPO_ROOT / "assets" / "data" / "deaths-by-age-group.csv"
RESULTS_DIR = REPO_ROOT / "assets" / "Results"

POP_COLUMNS = {
    "Population - Sex: all - Age: 0-4 - Variant: estimates": "0-4",
    "Population - Sex: all - Age: 5-14 - Variant: estimates": "5-14",
    "Population - Sex: all - Age: 15-24 - Variant: estimates": "15-24",
    "Population - Sex: all - Age: 25-64 - Variant: estimates": "25-64",
    "Population - Sex: all - Age: 65+ - Variant: estimates": "65+",
}

DEATH_COLUMNS = {
    "Deaths - Sex: all - Age: 0-9 - Variant: estimates": "0-9",
    "Deaths - Sex: all - Age: 10-19 - Variant: estimates": "10-19",
    "Deaths - Sex: all - Age: 20-29 - Variant: estimates": "20-29",
    "Deaths - Sex: all - Age: 30-39 - Variant: estimates": "30-39",
    "Deaths - Sex: all - Age: 40-49 - Variant: estimates": "40-49",
    "Deaths - Sex: all - Age: 50-59 - Variant: estimates": "50-59",
    "Deaths - Sex: all - Age: 60-69 - Variant: estimates": "60-69",
    "Deaths - Sex: all - Age: 70-79 - Variant: estimates": "70-79",
    "Deaths - Sex: all - Age: 80-89 - Variant: estimates": "80-89",
    "Deaths - Sex: all - Age: 90-99 - Variant: estimates": "90-99",
    "Deaths - Sex: all - Age: 100+ - Variant: estimates": "100+",
}

POP_GROUP_SPANS = {
    "0-4": 5,
    "5-14": 10,
    "15-24": 10,
    "25-64": 40,
    "65+": 46,
}

POP_GROUP_RANGES = {
    "0-4": (0, 4),
    "5-14": (5, 14),
    "15-24": (15, 24),
    "25-64": (25, 64),
    "65+": (65, 110),
}

DEATH_GROUP_RANGES = {
    "0-9": (0, 9),
    "10-19": (10, 19),
    "20-29": (20, 29),
    "30-39": (30, 39),
    "40-49": (40, 49),
    "50-59": (50, 59),
    "60-69": (60, 69),
    "70-79": (70, 79),
    "80-89": (80, 89),
    "90-99": (90, 99),
    "100+": (100, 110),
}


def _ensure_results_dir() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _save_figure(fig: plt.Figure, filename: str) -> None:
    _ensure_results_dir()
    output_path = RESULTS_DIR / filename
    fig.savefig(output_path, dpi=160, bbox_inches="tight")


def _aligned_population_from_row(pop_row: pd.Series) -> list[float]:
    # Approximate: split larger population groups into death-group ranges
    # using uniform distribution inside each population group.
    pop_values = {label: float(pop_row[col]) for col, label in POP_COLUMNS.items()}

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

    aligned = [
        pop_0_4 + pop_5_9,  # 0-9
        pop_10_14 + pop_15_19,  # 10-19
        pop_20_24 + pop_25_29,  # 20-29
        pop_30_39,  # 30-39
        pop_40_49,  # 40-49
        pop_50_59,  # 50-59
        pop_60_64 + pop_65_69,  # 60-69
        pop_70_79,  # 70-79
        pop_80_89,  # 80-89
        pop_90_99,  # 90-99
        pop_100_110,  # 100+
    ]

    return aligned


def _distribute_deaths_to_pop_groups(deaths_row: pd.Series) -> dict[str, float]:
    # Approximate by distributing deaths uniformly inside each death group
    # and then splitting into population group ranges by overlap length.
    pop_deaths: dict[str, float] = {label: 0.0 for label in POP_GROUP_RANGES}

    for death_col, death_label in DEATH_COLUMNS.items():
        death_min, death_max = DEATH_GROUP_RANGES[death_label]
        death_span = death_max - death_min + 1
        total_deaths = float(deaths_row[death_col])

        for pop_label, (pop_min, pop_max) in POP_GROUP_RANGES.items():
            overlap_min = max(death_min, pop_min)
            overlap_max = min(death_max, pop_max)
            if overlap_min > overlap_max:
                continue
            overlap_span = overlap_max - overlap_min + 1
            pop_deaths[pop_label] += total_deaths * (overlap_span / death_span)

    return pop_deaths


def _load_entity(df: pd.DataFrame, entity: str) -> pd.DataFrame:
    out = df[df["Entity"] == entity].copy()
    if out.empty:
        raise ValueError(f"Entity '{entity}' not found")
    return out


def plot_population_and_deaths(
    population_csv: Path,
    deaths_csv: Path,
    entity: str,
    year: int | None,
    output_suffix: str,
    show: bool,
) -> None:
    pop_df = pd.read_csv(population_csv)
    deaths_df = pd.read_csv(deaths_csv)

    pop_df = _load_entity(pop_df, entity)
    deaths_df = _load_entity(deaths_df, entity)

    if year is None:
        year = int(pop_df["Year"].max())

    pop_row = pop_df[pop_df["Year"] == year].iloc[0]
    deaths_row = deaths_df[deaths_df["Year"] == year].iloc[0]

    pop_values = [pop_row[col] for col in POP_COLUMNS]
    death_values = [deaths_row[col] for col in DEATH_COLUMNS]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].bar(list(POP_COLUMNS.values()), pop_values)
    axes[0].set_title(f"Población por edad ({entity}, {year})")
    axes[0].set_xlabel("Edad")
    axes[0].set_ylabel("Personas")

    axes[1].bar(list(DEATH_COLUMNS.values()), death_values, color="#d95f02")
    axes[1].set_title(f"Muertes por edad ({entity}, {year})")
    axes[1].set_xlabel("Edad")
    axes[1].set_ylabel("Muertes/año")

    plt.tight_layout()
    _save_figure(fig, f"bars_{entity}_{year}{output_suffix}.png")
    if show:
        plt.show()


def plot_death_rate_bars(
    population_csv: Path,
    deaths_csv: Path,
    entity: str,
    year: int | None,
    output_suffix: str,
    show: bool,
) -> None:
    pop_df = pd.read_csv(population_csv)
    deaths_df = pd.read_csv(deaths_csv)

    pop_df = _load_entity(pop_df, entity)
    deaths_df = _load_entity(deaths_df, entity)

    if year is None:
        year = int(pop_df["Year"].max())

    pop_row = pop_df[pop_df["Year"] == year].iloc[0]
    deaths_row = deaths_df[deaths_df["Year"] == year].iloc[0]

    aligned_pop = _aligned_population_from_row(pop_row)
    death_values = [float(deaths_row[col]) for col in DEATH_COLUMNS.keys()]

    rates = [
        death / pop if pop else 0 for death, pop in zip(death_values, aligned_pop)
    ]

    fig = plt.figure(figsize=(8, 4))
    plt.bar(list(DEATH_COLUMNS.values()), rates, color="#1b9e77")
    plt.title(f"Tasa de muerte por edad ({entity}, {year})")
    plt.xlabel("Edad")
    plt.ylabel("Muertes / población")
    plt.tight_layout()
    _save_figure(fig, f"rate_bars_{entity}_{year}{output_suffix}.png")
    if show:
        plt.show()


def plot_death_rate_heatmap(
    population_csv: Path,
    deaths_csv: Path,
    entity: str,
    output_suffix: str,
    show: bool,
) -> None:
    pop_df = pd.read_csv(population_csv)
    deaths_df = pd.read_csv(deaths_csv)

    pop_df = _load_entity(pop_df, entity)
    deaths_df = _load_entity(deaths_df, entity)

    years = sorted(set(pop_df["Year"]) & set(deaths_df["Year"]))
    rates = []

    for year in years:
        pop_row = pop_df[pop_df["Year"] == year].iloc[0]
        deaths_row = deaths_df[deaths_df["Year"] == year].iloc[0]

        aligned_pop = _aligned_population_from_row(pop_row)
        death_values = [float(deaths_row[col]) for col in DEATH_COLUMNS.keys()]

        row_rates = [
            death / pop if pop else 0
            for death, pop in zip(death_values, aligned_pop)
        ]
        rates.append(row_rates)

    rate_df = pd.DataFrame(
        rates,
        index=years,
        columns=list(DEATH_COLUMNS.values()),
    )

    fig = plt.figure(figsize=(8, 6))
    plt.imshow(rate_df.values, aspect="auto", origin="lower")
    plt.colorbar(label="Tasa muertes / población")
    plt.yticks(range(len(years)), years[:: max(1, len(years) // 10)])
    plt.xticks(range(len(rate_df.columns)), rate_df.columns, rotation=45)
    plt.title(f"Tasa de muerte por edad (heatmap) - {entity}")
    plt.tight_layout()
    _save_figure(fig, f"rate_heatmap_{entity}{output_suffix}.png")
    if show:
        plt.show()


def plot_death_rate_surface(
    population_csv: Path,
    deaths_csv: Path,
    entity: str,
    output_suffix: str,
    show: bool,
) -> None:
    pop_df = pd.read_csv(population_csv)
    deaths_df = pd.read_csv(deaths_csv)

    pop_df = _load_entity(pop_df, entity)
    deaths_df = _load_entity(deaths_df, entity)

    years = sorted(set(pop_df["Year"]) & set(deaths_df["Year"]))
    rates = []

    for year in years:
        pop_row = pop_df[pop_df["Year"] == year].iloc[0]
        deaths_row = deaths_df[deaths_df["Year"] == year].iloc[0]

        aligned_pop = _aligned_population_from_row(pop_row)
        death_values = [float(deaths_row[col]) for col in DEATH_COLUMNS.keys()]

        row_rates = [
            death / pop if pop else 0
            for death, pop in zip(death_values, aligned_pop)
        ]
        rates.append(row_rates)

    rate_df = pd.DataFrame(
        rates,
        index=years,
        columns=list(DEATH_COLUMNS.values()),
    )

    x = np.arange(len(rate_df.columns))
    y = np.arange(len(rate_df.index))
    xx, yy = np.meshgrid(x, y)
    zz = rate_df.values

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(xx, yy, zz, cmap="viridis", linewidth=0, antialiased=True)

    ax.set_xticks(x)
    ax.set_xticklabels(rate_df.columns, rotation=45, ha="right")
    ax.set_yticks(y[:: max(1, len(y) // 10)])
    ax.set_yticklabels(rate_df.index[:: max(1, len(y) // 10)])
    ax.set_xlabel("Edad")
    ax.set_ylabel("Año")
    ax.set_zlabel("Tasa muertes / población")
    ax.set_title(f"Tasa de muerte por edad (3D) - {entity}")

    plt.tight_layout()
    _save_figure(fig, f"rate_surface_{entity}{output_suffix}.png")
    if show:
        plt.show()


def plot_population_bucket_comparison(
    population_csv: Path,
    entity: str,
    year: int | None,
    output_suffix: str,
    show: bool,
) -> None:
    pop_df = pd.read_csv(population_csv)
    pop_df = _load_entity(pop_df, entity)

    if year is None:
        year = int(pop_df["Year"].max())

    pop_row = pop_df[pop_df["Year"] == year].iloc[0]

    original_labels = list(POP_COLUMNS.values())
    original_values = [float(pop_row[col]) for col in POP_COLUMNS.keys()]

    aligned_values = _aligned_population_from_row(pop_row)
    aligned_labels = list(DEATH_COLUMNS.values())

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=False)

    axes[0].bar(original_labels, original_values, color="#7570b3")
    axes[0].set_title(f"Población (grupos originales) - {entity}, {year}")
    axes[0].set_xlabel("Edad")
    axes[0].set_ylabel("Personas")

    axes[1].bar(aligned_labels, aligned_values, color="#1b9e77")
    axes[1].set_title(
        f"Población (grupos alineados a muertes) - {entity}, {year}"
    )
    axes[1].set_xlabel("Edad")
    axes[1].set_ylabel("Personas")

    plt.tight_layout()
    _save_figure(fig, f"population_compare_{entity}_{year}{output_suffix}.png")
    if show:
        plt.show()


def plot_death_rate_comparison(
    population_csv: Path,
    deaths_csv: Path,
    entity: str,
    year: int | None,
    output_suffix: str,
    show: bool,
) -> None:
    pop_df = pd.read_csv(population_csv)
    deaths_df = pd.read_csv(deaths_csv)

    pop_df = _load_entity(pop_df, entity)
    deaths_df = _load_entity(deaths_df, entity)

    if year is None:
        year = int(pop_df["Year"].max())

    pop_row = pop_df[pop_df["Year"] == year].iloc[0]
    deaths_row = deaths_df[deaths_df["Year"] == year].iloc[0]

    original_labels = list(POP_COLUMNS.values())
    original_pop = [float(pop_row[col]) for col in POP_COLUMNS.keys()]
    original_deaths = _distribute_deaths_to_pop_groups(deaths_row)
    original_rates = [
        (original_deaths[label] / pop) if pop else 0
        for label, pop in zip(original_labels, original_pop)
    ]

    aligned_labels = list(DEATH_COLUMNS.values())
    aligned_pop = _aligned_population_from_row(pop_row)
    aligned_deaths = [float(deaths_row[col]) for col in DEATH_COLUMNS.keys()]
    aligned_rates = [
        death / pop if pop else 0 for death, pop in zip(aligned_deaths, aligned_pop)
    ]

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=False)

    axes[0].bar(original_labels, original_rates, color="#7570b3")
    axes[0].set_title(
        f"Tasa (buckets originales) - {entity}, {year}"
    )
    axes[0].set_xlabel("Edad")
    axes[0].set_ylabel("Muertes / población")

    axes[1].bar(aligned_labels, aligned_rates, color="#1b9e77")
    axes[1].set_title(
        f"Tasa (buckets alineados a muertes) - {entity}, {year}"
    )
    axes[1].set_xlabel("Edad")
    axes[1].set_ylabel("Muertes / población")

    plt.tight_layout()
    _save_figure(fig, f"rate_compare_{entity}_{year}{output_suffix}.png")
    if show:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot population/death trends")
    parser.add_argument("--population-csv", type=Path, default=DEFAULT_POP_CSV)
    parser.add_argument("--deaths-csv", type=Path, default=DEFAULT_DEATHS_CSV)
    parser.add_argument("--entity", default="World")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument(
        "--mode",
        choices=[
            "bars",
            "rate-bars",
            "heatmap",
            "surface",
            "compare-pop",
            "compare-rate",
        ],
        default="bars",
        help=(
            "bars: distribución por edad, rate-bars: tasa por edad, "
            "heatmap: tasas vs año, surface: 3D, compare-pop: compara buckets, "
            "compare-rate: compara tasas"
        ),
    )
    parser.add_argument(
        "--output-suffix",
        default="",
        help="Sufijo opcional para nombrar los plots guardados",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Guardar sin abrir ventana",
    )

    args = parser.parse_args()

    output_suffix = f"_{args.output_suffix}" if args.output_suffix else ""
    show = not args.no_show

    if args.mode == "bars":
        plot_population_and_deaths(
            population_csv=args.population_csv,
            deaths_csv=args.deaths_csv,
            entity=args.entity,
            year=args.year,
            output_suffix=output_suffix,
            show=show,
        )
    elif args.mode == "rate-bars":
        plot_death_rate_bars(
            population_csv=args.population_csv,
            deaths_csv=args.deaths_csv,
            entity=args.entity,
            year=args.year,
            output_suffix=output_suffix,
            show=show,
        )
    elif args.mode == "heatmap":
        plot_death_rate_heatmap(
            population_csv=args.population_csv,
            deaths_csv=args.deaths_csv,
            entity=args.entity,
            output_suffix=output_suffix,
            show=show,
        )
    elif args.mode == "compare-pop":
        plot_population_bucket_comparison(
            population_csv=args.population_csv,
            entity=args.entity,
            year=args.year,
            output_suffix=output_suffix,
            show=show,
        )
    elif args.mode == "compare-rate":
        plot_death_rate_comparison(
            population_csv=args.population_csv,
            deaths_csv=args.deaths_csv,
            entity=args.entity,
            year=args.year,
            output_suffix=output_suffix,
            show=show,
        )
    else:
        plot_death_rate_surface(
            population_csv=args.population_csv,
            deaths_csv=args.deaths_csv,
            entity=args.entity,
            output_suffix=output_suffix,
            show=show,
        )


if __name__ == "__main__":
    main()
