# Import required libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split

# Set visualization style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# ==========================================
# 1. LOAD DATA & INITIAL INSPECTION
# ==========================================
# Using the standard IBM Telco Customer Churn dataset public URL
url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
df = pd.read_csv(url)

print("--- DATA SHAPE ---")
print(df.shape)

print("\n--- DATA TYPES & NON-NULL COUNTS ---")
print(df.info())

print("\n--- MISSING VALUES ---")
print(df.isnull().sum()[df.isnull().sum() > 0])

print(f"\n--- DUPLICATE ROWS ---: {df.duplicated().sum()}")

# Note: TotalCharges has empty strings represented as spaces in this dataset. Let's fix that.
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
print(
    f"Missing values in TotalCharges after conversion: {df['TotalCharges'].isnull().sum()}"
)

print("\n--- CLASS BALANCE (TARGET: Churn) ---")
print(df["Churn"].value_counts(normalize=True) * 100)

# ==========================================
# 2. ASSUMPTIONS & METRIC SELECTION
# ==========================================
"""
ASSUMPTIONS:
1. Customer churn is imbalanced (typically ~26% positive class), requiring metrics robust to class imbalance.
2. 'TotalCharges' contains missing values for new customers (tenure = 0), which can be imputed with 0 or median.
3. Features like 'tenure', 'Contract', and 'MonthlyCharges' will be strong predictors of churn.

METRIC TO OPTIMIZE: ROC-AUC / F1-Score
- We choose ROC-AUC because our dataset is moderately imbalanced, and ROC-AUC evaluates the model's ability to rank-order predictions across all classification thresholds. 
- Alternatively, F1-Score can be used if we prioritize balancing Precision and Recall to minimize false positives (wasted retention budgets) vs. false negatives (lost customers).
"""

# ==========================================
# 3. HOLD OUT 20% TEST SET IMMEDIATELY
# ==========================================
# Drop customerID as it's a unique identifier, not a feature
if "customerID" in df.columns:
    df_model = df.drop(columns=["customerID"])
else:
    df_model = df.copy()

# Split into Train+Val (80%) and Test (20%)
train_val_df, test_df = train_test_split(
    df_model, test_size=0.20, random_state=42, stratify=df_model["Churn"]
)

print(f"\nTrain + Validation set shape: {train_val_df.shape}")
print(f"Test set shape (Locked until final step): {test_df.shape}")

# ==========================================
# 4. EXPLORATORY DATA ANALYSIS (5 CHARTS)
# ==========================================

# Chart 1: Target Variable Distribution (Class Balance)
plt.figure(figsize=(6, 4))
sns.countplot(x="Churn", data=train_val_df, hue="Churn", palette="Set2")
plt.title("Distribution of Customer Churn (Target Variable)")
plt.xlabel("Churn Status")
plt.ylabel("Customer Count")
plt.savefig("eda_1_target_balance.png", bbox_inches="tight")
plt.show()

# Chart 2: Churn Rate by Contract Type
plt.figure(figsize=(8, 5))
sns.countplot(
    x="Contract", hue="Churn", data=train_val_df, palette="Set1"
)
plt.title("Churn Count by Contract Type")
plt.xlabel("Contract Type")
plt.ylabel("Count")
plt.legend(title="Churn")
plt.savefig("eda_2_contract_churn.png", bbox_inches="tight")
plt.show()

# Chart 3: Monthly Charges Distribution by Churn
plt.figure(figsize=(9, 5))
sns.histplot(
    data=train_val_df,
    x="MonthlyCharges",
    hue="Churn",
    element="step",
    common_norm=False,
    palette="muted",
    kde=True,
)
plt.title("Monthly Charges Distribution by Churn Status")
plt.xlabel("Monthly Charges ($)")
plt.ylabel("Density / Count")
plt.savefig("eda_3_monthly_charges.png", bbox_inches="tight")
plt.show()

# Chart 4: Tenure vs Churn (Boxplot)
plt.figure(figsize=(8, 5))
#sns.boxplot(x="Churn", y="tenure", data=train_val_df, palette="Pastel1")
# Change line 114 from:
# sns.boxplot(x="Churn", y="tenure", data=train_val_df, palette="Pastel1")

# To this:
sns.boxplot(
    x="Churn",
    y="tenure",
    data=train_val_df,
    hue="Churn",
    palette="Pastel1",
    legend=False,
)
plt.title("Customer Tenure Length vs. Churn Status")
plt.xlabel("Churn")
plt.ylabel("Tenure (Months)")
plt.savefig("eda_4_tenure_boxplot.png", bbox_inches="tight")
plt.show()

# Chart 5: Churn Rate by Internet Service
plt.figure(figsize=(8, 5))
sns.countplot(
    x="InternetService", hue="Churn", data=train_val_df, palette="Dark2"
)
plt.title("Churn Count by Internet Service Provider Type")
plt.xlabel("Internet Service")
plt.ylabel("Count")
plt.legend(title="Churn")
plt.savefig("eda_5_internet_service.png", bbox_inches="tight")
plt.show()

print(
    "\nEDA complete! All 5 charts have been displayed and saved locally as PNG files for your notebook submission."
)