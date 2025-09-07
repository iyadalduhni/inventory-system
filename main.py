from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ربط مع Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
        if user.data:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        supabase.table("users").insert({"email": email, "password": password}).execute()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])


@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        sku = request.form['sku']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        category = request.form['category']

        supabase.table("products").insert({
            "name": name,
            "sku": sku,
            "quantity": quantity,
            "price": price,
            "category": category
        }).execute()

    products = supabase.table("products").select("*").execute()
    total_value = sum([p['quantity'] * p['price'] for p in products.data])

    return render_template('report.html', products=products.data, total_value=total_value)


@app.route('/delete/<product_id>')
def delete_product(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    supabase.table("products").delete().eq("id", product_id).execute()
    return redirect(url_for('report'))


@app.route('/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_quantity = int(request.form['quantity'])
        supabase.table("products").update({"quantity": new_quantity}).eq("id", product_id).execute()
        return redirect(url_for('report'))

    product = supabase.table("products").select("*").eq("id", product_id).execute()
    if not product.data:
        return redirect(url_for('report'))

    return render_template('edit.html', product=product.data[0])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
