import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import validate_email, convert_int, convert_float, calc_times, format_date, apology, login_required

# Configure application
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
app.jinja_env.filters["format_date"] = format_date

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# set view mode for student / instructor versions of the site
# student view is default
viewMode = "student"

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///main.db")


@app.route("/")
def index():
    """Landing"""

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return render_template("login.html", error="email", message="Please enter your email address")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error="password", message="Please enter your password")

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          email=request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", error="email", message="Invalid email and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Set viewMode to user's role
        global viewMode
        viewMode = rows[0]['role']

        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        firstname = request.form.get("firstname").title()
        lastname = request.form.get("lastname").title()
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        role = request.form.get("role").lower()

        # ensure that first name was submitted
        if not firstname:
            return render_template("register.html", error="firstname", message="Please enter your first name")
        # ensure that last name was submitted
        if not lastname:
            return render_template("register.html", error="lastname", message="Please enter your last name")
        # ensure that email was submitted
        if not email:
            return render_template("register.html", error="email", message="Please enter your email address")
        # ensure that email is valid
        if not validate_email(email):
            return render_template("register.html", error="email", message="That is not a valid email address")
        # ensure that email doesn't exist
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                                    email=email)
        if len(rows) == 1:
            return render_template("register.html", error="email", message="That email address is already registered")
        # ensure that password was submitted
        if not password:
            return render_template("register.html", error="password", message="Please enter a password")
        # ensure that password and confirmation match
        if confirmation != password:
            return render_template("register.html", error="password", message="Those passwords don't match")
        # ensure that role was selected
        if role == "select a role":
            return render_template("register.html", error="role", message="Please select a role")

        # create account - insert user data into database
        user = db.execute("INSERT INTO users (email, hash, firstname, lastname, role) VALUES (:email, :hash, :firstname, :lastname, :role)",
                    email=email, hash=generate_password_hash(password), firstname=firstname, lastname=lastname, role=role)
        # set default course assignment
        db.execute("INSERT INTO courseAssignments (user_id, course_id) VALUES (:user, :course)",
                        user=user, course=0)

        # set session for user and log in
        session["user_id"] = db.execute("SELECT id FROM users WHERE email = :email",
                                        email=email)[0]['id']
        # set viewMode to user's role
        global viewMode
        viewMode = role

        flash("Registered successfully! Welcome to your dashboard!")
        return redirect("/dashboard")

    else:
        return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():

    if viewMode == "instructor":
        return render_template("dashboard_instructor.html")
    else:
        return render_template("dashboard_student.html")


@app.route("/user/<user_id>")
@login_required
def show_user_profile(user_id):

    # fetch user data, including assigned course
    user = db.execute("SELECT user_id, firstname, lastname, assigned_instructor, course_id, course_name FROM users JOIN courseAssignments ON users.id = courseAssignments.user_id JOIN courses ON courseAssignments.course_id = courses.id WHERE users.id = :user",
                        user=user_id)

    # check for "instructor" view mode
    if viewMode == "instructor":
        # check if current user (instructor) is assigned to the user being viewed
        if user[0]['assigned_instructor'] == session["user_id"]:
            # show "instructor view"

            # fetch and show course options
            courses = db.execute("SELECT id, course_name FROM courses")

            return render_template("profile_student.html", user=user, courses=courses)
        else:
            # show standard view
            return render_template("profile.html", user=user, instructorView=True)
    else:
        # show standard view
        return render_template("profile.html", user=user)


@app.route("/my_students", methods=["GET", "POST"])
@login_required
def my_students():

    if request.method == "POST":

        student = db.execute("SELECT * FROM users WHERE email = :email",
                    email=request.form.get("email"))

        # ensure email exists in database
        if len(student) != 1:
            return render_template("my_students.html", error="email", message="Email not found")
        # ensure student isn't already assigned to current user (instructor)
        elif student[0]['assigned_instructor'] == session["user_id"]:
            return render_template("my_students.html", error="email", message="Student is already assigned to you")
        # assign current user (instructor) to student
        else:
            db.execute("UPDATE users SET assigned_instructor = :user WHERE id = :student",
                        user=session["user_id"], student=student[0]['id'])

        flash("Added student")
        return redirect("/my_students")

    else:

        # fetch students
        students = db.execute("SELECT * FROM users WHERE assigned_instructor = :user",
                                user=session["user_id"])
        return render_template("my_students.html", students=students)


