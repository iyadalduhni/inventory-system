from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Supabase config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# ------------------- ROUTES -------------------

# Redirect root to login
@app.route("/")
def home():
    return redirect(url_for("login"))

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            auth_res = supabase.auth.sign_up({"email": email, "password": password})
            if auth_res.user:
                return redirect(url_for("login"))
            else:
                return render_template("register.html", error="Registration failed.")
        except Exception as e:
            return render_template("register.html", error=str(e))

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            auth_res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if auth_res.user:
                session["user"] = auth_res.user.email
                return redirect(url_for("report"))
            else:
                return render_template("login.html", error="Invalid credentials.")
        except Exception as e:
            return render_template("login.html", error=str(e))

    return render_template("login.html")

# Report (protected)
@app.route("/report")
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    # Example query from a table named "inventory"
    try:
        data = supabase.table("inventory").select("*").execute()
        rows = data.data if data else []
    except Exception as e:
        rows = []
        print("Error fetching report:", e)

    return render_template("report.html", user=session["user"], rows=rows)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ------------------- RUN -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
