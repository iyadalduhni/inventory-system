from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # غيّرها لمفتاح قوي

# إعداد Supabase
url = os.getenv("SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
key = os.getenv("SUPABASE_KEY", "YOUR_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

# الصفحة الرئيسية → تسجيل الدخول
@app.route("/")
def home():
    return redirect(url_for("login"))

# تسجيل مستخدم جديد
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            auth_response = supabase.auth.sign_up({"email": email, "password": password})
            if "user" in auth_response:
                flash("Registration successful. Please login.", "success")
                return redirect(url_for("login"))
            else:
                flash("Registration failed.", "danger")
        except Exception as e:
            flash(str(e), "danger")

    return render_template("register.html")

# تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user:
                session["user"] = email
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials", "danger")
        except Exception as e:
            flash("Login failed: " + str(e), "danger")

    return render_template("login.html")

# تسجيل الخروج
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# صفحة لوحة التحكم
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

# صفحة الجرد (عرض + إضافة + حذف منتجات)
@app.route("/report", methods=["GET", "POST"])
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    # إضافة منتج جديد
    if request.method == "POST":
        name = request.form["name"]
        sku = request.form["sku"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])

        supabase.table("products").insert({
            "name": name,
            "sku": sku,
            "quantity": quantity,
            "price": price
        }).execute()

        return redirect(url_for("report"))

    # جلب كل المنتجات
    data = supabase.table("products").select("*").execute()
    products = data.data if data.data else []

    # حساب إجمالي المخزون
    total_value = sum(p["quantity"] * p["price"] for p in products)

    return render_template("report.html", products=products, total_value=total_value)

# حذف منتج
@app.route("/delete_product/<id>", methods=["POST"])
def delete_product(id):
    supabase.table("products").delete().eq("id", id).execute()
    return redirect(url_for("report"))

if __name__ == "__main__":
    app.run(debug=True)
