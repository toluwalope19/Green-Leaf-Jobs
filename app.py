from flask import Flask, render_template, redirect, jsonify, session, request, json, flash
from flask_session import Session
import datetime
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helper import loggedIn_user_info
from sql import SQL

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

# Custom filter
#app.jinja_env.filters["usd"] = usd

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
    return render_template('index.html')

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
                rows = db.execute("SELECT id, email, password, user_type, photo FROM users WHERE email = :mail", mail=frm_email)

                #Ensure username exists and password is correct
                if len(rows) > 0:
                    if check_password_hash(rows[0]["password"], frm_password):
                        # Remember which user has logged in
                        session["user_id"] = rows[0]["id"]
                        if rows[0]["user_type"] == "applicant":
                            l_time = now.strftime("%H:%M:%S")
                            return render_template("/login.html", msg="You are logged-in sucessfully "+rows[0]["user_type"], logintime=l_time)
                        elif rows[0]["user_type"] == "employer":
                            # get login time                   
                            l_time = now.strftime("%H:%M:%S")        
                            return render_template("/login.html", msg="You are logged-in sucessfully "+rows[0]["user_type"], logintime=l_time)
                        else:        
                            # get list of users      
                            list_of_users = db.execute("SELECT * FROM users")
                            # get list of vacancies      
                            list_of_vacancies = db.execute("SELECT * FROM vacancies")
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

                            # get login time                    
                            l_time = now.strftime("%H:%M:%S")

                            return render_template(
                              "/admin/index.html", 
                              usertype=rows[0]["user_type"], 
                              logintime=l_time, 
                              users=usr, 
                              vacancies=vac,
                              applicantions=applitn, 
                              pix=rows[0]["photo"]
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
              reg_details = db.execute(
                "INSERT INTO users (last_name, first_name, email, address, password, user_type, photo, reg_date) VALUES (:last_name, :first_name, :email, :address, :hash_password, :user_type, :photo, :reg_date)",
                last_name=last_name.capitalize(), first_name=first_name.capitalize(), email=email, address=address, hash_password=hash_password, user_type=user_type, photo=photo, reg_date=reg_date)

              return render_template("/register.html", msg='User created successfully!')

          else:
            return render_template("/register.html", msg='An account associated with this email address already exists.')

    except Exception as err:
      return render_template("/register.html", msg=str(err))

# Admin - Delete User
@app.route("/delete", methods=["GET", "POST"])
def delete():
  """Admin delete user"""
  try:
    id = session["user_id"]
    if id and request.method == 'GET':
      delete_user = db.execute("DELETE FROM users WHERE id = %s", id)
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
@app.route("/vacancies", methods=["GET", "POST"])
def vacancies():
  rows = loggedIn_user_info(db)
  if request.method == "GET":
    _err = "No vacancies record found yet."
    """User add vacancies"""
    list_of_vacancies = db.execute("SELECT * FROM vacancies")
    if len(list_of_vacancies) > 0:
      vacancies = list_of_vacancies
                              
    # get login time                    
    l_time = now.strftime("%H:%M:%S")
    return render_template("/admin/index.html", msg=rows[0]["user_type"], logintime=l_time, vacancies=vacancies, _err=_err, pix=rows[0]["photo"])

  else:
    try:
      # user_id = session["user_id"]
      user_id = request.form.get("user_id")
      position = request.form.get("position")
      salary = request.form.get("salary")
      job_type = request.form.get("job_type")
      job_func_id = request.form.get("job_func_id")
      description = request.form.get("description")
      requirement = request.form.get("requirement")

      if not position or not salary or not job_type or not job_func_id or not user_id:
        #flash("All fields are required")
        return json.dumps({'message': 'All fields are required'})
      else:
        reg_details = db.execute("INSERT INTO vacancies (user_id, position, salary, job_type, job_func_id, description, requirement) VALUES (:user_id, :position, :salary, :job_type, :job_func_id, :description, :requirement)",
        user_id = user_id, position = position, salary = salary, job_type = job_type, job_func_id = job_func_id, description = description, requirement = requirement)

        return json.dumps({'message': 'Job successfully uploaded!'})

    except Exception as err:
      return json.dumps({'error': str(err)})
  


# Job Application route
@app.route("/application", methods=["POST"])
def application():
  """User apply for job"""
  try:
    # user_id = session["user_id"]
    user_id = request.form.get("user_id")
    vacancy_id = request.form.get("vacancy_id")
    experience = request.form.get("experience")
    qualification = request.form.get("qualification")
    date_time = now.strftime("%Y-%m-%d")

    if not experience or not qualification:
      return json.dumps({'message': 'All fields are required'})
    else:
      reg_details = db.execute("INSERT INTO application (user_id, vacancy_id, experience, qualification, date_time) VALUES (:user_id, :vacancy_id, :experience, :qualification, :date_time)",
      user_id = user_id, vacancy_id = vacancy_id, experience = experience, qualification = qualification, date_time = date_time)

      return json.dumps({'message': 'Job Application successfully!'})

  except Exception as err:
    return json.dumps({'error': str(err)})


# Add Company route
@app.route("/company", methods=["POST"])
def company():
  """Company route"""
  try:
    company_name = request.form.get("company_name")
    address = request.form.get("address")
    logo = request.form.get("logo")
    user_id = request.form.get("user_id")
    industry_id = request.form.get("industry_id")

    if not company_name or not address:
      return json.dumps({'message': 'All fields are required'})
    else:
      reg_details = db.execute("INSERT INTO company (company_name, address, logo, user_id, industry_id) VALUES (:company_name, :address, :logo, :user_id, :industry_id)",
      company_name = company_name, address = address, logo = logo, user_id = user_id, industry_id = industry_id)

      return json.dumps({'message': 'Company Added successfully!'})

  except Exception as err:
    return json.dumps({'error': str(err)})


# Add Comment route
@app.route("/comment", methods=["POST"])
def comment():
  """Comment route"""
  try:
    user_id = request.form.get("user_id")
    comment = request.form.get("comment")
    date_time = now.strftime("%Y-%m-%d")

    if not comment:
      return json.dumps({'message': 'Please enter your comment'})
    else:
      reg_details = db.execute(
        "INSERT INTO comments (user_id, comment, date_time) VALUES (:user_id, :comment, :date_time)",
        user_id = user_id, comment = comment, date_time = date_time)

      return json.dumps({'message': 'Company Added successfully!'})

  except Exception as err:
    return json.dumps({'error': str(err)})
