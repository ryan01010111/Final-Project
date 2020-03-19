from cs50 import SQL


db = SQL("sqlite:///main.db")

logs = db.execute("SELECT * FROM flightLogs WHERE user_id = 2")

course = db.execute("SELECT * FROM courses WHERE course_name = 'Private Pilot'")[0]




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
