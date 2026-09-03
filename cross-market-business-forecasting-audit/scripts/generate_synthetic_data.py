"""Generate the fictional datasets used by the portfolio notebooks.

The generator is deterministic: rerunning it with the same seed recreates the
CSV files exactly. The records imitate a small multi-market commercial dataset
but do not represent any real company, customer, or transaction.
"""

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 42
CUSTOMERS = 109
FORECAST_YEARS = np.arange(2018, 2026)
SEGMENT_YEARS = np.arange(2020, 2024)


def build_forecasting_data(rng: np.random.Generator) -> pd.DataFrame:
    customer_ids = np.arange(10_001, 10_001 + CUSTOMERS)
    region_codes = rng.choice(
        ["R-NORTH", "R-SOUTH", "R-EAST", "R-WEST"],
        size=CUSTOMERS,
        p=[0.30, 0.25, 0.25, 0.20],
    )
    starting_revenue = rng.lognormal(mean=9.0, sigma=0.42, size=CUSTOMERS)
    customer_growth = np.clip(rng.normal(0.025, 0.035, CUSTOMERS), -0.06, 0.10)

    # Shared annual movements create a realistic mix of trend and volatility.
    year_factor = {
        2018: 1.00,
        2019: 1.04,
        2020: 0.98,
        2021: 1.06,
        2022: 1.03,
        2023: 1.01,
        2024: 0.97,
        2025: 0.56,
    }

    rows: list[dict[str, object]] = []
    for customer_id, region_code, baseline, growth in zip(
        customer_ids, region_codes, starting_revenue, customer_growth
    ):
        for year in FORECAST_YEARS:
            elapsed = year - FORECAST_YEARS[0]
            noise = rng.lognormal(mean=0.0, sigma=0.075)
            revenue = baseline * ((1 + growth) ** elapsed) * year_factor[year] * noise
            rows.append(
                {
                    "Customer ID": int(customer_id),
                    "Region Code": region_code,
                    "Year": int(year),
                    "Revenue": round(float(revenue), 2),
                }
            )

    return pd.DataFrame(rows)


def build_segmentation_data(
    forecast: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    # Revenue is intentionally aligned to the following year in the forecasting
    # file. Notebook 01 detects this offset as a data-quality exercise.
    shifted_revenue = forecast[["Customer ID", "Year", "Revenue"]].copy()
    shifted_revenue["Year"] -= 1
    shifted_revenue = shifted_revenue.rename(columns={"Customer ID": "ID"})
    shifted_revenue = shifted_revenue[
        shifted_revenue["Year"].isin(SEGMENT_YEARS)
    ].copy()

    customer_ids = sorted(shifted_revenue["ID"].unique())
    archetype = {
        customer_id: int(index % 4)
        for index, customer_id in enumerate(customer_ids)
    }
    purchase_centres = {0: 18, 1: 34, 2: 58, 3: 25}

    purchase_counts = []
    for row in shifted_revenue.itertuples(index=False):
        centre = purchase_centres[archetype[row.ID]]
        year_step = int(row.Year - SEGMENT_YEARS[0])
        trend = {0: -1, 1: 2, 2: 1, 3: 0}[archetype[row.ID]] * year_step
        purchase_counts.append(max(2, int(round(rng.normal(centre + trend, 3.0)))))

    shifted_revenue["Number of Purchases"] = purchase_counts
    shifted_revenue["Average Spend"] = (
        shifted_revenue["Revenue"] / shifted_revenue["Number of Purchases"]
    ).round(2)
    shifted_revenue["Geography"] = "Fictional Region"

    return shifted_revenue[
        ["ID", "Year", "Geography", "Revenue", "Number of Purchases", "Average Spend"]
    ].sort_values(["ID", "Year"])


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    rng = np.random.default_rng(SEED)
    forecast = build_forecasting_data(rng)
    segmentation = build_segmentation_data(forecast, rng)

    forecast.to_csv(data_dir / "forecasting.csv", index=False)
    segmentation.to_csv(data_dir / "segmentation.csv", index=False)

    print(f"Created {len(forecast):,} forecasting rows")
    print(f"Created {len(segmentation):,} segmentation rows")


if __name__ == "__main__":
    main()
