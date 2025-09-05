from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "your-secret-key"  # ضروري عشان الـ session

# Supabase config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# --- Register Route ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if response.user:
                flash("✅ Account created! You can now log in.", "success")
                return redirect(url_for("login"))
            else:
                flash("❌ Registration failed. Try again.", "danger")
        except Exception as e:
            flash(str(e), "danger")

    return render_template("register.html")

# --- Login Route ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                session["user"] = email
                return redirect(url_for("report"))
            else:
                flash("❌ Invalid credentials", "danger")
        except Exception as e:
            flash(str(e), "danger")

    return render_template("login.html")

# --- Protected Page (Inventory Report) ---
@app.route("/report")
def report():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("report.html")

# --- Logout ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
