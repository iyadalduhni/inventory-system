from flask import Flask, render_template_string
from supabase import create_client
import os

app = Flask(__name__)

# Supabase config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# HTML template
report_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Inventory Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h2 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: center; }
        th { background-color: #007BFF; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h2>📦 Inventory Report</h2>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>SKU</th>
                <th>Quantity</th>
                <th>Cost Price</th>
                <th>Selling Price</th>
                <th>Created At</th>
            </tr>
        </thead>
        <tbody>
            {% for p in products %}
            <tr>
                <td>{{ p['name'] }}</td>
                <td>{{ p['sku'] }}</td>
                <td>{{ p['quantity'] }}</td>
                <td>{{ p['price'] }}</td>
                <td>{{ p['selling_price'] }}</td>
                <td>{{ p['created_at'] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route("/")
def index():
    data = supabase.table("products").select("*").execute()
    products = data.data
    return render_template_string(report_template, products=products)
    from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # غيرها لمفتاح قوي

# إعداد supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# بيانات تسجيل الدخول (مبدئيًا ثابتة)
USERNAME = "admin"
PASSWORD = "12345"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("report"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/report")
def report():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    response = supabase.table("products").select("*").execute()
    products = response.data
    return render_template("report.html", products=products)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

