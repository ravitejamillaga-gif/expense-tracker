from flask import Flask, render_template, request, redirect, session
from db import get_connection
import sqlite3

app = Flask(__name__)
app.secret_key = "expense_secret_key"


# ---------------- INIT DATABASE ----------------
def init_db():
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        amount REAL,
        category TEXT,
        priority TEXT,
        deadline TEXT,
        notes TEXT,
        expense_date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------------- LOGIN ----------------
@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_user():

    username = request.form["username"]
    password = request.form["password"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        session["user"] = username
        return redirect("/dashboard")

    return render_template("login.html", error="Wrong Username or Password")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (request.form["username"], request.form["password"])
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
    expenses = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    cursor.close()
    conn.close()

    return render_template("dashboard.html", expenses=expenses, total=total)


# ---------------- ADD EXPENSE ----------------
@app.route("/add", methods=["GET", "POST"])
def add_expense():

    if request.method == "POST":

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO expenses
            (title, amount, category, priority, deadline, notes, expense_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["title"],
            request.form["amount"],
            request.form["category"],
            request.form["priority"],
            request.form["deadline"],
            request.form["notes"],
            request.form["expense_date"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_expense.html")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete_expense(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/dashboard")


# ---------------- EDIT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_expense(id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        cursor.execute("""
            UPDATE expenses
            SET title=?, amount=?, category=?, priority=?, deadline=?, notes=?, expense_date=?
            WHERE id=?
        """, (
            request.form["title"],
            request.form["amount"],
            request.form["category"],
            request.form["priority"],
            request.form["deadline"],
            request.form["notes"],
            request.form["expense_date"],
            id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/dashboard")

    cursor.execute("SELECT * FROM expenses WHERE id=?", (id,))
    expense = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_expense.html", expense=expense)


# ---------------- COMPLETE (NO STATUS COLUMN) ----------------
@app.route("/complete/<int:id>")
def complete(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE expenses
        SET category = category || ' (Completed)'
        WHERE id=?
    """, (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/dashboard")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run()