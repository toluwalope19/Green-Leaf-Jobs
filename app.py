from flask import Flask, render_template, redirect, g

from sql import SQL

app = Flask(__name__)

db = SQL("sqlite:///green_leaf.db")

@app.route("/", methods=["GET"])
def get_something():
    loc  = db.execute('SELECT * FROM locations')
    return render_template("index.html", loctn=loc[0]["locations"])

