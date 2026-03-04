# 🎯 Nemotron Personas USA - Data Analysis Project

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Dataset](https://img.shields.io/badge/Dataset-1M_Records-green.svg)](https://huggingface.co/datasets/nvidia/Nemotron-Personas-USA)
[![Accuracy](https://img.shields.io/badge/Model_Accuracy-88.47%25-orange.svg)]()

## 📊 Overview
Comprehensive data science analysis of the NVIDIA Nemotron-Personas-USA dataset containing 1 million synthetic personas. This project applies advanced text analytics, machine learning clustering, and statistical modeling to uncover meaningful patterns and actionable insights.

## 🎉 Key Results
- ✅ **100% Data Completeness** across 1M records
- 🎯 **10 Distinct Life-Stage Clusters** discovered through unsupervised learning
- 📈 **88.47% Model Accuracy** for persona classification
- 🔤 **354+ Unique Terms** identified through TF-IDF analysis
- 📊 **Highly Significant Age-Cluster Correlation** (F-stat: 248,794, p < 0.0001)

📖 **[View Detailed Results →](ANALYSIS_RESULTS.md)**

## 📁 Project Structure
```
Nemotron_Personas_USA/
│
├── nemotron_analysis.ipynb    # Main analysis notebook with all code
├── ANALYSIS_RESULTS.md         # Comprehensive results documentation
├── ALGORITHMS_EXPLAINED.md     # Technical methodology explanations
├── PROJECT_SUMMARY.md          # Executive summary
├── QUICKSTART.md               # Quick start guide
├── requirements.txt            # Python dependencies
└── myenv/                      # Virtual environment
```

## 🚀 Quick Start

### Installation
```bash
# Create virtual environment
python -m venv myenv

# Activate environment (Windows)
myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage
Open and run `nemotron_analysis.ipynb` in Jupyter Lab or VS Code with Jupyter extension.

## 🎯 Analysis Components

### 1. Data Exploration
- Dataset statistics and quality assessment
- Distribution analysis across 23 features
- Missing value detection and duplicate checking

### 2. Text Mining & NLP
- TF-IDF vectorization for term importance
- Word cloud generation for visual analysis
- Keyword co-occurrence network analysis
- 354+ distinctive terms identified

### 3. Clustering Analysis
- K-Means clustering with elbow method optimization
- UMAP dimensionality reduction for visualization
- 10 distinct persona clusters identified
- Cluster characterization with top keywords

### 4. Statistical Analysis
- ANOVA testing for age-cluster correlation
- Chi-square tests for categorical associations
- Cramér's V for association strength measurement
- Strong education-field coupling discovered (V=0.447)

### 5. Machine Learning
- Random Forest classifier for cluster prediction
- 88.47% testing accuracy achieved
- Feature importance analysis revealing key predictors
- Cross-validation for model generalization

### 6. Visualization
- Interactive Plotly dashboards
- Word clouds for text features
- UMAP cluster projections
- Feature importance charts
- Executive summary dashboard

## 🔍 Key Findings

### Life-Stage Based Segmentation
The clustering algorithm naturally discovered age-based segments:
- **Cluster 0:** Retired/Seniors (avg age 71) - *retired, community, volunteer*
- **Cluster 1:** Mid-Career Professionals (35) - *leverages, meticulous, expertise*
- **Cluster 2:** Young Aspirants (19) - *aspiring, digital, blends*
- **Cluster 3:** Mid-Career Explorers (35) - *blends, curiosity, practical*
- **Cluster 4:** Veteran Professionals (59) - *veteran, decades, experience*
- **Cluster 5:** Young Children (8) - *lego, budding, building*
- **Cluster 6:** Seasoned Experts (51) - *seasoned, leverages, decades*
- **Cluster 7:** Competitive Mid-Career (39) - *drive, competitive, leverages*
- **Cluster 8:** Safety/Technical Experts (46) - *safety, expertise, meticulous*
- **Cluster 9:** Pre-Teens (11) - *budding, curiosity, future*

### Top TF-IDF Terms
1. **meticulous** (0.094) - Precision-oriented individuals
2. **leverages** (0.094) - Strategic skill application
3. **curiosity** (0.087) - Learning-oriented personas
4. **expertise** (0.077) - Domain specialists
5. **community** (0.069) - Socially engaged individuals

### Strongest Keyword Associations
- **leverages + meticulous:** 132,854 co-occurrences
- **leverages + expertise:** 115,487 co-occurrences
- **curiosity + practical:** 76,371 co-occurrences

## 🛠️ Technologies Used
- **Python 3.x** - Primary programming language
- **pandas & numpy** - Data manipulation and numerical computing
- **scikit-learn** - Machine learning (K-Means, Random Forest, TF-IDF)
- **umap-learn** - Dimensionality reduction and visualization
- **plotly** - Interactive visualizations
- **matplotlib** - Static visualizations
- **wordcloud** - Text visualization
- **nltk** - Natural language processing
- **scipy** - Statistical analysis
- **datasets (Hugging Face)** - Dataset loading

## 📖 Documentation
- **[ANALYSIS_RESULTS.md](ANALYSIS_RESULTS.md)** - Full analysis results with visualizations
- **[ALGORITHMS_EXPLAINED.md](ALGORITHMS_EXPLAINED.md)** - Technical methodology
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Executive summary
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide

## 🎯 Strategic Recommendations
1. **Segmentation Strategy:** Utilize 10 clusters for personalized targeting
2. **Text Mining:** Leverage keyword insights for content creation
3. **Model Deployment:** Implement Random Forest for real-time classification
4. **Pattern Monitoring:** Track keyword trends over time
5. **Feature Engineering:** Create derived features from associations

## 📊 Dataset Information
- **Source:** [NVIDIA Nemotron-Personas-USA](https://huggingface.co/datasets/nvidia/Nemotron-Personas-USA)
- **Records:** 1,000,000 synthetic personas
- **Features:** 23 (22 text, 1 numeric)
- **Quality:** 100% complete, no missing values
- **Size:** ~13.5 GB in memory

## 🤝 Contributing
This is an analysis project. For questions or collaboration opportunities, please reach out.

## 📝 License
This project analyzes publicly available data from NVIDIA's Nemotron-Personas-USA dataset.

## 📧 Contact
**Analyst:** LucyDev256  
**Completed:** March 4, 2026

---

⭐ **If you find this analysis useful, please consider starring this repository!**
