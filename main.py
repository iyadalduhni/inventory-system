from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Supabase connection
url = os.getenv("SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
key = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_KEY")
supabase: Client = create_client(url, key)


# -------------------- Routes --------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------- Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            supabase.auth.sign_up({"email": email, "password": password})
            return redirect(url_for("login"))
        except Exception as e:
            error = str(e)
    return render_template("register.html", error=error)

# ---------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session["user"] = email
            return redirect(url_for("dashboard"))
        except Exception:
            error = "Invalid credentials"
    return render_template("login.html", error=error)

# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

# ---------- Inventory Report ----------
@app.route("/report", methods=["GET", "POST"])
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        sku = request.form["sku"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        category = request.form["category"]

        supabase.table("products").insert({
            "name": name,
            "sku": sku,
            "quantity": quantity,
            "price": price,
            "category": category
        }).execute()

    products = supabase.table("products").select("*").execute().data

    total_value = sum([p["quantity"] * p["price"] for p in products])
    return render_template("report.html", products=products, total_value=total_value)

# ---------- Delete Product ----------
@app.route("/delete/<string:product_id>", methods=["POST"])
def delete(product_id):
    supabase.table("products").delete().eq("id", product_id).execute()
    return redirect(url_for("report"))

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
