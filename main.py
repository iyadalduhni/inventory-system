from flask import Flask
from supabase import create_client
import os

app = Flask(__name__)

# Connect to Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

@app.route("/")
def home():
    products = supabase.table("products").select("*").execute().data or []
    return str(products)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
