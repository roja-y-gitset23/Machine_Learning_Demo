import joblib
import pandas as pd


def predict_churn(input_csv_path, output_csv_path="predictions.csv"):
    # Load model
    model = joblib.load("churn_model.pkl")

    # Load new data
    new_data = pd.read_csv(input_csv_path)

    # Apply same feature engineering
    df_feat = new_data.copy()
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

    # Predict probabilities
    probabilities = model.predict_proba(df_feat)[:, 1]

    # Save output
    output_df = new_data.copy()
    output_df["Churn_Probability"] = probabilities
    output_df["Predicted_Churn"] = (probabilities >= 0.079).astype(int)

    output_df.to_csv(output_csv_path, index=False)
    print(f"Predictions saved successfully to {output_csv_path}")


if __name__ == "__main__":
    # Example usage (pass your new customer CSV file path here)
    # predict_new.py new_customers.csv
    pass

if __name__ == "__main__":
    # Correct: calling the actual function name 'predict_churn'
    predict_churn("new_customers.csv", "predictions.csv")
