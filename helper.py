import os
from flask import redirect, render_template, request, session

def loggedIn_user_info(db):
    rows = db.execute("SELECT id, email, password, user_type, photo FROM users WHERE id = :id", id=session["user_id"])
    return rows

# Get Job Functions from db
def job_function(db):
  job_query = db.execute("SELECT * FROM job_functions")
  return job_query

# Get industires from db
def ind_function(db):
  ind_query = db.execute("SELECT * FROM industries")
  return ind_query

# Get locations from db
def loctn_function(db):
  loctn_query = db.execute("SELECT * FROM locations")
  return loctn_query
