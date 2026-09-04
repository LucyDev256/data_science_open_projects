# Data

The two CSV files in this directory are deterministic, fictional datasets made
for this portfolio case study. They do not describe real customers, markets, or
company performance.

- `forecasting.csv`: annual revenue by fictional customer and regional code,
  2018–2025.
- `segmentation.csv`: annual customer behaviour measures, 2020–2023.

Recreate both files from the project root with:

```bash
python scripts/generate_synthetic_data.py
```

The fixed random seed in the generator makes the files reproducible.
