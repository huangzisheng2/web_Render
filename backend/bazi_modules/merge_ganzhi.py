#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并ganzhi_relation_database到zonghe_database的脚本
"""

def merge_files():
    # 读取ganzhi_relation_database.py的内容
    with open('ganzhi_relation_database.py', 'r', encoding='utf-8') as f:
        ganzhi_content = f.read()
    
    # 提取类定义
    class_start = ganzhi_content.find('class GanZhiRelationInfo:')
    main_start = ganzhi_content.find("if __name__ == '__main__':")
    if main_start == -1:
        main_start = len(ganzhi_content)
    
    classes_code = ganzhi_content[class_start:main_start].rstrip()
    
    # 移除末尾的注释和空行
    if '# 创建全局数据库实例' in classes_code:
        classes_code = classes_code[:classes_code.rfind('# 创建全局数据库实例')].rstrip()
    
    # 读取zonghe_database.py的内容
    with open('zonghe_database.py', 'r', encoding='utf-8') as f:
        zonghe_content = f.read()
    
    # 移除导入语句
    zonghe_content = zonghe_content.replace(
        '# 导入天干地支作用关系数据库\nfrom ganzhi_relation_database import GanZhiRelationDatabase, ganzhi_relation_db\n\n',
        ''
    )
    
    # 移除对ganzhi_relation_db的引用
    zonghe_content = zonghe_content.replace(
        '# 初始化天干地支作用关系数据库\n        self.ganzhi_relation_db = ganzhi_relation_db',
        '# 初始化天干地支作用关系数据库\n        self.ganzhi_relation_db = GanZhiRelationDatabase()'
    )
    
    # 在RiZhuInfo类之前插入GanZhiRelationInfo和GanZhiRelationDatabase类
    rizhu_info_pos = zonghe_content.find('class RiZhuInfo:')
    
    new_content = (
        zonghe_content[:rizhu_info_pos] + 
        classes_code + 
        '\n\n\n' + 
        zonghe_content[rizhu_info_pos:]
    )
    
    # 保存合并后的文件
    with open('zonghe_database_merged.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("合并完成！新文件: zonghe_database_merged.py")
    print(f"原文件行数: {len(zonghe_content.split(chr(10)))}")
    print(f"新文件行数: {len(new_content.split(chr(10)))}")

if __name__ == '__main__':
    merge_files()
