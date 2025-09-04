from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # لازم تغيرها لقيمة أقوى

# Supabase config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


# صفحة تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # مثال بسيط (ممكن تطوره وتخليه يشيك من supabase)
        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect(url_for("report"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)


# صفحة التقرير (Inventory Report)
@app.route("/report")
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    response = supabase.table("inventory").select("*").execute()
    data = response.data
    return render_template("report.html", data=data)


# صفحة تسجيل الخروج
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
