#!/Users/jack/Documents/projects/22-dash/venv/bin/python3

import gspread
import sqlite3
# import matplotlib
# import image edditing lib

db = "/Users/jack/Documents/logs/money.db" 
budget = "path"

def total_cat_in_month(year, month, cat):
    """
    year: int of year to search in
    month: int of month to search in
    cat: string of category to search for
    returns: float total of all spending of cat in year, month
    """
    total = 0
    # get total spending of cat from google sheets
    sa = gspread.service_account()
    sh = sa.open("money")
    wks = sh.worksheet("flow")
    rows = wks.get_all_values()[1:]
    for r in rows:
        if int(r[4][:4]) == year and int(r[4][4:6]) == month and r[5].strip() == cat:
            total += float(r[0])
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

# get current food spending from db + google
print(total_cat_in_month(2022, 6, "food"))

# plot food spending as a bar from 0 to 100% of budget
# add chart to a copy of desktop background
# set desktop background to the copy with the chart
# execut script once an hour (external script)

