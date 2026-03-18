import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

file_name = "heart_failure_clinical_records.csv"  
if file_name.endswith(".csv"):
    df = pd.read_csv(file_name)
elif file_name.endswith(".xlsx"):
    df = pd.read_excel(file_name)
else:
    raise ValueError("Use CSV or Excel file only.")

print("\n✅ Dataset loaded successfully!")
print("Columns:", df.columns.tolist())
print("Shape:", df.shape)


target_col = df.columns[-1]   
X = df.drop(target_col, axis=1)
y = df[target_col]
print(f"\nTarget column detected: {target_col}")


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "KNN": KNeighborsClassifier(),
    "SVM": SVC(probability=True, random_state=42),
    "Naive Bayes": GaussianNB()
}
if HAS_XGB:
    models["XGBoost"] = XGBClassifier(eval_metric="logloss", random_state=42)

results = []
best_model = None
best_score = -1

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    metrics = {
        "Model": name,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1 Score": f1_score(y_test, y_pred),
        "ROC-AUC": roc_auc_score(y_test, y_prob) if y_prob is not None else np.nan
    }
    results.append(metrics)

 
    if metrics["Accuracy"] > best_score:
        best_score = metrics["Accuracy"]
        best_model = (name, model)

results_df = pd.DataFrame(results)
print("\n📊 Model Comparison:\n")
print(results_df.sort_values(by="Accuracy", ascending=False))

os.makedirs("models", exist_ok=True)
best_name, best_clf = best_model
joblib.dump(best_clf, "models/best_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")

print(f"\n✅ Best model saved: {best_name} → models/best_model.pkl")
print("✅ Scaler saved → models/scaler.pkl")
