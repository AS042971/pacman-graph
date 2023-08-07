#!/usr/bin/python3

import json
import os
import argparse

item_rules = {
    '命运-冠位指定': '命运-\n冠位指定',
    'Nikke胜利女神': 'Nikke\n胜利女神',
    '火影忍者疾风传（泛二次元手游）': '火影忍者\n疾风传',
    '重返未来1999': '重返未来\n1999',
    '偶像梦幻祭2': '偶像\n梦幻祭2',
    '光与夜之恋': '光与夜\n之恋'
}

def handleData(data: str) -> object:
    title = data[0].strip()
    unit = data[1].strip()
    main_obj = []
    eye_obj = []
    ghosts_obj = []
    others_obj = []

    for line_idx in range(2, len(data)):
        line = data[line_idx].strip()
        if line == '':
            break
        items = line.split('\t')
        item_name = items[0].strip()
        if item_name in item_rules:
            item_name = item_rules[item_name]
        obj = {
            'name': item_name,
            'value': float(items[1])
        }
        if items[2] == 'A':
            main_obj.append(obj)
        elif items[2] == 'B':
            eye_obj.append(obj)
        elif items[2] == 'C':
            ghosts_obj.append(obj)
        else:
            others_obj.append(obj)

    return {
        "title": title,
        "unit": unit,
        "eye-title": "其他米哈游游戏",
        "others-title": "其他游戏",
        "pacman-main": main_obj,
        "pacman-eye": eye_obj,
        "pacman-ghosts": ghosts_obj,
        "pacman-others": others_obj
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="./data.txt",
                        help="文本格式数据库")
    parser.add_argument("--database", default="./data.json",
                        help="json格式数据库")
    args = parser.parse_args()
    if not os.path.exists(args.source):
        print(f'数据源 {args.source} 不存在')
    with open(args.source,'r',encoding='utf8') as data:
        all_data = data.readlines()
        json_data = handleData(all_data)
        with open(args.database, 'w', encoding='utf8') as database:
            json.dump(json_data, database, ensure_ascii=False, indent=2)
