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

#fetch Vacancies
def fetch_vancacies(db):
    list_of_vacancies = db.execute("SELECT * FROM vacancies INNER JOIN users "+
        "ON vacancies.user_id=users.id INNER JOIN job_functions ON vacancies.job_func_id=job_functions.id")
    return list_of_vacancies


#fetch jobs
def fetch_jobs(db):
    job_listing = db.execute("SELECT * FROM users INNER JOIN company "+
        "ON users.id=company.user_id INNER JOIN vacancies ON vacancies.user_id=company.id ORDER BY id DESC LIMIT 0, 3")
    if len(job_listing) > 0:
      return job_listing
    else:
      return ""


#fetch jobs
def fetch_search(db, job_id, ind_id, loc_id):
    srch_rslt = db.execute("SELECT * FROM vacancies INNER JOIN job_functions ON vacancies.job_func_id = job_functions.id"+
                           " WHERE job_func_id=:jID", jID=job_id)
    return srch_rslt
