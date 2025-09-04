from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "your-secret-key"  # غيّرها لقيمة قوية

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

        # تحقق ثابت (للتجربة) ممكن يتغير لاحقاً لمستخدمين Supabase
        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect(url_for("inventory_report"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

# ---------------------------
# صفحة تقرير الجرد
# ---------------------------
@app.route("/report")
def inventory_report():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        response = supabase.table("inventory").select("*").execute()
        data = response.data
    except Exception as e:
        data = []
        print("Error fetching data:", e)

    return render_template("report.html", items=data)

# ---------------------------
# تسجيل الخروج
# ---------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------------------------
# تشغيل التطبيق
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
