# -*- coding: utf-8 -*-

from io import BytesIO

from PIL import ImageFont, ImageDraw, Image

from functions import get_day_week
from helper import int_to_day

def image_food_dict(school_name, food_dicts):
    """
    한 달 급식 정보를 이미지화 해주는 함수.

    :param school_name: string, 학교 이름.
    :param food_dicts: tuple(int, dict), get_food_info에서 제공하는 dict를 가져와야함.

    :return: io.BytesIO. 이미지.
    """

    title_font_size = 60
    content_font_size = 25

    title_f = ImageFont.truetype("font/malgunbd.ttf", title_font_size)
    content_f = ImageFont.truetype("font/malgunsl.ttf", content_font_size)

    top_margin = 300
    bottom_margin = 160
    left_margin = 140
    right_margin = 140

    line_width = 3
    box_width = 250
    box_height = 300
    box_margin = 10
    week_box_height = content_font_size + box_margin * 2

    first_date = food_dicts[1][0]['food_date']
    last_date = food_dicts[1][-1]['food_date']
    first_day = get_day_week(first_date)
    last_day = get_day_week(last_date)
    week_length = int((first_day + int(last_date) - int(first_date)) / 7 + 1)

    table = list()

    for i in range(week_length):
        table.append([None]*7)
        
    assign_day = first_day
    assign_week = 0
    week_presence = []
    previous_date = first_date
    box_max_height = 0

    food_type = food_dicts[1][0]['food_name']
    food_year = int(food_dicts[1][0]['food_date'][0:4])
    food_month = int(food_dicts[1][0]['food_date'][4:6])

    for food_dict in food_dicts[1]:
        assign_day += int(food_dict['food_date']) - int(previous_date)

        while assign_day >= 7:
            assign_day -= 7
            assign_week += 1
            
        food_dict['food_info'] = food_dict['food_info'].replace("<br/>", "\n")

        food_date = food_dict['food_date'][6:8]

        text = f"{food_date}\n\n{food_dict['food_info']}"

        text = text_wrap(text, content_f, box_width - 2 * box_margin)

        text_height = content_f.getsize_multiline(text)[1] + 2 * box_margin
        
        if text_height > box_max_height:
            box_max_height = text_height

        table[assign_week][assign_day] = text

        previous_date = food_dict['food_date']
        
        if assign_day not in week_presence:
            week_presence.append(assign_day)

    box_height = box_max_height

    week_presence.sort()

    background_width = left_margin + right_margin + len(week_presence) * box_width
    background_height = top_margin + bottom_margin + (len(table)) * box_height + week_box_height

    background = Image.new("L", (background_width, background_height), 255)

    draw = ImageDraw.Draw(background)

    for i in range(len(week_presence)+1):
        draw.line((left_margin+box_width*i, top_margin, left_margin+box_width*i, background_height-bottom_margin), width=line_width)

    draw.line((left_margin, top_margin, background_width-right_margin, top_margin))

    for i in range(week_length+1):
        draw.line((left_margin, top_margin+week_box_height+box_height*i, background_width-right_margin, top_margin+week_box_height+box_height*i), width=line_width)

    title = text_wrap(f"{school_name} {food_year}년 {food_month}월 {food_type}", title_f, background_width - left_margin - right_margin)
    draw.multiline_text((background_width*0.5, top_margin*0.5), title, font=title_f, fill=0, anchor="mm", align="center")
    
    for i in range(len(week_presence)):
        draw.text((left_margin+box_width*(0.5+i), top_margin+box_margin), int_to_day[week_presence[i]], font=content_f, fill=0, anchor="mt")

    for i in range(len(table)):
        for j in range(len(week_presence)):
            if table[i][week_presence[j]] is None:
                continue
            
            draw.multiline_text((left_margin+box_width*(j+0.5), top_margin+week_box_height+box_height*i+box_margin), table[i][week_presence[j]], font=content_f, fill=0, anchor="ma", align="center")

    file = BytesIO()
    background.save(file, "PNG")
    file.seek(0)

    return file

def text_wrap(text, font, max_width):
    lines = []

    if font.getsize(text)[0] <= max_width:
        return text

    for text_line in text.split("\n"):
        if font.getsize(text_line)[0] <= max_width:
            lines.append(text_line)

        else:
            prev_i = 0
            line = ""
            for i in range(len(text_line)):
                line = text_line[prev_i:i+1]
                if font.getsize(line)[0] > max_width:
                    lines.append(text_line[prev_i:i])
                    prev_i = i
                    continue

                if i == len(text_line) - 1 :
                    lines.append(text_line[prev_i:i])

    wrapped_text = "\n".join(lines)
    return wrapped_text