from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # غيرها بمفتاح آمن

# Supabase connection
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# ---------------- Routes ---------------- #

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
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
            return render_template("register.html", error="Registration failed")
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])


@app.route("/report")
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    products = supabase.table("products").select("*").execute().data
    total_value = sum([p["quantity"] * p["price"] for p in products])

    return render_template("report.html", products=products, total_value=total_value)


@app.route("/add_product", methods=["POST"])
def add_product():
    if "user" not in session:
        return redirect(url_for("login"))

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

    return redirect(url_for("report"))


@app.route("/delete_product/<id>", methods=["POST"])
def delete_product(id):
    if "user" not in session:
        return redirect(url_for("login"))

    supabase.table("products").delete().eq("id", id).execute()
    return redirect(url_for("report"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- Run ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
