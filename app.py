from flask import Flask, render_template, redirect, jsonify, session, request, json, flash
from flask_session import Session
import datetime
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helper import redirect_on_vacancy_add, job_function, ind_function, loctn_function, fetch_vancacies, fetch_jobs, fetch_search
from sql import SQL
import smtplib, ssl

# Instantiate app
app = Flask(__name__)

# Get current date and time
now = datetime.datetime.now()


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///green_leaf.db")

now = datetime.datetime.now()

# root route
@app.route("/")
def index():
    jobs = job_function(db)
    industries = ind_function(db)
    locations = loctn_function(db)
    job_listing = fetch_jobs(db)
    return render_template('index.html', jobs=jobs, industries=industries, locations=locations, job_listing=job_listing)

# login route
@app.route("/login", methods=["GET", "POST"])
def login():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Grab form data
        frm_email = request.form.get("email")
        frm_password = request.form.get("password")

        if frm_email:
            if frm_password:
                # Query database for username

                rows = db.execute("SELECT id, first_name, last_name, id, email, password, user_type, photo FROM users WHERE email = :mail", mail=frm_email)

                #Ensure username exists and password is correct
                if len(rows) > 0:
                    if check_password_hash(rows[0]["password"], frm_password):

                      # Remember which user has logged in
                        session["user"] = rows
                        session["l_time"] = now.strftime("%H:%M:%S")
                        
                        # employer login logic
                        if rows[0]["user_type"] == "employer":

                          # get list of vacancies
                            list_of_vacancies = fetch_vancacies(db)

                            vac = []
                            if len(list_of_vacancies) > 0:
                              vac = list_of_vacancies

                            # Query database for list of job-function
                            jobFunc_rows = db.execute("SELECT * FROM job_functions")

                            return render_template(
                              "/employer/index.html",
                              usertype = session["user"][0]["user_type"],
                              logintime = session["l_time"],
                              pix = session["user"][0]["photo"],
                              name = session["user"][0]["first_name"]+" "+session["user"][0]["last_name"],
                              vacancies=vac,
                              jf=jobFunc_rows
                            )

                        # admin login logic
                        else:
                            # get list of users
                            list_of_users = db.execute("SELECT * FROM users")
                            # get list of vacancies
                            list_of_vacancies = fetch_vancacies(db)
                            # get list of applications
                            list_of_applications = db.execute("SELECT * FROM application")

                            usr =[]
                            vac = []
                            applitn = []

                            if len(list_of_users) > 0:
                              usr = list_of_users

                            if len(list_of_vacancies) > 0:
                              vac = list_of_vacancies

                            if len(list_of_applications) > 0:
                              applitn = list_of_applications

                            return render_template(
                              "/admin/index.html",
                              usertype = session["user"][0]["user_type"],
                              logintime = session["l_time"],
                              pix = session["user"][0]["photo"],
                              name = session["user"][0]["first_name"]+" "+session["user"][0]["last_name"],
                              vacancies=vac,
                              applicantions=applitn,
                              users=usr
                            )
                    else:
                        return render_template("/login.html", msg="Invalid password")
                else:
                    return render_template("/login.html", msg="Invalid username")
            else:
                return render_template("/login.html", msg="Please supply password")
        else:
            return render_template("/login.html", msg="Please supply email")

    else:
      return render_template("/login.html")


# register route
@app.route("/register", methods=["GET","POST"])
def register():
  if request.method == "GET":
    return render_template("/register.html")
  else:
    """Register user"""
    try:
      # Grab form data
      last_name = request.form.get("last_name")
      first_name = request.form.get("first_name")
      email = request.form.get("email")
      address = request.form.get("address")
      password = request.form.get("password")
      confirm_password = request.form.get("confirm_password")
      user_type = request.form.get("user_type")
      photo = "../static/images/person_1.jpg"
      reg_date = now.strftime("%Y-%m-%d")

      # Validate form data
      if not first_name:
        return render_template("/register.html", msg='Please supply your First Name')
      elif not last_name:
        return render_template("/register.html", msg='Please supply your Last Name')
      elif not email:
        return render_template("/register.html", msg="Please supply your email")
      elif not password:
        return render_template("/register.html", msg="Please supply password!")
      elif password != confirm_password:
        return render_template("/register.html", msg='Confirm password does not match')
      elif not address:
        return render_template("/register.html", msg='Please password is incorrect')
      else:
          # Check if user is registered
          verify_user = db.execute("SELECT * FROM users WHERE email = :email", email=email)

          if len(verify_user) is 0:

              # hash password
              hash_password = generate_password_hash(password)

              # send user details to db
              db.execute("INSERT INTO users (last_name, first_name, email, address, password, user_type, photo, reg_date) VALUES (:last_name, :first_name, :email, :address, :hash_password, :user_type, :photo, :reg_date)",
                last_name=last_name.capitalize(), first_name=first_name.capitalize(), email=email, address=address, hash_password=hash_password, user_type=user_type, photo=photo, reg_date=reg_date)
                        
              rows = db.execute("SELECT first_name, last_name, id, email, password, user_type, photo FROM users WHERE email = :mail", mail=email)
              
              # Remember which user has logged in
              session["user"] = rows
              # get list of vacancies
              session["l_time"] = now.strftime("%H:%M:%S")
              name=rows[0]["first_name"]+" "+rows[0]["last_name"]
              usertype=session["user"][0]["user_type"]
              pix=session["user"][0]["photo"]

              # get list of vacancies
              list_of_vacancies = fetch_vancacies(db)

              # Query database for list of job-function
              jobFunc_rows = db.execute("SELECT * FROM job_functions")

              return render_template(
                "/employer/index.html",
                usertype=usertype,
                logintime=session["l_time"],
                pix=pix,
                name=name,
                vacancies=list_of_vacancies,
                jf=jobFunc_rows
                )

          else:
            return render_template("/register.html", msg='An account associated with this email address already exists.')

    except Exception as err:
      return render_template("/register.html", msg=str(err))

