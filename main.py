from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # غيّرها لقيمة قوية

# Supabase config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# بيانات الدخول (ممكن تغيرهم أو تجيبهم من قاعدة البيانات لاحقاً)
USERNAME = "admin"
PASSWORD = "1234"


# صفحة تسجيل الدخول
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("report"))
        else:
            return render_template("login.html", error="Username or password is incorrect")

    return render_template("login.html")


# صفحة تسجيل الخروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# صفحة تقرير المخزون
@app.route("/report")
def report():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # جلب البيانات من Supabase
    data = supabase.table("inventory").select("*").execute()
    rows = data.data

    return render_template("report.html", rows=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
