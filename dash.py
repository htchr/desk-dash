#!/Users/jack/Documents/projects/22-dash/venv/bin/python3

import datetime
import gspread
import sqlite3
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os
import sys
dolla = "/Users/jack/Documents/projects/22-dolla/"
sys.path.append(dolla)
from money import get_cats

db = "/Users/jack/Documents/logs/money.db" 
menlo = "/Users/jack/Library/Fonts/Menlo-Regular.ttf"
back_path = "/Users/jack/Pictures/backgrounds/background.jpeg"
save_path = "/Users/jack/Pictures/background/"

def total_cat_in_month(cat, year=0, month=0):
    """
    sum all spending of a category within a given month
    search across google sheets money sheet and money.db
    ---
    cat: string of category to search for
    year: int of year to search in
    month: int of month to search in
    returns: int total of all spending of cat in year, month / None if google api is down
    """
    if year == 0 or month == 0:
        now = datetime.date.today()
        year = now.year
        month = now.month
    total = 0
    if cat == "month":
        cats = get_cats("out")
    else:
        cats = [cat]
    # get total spending of cat from google sheets
    try:
        sa = gspread.service_account()
        sh = sa.open("money")
        wks = sh.worksheet("flow")
        rows = wks.get_all_values()[1:]
        for c in cats:
            for r in rows:
                try: # there may be rows with empty values
                    if int(r[4][:4]) == year and int(r[4][4:6]) == month and r[5].strip() == c:
                        total += float(r[0])
                except:
                    continue
    # if google api is down return None
    except:
        return None
    # get total spending of cat from money.db
    con = sqlite3.connect(db)
    cur = con.cursor()
    for c in cats:
        cur.execute("""SELECT * FROM flow WHERE 
                       year = ?
                       AND month = ?
                       AND cat = ?""",
                    (year, month, c))
        for r in cur.fetchall():
            total += r[1]
    con.close()
    return int(total)

def cc_spending():
    """
    returns: total current spending on my credit card / None
    """
    try:
        sa = gspread.service_account()
        sh = sa.open("money")
        wks = sh.worksheet("cc")
        cc = wks.acell("A1").value
        cc = float(cc)
        return(int(cc))
    except:
        return None

def color_picker(current, budget):
    """
    gradient green to red as current spending reaches budget
    ---
    current: int of the current value of category
    budget: int of max value of category
    returns: tuple (r, g, b) of color selection
    """
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
    return color

def bar(im, pixels, current, budget, cat, starting_height, width, color, 
        neutral_fill_color=(160,160,160), background_color=(0,0,0), bar_height=22, font_height=20,
        bezel=0.35, buffer=0.96, spacing=30):
    """
    draw a bar chart across the desktop
    ---
    im: image from PIL.Image.open(image_path)
    pixels: im.load() from PIL
    cuurent: int of current value of category
    budget: int of max value for category
    cat: string name of category
    starting_height: int where bar chart should begin (0,0 at top left corner)
    bar_height: int of the height of the bar chart
    width: int of the width of the bar chart
    color: tuple (r, g, b) of the fill color
    neutral_fill_color: tuple (r, g, b) of the remainer fill color
    background_color: tuple (r, g, b) of the border area around the bar chart
    returns: n/a
    """
    fill = min(current / budget, 1)
    # fill in bar background:
    for i in range(width):
        for j in range(starting_height, starting_height + bar_height):
            pixels[i, j] = background_color
    # fill in bar chart
    for i in range(int(width * buffer * fill)):
        for j in range(starting_height + int(bar_height * bezel), 
                       starting_height + int(bar_height * (1-bezel))):
            pixels[i, j] = color
    # fill in remainer as gray
    for i in range(int(width * buffer * fill), int(width * buffer)+1):
        for j in range(starting_height + int(bar_height * bezel), 
                       starting_height + int(bar_height * (1-bezel))):
            pixels[i, j] = neutral_fill_color
    font = ImageFont.truetype(menlo, font_height)
    draw = ImageDraw.Draw(im)
    draw.text((int(width * buffer + spacing), starting_height),
              str(current) + cat[0], font=font, fill=(255, 255, 255))

def draw():
    """
    draw multiple functions on the desktop background
    ---
    returns: n/a
    """
    with Image.open(back_path) as im:
        pixels = im.load()
        width, height = im.size
        # total monthly spending
        month = total_cat_in_month("month")
        month_color = color_picker(month, 2000)
        bar(im, pixels, month, 2000, "month", 1942, width, month_color)
        # food spending bar chart
        food = total_cat_in_month("food")
        food_color = color_picker(food, 500)
        bar(im, pixels, food, 500, "food", 1920, width, food_color)
        # cc spending bar chart
        cc = cc_spending()
        cc_color = (255, 255, 255)
        bar(im, pixels, cc, 1000, "cc", 1898, width, cc_color)
        # marching bars
        # save image
        os.system("rm {}*.jpeg".format(save_path))
        now = datetime.datetime.now()
        name = "{}{}{}{}.jpeg".format(now.day, now.hour, now.minute, now.second)
        im.save(save_path + name)

if __name__ == "__main__":
    draw()