@app.route("/assign_course/<user_id>", methods=["POST"])
@login_required
def assign_course(user_id):
    """ assign course to student """

    newCourse = request.form.get("assignedCourse")
    if newCourse != "initial":
        db.execute("UPDATE courseAssignments SET course_id = :newCourse WHERE user_id = :user_id",
                    newCourse=newCourse, user_id=user_id)

        flash("Course changed")
        return redirect(f"/user/{user_id}")

    else:
        flash("Course could not be changed")
        return redirect(f"/user/{user_id}")


@app.route("/logbook", methods=["GET", "POST"])
@login_required
def logbook():

    if request.method == "POST":
        """Update Flight Log"""

        user = session["user_id"]
        date = request.form.get("entryDate")
        log_type = request.form.get("logType")
        route = request.form.get("route")
        aircraft = request.form.get("aircraft")
        aircraft_ident = request.form.get("ident")
        sel = convert_float(request.form.get("sel"))
        mel = convert_float(request.form.get("mel"))
        tailwheel = convert_float(request.form.get("tailwheel"))
        high_performance = convert_float(request.form.get("highPerformance"))
        total_hours = convert_float(request.form.get("totalTime"))
        night_dual = convert_float(request.form.get("nightTime"))
        dual = convert_float(request.form.get("dual"))
        pic = convert_float(request.form.get("pic"))
        takeoff_day = convert_int(request.form.get("takeoffDay"))
        land_day = convert_int(request.form.get("landDay"))
        takeoff_night = convert_int(request.form.get("takeoffNight"))
        land_night = convert_int(request.form.get("landNight"))
        takeoff_tower = convert_int(request.form.get("takeoffTower"))
        land_tower = convert_int(request.form.get("landTower"))
        maneuver = convert_float(request.form.get("maneuver"))
        cc_dual = convert_float(request.form.get("ccDual"))
        cc_solo = convert_float(request.form.get("ccSolo"))
        cc_night = convert_int(request.form.get("ccNight"))
        cc_150 = convert_int(request.form.get("cc150"))
        instrument_actual = convert_float(request.form.get("instActual"))
        instrument_sim = convert_float(request.form.get("instSim"))
        instrument_approach = convert_int(request.form.get("instAppr"))

        sel = calc_times(sel, total_hours)
        mel = calc_times(mel, total_hours)
        tailwheel = calc_times(tailwheel, total_hours)
        high_performance = calc_times(high_performance, total_hours)
        dual = calc_times(dual, total_hours)
        pic = calc_times(pic, total_hours)

        if not date:

            flash("Error: Please enter a date!")
            return render_template("logbook.html")

        else:
            # insert log entry
            db.execute("INSERT INTO flightLogs (user_id, date, log_type, route, aircraft, aircraft_ident, sel, mel, tailwheel, high_performance, total_hours, night_dual, dual, pic, takeoff_day, land_day, takeoff_night, land_night, takeoff_tower, land_tower, maneuver, cc_dual, cc_solo, cc_night, cc_150, instrument_actual, instrument_sim, instrument_approach) VALUES (:user, :date, :log_type, :route, :aircraft, :aircraft_ident, :sel, :mel, :tailwheel, :high_performance, :total_hours, :night_dual, :dual, :pic, :takeoff_day, :land_day, :takeoff_night, :land_night, :takeoff_tower, :land_tower, :maneuver, :cc_dual, :cc_solo, :cc_night, :cc_150, :instrument_actual, :instrument_sim, :instrument_approach)",
                        user=user, date=date, log_type=log_type, route=route, aircraft=aircraft, aircraft_ident=aircraft_ident, sel=sel, mel=mel, tailwheel=tailwheel, high_performance=high_performance, total_hours=total_hours, night_dual=night_dual, dual=dual, pic=pic, takeoff_day=takeoff_day, land_day=land_day, takeoff_night=takeoff_night, land_night=land_night, takeoff_tower=takeoff_tower, land_tower=land_tower, maneuver=maneuver, cc_dual=cc_dual, cc_solo=cc_solo, cc_night=cc_night, cc_150=cc_150, instrument_actual=instrument_actual, instrument_sim=instrument_sim, instrument_approach=instrument_approach)

            logs = db.execute("SELECT * FROM flightLogs WHERE user_id = :user",
                                user=user)

            flash("Log entry successful")
            return render_template("logbook.html", logs=logs)

    else:

        logs = db.execute("SELECT * FROM flightLogs WHERE user_id = :user",
                                user=session["user_id"])
        return render_template("logbook.html", logs=logs)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
