# Payment Fraud Detection

Detect fraudulent transactions from a large-scale financial dataset using LightGBM and XGBoost with automated hyperparameter tuning via Optuna. Built with a full SQL-based data pipeline and GPU-accelerated training.

---

## Results

| Metric | Score |
|--------|-------|
| Best Model | LightGBM |
| Accuracy | *(paste your value from `study.best_value`)* |
| AUC Score | *(paste from `roc_auc_score` output)* |

> Best model selected automatically by Optuna across 10 trials comparing LightGBM and XGBoost.

---

## Tech Stack

- **Language:** Python, SQL
- **ML Models:** LightGBM, XGBoost
- **Hyperparameter Tuning:** Optuna (10 trials, GPU-accelerated)
- **Database:** SQLite (full EDA run via SQL queries)
- **Data:** Pandas, NumPy
- **Visualization:** Matplotlib, Seaborn
- **Model Saving:** Pickle

---

## Dataset

- **Size:** 1.27M+ financial transactions
- **Source:** PaySim synthetic financial dataset (`PS.csv`)
- **Target:** `isFraud` (binary — 0 or 1)
- **Class imbalance:** Fraud cases represent < 1% of all transactions
- **Features:** `step`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `type`, `isFlaggedFraud`

> Dataset not included due to size. Download from [Kaggle — PaySim Financial Dataset](https://www.kaggle.com/datasets/ealaxi/paysim1) and place `PS.csv` in the root directory.

---

## Project Structure

```
payment-fraud-detection/
├── README.md
├── requirements.txt
├── Payment_fraud.ipynb        # Full pipeline notebook
└── lgb_classifier.pkl         # Saved LightGBM model
```

---

## How It Works

**1. Data Cleaning**
- Removed duplicates from 1.27M+ rows
- Custom outlier removal using IQR — **fraud rows preserved unconditionally** to prevent data loss on the minority class
- Label encoded transaction `type` column

**2. SQL Database Pipeline**
- Cleaned data loaded into a SQLite database (`fraud_1.db`)
- All EDA queries run directly via SQL — univariate, bivariate, and correlation analysis on 60,000-row samples
- Demonstrates real-world data engineering workflow beyond standard pandas

**3. Exploratory Data Analysis**
- Target variable distribution (fraud vs non-fraud)
- Univariate: `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`
- Bivariate: fraud distribution vs each numeric feature (boxplots)
- Categorical: transaction type vs fraud rate (countplot + barplot)
- Correlation heatmap across all features

**4. Hyperparameter Tuning with Optuna**
- Tuned LightGBM and XGBoost simultaneously in one Optuna study
- `scale_pos_weight` set automatically from class ratio to handle severe imbalance
- GPU-accelerated training (`device="gpu"` for LightGBM, `device="cuda"` for XGBoost)
- Best model selected after 10 trials

**5. Evaluation**
- Confusion matrix
- Classification report (precision, recall, F1-score per class)
- ROC curve + AUC score
- Precision-Recall curve (more informative than ROC for imbalanced data)

---

## How to Run

```bash
# Clone the repo
git clone https://github.com/Rahul107213/payment-fraud-detection
cd payment-fraud-detection

# Install dependencies
pip install -r requirements.txt

# Add dataset
# Download PS.csv from Kaggle and place in root directory

# Run the notebook
jupyter notebook Payment_fraud.ipynb
```

---

## Requirements

```
pandas
numpy
scikit-learn
xgboost
lightgbm
optuna
matplotlib
seaborn
jupyter
```

---

## Key Features

- **SQL-based EDA** — all analysis queries run on SQLite, not just pandas DataFrames
- **Fraud-safe outlier removal** — custom IQR function that never removes fraud rows, preventing silent data leakage
- **GPU training** — LightGBM and XGBoost both configured for GPU acceleration
- **Class imbalance handling** — `scale_pos_weight` computed from actual class ratio and passed to XGBoost automatically
- **Full evaluation suite** — confusion matrix, classification report, ROC-AUC, and Precision-Recall curve
