from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # غيّرها لمفتاح قوي وسري

# إعداد Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# بيانات تسجيل الدخول (مبدئياً ثابتة)
USERNAME = "admin"
PASSWORD = "12345"

# صفحة تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("report"))
        else:
            error = "❌ Invalid username or password"
    return render_template("login.html", error=error)

# تسجيل الخروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# الصفحة الرئيسية (تحويل للـ report)
@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return redirect(url_for("report"))

# صفحة التقرير
@app.route("/report")
def report():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    response = supabase.table("products").select("*").execute()
    products = response.data
    return render_template("report.html", products=products)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
