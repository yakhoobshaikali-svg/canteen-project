from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "canteen_secret"

# -------- DATABASE SETUP --------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        image TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item_id INTEGER,
        quantity INTEGER,
        status TEXT)""")

    conn.commit()
    conn.close()

init_db()

# -------- HOME --------
@app.route("/")
def home():
    return redirect("/login")

# -------- REGISTER --------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                  (name,email,password,"customer"))
        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("register.html")

# -------- LOGIN --------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?",
                  (email,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["role"] = user[4]

            if user[4] == "admin":
                return redirect("/admin")
            else:
                return redirect("/menu")

    return render_template("login.html")

# -------- MENU --------
@app.route("/menu")
def menu():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    conn.close()
    return render_template("menu.html", items=items)

# -------- ORDER --------
@app.route("/order/<int:item_id>", methods=["POST"])
def order(item_id):
    quantity = request.form["quantity"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id,item_id,quantity,status) VALUES (?,?,?,?)",
              (session["user_id"],item_id,quantity,"Pending"))
    conn.commit()
    conn.close()

    return redirect("/menu")

# -------- ADMIN --------
@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""SELECT orders.id, users.name, items.name, orders.quantity, orders.status
                 FROM orders
                 JOIN users ON orders.user_id = users.id
                 JOIN items ON orders.item_id = items.id""")
    orders = c.fetchall()
    conn.close()
    return render_template("admin.html", orders=orders)

# -------- UPDATE STATUS --------
@app.route("/update/<int:order_id>/<status>")
def update(order_id, status):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE orders SET status=? WHERE id=?",
              (status,order_id))
    conn.commit()
    conn.close()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)
