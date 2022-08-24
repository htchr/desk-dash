#!/Users/jack/Documents/projects/22-dash/venv/bin/python3

import datetime
import gspread
import sqlite3
import matplotlib.pyplot as plt
# import image edditing lib

db = "/Users/jack/Documents/logs/money.db" 
budget = "/Users/jack/Documents/projects/22-dash/budget.csv"

def total_cat_in_month(cat, year=0, month=0):
    """
    sum all spending of a category within a given month
    search across google sheets money sheet and money.db
    ---
    cat: string of category to search for
    year: int of year to search in
    month: int of month to search in
    returns: float total of all spending of cat in year, month
    """
    if year == 0 or month == 0:
        now = datetime.date.today()
        year = now.year
        month = now.month
    total = 0
    # get total spending of cat from google sheets
    sa = gspread.service_account()
    sh = sa.open("money")
    wks = sh.worksheet("flow")
    rows = wks.get_all_values()[1:]
    for r in rows:
        try: # there may be rows with empty values
            if int(r[4][:4]) == year and int(r[4][4:6]) == month and r[5].strip() == cat:
                total += float(r[0])
        except:
            continue
    # get total spending of cat from money.db
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("""SELECT * FROM flow WHERE 
                   year = ?
                   AND month = ?
                   AND cat = ?""",
                (year, month, cat))
    for r in cur.fetchall():
        total += r[1]
    con.close()
    return total

def bar(cat):
    """
    cat: string of category to plot
    returns: None
    """
    label = [cat]
    value = [total_cat_in_month(cat)]
    plt.bar(label, value)
    plt.show()

# get current food spending from db + google
# print(total_cat_in_month("food"))

# plot food spending as a bar from 0 to 100% of budget
bar("food")

# add chart to a copy of desktop background
# set desktop background to the copy with the chart
# execut script once an hour (external script)

