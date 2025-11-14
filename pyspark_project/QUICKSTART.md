# 🚀 Quick Start Guide

## Setup Your PySpark Healthcare Analytics Project

This guide will get you from zero to running PySpark on GCP in 15 minutes.

---

## 📋 Prerequisites

✅ **Python 3.8+** installed  
✅ **Google Cloud Account** (free tier works)  
✅ **Git** installed  
✅ **Basic terminal knowledge**

---

## 🔧 Step 1: Install Dependencies (5 minutes)

### Install Python packages:
```bash
cd pyspark_project
pip install -r requirements.txt
```

This installs:
- PySpark 3.5.0 (big data processing)
- Google Cloud libraries (BigQuery, Storage, Dataproc)
- Jupyter (notebooks)
- Pandas, NumPy (data manipulation)
- Matplotlib, Seaborn (visualization)

---

## ☁️ Step 2: Setup Google Cloud (5 minutes)

### Install Google Cloud SDK:

**Windows:**
```powershell
# Download from: https://cloud.google.com/sdk/docs/install
# Or use PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

**Mac/Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Initialize gcloud:
```bash
gcloud init
```

Follow prompts to:
1. Login to your Google account
2. Select or create a project
3. Select default region (recommend: `us-central1`)

### Authenticate for local development:
```bash
gcloud auth application-default login
```

This allows your local code to access BigQuery and Cloud Storage.

---

## 🗂️ Step 3: Create GCP Resources (3 minutes)

### Option A: Use automated script (recommended):
```bash
# Edit scripts/setup_gcp.sh first - change PROJECT_ID
bash scripts/setup_gcp.sh
```

### Option B: Manual setup:
```bash
# Set your project
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable dataproc.googleapis.com

# Create storage bucket
gsutil mb -l us-central1 gs://$PROJECT_ID-healthcare-data

# Create BigQuery dataset
bq mk --location=US healthcare_processed
```

---

## ⚙️ Step 4: Configure Project (2 minutes)

### Edit `config/gcp_config.yaml`:
```yaml
project:
  id: your-gcp-project-id  # CHANGE THIS
  region: us-central1

storage:
  bucket: your-healthcare-bucket  # CHANGE THIS
```

### Edit `config/spark_config.yaml`:
```yaml
cluster:
  project_id: your-gcp-project-id  # CHANGE THIS
```

---

## 🧪 Step 5: Test Installation (2 minutes)

### Test local PySpark:
```bash
python -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.master('local[*]').getOrCreate(); print(f'✅ PySpark {spark.version} works!'); spark.stop()"
```

### Test BigQuery connection:
```python
python -c "
from google.cloud import bigquery
client = bigquery.Client()
query = 'SELECT COUNT(*) as count FROM \`bigquery-public-data.cms_synthetic_patient_data_omop.person\`'
result = client.query(query).to_dataframe()
print(f'✅ BigQuery works! Found {result[\"count\"][0]:,} patients')
"
```

---

## 🎯 Step 6: Run First Notebook

```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

This notebook will:
1. Create Spark session with BigQuery connector
2. Load 10,000 synthetic patients from GCP
3. Load 50,000 hospital encounters
4. Join and analyze the data
5. Calculate patient statistics
6. Visualize results

---

## 🚨 Troubleshooting

### "Permission denied" errors:
```bash
# Re-authenticate
gcloud auth application-default login
gcloud auth login
```

### "Module not found" errors:
```bash
# Reinstall packages
pip install --upgrade -r requirements.txt
```

### "Project not found" errors:
- Make sure you updated `config/gcp_config.yaml` with your project ID
- Check: `gcloud config get-value project`

### PySpark won't start:
```bash
# Check Java is installed (required for Spark)
java -version

# If not, install:
# Windows: https://adoptium.net/
# Mac: brew install openjdk@11
# Linux: sudo apt-get install openjdk-11-jdk
```

---

## 📊 What's Next?

After the quick start, explore:

1. **Feature Engineering** - Create ML features from patient data
2. **Model Training** - Build readmission prediction model
3. **Deploy to Dataproc** - Run on GCP cluster (100x faster)
4. **Production Pipeline** - Automate with Cloud Composer

---

## 📚 Resources

- **PySpark Docs**: https://spark.apache.org/docs/latest/api/python/
- **BigQuery Docs**: https://cloud.google.com/bigquery/docs
- **Synthea Data**: https://synthetichealth.github.io/synthea/
- **GCP Free Tier**: https://cloud.google.com/free

---

## 💡 Tips

**Cost Optimization:**
- Use **sample data** (LIMIT 10000) during development
- **Stop Dataproc clusters** when not in use
- Use **spot instances** (70% cheaper)
- **Delete old data** from Cloud Storage

**Performance:**
- **Partition** large tables by date
- Use **Parquet** format (10x faster than CSV)
- **Cache** frequently used DataFrames
- Use **broadcast joins** for small tables

---

## ✅ Verification Checklist

Before moving to production, verify:

- [ ] Python packages installed (`pip list | grep pyspark`)
- [ ] gcloud CLI authenticated (`gcloud auth list`)
- [ ] GCS bucket created (`gsutil ls`)
- [ ] BigQuery dataset created (`bq ls`)
- [ ] Config files updated with project ID
- [ ] Can connect to BigQuery public data
- [ ] Jupyter notebook runs successfully
- [ ] PySpark session starts locally

---

## 🎉 You're Ready!

Your PySpark healthcare analytics environment is ready. Start with:

```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

Happy analyzing! 🏥📊🚀
