import os
import sqlite3
import hashlib
import secrets
from flask import Flask, flash, redirect, render_template, request, session, jsonify, send_from_directory
from flask_session import Session

# Configure application
app = Flask(__name__, static_folder='static')

# Configure session to use filesystem (instead of signed cookies)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Secret key for session management
app.secret_key = 'your_secret_key_here'

ACTIVITY = [
        "sedentary",
        "lightly_active",
        "moderately_active",
        "very_active",
        "extra_active"
]

# Database connection
def get_db_connection():
    conn = sqlite3.connect('userdata.db')
    conn.row_factory = sqlite3.Row
    return conn

# Password hashing
def generate_password_hash(password):
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest()

def check_password_hash(hashed_password, password):
    salt = hashed_password[:32]
    return hashed_password == hashlib.sha256((password + salt).encode()).hexdigest()

# Routes
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ecommerce', methods=["GET", "POST"])
def ecommerce():
    if request.method == "POST":
        if 'user_id' not in session:
            flash("You must be logged in to add items to the cart.")
            return redirect("/login")

        user_id = session['user_id']
        product_title = request.form.get("product_title")
        product_price = float(request.form.get("product_price"))

        conn = get_db_connection()
        conn.execute("INSERT INTO cart_items (user_id, product_title, product_price) VALUES (?, ?, ?)",
                     (user_id, product_title, product_price))
        conn.commit()
        conn.close()

        flash("Item added to cart!")
        return redirect("/ecommerce")

    else:
        conn = get_db_connection()
        products = conn.execute("SELECT * FROM gym_products").fetchall()
        conn.close()
        return render_template("ecommerce.html", products=products)

@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        passw = request.form.get("password")
        if not username or not passw:
            flash("Enter the complete details")
        else:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
            conn.close()
            if len(rows) != 1:
                flash("Not a Correct username")
            else:
                hashed_password = rows[0]["password"]
                password_match = check_password_hash(hashed_password, passw)
                if password_match:
                    session["user_id"] = rows[0]["id"]
                    return redirect("/")
    else:
        return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if session.get("user_id") is not None:
        return redirect("/profile")

    if request.method == "POST":
        name = request.form.get("fullname")
        username = request.form.get("username")
        age = int(request.form.get("age"))
        height = int(request.form.get("height"))
        weight = int(request.form.get("weight"))
        mail = request.form.get("email")
        passw = request.form.get("ypassword")
        passworde = generate_password_hash(passw)
        number = request.form.get("phone")
        address = request.form.get("address")
        landmark = request.form.get("landmark")
        city = request.form.get("city")
        state = request.form.get("state")
        zip = request.form.get("zipcode")
        member = request.form.get("membership")
        gender = request.form.get("gender")
        activity = request.form.get("activity")

        # Check if all required fields are provided
        if not (name and username and age and height and weight and mail and passw and number and address and landmark and city and state and zip and member):
            flash("Please fill in all required fields.")
            return redirect("/register")

        # Check if the username already exists
        conn = get_db_connection()
        existing_user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        if existing_user:
            flash("Username already exists. Please choose a different username.")
            return redirect("/register")

        # Calculate BMR and BMI
        bmr = 0
        bmi = weight / (height ** 2)
        if gender == "male":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        elif gender == "female":
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

        # Calculate TDEE and calories
        activity_levels = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        tdee = bmr * activity_levels[activity]
        calories_needed = tdee + 500
        calories_needed_lose = tdee - 500

        # Insert user into the database
        if member == "free":
            conn.execute("INSERT INTO users (username, full_name, password, email, address, landmark, city, state, zip, phone_number, is_premium) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (username, name, passworde, mail, address, landmark, city, state, zip, number, False))
        else:
            conn.execute("INSERT INTO users (username, full_name, password, email, address, landmark, city, state, zip, phone_number, is_premium) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (username, name, passworde, mail, address, landmark, city, state, zip, number, True))

        # Get the newly created user's ID
        user_m_id = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        session["user_id"] = user_m_id[0]["id"]

        # Insert health records for the user
        conn.execute("INSERT INTO health_records (bmi, bmr, daily_calories_needed, calories_to_lose, user_id) VALUES (?, ?, ?, ?, ?)",
                   (bmi, bmr, calories_needed, calories_needed_lose, user_m_id[0]["id"]))
        conn.commit()
        conn.close()

        flash("Registration successful!")
        return redirect("/profile")

    else:
        return render_template("register.html", activity=ACTIVITY)

@app.route('/add_product', methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        product_title = request.form.get("product_title")
        product_price = float(request.form.get("product_price"))
        category = request.form.get("category")
        image_url = request.form.get("image_url")  # Get the image URL from the form

        conn = get_db_connection()
        conn.execute("INSERT INTO gym_products (product_name, price, category, image_url) VALUES (?, ?, ?, ?)",
                   (product_title, product_price, category, image_url))
        conn.commit()
        conn.close()

        flash("Product added successfully!")
        return redirect("/ecommerce")
    else:
        return render_template("add_product.html")

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    user_id = session['user_id']
    data = request.json

    product_title = data.get("product_title")
    product_price = data.get("product_price")

    conn = get_db_connection()
    conn.execute("INSERT INTO cart_items (user_id, product_title, product_price) VALUES (?, ?, ?)",
               (user_id, product_title, product_price))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Item added to cart"})

@app.route('/profile', methods=["GET", "POST"])
def profile():
    if session.get("user_id") is None:
        return redirect("/login")

    user_id = session['user_id']
    conn = get_db_connection()
    user_data_f = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
    health_records = conn.execute("SELECT * FROM health_records WHERE user_id = ?", (user_id,)).fetchall()
    cart_items = conn.execute("SELECT * FROM cart_items WHERE user_id = ?", (user_id,)).fetchall()
    purchase_histories = conn.execute("SELECT * FROM purchase_history WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()

    return render_template("profile.html", user_data=user_data_f[0], health=health_records[0], cart_items=cart_items, purchase_history=purchase_histories)

@app.route('/logout')
def logout():
    session.clear()
    return render_template("logout.html")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True)