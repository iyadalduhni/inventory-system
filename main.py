from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")

# Supabase Config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


# ========== ROUTES ==========

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("report"))
    return redirect(url_for("login"))


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if response.user:
                flash("Account created successfully! Please login.", "success")
                return redirect(url_for("login"))
            else:
                flash("Registration failed. Try another email.", "danger")
        except Exception as e:
            flash(str(e), "danger")

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                session["user"] = response.user.email
                return redirect(url_for("report"))
            else:
                flash("Invalid credentials!", "danger")
        except Exception as e:
            flash(str(e), "danger")

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# ---------- REPORT ----------
@app.route("/report")
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        data = supabase.table("inventory").select("*").execute()
        items = data.data
    except Exception as e:
        items = []
        flash(str(e), "danger")

    return render_template("report.html", items=items)


# ========== START ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
