import os
from flask import redirect, render_template, request, session



def loggedIn_user_info(db):
    rows = db.execute("SELECT id, email, password, user_type, photo FROM users WHERE id = :id", id=session["user_id"])
    return rows