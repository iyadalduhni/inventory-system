from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")

# Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# -------------------- Routes --------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

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
        except Exception as e:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            supabase.auth.sign_up({"email": email, "password": password})
            return redirect(url_for("login"))
        except Exception as e:
            return render_template("register.html", error="Error creating account")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    products = supabase.table("products").select("*").execute().data
    return render_template("dashboard.html", user=session["user"], products=products)

@app.route("/report", methods=["GET", "POST"])
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        sku = request.form["sku"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        category = request.form.get("category")

        supabase.table("products").insert({
            "name": name,
            "sku": sku,
            "quantity": quantity,
            "price": price,
            "category": category
        }).execute()

    products = supabase.table("products").select("*").execute().data
    total_value = sum(p["quantity"] * p["price"] for p in products)
    return render_template("report.html", products=products, total_value=total_value)

@app.route("/delete/<product_id>", methods=["POST"])
def delete_product(product_id):
    supabase.table("products").delete().eq("id", product_id).execute()
    return redirect(url_for("report"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
