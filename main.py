from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "supersecret"  # لازم تغيرها لقيمة قوية

# 🔹 Supabase config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


# =====================[ صفحة تسجيل الدخول ]=====================
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 🔹 تحقق بسيط (ممكن تخلي بيانات المستخدمين بجدول في Supabase)
        if username == "admin" and password == "1234":
            session["logged_in"] = True
            return redirect(url_for("report"))
        else:
            error = "اسم المستخدم أو كلمة المرور غير صحيحة"
    return render_template("login.html", error=error)


# =====================[ صفحة تقرير الجرد ]=====================
@app.route("/report")
def report():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # جلب البيانات من جدول inventory
    data = supabase.table("inventory").select("*").execute()
    rows = data.data if data.data else []

    return render_template("report.html", rows=rows)


# =====================[ تسجيل الخروج ]=====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =====================[ Run محليًا فقط ]=====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
