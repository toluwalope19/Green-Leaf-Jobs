from flask import Flask, render_template, redirect, jsonify, session, request, json
from flask_session import Session
import datetime
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
#from helpers import loggedIn_user
from sql import SQL

# Instantiate app
app = Flask(__name__)


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
                    if rows[0]["password"] == frm_password: 
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
                            users_err = "No registration made yet."
                            # get list of users      
                            list_of_users = db.execute("SELECT * FROM users")
                            if len(list_of_users) > 0:
                              users = list_of_users
                              
                            # get login time                    
                            l_time = now.strftime("%H:%M:%S")
                            return render_template("/admin/index.html", msg=rows[0]["user_type"], logintime=l_time, usr=users, _err=users_err, pix=rows[0]["photo"])
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
@app.route("/register", methods=["GET", "POST"])
def register():
  """Register user"""
  try:
    # Grab form data
    last_name = request.form.get("lastname")
    first_name = request.form.get("firstname")
    email = request.form.get("email")
    address = request.form.get("address")
    password = request.form.get("password")
    confirm_password = request.form.get("password")
    reg_date = now.strftime("%d-%m-%y")

    # Validate form data
    if not last_name and not first_name:
      flash("Please Supply your First Name and Last Name")
    elif not email:
      flash("Please Supply your First Name and Last Name")
    elif password != confirm_password:
      flash("Please password is incorrect")
    elif not address:
      flash("Please password is incorrect")
    else:
        # Check if user is registered
        verify_user = db.execute("SELECT * FROM users WHERE email = %s", email)

        if len(verify_user) is 0:

            # hash password
            hash_password = generate_password_hash(password)

            # send user details to db
            reg_details = db.execute(
              "INSERT INTO users (last_name, first_name, email, address, password, reg_date) VALUES (?, ?, ?, ?, ?, ?)", (last_name, first_name, email, address, hash_password, reg_date))

            return json.dumps({'message': 'User created successfully!'})

        else:
          return json.dumps({'error': str(verify_user[0]),'message': 'An account associated with this email address already exists.'})

  except Exception as err:
    return json.dumps({'error': str(err)})

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


# admin page
@app.route("/admin", methods=["GET", "POST"])
def admin():
  if request.method == "GET":
    # get list of registered users
    list_of_users = db.execute("SELECT * FROM users")
    return render_template("/admin/admin.html", users=list_of_users, rtn="returned")

    # get list of vacacies 

  #else:
    #else


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

