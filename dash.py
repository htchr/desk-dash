#!/Users/jack/Documents/projects/22-dash/venv/bin/python3

import datetime
import gspread
import sqlite3
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import subprocess

db = "/Users/jack/Documents/logs/money.db" 
background = "/Users/jack/Pictures/background/background.jpeg"
bar = "/Users/jack/Documents/projects/22-dash/bar.jpeg"
menlo = "/Users/jack/Library/Fonts/Menlo-Regular.ttf"
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

def new_bar(height, back_path=background, path=bar):
    """
    back_path: string file path location to desktop background
    path: sting file path location to save the image
    returns: n/a
    """
    with Image.open(back_path) as back:
        width = back.size[0]
    im = Image.new(mode="RGB", size=(width, height))
    im.save(path)

def color_bar(current, budget, cat, path=bar):
    """
    current: int / float of current spending
    budget: int of max spending per month
    cat: string of spending category
    path: string of file path to image
    returns: n/a
    """
    # settings:
    bezel = 0.3
    buffer = 0.96
    spacing = 100
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
    try:
        with Image.open(path) as im:
            pixels = im.load()
            width, height = im.size
            for i in range(int(width * buffer * min(fill, 1))):
                for j in range(int(height * bezel), int(height * (1-bezel))):
                    pixels[i, j] = color
            if fill < 1:
                for i in range(int(width * buffer * fill), int(width * buffer)+1):
                    for j in range(int(height * bezel), int(height * (1-bezel))):
                        pixels[i, j] = (160, 160, 160)
            for i in range(int(width * buffer) + 1, width):
                for j in range(height):
                    pixels[i, j] = (0, 0, 0)
            font = ImageFont.truetype(menlo, 75)
            draw = ImageDraw.Draw(im)
            draw.text((int(width * buffer + spacing), 0), 
                      str(current) + cat[0], font=font, fill=(255, 255, 255))
            im.save(path)
    except OSError:
        new_bar(80)
        color_bar(current, budget, cat)

def paste_bar(height, bar_path=bar, back_path=background):
    with Image.open(r"{}".format(background)) as back:
        with Image.open(r"{}".format(bar)) as im:
            back.paste(im, (0, height))
        back.save(back_path)

def set_background(back_path=background):
    # source: https://pastebin.com/wHr1pV7k
    try:
        SCRIPT = """/usr/bin/osascript<<END
                 tell application "Finder"
                 set desktop picture to POSIX file "%s"
                 end tell
                 END"""
        subprocess.Popen(SCRIPT%back_path, shell=True)
    except:
        return False

current = int(total_cat_in_month("food"))
color_bar(current, 600, "food")
paste_bar(6383)
# 6380
set_background()

