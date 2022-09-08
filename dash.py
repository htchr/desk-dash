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
    # get total spending of cat from google sheets
    try:
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
    # if google api is down return None
    except:
        return None
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

def color_bar(current, budget, cat, starting_height, bar_height, color, neutral_fill_color = (160, 160, 160), background_color = (0,0,0), back_path=back_path, bezel = 0.35, buffer = 0.96, spacing = 30):
    """
    draw multiple bar charts across the desktop background
    ---
    cuurent: int of current value of category
    budget: int of max value for category
    cat: string name of category
    starting_height: int where bar chart should begin (0,0 at top left corner)
    bar_height: int of the height of the bar chart
    color: tuple (r, g, b) of the fill color
    neutral_fill_color: tuple (r, g, b) of the remainer fill color
    background_color: tuple (r, g, b) of the border area around the bar chart
    back_path: string filepath for the background template file
    bezel: float of the percentage reserved for background around the bar chart
    buffer: float of the percentage of width reserved for text at the end
    spacing: int of the number of pixels between bar chart and text
    returns: n/a
    """
    with Image.open(back_path) as im:
        pixels = im.load()
        width, height = im.size
        for bar in range(len(current)):
            fill = min(current[bar] / budget[bar], 1)
            # fill in bar background:
            for i in range(width):
                for j in range(starting_height[bar], starting_height[bar] + bar_height[bar]):
                    pixels[i, j] = background_color
            # fill in bar chart
            for i in range(int(width * buffer * fill)):
                for j in range(starting_height[bar] + int(bar_height[bar] * bezel), 
                            starting_height[bar] + int(bar_height[bar] * (1-bezel))):
                    pixels[i, j] = color[bar]
            # fill in remainer as gray
            for i in range(int(width * buffer * fill), int(width * buffer)+1):
                for j in range(starting_height[bar] + int(bar_height[bar] * bezel), 
                            starting_height[bar] + int(bar_height[bar] * (1-bezel))):
                    pixels[i, j] = neutral_fill_color
            font = ImageFont.truetype(menlo, 20)
            draw = ImageDraw.Draw(im)
            draw.text((int(width * buffer + spacing), starting_height[bar]),
                    str(current[bar]) + cat[bar][0], font=font, fill=(255, 255, 255))
        os.system("rm {}*.jpeg".format(save_path))
        now = datetime.datetime.now()
        name = "{}{}{}{}.jpeg".format(now.day, now.hour, now.minute, now.second)
        im.save(save_path + name)

current = total_cat_in_month("food")
cc = cc_spending()
if current != None and cc != None:
    color = color_picker(current, 500)
    color_bar((current, cc), (500, 1000), ("food", "cc"), 
              (1942, 1920), (22, 22), (color, (255, 255, 255)))

