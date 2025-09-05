from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # غيّرها لقيمة قوية

# Supabase config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# ---------------------------
# صفحة تسجيل الدخول
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # تسجيل دخول عبر Supabase Auth
        try:
            user = supabase.auth.sign_in_with_password(
                {"email": username, "password": password}
            )
            if user:
                session["user"] = username
                return redirect(url_for("report"))
            else:
                error = "Invalid credentials"
        except Exception as e:
            error = f"Login failed: {e}"

    return render_template("login.html", error=error)

# ---------------------------
# صفحة تقرير الجرد
# ---------------------------
@app.route("/report")
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        response = supabase.table("inventory").select("*").execute()
        rows = response.data
    except Exception as e:
        rows = []
        print("Error fetching inventory:", e)

    return render_template("report.html", rows=rows)

# ---------------------------
# تسجيل الخروج
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------------------
# Run محلياً
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
