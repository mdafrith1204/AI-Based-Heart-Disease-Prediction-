import sys
import os
import requests
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, redirect, session
from chatbot import get_chatbot_response
from auth import auth_bp
from db import init_db, save_prediction, get_db_connection
from model_utils import load_model_and_scaler, make_prediction

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.register_blueprint(auth_bp)

init_db()

model, scaler = load_model_and_scaler()



@app.route("/")
def index():

    if "user_id" not in session and not session.get("guest"):
        return redirect("/login")

    return render_template("index.html")



@app.route("/guest")
def guest_mode():

    session["guest"] = True
    session["user_id"] = None
    session["username"] = "Guest"

    return redirect("/")



@app.route("/predict", methods=["GET", "POST"])
def predict():

    if request.method == "POST":

        age = float(request.form["age"])
        anaemia = float(request.form["anaemia"])
        cpk = float(request.form["creatinine_phosphokinase"])
        diabetes = float(request.form["diabetes"])
        ef = float(request.form["ejection_fraction"])
        high_bp = float(request.form["high_blood_pressure"])
        platelets = float(request.form["platelets"])
        serum_creatinine = float(request.form["serum_creatinine"])
        serum_sodium = float(request.form["serum_sodium"])
        sex = float(request.form["sex"])
        smoking = float(request.form["smoking"])

        features = [
            age, anaemia, cpk, diabetes, ef,
            high_bp, platelets, serum_creatinine,
            serum_sodium, sex, smoking
        ]

        prediction, probability = make_prediction(model, scaler, features)


        if session.get("user_id") and not session.get("guest"):
            save_prediction(session["user_id"], prediction, probability)

        return render_template(
            "result.html",
            prediction=prediction,
            probability=probability
        )

    return render_template("predict.html")


@app.route("/dashboard")
def dashboard():

    if session.get("guest"):
        return redirect("/")

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT prediction, probability, created_at FROM predictions WHERE user_id=? ORDER BY created_at ASC",
        (session["user_id"],)
    )

    history = cursor.fetchall()
    conn.close()

    total = len(history)
    high = sum(1 for h in history if h[0] == "High Risk")
    low = sum(1 for h in history if h[0] == "Low Risk")

    dates = [h[2] for h in history]
    probabilities = [h[1] for h in history]

    return render_template(
        "dashboard.html",
        history=history,
        total=total,
        high=high,
        low=low,
        dates=dates,
        probabilities=probabilities
    )



@app.route("/chat")
def chat_page():
    return render_template("chatbot.html")


@app.route("/chatbot", methods=["POST"])
def chatbot_api():

    user_message = request.json.get("message", "")
    reply = get_chatbot_response(user_message)

    return jsonify({"reply": reply})


@app.route("/symptoms")
def symptoms():
    return render_template("symptoms.html")


@app.route("/precautions")
def precautions():
    return render_template("precautions.html")


@app.route("/heartfailure")
def heartfailure():
    return render_template("heartfailure.html")


@app.route("/hospitals")
def hospitals_page():

    if "user_id" not in session and not session.get("guest"):
        return redirect("/login")

    return render_template("nearby_hospitals.html")



def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat/2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


@app.route("/nearby-hospitals")
def nearby_hospitals():

    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))

    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:10000,{lat},{lon});
      node["amenity"="clinic"](around:10000,{lat},{lon});
      node["amenity"="laboratory"](around:10000,{lat},{lon});
    );
    out;
    """

    try:

        response = requests.get(overpass_url, params={'data': query}, timeout=15)

        if response.status_code != 200:
            return jsonify({"hospitals": []})

        data = response.json()

    except Exception as e:
        print("Overpass API Error:", e)
        return jsonify({"hospitals": []})

    hospitals = []

    for element in data.get("elements", []):

        tags = element.get("tags", {})

        name = tags.get("name", "Medical Facility")
        facility_type = tags.get("amenity", "medical")
        phone = tags.get("phone", "Contact Hospital")

        distance = calculate_distance(
            lat,
            lon,
            element["lat"],
            element["lon"]
        )

        hospitals.append({
            "name": name,
            "type": facility_type.capitalize(),
            "lat": element["lat"],
            "lon": element["lon"],
            "phone": phone,
            "distance": round(distance, 2)
        })

    hospitals = sorted(hospitals, key=lambda x: x["distance"])

    return jsonify({"hospitals": hospitals})



if __name__ == "__main__":
    app.run(debug=True)