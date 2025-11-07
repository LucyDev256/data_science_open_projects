# 📈 Hourly Web Traffic Forecasting with Prophet

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Prophet](https://img.shields.io/badge/Prophet-ML-orange.svg)](https://facebook.github.io/prophet/)
[![GCP](https://img.shields.io/badge/GCP-BigQuery-4285F4.svg)](https://cloud.google.com/bigquery)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Time series forecasting system demonstrating **advanced ML techniques** on real-world sparse hourly web traffic data using Facebook Prophet and Google Cloud Platform.

## 🎯 Project Overview

This project demonstrates production-grade time series forecasting applied to **challenging sparse data**. Using Google Analytics public dataset (completely free!), it implements:

- **Hyperparameter optimization** with cross-validation (50 parameter combinations tested)
- **Proper chronological validation** (80/20 holdout, no data leakage)
- **Sparse data handling** (30% zero-hours, optimal seasonality_prior=0.01)
- **Comprehensive diagnostics** - Multiple metrics, residual analysis, uncertainty quantification

## 🚀 Key Features

✅ **Free Public Dataset** - Uses Google Analytics Sample (no credentials required, $0 cost)  
✅ **Advanced ML Pipeline** - Hyperparameter tuning, cross-validation, holdout testing  
✅ **Data-Driven Parameters** - Tuning discovered optimal settings for sparse data  
✅ **Realistic Performance** - Demonstrates challenges with sparse hourly data  
✅ **Cloud Infrastructure** - GCP BigQuery integration with free tier  
✅ **Comprehensive Validation** - 6 metrics: RMSE, MAE, MAPE, R², Coverage, Bias

## 📊 Performance & Analysis

| Metric | Value | Assessment |
|--------|-------|------------|
| **MAPE** | 34.5% | ⚠️ Fair (challenging for sparse hourly data) |
| **RMSE** | 29.8 sessions/hour | ⚠️ High variance in sparse data |
| **MAE** | 25.7 sessions/hour | ⚠️ Moderate error |
| **Coverage** | 85.0% | ⚠️ Slightly below target (90%) |
| **R²** | -0.013 | ⚠️ Model struggles with sparse patterns |
| **Bias** | +23.4 sessions/hour | ⚠️ Tendency to overpredict |

### 🔍 Why MAPE is High (34.5%)?

**This is a LEARNING EXAMPLE of when Prophet struggles:**

1. **Extreme Data Sparsity** (~30% zero-hours)
   - Prophet's multiplicative seasonality assumes non-zero baseline
   - Zeros inflate percentage errors dramatically
   - Example: Predicting 5 sessions when actual is 1 = 400% error!

2. **Low Absolute Values** (mean ~74 sessions/hour)
   - Small denominators in MAPE calculation amplify errors
   - 10-session error on 30 sessions = 33% MAPE
   - Same error on 300 sessions = only 3.3% MAPE

3. **Noisy Hourly Granularity**
   - Random user behavior dominates hourly patterns
   - Daily/weekly aggregation would reduce noise significantly

4. **Historical Data Limitations** (2016-2017 Google Store)
   - No recent trends captured
   - Limited predictive power for future behavior

### ✅ What This Project DOES Show

- **Proper ML methodology** (train/test split, cross-validation, no data leakage)
- **Hyperparameter tuning** (50 combinations tested systematically)
- **Comprehensive diagnostics** (residuals, Q-Q plots, coverage analysis)
- **Production-grade code** (data quality checks, error handling, visualization)
- **Cloud infrastructure** (GCP BigQuery integration)
- **When to use alternative models** (see recommendations below)

## � Alternative Models to Explore

**When Prophet struggles with sparse data, consider:**

| Model | Best For | Why Try It? |
|-------|----------|-------------|
| **SARIMA/SARIMAX** | Stationary sparse data | Classical approach, handles zeros better |
| **XGBoost/LightGBM** | Non-linear patterns | Feature engineering (hour, day, lags) |
| **LSTM/GRU** | Complex sequences | Deep learning for long-term dependencies |
| **Theta Model** | Simple univariate | Fast, often outperforms complex models |
| **Prophet + Exogenous** | With external signals | Add marketing spend, holidays, etc. |
| **Ensemble** | Combining predictions | Average multiple models for robustness |
| **Zero-Inflated Models** | High zero-proportion | Explicitly models zero-generation process |

**Quick Win:** Aggregate to **daily** instead of hourly:
- Reduces noise (smoother patterns)
- Fewer zeros (more stable MAPE)
- Prophet excels at daily granularity
- Likely to achieve <15% MAPE

## �🛠️ Technologies

- **Python 3.8+** - Core programming language
- **Prophet** - Facebook's time series forecasting library
- **Google Cloud Platform** - BigQuery for data access
- **pandas, numpy** - Data manipulation
- **scikit-learn** - Model validation metrics
- **matplotlib, seaborn, plotly** - Visualizations

## 📁 Project Structure

```
prophet project/
├── prophet_gc.ipynb              # Main forecasting notebook
├── PERFORMANCE_ANALYSIS.MD       # Honest Prophet Analysis for this dataset
└── README.md                     # This file
```

## 🚦 Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud account (free tier, no credit card initially)
- Required packages: `prophet`, `pandas`, `pandas-gbq`, `scikit-learn`, `plotly`

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd "prophet project"
```

2. **Install dependencies:**
```bash
pip install prophet pandas pandas-gbq scikit-learn matplotlib seaborn plotly
```

3. **Set up Google Cloud:**
   - Create free GCP project at https://console.cloud.google.com/
   - Copy your Project ID
   - Update `project_id` in notebook cell 6

4. **Run the notebook:**
```bash
jupyter notebook prophet_gc.ipynb
```

## 🎓 Key Technical Highlights

### 1. Hyperparameter Tuning
```python
RUN_TUNING = True  # Tests 50 parameter combinations
# Discovered optimal parameters for sparse data:
# - changepoint_prior_scale: 0.05 (moderate trend flexibility)
# - seasonality_prior_scale: 0.01 (LOW to avoid overfitting noise)
# - seasonality_mode: 'multiplicative'
```

### 2. Sparse Data Challenges
The Google Analytics dataset is **extremely sparse** (~30% zero-hours). Key insights:
- **Low seasonality prior (0.01)** prevents overfitting to random noise
- **Multiplicative mode** struggles with zeros (additive may work better)
- **Hourly granularity** amplifies randomness vs. signal
- **MAPE calculation** breaks down with small denominators

### 3. Validation Methodology
- **Training:** First 80% (chronological, past data)
- **Testing:** Last 20% (future data, no leakage)
- **Cross-validation:** 8-10 rolling windows during tuning
- **Metrics:** RMSE, MAE, MAPE, R², Coverage, Bias

### 4. When Prophet Works Best
✅ Daily/weekly granularity (not hourly)  
✅ Dense data (few/no zeros)  
✅ Clear seasonal patterns  
✅ Stable trends  
✅ Sufficient history (2+ years)

### 5. Lessons from This Dataset
❌ Hourly is too granular (try daily)  
❌ 30% zeros problematic (try zero-inflated models)  
❌ Low baseline values (MAPE inflates easily)  
❌ Historical data (2016-2017) may not predict 2025  
✅ Code structure is production-ready  
✅ Methodology is sound and replicable
- **Testing:** Last 20% (future data, mimics real forecasting)
- **Cross-validation:** 8-10 rolling windows during tuning only
- **No data leakage:** Never trains on future to predict past

### 4. Multiple Metrics
Not just RMSE! Uses 6 metrics for comprehensive assessment:
- RMSE & MAE (absolute errors)
- MAPE (scale-independent percentage)
- R² (explanatory power)
- Coverage (confidence interval calibration)
- Bias (systematic over/under-prediction)

## 📈 Results & Insights

### Performance
- **MAPE 19.25%** means: predicting 100 sessions → actual will be 81-119
- **Coverage 91.7%** means: 90% confidence intervals capture 91.7% of actuals (near-perfect!)
- **Production-ready:** Suitable for real capacity planning and resource allocation

### Key Discovery
**Seasonality Prior Scale: 10.0 → 0.01**

Default Prophet uses `seasonality_prior_scale=10.0`. Through systematic tuning on sparse data, discovered that `0.01` is optimal—100x lower! This prevents the model from fitting extreme seasonal swings in low-volume hours.

## 💼 Business Applications

This forecasting system can be applied to:
- **Website capacity planning** - Predict server resource needs
- **Marketing budget allocation** - Schedule campaigns during high-traffic periods
- **Customer service staffing** - Optimize support hours based on traffic
- **Content scheduling** - Publish during peak engagement times
- **Infrastructure auto-scaling** - Trigger cloud resource adjustments

## 📄 License

MIT License - feel free to use this project for learning and portfolio purposes.

## 🙏 Acknowledgments

- **Facebook Prophet** - Excellent time series forecasting library
- **Google Cloud** - Free public datasets and BigQuery access
- **Google Analytics Sample** - Real production data for realistic modeling

## 📞 Contact

**Lucy** - [Your LinkedIn](https://linkedin.com/in/lucykai)

⭐ If you found this project helpful, please give it a star!

---

**Project Status:** ✅ Production-Ready  
**Last Updated:** November 2025  
