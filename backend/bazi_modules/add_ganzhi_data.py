#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加天干地支作用关系数据到数据库
"""

import re

# 读取原始数据文件
with open('ganzhi_data_raw.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 解析数据
# 每个命理组合以"命理组合\t核心概念\t心理特质\t积极作用\t消极作用\t行为模式\t成长建议"格式存储

lines = content.strip().split('\n')

# 生成Python代码
output_lines = []
output_lines.append('        # ============ 拱会局 ============')
output_lines.append('')

current_section = None

for line in lines:
    line = line.strip()
    if not line:
        continue
    
    # 检测章节标题
    if line.startswith('寅辰拱会卯木'):
        output_lines.append('')
        output_lines.append('        # ============ 拱会局 ============')
        output_lines.append('')
    elif line.startswith('申子辰合水局'):
        output_lines.append('')
        output_lines.append('        # ============ 三合局 ============')
        output_lines.append('')
    elif line.startswith('亥卯半合木'):
        output_lines.append('')
        output_lines.append('        # ============ 半合局 ============')
        output_lines.append('')
    elif line.startswith('子丑合化土'):
        output_lines.append('')
        output_lines.append('        # ============ 六合 ============')
        output_lines.append('')
    elif line.startswith('寅丑暗合'):
        output_lines.append('')
        output_lines.append('        # ============ 暗合 ============')
        output_lines.append('')
    elif line.startswith('子午六冲'):
        output_lines.append('')
        output_lines.append('        # ============ 六冲 ============')
        output_lines.append('')
    elif line.startswith('寅巳申三刑'):
        output_lines.append('')
        output_lines.append('        # ============ 三刑 ============')
        output_lines.append('')
    elif line.startswith('辰辰 / 午午 / 酉酉 / 亥亥自刑'):
        output_lines.append('')
        output_lines.append('        # ============ 自刑 ============')
        output_lines.append('')
    elif line.startswith('子酉六破'):
        output_lines.append('')
        output_lines.append('        # ============ 六破 ============')
        output_lines.append('')
    elif line.startswith('子未六害'):
        output_lines.append('')
        output_lines.append('        # ============ 六害 ============')
        output_lines.append('')
    elif line.startswith('甲己合化土'):
        output_lines.append('')
        output_lines.append('        # ============ 天干五合 ============')
        output_lines.append('')
    elif line.startswith('甲木克戊土'):
        output_lines.append('')
        output_lines.append('        # ============ 天干相克 ============')
        output_lines.append('')
    elif line.startswith('甲木生丙火'):
        output_lines.append('')
        output_lines.append('        # ============ 天干相生 ============')
        output_lines.append('')
    elif line.startswith('天干五合合绊核心规则'):
        output_lines.append('')
        output_lines.append('        # ============ 天干五合合绊 ============')
        output_lines.append('')
    elif line.startswith('甲庚相冲'):
        output_lines.append('')
        output_lines.append('        # ============ 天干相冲 ============')
        output_lines.append('')
    
    # 解析数据行
    parts = line.split('\t')
    if len(parts) >= 7:
        name = parts[0].strip()
        core_concept = parts[1].strip()
        psychological = parts[2].strip()
        positive_effect = parts[3].strip()
        negative_effect = parts[4].strip()
        behavior = parts[5].strip()
        advice = parts[6].strip()
        
        # 生成_add_relation调用
        output_lines.append(f"        self._add_relation(")
        output_lines.append(f"            '{name}',")
        output_lines.append(f"            '{core_concept}',")
        output_lines.append(f"            '{psychological}',")
        output_lines.append(f"            '{positive_effect}',")
        output_lines.append(f"            '{negative_effect}',")
        output_lines.append(f"            '{behavior}',")
        output_lines.append(f"            '{advice}'")
        output_lines.append(f"        )")
        output_lines.append("")

# 写入输出文件
with open('ganzhi_data_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("数据解析完成，已生成 ganzhi_data_output.txt")
