import os
from flask import redirect, render_template, request, session


# fetch users
def loggedIn_user_info(db):
    rows = db.execute("SELECT id, email, password, user_type, photo FROM users WHERE id = :id", id=session["user_id"])
    return rows

#fetch Vacancies
def fetch_vancacies(db):
    list_of_vacancies = db.execute("SELECT * FROM vacancies INNER JOIN users "+
        "ON vacancies.user_id=users.id INNER JOIN job_functions ON vacancies.job_func_id=job_functions.id")
    return list_of_vacancies