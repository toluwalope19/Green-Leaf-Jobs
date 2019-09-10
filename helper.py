import os
from flask import redirect, render_template, request, session

def redirect_on_vacancy_add(db, msg, row):  
    #User add vacancies
    list_of_vacancies = db.execute("SELECT * FROM vacancies WHERE user_id=:user", user=row[0]["id"])
    jobFunc_rows = db.execute("SELECT * FROM job_functions")
    # redirect
    return render_template(
      "/employer/index.html", 
        msg = msg,
        vacancies=list_of_vacancies, 
        usertype = row[0]["user_type"],
        logintime = session["l_time"],
        pix = row[0]["photo"],
        name = row[0]["first_name"]+" "+row[0]["last_name"],
        jf=jobFunc_rows
    )

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


def perform_delete(db, table, id, loc, row):
  db.execute("DELETE FROM "+table+" WHERE id = :item", item=id)
  vac = db.execute("SELECT * FROM vacancies WHERE user_id=:user", user=row[0]["id"])
  jobFunc_rows = db.execute("SELECT * FROM job_functions")
  applitn = db.execute("SELECT * FROM application")
  msg = "Deleted!"
 

  if loc == "ad":
    return render_template(
      "/admin/index.html",
      usertype = session["user"][0]["user_type"],
      logintime = session["l_time"],
      pix = session["user"][0]["photo"],
      name = session["user"][0]["first_name"]+" "+session["user"][0]["last_name"],
      vacancies=vac,
      applicantions=applitn,
      users=db.execute("SELECT * FROM users")
    )
  elif loc == "emp":
    return render_template(
      "/employer/index.html", 
        msg = msg,
        vacancies=vac, 
        usertype = row[0]["user_type"],
        logintime = session["l_time"],
        pix = row[0]["photo"],
        name = row[0]["first_name"]+" "+row[0]["last_name"],
        jf=jobFunc_rows
    )
  else:
    sd
