from flask import Blueprint, request, render_template, redirect, session
from db import get_db_connection, create_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user and user["password"] == password:

            session["user_id"] = user["id"]
            session["username"] = user["name"]

            return redirect("/") 

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            create_user(name, email, password)
            return redirect("/login")

        except:
            return render_template("register.html", error="Email already exists")

    return render_template("register.html")

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")