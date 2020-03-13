import os
import requests
import re

from flask import redirect, render_template, request, session
from functools import wraps


# email validation
def validate_email(email):

    # regular expression for email validation
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    if(re.search(regex,email)):
        return True
    else:
        False

# convert inputs to integers, if input is not empty
def convert_int(x):

    if x:
        return int(x)
    else:
        return None


# convert inputs to floats, if input is not empty
def convert_float(x):

    if x:
        return float(x)
    else:
        return None


# calculate time for logbook categories
def calc_times(cat, time):

    if cat == 1:
        return time
    else:
        return None


# format dates
def format_date(date):

    fDate = date[5:7] + "-" + date[8:10] + "-" + date[0:4]
    return fDate


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
