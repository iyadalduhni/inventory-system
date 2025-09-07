from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Supabase credentials
url = os.getenv("SUPABASE_URL", "https://YOUR-PROJECT.supabase.co")
key = os.getenv("SUPABASE_KEY", "YOUR-SERVICE-ROLE-KEY")
supabase = create_client(url, key)

# ------------------- AUTH -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['user'] = email
            return redirect(url_for('dashboard'))
        except Exception as e:
            error = "Invalid email or password"
    return render_template("login.html", error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            return redirect(url_for('login'))
        except Exception as e:
            error = "Registration failed. Try another email."
    return render_template("register.html", error=error)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ------------------- DASHBOARD -------------------
@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html", user=session['user'])

# ------------------- INVENTORY -------------------
@app.route('/report')
def report():
    if 'user' not in session:
        return redirect(url_for('login'))

    products = supabase.table("products").select("*").execute()
    total_value = sum([p['quantity'] * p['price'] for p in products.data])
    return render_template("report.html", products=products.data, total_value=total_value)


@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    sku = request.form['sku']
    quantity = request.form['quantity']
    price = request.form['price']

    supabase.table("products").insert({
        "name": name,
        "sku": sku,
        "quantity": int(quantity),
        "price": float(price)
    }).execute()

    return redirect(url_for('report'))


@app.route('/delete_product/<string:product_id>')
def delete_product(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    supabase.table("products").delete().eq("id", product_id).execute()
    return redirect(url_for('report'))


@app.route('/edit_product/<string:product_id>', methods=['POST'])
def edit_product(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    sku = request.form['sku']
    quantity = request.form['quantity']
    price = request.form['price']

    supabase.table("products").update({
        "name": name,
        "sku": sku,
        "quantity": int(quantity),
        "price": float(price)
    }).eq("id", product_id).execute()

    return redirect(url_for('report'))


# ------------------- RUN -------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
