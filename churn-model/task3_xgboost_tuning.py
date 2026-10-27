import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_recall_curve, roc_auc_score, roc_curve
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

# ==========================================
# 1. LOAD DATA & RE-ESTABLISH SPLIT
# ==========================================
url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
df = pd.read_csv(url)

df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
if "customerID" in df.columns:
    df = df.drop(columns=["customerID"])

df["Churn"] = df["Churn"].apply(lambda x: 1 if x == "Yes" else 0)

train_val_df, test_df = train_test_split(
    df, test_size=0.20, random_state=42, stratify=df["Churn"]
)


# ==========================================
# 2. FEATURE ENGINEERING (Consistent with Task 2)
# ==========================================
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


train_val_df = engineer_features(train_val_df)
test_df = engineer_features(test_df)

X_train = train_val_df.drop(columns=["Churn"])
y_train = train_val_df["Churn"]

X_test = test_df.drop(columns=["Churn"])
y_test = test_df["Churn"]

# Calculate scale_pos_weight for XGBoost class imbalance
neg_count = (y_train == 0).sum()
pos_count = (y_train == 1).sum()
scale_pos_weight_val = neg_count / pos_count

# Preprocessing Setup
numeric_features = X_train.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()
categorical_features = X_train.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

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

# ==========================================
# 3. DEFINE MODELS & TUNE TOP 2 MODELS
# ==========================================
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Logistic Regression Baseline
lr_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
    ]
)

# Random Forest Tuning
rf_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(random_state=42)),
    ]
)
rf_params = {
    "classifier__n_estimators": [100, 200, 300],
    "classifier__max_depth": [10, 20, None],
    "classifier__min_samples_split": [2, 5, 10],
}
rf_search = RandomizedSearchCV(
    rf_pipeline,
    param_distributions=rf_params,
    n_iter=5,
    scoring="roc_auc",
    cv=cv,
    random_state=42,
    n_jobs=-1,
)
rf_search.fit(X_train, y_train)
best_rf = rf_search.best_estimator_

# XGBoost Tuning
xgb_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            XGBClassifier(
                scale_pos_weight=scale_pos_weight_val,
                eval_metric="logloss",
                random_state=42,
            ),
        ),
    ]
)
xgb_params = {
    "classifier__n_estimators": [100, 200],
    "classifier__max_depth": [3, 5, 7],
    "classifier__learning_rate": [0.01, 0.1, 0.2],
}
xgb_search = RandomizedSearchCV(
    xgb_pipeline,
    param_distributions=xgb_params,
    n_iter=5,
    scoring="roc_auc",
    cv=cv,
    random_state=42,
    n_jobs=-1,
)
xgb_search.fit(X_train, y_train)
best_xgb = xgb_search.best_estimator_

# ==========================================
# 4. EVALUATE & COMPARE MODELS ON TEST SET
# ==========================================
models = {
    "Logistic Regression": lr_pipeline.fit(X_train, y_train),
    "Tuned Random Forest": best_rf,
    "Tuned XGBoost": best_xgb,
}

comparison_data = []
plt.figure(figsize=(8, 6))

for name, model in models.items():
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    auc = roc_auc_score(y_test, y_pred_proba)
    f1 = f1_score(y_test, y_pred)

    comparison_data.append(
        {"Model": name, "Test ROC-AUC": round(auc, 3), "Test F1": round(f1, 3)}
    )

    # Plot ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})")

plt.plot([0, 1], [0, 1], "k--", label="Random Guess")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve Comparison Across Models")
plt.legend(loc="lower right")
plt.savefig("roc_comparison.png", bbox_inches="tight")
plt.show()

comparison_df = pd.DataFrame(comparison_data)
print("\n=== FINAL MODEL COMPARISON TABLE ===")
print(comparison_df.to_markdown(index=False))
comparison_df.to_markdown("comparison_tables.md", index=False)


# ==========================================
# 5. BUSINESS THRESHOLD OPTIMIZATION (CATCH 75% CHURNERS)
# ==========================================
# Using Tuned XGBoost as the best model
best_model = best_xgb
y_proba_best = best_model.predict_proba(X_test)[:, 1]

precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba_best)
# Find threshold where recall >= 0.75
idx = np.where(recalls >= 0.75)[0][0]
optimal_threshold = thresholds[idx]

print(f"\nOptimal Decision Threshold to catch >=75% churners: {optimal_threshold:.3f}")


# ==========================================
# 6. FEATURE IMPORTANCE VISUALIZATION
# ==========================================
# Extract feature names from preprocessor
cat_encoder = (
    best_model.named_steps["preprocessor"]
    .named_transformers_["cat"]
    .named_steps["onehot"]
)
encoded_cat_features = cat_encoder.get_feature_names_out(categorical_features).tolist()
all_features = numeric_features + encoded_cat_features

importances = best_model.named_steps["classifier"].feature_importances_
feat_imp_df = pd.DataFrame(
    {"Feature": all_features, "Importance": importances}
).sort_values(by="Importance", ascending=False)

# Plot top 10 features
plt.figure(figsize=(10, 6))
top_features = feat_imp_df.head(10)
plt.barh(top_features["Feature"][::-1], top_features["Importance"][::-1], color="teal")
plt.xlabel("Feature Importance Score")
plt.title("Top 10 Feature Importances (Tuned XGBoost)")
plt.savefig("feature_importance.png", bbox_inches="tight")
plt.show()

print("\n--- TOP 5 FEATURES & BUSINESS INTERPRETATION ---")
print(top_features.head(5).to_markdown(index=False))

import joblib

# Save the best tuned model
joblib.dump(best_xgb, "churn_model.pkl")
print("Model successfully saved as churn_model.pkl")