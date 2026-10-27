# Import required libraries
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ==========================================
# 1. LOAD DATA & RE-ESTABLISH SPLIT
# ==========================================
url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
df = pd.read_csv(url)

# Clean TotalCharges and target variable
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
if "customerID" in df.columns:
    df = df.drop(columns=["customerID"])

df["Churn"] = df["Churn"].apply(lambda x: 1 if x == "Yes" else 0)

# Maintain the same 80/20 split strategy from Task 1
train_val_df, test_df = train_test_split(
    df, test_size=0.20, random_state=42, stratify=df["Churn"]
)


# ==========================================
# 2. CREATE AT LEAST 4 NEW FEATURES
# ==========================================
def engineer_features(data):
    df_feat = data.copy()

    # Feature 1: Tenure Group (Binned tenure ranges)
    df_feat["TenureGroup"] = pd.cut(
        df_feat["tenure"],
        bins=[-1, 12, 24, 48, 60, 100],
        labels=["0-1 yr", "1-2 yrs", "2-4 yrs", "4-5 yrs", "5+ yrs"],
    ).astype(str)

    # Feature 2: Service Count (Total active optional services)
    service_cols = [
        "PhoneService",
        "MultipleLines",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
    ]
    df_feat["ServiceCount"] = (df_feat[service_cols] == "Yes").sum(axis=1)

    # Feature 3: Total-to-Monthly Charges Ratio
    df_feat["TotalToMonthlyRatio"] = df_feat["TotalCharges"] / (
        df_feat["MonthlyCharges"] + 1
    )

    # Feature 4: Average Charge Per Tenure Month
    df_feat["AvgChargePerMonth"] = df_feat["TotalCharges"] / (
        df_feat["tenure"] + 1
    )

    return df_feat


train_val_df = engineer_features(train_val_df)

# Separate features (X) and target (y)
X = train_val_df.drop(columns=["Churn"])
y = train_val_df["Churn"]

# Identify column data types
numeric_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()
categorical_features = X.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

# ==========================================
# 3. COLUMN TRANSFORMER & PIPELINE SETUP
# ==========================================
numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        (
            "onehot",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
        ),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

'''
# ==========================================
# 4. BASELINE MODELS & 5-FOLD CV
# ==========================================
models = {
    "Logistic Regression": Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    ),
    "Random Forest": Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(n_estimators=100, random_state=42),
            ),
        ]
    ),
}

scoring_metrics = {"roc_auc": "roc_auc", "f1": "f1"}

results = []
for name, model in models.items():
    cv_results = cross_validate(
        model, X, y, cv=5, scoring=scoring_metrics, n_jobs=-1
    )
    mean_auc = cv_results["test_roc_auc"].mean()
    mean_f1 = cv_results["test_f1"].mean()

    results.append(
        {
            "Model": name,
            "CV ROC-AUC": round(mean_auc, 2),
            "CV F1": round(mean_f1, 2),
        }
    )

results_df = pd.DataFrame(results)

# ==========================================
# 5. OUTPUT RESULTS TABLE & SAVE
# ==========================================
print("\n=== FINAL RESULTS TABLE ===")
print(results_df.to_markdown(index=False))

# Save table to markdown for project commit
results_df.to_markdown("comparison_table.md", index=False)
print(
    "\nResults successfully saved to 'comparison_table.md' for your repository commit!"
)
'''
from sklearn.dummy import DummyClassifier

# ==========================================
# 4. BASELINE MODELS & 5-FOLD CV (WITH DUMMY)
# ==========================================
models = {
    "Dummy Classifier (Most Frequent)": Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                DummyClassifier(strategy="most_frequent", random_state=42),
            ),
        ]
    ),
    "Logistic Regression": Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    ),
    "Random Forest": Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(n_estimators=100, random_state=42),
            ),
        ]
    ),
}

scoring_metrics = {"roc_auc": "roc_auc", "f1": "f1"}

results = []
for name, model in models.items():
    cv_results = cross_validate(
        model, X, y, cv=5, scoring=scoring_metrics, n_jobs=-1
    )
    mean_auc = cv_results["test_roc_auc"].mean()
    mean_f1 = cv_results["test_f1"].mean()

    results.append(
        {
            "Model": name,
            "CV ROC-AUC": round(mean_auc, 2),
            "CV F1": round(mean_f1, 2),
        }
    )

results_df = pd.DataFrame(results)

# ==========================================
# 5. OUTPUT RESULTS TABLE & SAVE
# ==========================================
print("\n=== FINAL RESULTS TABLE (WITH DUMMY BASELINE) ===")
print(results_df.to_markdown(index=False))

# Save updated table to markdown
results_df.to_markdown("comparison_table.md", index=False)
print(
    "\nUpdated results successfully saved to 'comparison_table.md' for your commit!"
)