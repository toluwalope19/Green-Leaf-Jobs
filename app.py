from flask import Flask, render_template, redirect, jsonify, session, request
# from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from sql import SQL

# Instantiate app
app = Flask(__name__)

db = SQL("sqlite:///green_leaf.db")

# root route
@app.route("/")
def index():
    return render_template('index.html')

# login route
@app.route("/login", methods=["GET", "POST"])
def login():
  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    # Grab form data
    email = request.form.get("email")
    password = request.form.get("password")

    if email:
      if password:
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = email")

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
          return render_template("/login.html", msg="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

      else:
        return render_template("/login.html", msg="Please supply password")
    else:
      return render_template("/login.html", msg="Please supply email")



