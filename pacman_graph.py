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

    for idx, item in enumerate(pacman_main_sorted):
        ratio = item['value']
        if idx == 0:
            ratio += sum(c['value'] for c in pacman_eye)
        if idx % 2 == 0:
            color = (255, 255, 0)
        else:
            color = (255, 255, 32)
        delta_angle = 360 * ratio
        draw.pieslice([100, 100, 900, 900], start=current_angle - delta_angle, end=current_angle, fill=color, outline=(0,0,0))

        font_angle = 2 * math.pi - (current_angle - delta_angle / 2) / 180 * math.pi
        font_cx = 500 + 250 * math.cos(font_angle)
        font_cy = 500 - 250 * math.sin(font_angle)
        _, _, w, h = draw.textbbox((0, 0), item['name'], font=font)
        # if idx == 0:
        draw.text((font_cx - w/2, font_cy - h/2), item['name'], (0,0,0), align='center', font=font)
        ratio_str = f'{int(ratio*1000*mul)/10}%'
        _, _, w, h = draw.textbbox((0, 0),ratio_str, font=font)
        draw.text((font_cx - w/2, font_cy - h/2 + 40), ratio_str, (0,0,0), align='center', font=font)
        current_angle -= delta_angle

    eye_radius = math.sqrt(eye_ratio) * 400
    eye_angle = 0
    for idx, item in enumerate(pacman_eye):
        ratio = item['value']
        relative_ratio = ratio / eye_ratio
        if idx % 2 == 0:
            color = (0,0,0)
        else:
            color = (128,128,128)
        draw.pieslice([550 - eye_radius, 300 - eye_radius, 550 + eye_radius, 300 + eye_radius], start=eye_angle, end=eye_angle + relative_ratio * 360, fill=color)
        eye_angle += relative_ratio * 360

    _, _, w, h = draw.textbbox((0, 0), eye_title, font=font)
    # if idx == 0:
    draw.text((550 - w/2, 200 - h/2), eye_title, (0,0,0), align='center', font=font)
    ratio_str = f'{int(eye_ratio*1000*mul)/10}%'
    _, _, w, h = draw.textbbox((0, 0),ratio_str, font=font)
    draw.text((550 - w/2, 200 - h/2 + 40), ratio_str, (0,0,0), align='center', font=font)

def appendGhost(img: Image, draw: ImageDraw, ghost: Image, center_x: float, center_y: float, radius: float, name: str, ratio: float, idx: int, mul: float):
    ghost_resize = ghost.resize((int(radius*2), int(radius*2)))
    img.paste(ghost_resize, (int(center_x - radius), int(center_y - radius)), ghost_resize)
    ratio_str = f'{int(ratio*1000*mul)/10}%'
    font = ImageFont.truetype('C:\\Windows\\Fonts\\Deng.ttf', int(math.sqrt(ratio) * 250))
    _, _, w, h = draw.textbbox((0, 0), name, font=font)
    draw.text((center_x - w/2, center_y - h/2 + 150), name, (255,255,255), align='center', font=font)
    _, _, w, h = draw.textbbox((0, 0), ratio_str, font=font)
    draw.text((center_x - w/2, center_y - h/2 - 120), ratio_str, (255,255,255), align='center', font=font)

def drawGhosts(img: Image, draw: ImageDraw, pacman_ghost: list, mul: float):
    # 不包括ghost图片周围的空白部分
    ghost_img = Image.open('./ghost.png')
    full_circle_area = math.pi * 400 * 400
    ghost_ratio = 0.711
    pacman_ghost_sorted = sorted(pacman_ghost, key = lambda item: 0 if item['name'] == '其他' else item['value'], reverse=True)
    center_x = 650
    for idx, item in enumerate(pacman_ghost_sorted):
        ghost_area = full_circle_area * item['value'] / ghost_ratio
        ghost_radius = math.sqrt(ghost_area) / 2
        center_x += ghost_radius * 1.25
        appendGhost(img, draw, ghost_img, center_x, 480, ghost_radius, item['name'], item["value"], idx, mul)
        center_x += ghost_radius * 1.25

def pacmanGraph(data: dict) -> Image:
    total_num, normalized_data, mul = normalize(data)
    image = Image.new('RGB', (2800, 1000))
    draw = ImageDraw.Draw(image)
    drawPacmanMain(draw, normalized_data['pacman-main'], normalized_data['pacman-eye'], normalized_data['eye-title'], mul)
    drawGhosts(image, draw, normalized_data['pacman-ghosts'], mul)
    title_str = f"{data['title']}( 1% = {int(total_num / 100 / mul)} {data['unit']} )"
    font = ImageFont.truetype('C:\\Windows\\Fonts\\Deng.ttf', 75)
    draw.text((800, 150), title_str, (255, 255, 255), align='center', font=font)
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
