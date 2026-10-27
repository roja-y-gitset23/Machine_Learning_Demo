# Bonus: SHAP Explanations for 3 Individual Predictions

**Project:** Customer Churn Prediction (Telco Customer Churn)
**Model explained:** `<best_name>` (chosen model, trained on the training set)
**Data used:** held-out test set (1,409 customers)
**Decision threshold:** `<threshold>` (chosen to catch about 75% of churners)

> How to use this file: run the SHAP cells in the notebook, then replace every `<...>` with your own output. Text in *italics* is example wording to adapt to your real top features.

---

## 1. What SHAP shows

SHAP splits one prediction into the contribution of each feature.

- The **base value** `E[f(X)]` is the model's average output over the data.
- Each bar shows how far one feature moves the prediction away from that average.
- **Red bars push toward churn. Blue bars push toward staying.**
- The base value plus all the bars gives the model's final output `f(x)` for that customer.
- SHAP values are in units of `<probability of churn / log-odds of churn>` (Random Forest = probability, XGBoost and Logistic Regression = log-odds).

---

## 2. The three customers

| Customer type | Test row | Predicted churn probability | Flagged at threshold? | Actual outcome |
|---|---|---|---|---|
| High risk (highest probability) | `<i>` | `<0.xx>` | `<Yes>` | `<Churned / Stayed>` |
| Low risk (lowest probability) | `<i>` | `<0.xx>` | `<No>` | `<Churned / Stayed>` |
| Borderline (closest to threshold) | `<i>` | `<0.xx>` | `<Yes/No>` | `<Churned / Stayed>` |

---

## 3. Customer 1: High risk

![High risk SHAP](images/shap_high_risk.png)

**Profile:** Contract = `<Month-to-month>`, tenure = `<2>` months, InternetService = `<Fiber optic>`, MonthlyCharges = `<85>`, PaymentMethod = `<Electronic check>`

**Top 5 contributions (from the output):**

| Feature | SHAP value | Direction |
|---|---|---|
| `<Contract_Month-to-month>` | `<+0.xx>` | Toward churn |
| `<tenure>` | `<+0.xx>` | Toward churn |
| `<InternetService_Fiber optic>` | `<+0.xx>` | Toward churn |
| `<MonthlyCharges>` | `<+0.xx>` | Toward churn |
| `<PaymentMethod_Electronic check>` | `<+0.xx>` | Toward churn |

**Explanation:** *This customer is on a month-to-month contract, so they can leave at any time without a penalty. They joined very recently, and customers in their first months are the most likely to leave. They also pay a high monthly bill for fiber optic, which is the service type with the highest churn in our data. All the large bars point toward churn and almost nothing pulls the risk down, which is why the model gives a very high probability.*

**Business action:** *Contact this customer first. Offer a discount for moving to a 1-year contract, and add a welcome or check-in call.*

---

## 4. Customer 2: Low risk

![Low risk SHAP](images/shap_low_risk.png)

**Profile:** Contract = `<Two year>`, tenure = `<65>` months, InternetService = `<DSL>`, MonthlyCharges = `<45>`, PaymentMethod = `<Credit card (automatic)>`

**Top 5 contributions (from the output):**

| Feature | SHAP value | Direction |
|---|---|---|
| `<Contract_Two year>` | `<-0.xx>` | Toward staying |
| `<tenure>` | `<-0.xx>` | Toward staying |
| `<MonthlyCharges>` | `<-0.xx>` | Toward staying |
| `<PaymentMethod_Credit card (automatic)>` | `<-0.xx>` | Toward staying |
| `<InternetService_DSL>` | `<-0.xx>` | Toward staying |

**Explanation:** *This customer has a two-year contract and more than five years of history with the company, which are the two strongest signs of loyalty. Their bill is moderate and they pay automatically, which also lowers the risk. The model sees no strong reason to expect churn.*

**Business action:** *No retention spend needed. This is a good customer to target for upgrades or referral offers instead.*

---

## 5. Customer 3: Borderline

![Borderline SHAP](images/shap_borderline.png)

**Profile:** Contract = `<One year>`, tenure = `<20>` months, InternetService = `<Fiber optic>`, MonthlyCharges = `<80>`, PaymentMethod = `<Electronic check>`

**Top 5 contributions (from the output):**

| Feature | SHAP value | Direction |
|---|---|---|
| `<feature 1>` | `<+/-0.xx>` | `<Toward churn / staying>` |
| `<feature 2>` | `<+/-0.xx>` | `<Toward churn / staying>` |
| `<feature 3>` | `<+/-0.xx>` | `<Toward churn / staying>` |
| `<feature 4>` | `<+/-0.xx>` | `<Toward churn / staying>` |
| `<feature 5>` | `<+/-0.xx>` | `<Toward churn / staying>` |

**Explanation:** *The model is torn on this customer. Their one-year contract and some months of tenure pull the risk down, but a high fiber bill and electronic check payment pull it up. The two sides roughly cancel out, so the prediction sits close to the decision threshold. A small change, such as a price increase or a service problem, could tip this customer either way.*

**Business action:** *This is where a cheap, low-cost offer is most worthwhile, for example an autopay discount or a service check-in. Test it with an A/B comparison.*

---

## 6. Summary

| Customer | Main reason for the prediction | Suggested action |
|---|---|---|
| High risk | `<Short contract, short tenure, high fiber bill>` | `<Priority call and contract offer>` |
| Low risk | `<Long contract, long tenure, autopay>` | `<No retention spend>` |
| Borderline | `<Mixed signals>` | `<Low-cost nudge and A/B test>` |

**Consistency with global importance:** The features that matter most for these three customers (`<contract, tenure, internet service, charges, payment method>`) match the top features in the feature importance chart, which suggests the model behaves consistently.

---

## 7. Limitations

- SHAP explains **why the model made a prediction**, not why the customer will actually leave. It shows association, not cause.
- Three customers are only examples. They do not describe the whole customer base. The optional global SHAP summary (`images/shap_summary.png`) gives the overall picture.
- Features that are correlated (for example `tenure`, `TotalCharges` and `avg_spend_per_month`) share credit between them, so one of them can look less important than it really is.
- One-hot categories such as Contract are split across several columns, so each column's contribution looks smaller than the contribution of the whole feature.