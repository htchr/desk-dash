#!/Users/jack/Documents/projects/22-dash/venv/bin/python3

import datetime
import gspread
import sqlite3
from PIL import Image

db = "/Users/jack/Documents/logs/money.db" 
budget = "/Users/jack/Documents/projects/22-dash/budget.csv"
bar = "/Users/jack/Documents/projects/22-dash/bar.jpeg"
background = "/Users/jack/Pictures/background.jpeg"

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

def new_bar(width, height, path=bar):
    """
    width: int of image width
    height: int of image height
    path: sting file path location to save the image
    returns: n/a
    """
    im = Image.new(mode="RGB", size=(width, height))
    im.save(path)

def color(current, budget, path=bar):
    """
    current: int / float of current spending
    budget: int of max spending per month
    path: string of file path to image
    """
    # settings:
    bezel = 0.2
    buffer = 0.95
    # gradient green to red as current spending reaches budget
    fill = current / budget
    if fill < 0.18:
        color = (105, 179, 76)
    elif fill < 0.36:
        color = (172, 179, 52)
    elif fill < 0.54:
        color = (250, 183, 51)
    elif fill < 0.72:
        color = (255, 142, 21)
    elif fill < 0.9:
        color = (255, 78, 17)
    else:
        color = (255, 13, 13)
    # color bar chart
    with Image.open(path) as im:
        pixels = im.load()
        width, height = im.size
        for i in range(int(width*buffer*min(fill, 1))):
            for j in range(int(height*bezel), int(height*(1-bezel))):
                pixels[i, j] = color
        if fill < 1:
            for i in range(int(width*buffer*fill), int(width*buffer)+1):
                for j in range(int(height*bezel), int(height*(1-bezel))):
                    pixels[i, j] = (160, 160, 160)
        im.save(path)

# get current food spending from db + google
# print(total_cat_in_month("food"))

# create new bar chart if background changes
# new_bar(8808, 100)

# color in bar based on % of budget spent
color(100, 500)

# paste bar chart to desktop background
# update with crontab

