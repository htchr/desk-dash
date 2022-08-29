#!/Users/jack/Documents/projects/22-dash/venv/bin/python3

import datetime
import gspread
import sqlite3
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os

db = "/Users/jack/Documents/logs/money.db" 
menlo = "/Users/jack/Library/Fonts/Menlo-Regular.ttf"
back_path = "/Users/jack/Pictures/backgrounds/background.jpeg"
bar_path = "/Users/jack/Documents/projects/22-dash/bar.jpeg"
save_path = "/Users/jack/Pictures/background/"

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

def new_bar(height, back_path=back_path, bar_path=bar_path):
    """
    save a new canvas for the bar chart
    the width is the same as the background image
    ---
    height: int of the vertical pixel height of the image
    back_path: string file path location to desktop back_path
    bar_path: sting file path location to save the image
    returns: n/a
    """
    with Image.open(back_path) as back:
        width = back.size[0]
    im = Image.new(mode="RGB", size=(width, height))
    im.save(bar_path)

def color_bar(current, budget, cat, height, bar_path=bar_path):
    """
    color in the bar chart according to current spending
    gradiate from green to red as spending approches budget
    ---
    current: int / float of current spending
    budget: int of max spending per month
    cat: string of spending category
    bar_path: string of file path to image
    returns: n/a
    """
    # settings:
    bezel = 0.35
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
        with Image.open(bar_path) as im:
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
            im.save(bar_path)
    # if bar chart doesn't exist, create it and run again
    except OSError:
        new_bar(height)
        color_bar(current, budget, cat, height)

def paste_bar(height, bar_path=bar_path, back_path=back_path, save_path=save_path):
    """
    open an existing background image
    paste the bar chart according to the height parameter
    save as a copy in new directory
    ---
    height: int of pixel height to paste the bar on the background
    bar_path: string of filepath to the barchart jpeg
    back_path: string of filepath to the background image to copy
    save_path: string of filepath where to save the new background with barchart
    """
    with Image.open(r"{}".format(back_path)) as back:
        with Image.open(r"{}".format(bar_path)) as im:
            back.paste(im, (0, height))
        now = datetime.datetime.now()
        name = "{}{}{}{}.jpeg".format(now.day, now.hour, now.minute, now.second)
        back.save(save_path + name)

# get current spending of category for this month
current = int(total_cat_in_month("food"))
# fill in bar chart to fit current spending
color_bar(current, 500, "food", 80)
# remove old background image
os.system("rm {}*.jpeg".format(save_path))
# save new background image
# 6383 = bottom of mac screen
# 960 = top of screen
paste_bar(6385)