# Admin - Delete
@app.route("/delete", methods=["GET"])
def delete():
  #Admin delete user
  try:
    id = session["user_id"]
    if id and request.method == 'GET':
      db.execute("DELETE FROM users WHERE id = %s", id)
    return redirect('/')
  except Exception as err:
    return json.dumps({'error': str(err)})


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

# Add Vacancies route
@app.route("/vacancies", methods=["POST"])
def vacancies():
  if request.method == "POST":
    try:
      position = request.form.get("position")
      salary = request.form.get("salary")
      job_type = request.form.get("job_type")
      job_func_id = request.form.get("job_func_id")
      description = request.form.get("description")
      requirement = request.form.get("requirement")

      if not position or not salary or not job_type or not job_func_id:
        msg='All fields are required!'
        return redirect_on_vacancy_add(db,msg,session["user"])
      else:
        if job_type != "---Select User Type---":
          if job_func_id != "---Select Job Function---":
            db.execute("INSERT INTO vacancies (user_id, position, salary, job_type, job_func_id, description, requirement) VALUES (:user_id, :position, :salary, :job_type, :job_func_id, :description, :requirement)",
            user_id = session["user"][0]["id"], position = position, salary = salary, job_type = job_type, job_func_id = job_func_id, description = description, requirement = requirement)
            
            msg='Job vacancy added!'
            return redirect_on_vacancy_add(db,msg,session["user"])
            
          else:
            msg='You did not select a job function'
            return redirect_on_vacancy_add(db,msg,session["user"])
        else:
          msg='You did not select a user type'
          return redirect_on_vacancy_add(db,msg,session["user"])
    except Exception as err:
      msg=str(err)
      return redirect_on_vacancy_add(db,msg,session["user"])

# Job Application route
@app.route("/application", methods=["POST"])
def application():
  """User apply for job"""
  try:
    # user_id = session["user_id"]
    name = request.form.get("fname")
    qual = request.form.get("qual")
    experience = request.form.get("experience")
    date_time = now.strftime("%Y-%m-%d")
    job_id = request.form.get("job_id")

    #return json.dumps({'message': name+" "+qual+" "+experience+" "+date_time+" "+job_id}) 

    if not experience or not qual or not name:
       return json.dumps({'message': 'All fields are required'})
    else:
       db.execute("INSERT INTO application (vacancy_id, experience, qualification, date_time, applicant) VALUES (:vacancy_id, :experience, :qualification, :date_time, :applicant)",
       vacancy_id = job_id, experience = experience, qualification = qual, date_time = date_time, applicant=name)

    return render_template("/job_details.html", msg="Application completed successfully!", job_details=job_id)

  except Exception as err:
    return json.dumps({'error': str(err)})

# About route
@app.route("/about", methods=["GET"])
def about():
  return render_template("/about.html")


# employer route
@app.route("/employer", methods=["GET", "POST"])
def employer():
  return render_template("/employer/index.html")


# Job Listing route
@app.route("/job-search", methods=["POST"])
def job_search():
  try:
    job = request.form.get("job_selected")
    ind = request.form.get("ind_selected")
    loctn = request.form.get("loctn_selected")

    search_result = fetch_search(db, job, ind, loctn)

    return render_template("/job_search.html", search_result=search_result, totalsearch= len(search_result))

  except Exception as err:
    return json.dumps({'error': str(err)})


# contact route
@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "GET":
      return render_template("/contact.html")
    else:
      try:
        first_name = request.form.get("fname")
        last_name = request.form.get("lname")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        if not first_name or not last_name or not email or not subject or not message:
          return json.dumps({'message': 'All fields are required'})
        else:
         server = smtplib.SMTP("smtp.gmail.com",587)
         server.starttls()
         server.login("decagreenleafjobs19@gmail.com", "decagon19")
         server.sendmail("decagreenleafjobs19@gmail.com", email, message)
         return render_template("/contact.html", msg="Message sent")

      except Exception as err:
        return render_template("/contact.html", msg=str(err))


# contact route
@app.route("/job_listing", methods=["GET"])
def job_listing():
    locations = loctn_function(db)
    job_listing = fetch_jobs(db)
    return render_template('job_listing.html',locations=locations, job_listing=job_listing, numlist=len(job_listing))

@app.route("/job_details")
def job_details():
    job_id = request.args.get("jobID") 
    job_details = db.execute("SELECT * FROM users INNER JOIN company ON users.id=company.user_id INNER JOIN vacancies ON vacancies.user_id=company.id WHERE vacancies.id=:jID", jID=job_id)
    return render_template('/job_details.html', job_details=job_details)
    
# Add Company route
# @app.route("/company", methods=["POST"])
# def company():
#   """Company route"""
#   try:
#     company_name = request.form.get("company_name")
#     address = request.form.get("address")
#     logo = request.form.get("logo")
#     user_id = request.form.get("user_id")
#     industry_id = request.form.get("industry_id")

#     if not company_name or not address:
#       return json.dumps({'message': 'All fields are required'})
#     else:
#       reg_details = db.execute("INSERT INTO company (company_name, address, logo, user_id, industry_id) VALUES (:company_name, :address, :logo, :user_id, :industry_id)",
#       company_name = company_name, address = address, logo = logo, user_id = user_id, industry_id = industry_id)

#       return json.dumps({'message': 'Company Added successfully!'})

#   except Exception as err:
#     return json.dumps({'error': str(err)})
