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

    fDate = date[5:7] + "-" + date[8:10] + "-" + date[2:4]
    return fDate


def calc_progress(logs, course):

    # create dictionary for holding sums of training items
    logSum = {}

    for item in course:
        if item not in ['id', 'is_standard', 'course_name']:
            logSum[item] = 0


    # sum up log items and write to logSum dict
    for log in logs:
        for item, val in log.items():
            if item in logSum:
                if type(val) == type(0) or type(val) == type(0.0):
                    logSum[item] = round(logSum[item] + val, 2)

            elif item == 'log_type' and val not in ['Standard', 'Prior Hours', "Check Ride Prep"]:
                logSum[val.replace(" ", "_").lower()] = 1


    # compare sum of items to course reqs, and sum up their individual completion percentages
    # count number of req items
    reqPercSum = 0
    reqCounter = 0

    for x, y in logSum.items():
        if course[x]:
            if y < course[x]:
                reqPercSum += round(y / course[x], 2)
                reqCounter += 1

            else:
                reqPercSum += 1
                reqCounter += 1


    # divide sum by number of req items to get avg
    currentProgress = int(round(reqPercSum / reqCounter, 2) * 100)
    return currentProgress


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
