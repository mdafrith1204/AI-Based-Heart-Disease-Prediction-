import pickle
import joblib
import numpy as np

def load_model_and_scaler():
    model = pickle.load(open("models/best_model.pkl", "rb"))
    scaler = joblib.load("models/scaler.pkl")
    return model, scaler


def make_prediction(model, scaler, features):
    X = np.array([features])
    X_scaled = scaler.transform(X)

    prediction = model.predict(X_scaled)[0]

    if hasattr(model, "predict_proba"):
        prob = float(model.predict_proba(X_scaled)[0][1]) * 100
    else:
        prob = 50

    result = "High Risk" if prediction == 1 else "Low Risk"
    return result, round(prob, 2)
