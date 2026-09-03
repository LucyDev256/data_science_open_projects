# Cross-Market Business Forecasting Audit

An end-to-end portfolio case study combining customer revenue forecasting,
behavioural segmentation, promotion-effect estimation, price sensitivity, and
BigQuery customer-order analysis.

All customer records, market labels, product names, and commercial values are
fictional. The repository is designed to demonstrate analytical reasoning and
reproducible implementation—not to represent any real company.

## What this project demonstrates

| Case study | Business question | Methods |
|---|---|---|
| Revenue forecasting and segmentation | How might customer revenue develop, and which behavioural groups emerge? | Per-series linear regression, rolling-origin validation, WAPE, standardization, K-means, transition matrices |
| Promotion-effect audit | How much of an observed sales increase can reasonably be associated with a promotion? | Comparison-market counterfactual, additive robustness check, historical sensitivity range |
| Price-increase audit | Did buyer activity noticeably change after a 3% price increase? | Seasonally matched pre/post comparison, adjusted baseline, Welch t-test, sales-per-buyer context |
| Customer-order SQL audit | Which products drive sales, how do customers enter, and how quickly do they return? | BigQuery CTEs, window functions, `QUALIFY`, `LEAD`, conditional aggregation |

## Selected findings

- Rolling validation exposes a structural-break risk: linear-regression WAPE is
  below 10% in 2022–2024 but rises to 76.5% in the deliberately shocked final
  year. The model is useful as a transparent baseline, not as a production-ready
  forecast.
- A data-quality audit detects that the segmentation revenue labels align
  perfectly only after a one-year shift. The datasets are therefore kept
  separate rather than joined under an unsupported calendar assumption.
- Four working customer segments emerge: high-value/high-spend, growing
  mid-value, frequent lower-basket, and declining lower-value.
- The fictional promotion audit produces a sensitivity range of `$1.1M–$1.7M`
  in incremental sales, while explicitly separating observed growth from causal
  proof and from profit or ROI.
- The fictional price audit estimates 3.3% fewer buyer-months than the adjusted
  expectation. Its exploratory test yields `p ≈ 0.054`, so the evidence is not
  presented as statistically significant or causal.
- The SQL case handles line-level versus order-level grain before sequencing
  first and second purchases, avoiding a common source of duplicated orders.

These findings are illustrative outputs of synthetic data.

## Repository structure

```text
cross-market-business-forecasting-audit/
├── data/
│   ├── forecasting.csv
│   ├── segmentation.csv
│   └── README.md
├── notebooks/
│   ├── 01_revenue_forecasting_and_segmentation.ipynb
│   ├── 02_promotion_effect_audit.ipynb
│   └── 03_price_increase_audit.ipynb
├── outputs/
│   ├── simple_customer_segments_2021_2023.csv
│   ├── simple_forecast_1_year.csv
│   ├── simple_forecast_3_years.csv
│   ├── simple_linear_regression_validation.csv
│   ├── simple_movement_2021_2022.csv
│   └── simple_movement_2022_2023.csv
├── scripts/
│   └── generate_synthetic_data.py
├── sql/
│   └── customer_order_audit_bigquery.sql
├── README.md
└── requirements.txt
```

## Run locally

```bash
git clone https://github.com/LucyDev256/data_science_open_projects.git
cd data_science_open_projects/cross-market-business-forecasting-audit

python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS or Linux
source .venv/bin/activate
```

Install dependencies and start Jupyter:

```bash
python -m pip install -r requirements.txt
jupyter lab
```

Open the notebooks from the project root. Their verified outputs are committed,
so the analysis can also be reviewed directly on GitHub.

To recreate the synthetic CSV files:

```bash
python scripts/generate_synthetic_data.py
```

## Running the SQL case

The SQL file uses BigQuery Standard SQL and includes its own fictional `ORDERS`
data as a temporary table. Open the complete file in the BigQuery editor and run
it as a multi-statement script. The final result sets cover:

1. 2026 sales and share by product line;
2. each customer's first order;
3. customer-level first-to-second-order timing;
4. timing aggregated by the first-purchased product line.

## Analytical boundaries

- Linear regression extrapolates a straight trend and does not model seasonality
  or structural breaks.
- K-means depends on scaling, outliers, and the chosen number of clusters.
- The commercial audits use small aggregate samples and cannot establish causal
  effects without stronger control data or experimental design.
- Revenue lift is not equivalent to contribution margin, profit, or ROI.

The notebooks make these limitations visible because communicating uncertainty
is part of the analytical deliverable.
