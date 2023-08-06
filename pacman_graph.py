#!/usr/bin/python3

import json
import sys
import os
import argparse
import math
from PIL import Image, ImageDraw, ImageFont

def normalize(data: dict) -> tuple[float, dict, float]:
    total_num = \
        sum(c['value'] for c in data['pacman-main']) +\
        sum(c['value'] for c in data['pacman-eye']) +\
        sum(c['value'] for c in data['pacman-ghosts'])
    total_ref = total_num
    normalized_data = data.copy()
    for key in ['pacman-main', 'pacman-eye', 'pacman-ghosts']:
        for item in normalized_data[key]:
            if 'ref' in item:
                total_ref = item['value'] / item['ref']
            item['value'] /= total_num
    mul = total_num / total_ref
    return total_num, normalized_data, mul

def drawPacmanMain(draw: ImageDraw, pacman_main: list, pacman_eye: list, eye_title: str, mul: float):
    eye_ratio = sum(c['value'] for c in pacman_eye)
    main_ratio = sum(c['value'] for c in pacman_main) + eye_ratio
    pacman_main_sorted = sorted(pacman_main, key = lambda item: item['value'], reverse=True)
    current_angle = 360 - 360 * (1-main_ratio) / 2
    font = ImageFont.truetype('C:\\Windows\\Fonts\\Deng.ttf', 40)
    font2 = ImageFont.truetype('C:\\Windows\\Fonts\\arialbd.ttf', 50)

    for idx, item in enumerate(pacman_main_sorted):
        ratio = item['value']
        draw_ratio = ratio
        if idx == 0:
            draw_ratio += sum(c['value'] for c in pacman_eye)
        color = (255, 255, 0)
        delta_angle = 360 * draw_ratio
        draw.pieslice([100, 100, 900, 900], start=current_angle - delta_angle, end=current_angle, fill=color, outline=(0,0,0))

        if idx == 0:
            font_angle = 2 * math.pi - (current_angle - delta_angle * 0.6) / 180 * math.pi
        else:
            font_angle = 2 * math.pi - (current_angle - delta_angle * 0.5) / 180 * math.pi
        font_cx = 500 + 250 * math.cos(font_angle)
        font_cy = 500 - 250 * math.sin(font_angle)
        _, _, w, h = draw.textbbox((0, 0), item['name'], font=font)
        # if idx == 0:
        draw.text((font_cx - w/2, font_cy - h/2), item['name'], (0,0,0), align='center', font=font)
        ratio_str = f'{int(math.ceil(ratio*1000*mul))/10}%'
        _, _, w, h = draw.textbbox((0, 0),ratio_str, font=font)
        draw.text((font_cx - w/2-15, font_cy - h/2 + 40), ratio_str, (0,0,0), align='center', font=font2)
        current_angle -= delta_angle

    eye_radius = math.sqrt(eye_ratio) * 400
    eye_angle = 0
    for idx, item in enumerate(pacman_eye):
        ratio = item['value']
        relative_ratio = ratio / eye_ratio
        if len(pacman_eye) % 2 == 0:
            if idx % 2 == 0:
                color = (0,0,0)
            else:
                color = (128,128,128)
        else:
            if idx % 3 == 0:
                color = (0,0,0)
            elif idx % 3 == 1:
                color = (64,64,64)
            else:
                color = (128,128,128)
        draw.pieslice([550 - eye_radius, 300 - eye_radius, 550 + eye_radius, 300 + eye_radius], start=eye_angle, end=eye_angle + relative_ratio * 360, fill=color)
        eye_angle += relative_ratio * 360


    _, _, w, h = draw.textbbox((0, 0), eye_title, font=font)
    # if idx == 0:
    draw.text((550 - w/2, 220 - eye_radius - h/2), eye_title, (0,0,0), align='center', font=font)
    ratio_str = f'{int(math.ceil(eye_ratio*1000*mul))/10}%'
    _, _, w, h = draw.textbbox((0, 0),ratio_str, font=font)
    draw.text((550 - w/2-15, 220 - eye_radius - h/2 + 40), ratio_str, (0,0,0), align='center', font=font2)

    eye_str = f'* {eye_title}包括: '
    for idx, item in enumerate(pacman_eye):
        eye_str += f"{item['name']} ({int(math.ceil(item['value']*1000*mul))/10}%)"
        if idx != len(pacman_eye) - 1:
            eye_str += ', '
    draw.text((800, 800), eye_str, (255, 255, 255), align='left', font=font)

    return main_ratio + eye_ratio

