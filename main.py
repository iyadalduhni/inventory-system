from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client
import os

# إعداد التطبيق
app = Flask(__name__)

# Supabase config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)


# صفحة تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # تحقق مبدئي (تقدر تغيره لمصادقة حقيقية لاحقًا)
        if username == "admin" and password == "1234":
            return redirect(url_for("report"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


# صفحة التقرير (Inventory Report)
@app.route("/")
def report():
    data = supabase.table("inventory").select("*").execute()
    rows = data.data if data.data else []
    return render_template("report.html", rows=rows)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
