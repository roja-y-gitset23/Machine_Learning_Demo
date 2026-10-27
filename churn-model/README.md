# Customer Churn Prediction Pipeline - Final Report

## 1. Problem Statement
Customer attrition severely impacts recurring revenue in the telecom sector. The objective is to proactively identify high-risk customers to target with retention campaigns.

## 2. Data Overview
- **Dataset**: IBM Telco Customer Churn (7,043 rows, 21 initial columns).
- **Target**: Churn (Yes/No), with a class imbalance of ~26.5% positive class.
- **Split**: 80% Train/Validation, 20% Held-out Test Set (locked).

## 3. Methodology & Modeling
- **Preprocessing**: ColumnTransformer handling missing values (median imputation for numerical, constant for categorical) and OneHotEncoding.
- **Feature Engineering**: Added `TenureGroup`, `ServiceCount`, `TotalToMonthlyRatio`, and `AvgChargePerMonth`.
- **Models Evaluated**: Logistic Regression, Tuned Random Forest, and Tuned XGBoost (using `scale_pos_weight` for class imbalance).

## 4. Results
| Model | Test ROC-AUC | Test F1 |
| :--- | :--- | :--- |
| Logistic Regression | 0.846 | 0.587 |
| Tuned Random Forest | 0.839 | 0.571 |
| Tuned XGBoost | 0.844 | 0.636 |

- **Selected Model**: Tuned XGBoost (highest F1-score of 0.636).
- **Threshold Tuning**: Adjusted decision threshold to $0.079$ to catch $\ge 75\%$ of actual churners.

## 5. Limitations
- Model relies heavily on contract type, meaning customers on month-to-month plans skew predictions regardless of satisfaction scores.
- Absence of direct customer support interaction logs or sentiment data.

## 6. Recommendations
1. **Targeted Incentives**: Automatically trigger discount offers or loyalty bonuses for month-to-month fiber optic customers approaching their renewal periods.
2. **Bundle Security Services**: Offer free or discounted online security add-ons to mitigate churn risk in vulnerable segments.