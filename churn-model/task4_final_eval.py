import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

# 1. Load data & re-split to get the exact test set
url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
df = pd.read_csv(url)

df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
if "customerID" in df.columns:
    df = df.drop(columns=["customerID"])
df["Churn"] = df["Churn"].apply(lambda x: 1 if x == "Yes" else 0)

train_val_df, test_df = train_test_split(
    df, test_size=0.20, random_state=42, stratify=df["Churn"]
)


# Feature Engineering function (same as previous tasks)
def engineer_features(data):
    df_feat = data.copy()
    df_feat["TenureGroup"] = pd.cut(
        df_feat["tenure"],
        bins=[-1, 12, 24, 48, 60, 100],
        labels=["0-1 yr", "1-2 yrs", "2-4 yrs", "4-5 yrs", "5+ yrs"],
    ).astype(str)

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
    df_feat["TotalToMonthlyRatio"] = df_feat["TotalCharges"] / (
        df_feat["MonthlyCharges"] + 1
    )
    df_feat["AvgChargePerMonth"] = df_feat["TotalCharges"] / (
        df_feat["tenure"] + 1
    )
    return df_feat


test_df_feat = engineer_features(test_df)
X_test = test_df_feat.drop(columns=["Churn"])
y_test = test_df_feat["Churn"]

# 2. Retrain or load best model (using XGBoost pipeline setup from Task 3)
# For simplicity, we assume best_xgb is trained or you can load it if saved.
# Let's save the model pipeline as 'churn_model.pkl' from your Task 3 script.
# (Make sure you ran joblib.dump(best_xgb, 'churn_model.pkl') in Task 3)

'''try:
    best_model = joblib.load("churn_model.pkl")
except:
    print(
    "Please ensure 'churn_model.pkl' is saved from your Task 3 training script."
)'''
import os
import joblib

# 2. Load the saved best model
model_path = 'churn_model.pkl'

if os.path.exists(model_path):
    best_model = joblib.load(model_path)
    print("Model 'churn_model.pkl' loaded successfully!")
else:
    raise FileNotFoundError(
        f"'{model_path}' not found. Please run your Task 3 script with joblib.dump(best_xgb, 'churn_model.pkl') first."
    )

# 3. Final Test Evaluation using optimized threshold (~0.079 from Task 3)
THRESHOLD = 0.079
y_proba = best_model.predict_proba(X_test)[:, 1]
y_pred = (y_proba >= THRESHOLD).astype(int)

test_auc = roc_auc_score(y_test, y_proba)
test_f1 = f1_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

print(f"--- FINAL HELD-OUT TEST RESULTS ---")
print(f"Test ROC-AUC: {test_auc:.3f}")
print(f"Test F1-Score: {test_f1:.3f}")
print(f"Confusion Matrix:\n{conf_matrix}")