def appendGhost(img: Image, draw: ImageDraw, ghost: Image, center_x: float, center_y: float, radius: float, name: str, ratio: float, idx: int, mul: float, ghost0_radius: float):
    ghost_resize = ghost.resize((int(radius*2), int(radius*2)))
    img.paste(ghost_resize, (int(center_x - radius), int(center_y - radius)), ghost_resize)
    ratio_str = f'{int(math.ceil(ratio*1000*mul))/10}%'
    font = ImageFont.truetype('C:\\Windows\\Fonts\\Deng.ttf', int(math.sqrt(ratio) * 250))
    font2 = ImageFont.truetype('C:\\Windows\\Fonts\\arialbd.ttf', int(math.sqrt(ratio) * 250))
    _, _, w, h = draw.textbbox((0, 0), name, font=font)
    draw.text((center_x - w/2, center_y - h/2 + ghost0_radius * 1.7), name, (255,255,255), align='center', font=font)
    _, _, w, h = draw.textbbox((0, 0), ratio_str, font=font)
    draw.text((center_x - w/2, center_y - h/2 - ghost0_radius * 1.4), ratio_str, (255,255,255), align='center', font=font2)

def drawGhosts(img: Image, draw: ImageDraw, pacman_ghost: list, mul: float, center_x: float):
    # 不包括ghost图片周围的空白部分
    ghost_img = Image.open('./ghost.png')
    full_circle_area = math.pi * 400 * 400
    ghost_ratio = 0.711
    pacman_ghost_sorted = sorted(pacman_ghost, key = lambda item: 0 if item['name'] == '其他' else item['value'], reverse=True)
    ghost0_area = full_circle_area * pacman_ghost_sorted[0]['value'] / ghost_ratio
    ghost0_radius = math.sqrt(ghost0_area) / 2
    for idx, item in enumerate(pacman_ghost_sorted):
        ghost_area = full_circle_area * item['value'] / ghost_ratio
        ghost_radius = math.sqrt(ghost_area) / 2
        center_x += ghost_radius * 1.25
        appendGhost(img, draw, ghost_img, center_x, 480, ghost_radius, item['name'], item["value"], idx, mul, ghost0_radius)
        center_x += ghost_radius * 1.25

def pacmanGraph(data: dict) -> Image:
    total_num, normalized_data, mul = normalize(data)
    image = Image.new('RGB', (2800, 1000))
    draw = ImageDraw.Draw(image)
    main_ratio = drawPacmanMain(draw, normalized_data['pacman-main'], normalized_data['pacman-eye'], normalized_data['eye-title'], mul)
    angle = 2 * math.pi * (1 - main_ratio)
    center_x = 400 * math.cos(angle / 2) + 500
    center_x_2 = 180 / math.tan(angle / 2) + 500
    drawGhosts(image, draw, normalized_data['pacman-ghosts'], mul, max(min(center_x_2, center_x), 600))
    title_str = f"{data['title']} ( 1% = {int(total_num / 100 / mul)} {data['unit']} )"
    font = ImageFont.truetype('C:\\Windows\\Fonts\\simkai.ttf', 75)
    draw.text((800, 150), title_str, (255, 255, 255), align='left', font=font)
    return image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="./data.json",
                        help="Pacman图数据源")
    parser.add_argument("--output", default="./pacman.png",
                        help="输出路径")
    args = parser.parse_args()
    if not os.path.exists(args.database):
        print(f'数据源 {args.database} 不存在')
    with open(args.database,'r',encoding='utf8') as data:
        json_data = json.load(data)
        image = pacmanGraph(json_data)
        image.save(args.output)
