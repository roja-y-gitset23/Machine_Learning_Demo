import joblib
import pandas as pd
import numpy as np
import shap
from sklearn.model_selection import train_test_split

# 1. Load Data & Re-establish Test Split
url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
df = pd.read_csv(url)

df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
if "customerID" in df.columns:
    df = df.drop(columns=["customerID"])
df["Churn"] = df["Churn"].apply(lambda x: 1 if x == "Yes" else 0)

train_val_df, test_df = train_test_split(df, test_size=0.20, random_state=42, stratify=df["Churn"])

def engineer_features(data):
    df_feat = data.copy()
    df_feat["TenureGroup"] = pd.cut(
        df_feat["tenure"], bins=[-1, 12, 24, 48, 60, 100],
        labels=["0-1 yr", "1-2 yrs", "2-4 yrs", "4-5 yrs", "5+ yrs"]
    ).astype(str)
    
    service_cols = ['PhoneService', 'MultipleLines', 'OnlineSecurity', 'OnlineBackup', 
                    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
    df_feat["ServiceCount"] = (df_feat[service_cols] == "Yes").sum(axis=1)
    df_feat["TotalToMonthlyRatio"] = df_feat["TotalCharges"] / (df_feat["MonthlyCharges"] + 1)
    df_feat["AvgChargePerMonth"] = df_feat["TotalCharges"] / (df_feat["tenure"] + 1)
    return df_feat

test_df_feat = engineer_features(test_df)
X_test = test_df_feat.drop(columns=["Churn"])
y_test = test_df_feat["Churn"].reset_index(drop=True)

# 2. Load Saved Model Pipeline
model = joblib.load("churn_model.pkl")

# Extract Preprocessor and XGBoost Classifier steps
preprocessor = model.named_steps["preprocessor"]
xgb_clf = model.named_steps["classifier"]

# Transform X_test into numeric array using the fitted preprocessor
X_test_transformed = preprocessor.transform(X_test)

# Get feature names after OneHotEncoding
cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
numeric_features = X_test.select_dtypes(include=["int64", "float64"]).columns.tolist()
categorical_features = X_test.select_dtypes(include=["object", "string", "category"]).columns.tolist()
encoded_cat_features = cat_encoder.get_feature_names_out(categorical_features).tolist()
all_features = numeric_features + encoded_cat_features

# 3. Compute SHAP Values using TreeExplainer
explainer = shap.TreeExplainer(xgb_clf)
shap_values = explainer(X_test_transformed)

# 4. Select 3 Specific Customers to Explain
# Customer A: High-risk Churner (True Churn = 1, High Probability)
# Customer B: Loyal Customer (True Churn = 0, Low Probability)
# Customer C: Borderline / Medium Risk Case

y_proba = model.predict_proba(X_test)[:, 1]
indices = {
    "Customer A (High Risk Churner)": np.where(y_test == 1)[0][0],
    "Customer B (Loyal Long-term Customer)": np.where(y_test == 0)[0][0],
    "Customer C (Borderline Case)": np.where((y_proba > 0.4) & (y_proba < 0.6))[0][0] if len(np.where((y_proba > 0.4) & (y_proba < 0.6))[0]) > 0 else 2
}

print("=== SHAP INDIVIDUAL PREDICTION EXPLANATIONS ===\n")

for title, idx in indices.items():
    cust_proba = y_proba[idx]
    cust_actual = y_test.iloc[idx]
    
    print(f"--- {title} (Index: {idx}) ---")
    print(f"Predicted Churn Probability: {cust_proba:.3f} | Actual Churn Status: {cust_actual}")
    
    # Get SHAP values for this specific customer
    cust_shap = shap_values.values[idx]
    feature_contrib = pd.DataFrame({
        "Feature": all_features,
        "SHAP Value": cust_shap,
        "Feature Value": X_test_transformed[idx]
    }).sort_values(by="SHAP Value", key=abs, ascending=False)
    
    print("Top 3 features pushing prediction:")
    print(feature_contrib.head(3).to_markdown(index=False))
    print("\n" + "="*50 + "\n")