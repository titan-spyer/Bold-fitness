from flask import Flask, flash, redirect, render_template, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_folder='static')



@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ecommerce')
def ecommerce():
    return render_template("ecommerce.html")

@app.route('/login')
def login():
    if request.method == "POST":
        username = request.form.get("username")
        passw = request.form.get("password")
        if not username or not passw:
            flash("Kindly Fill all The credientials")
        else:
            ...
    else:
        return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("fullname")
        username = request.form.get("username")
        age = request.form.get("age")
        height = request.form.get("height")
        weight = request.form.get("weight")
        mail = request.form.get("email")
        passw = request.form.get("password")
        password = generate_password_hash(passw)
        number = request.form.get("phone")
        address = request.form.get("address")
        landmark = request.form.get("landmark")
        city = request.form.get("city")
        state = request.form.get("state")
        zip = request.form.get("zipcode")
        member = request.form.get("membership")
        if not (name or username or age or height or weight or mail or passw or number or address or landmark or city or state or zip or member):
            flash("Kindly fill all the data")
        else:
            if member == "free":
                flash("correct")
            else:
                flash("incorrect")

    else:
        return render_template("register.html")

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if request.method == 'POST':
        data = request.json

        username = data.get('username')
        product_title = data.get('product_title')
        product_price = data.get('product_price')



if __name__ == '__main__':
    app.run(debug=True)

