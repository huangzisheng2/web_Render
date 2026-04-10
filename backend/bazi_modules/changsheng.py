#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
12长生模块
实现天干地支到12长生状态的精确映射计算
"""

# 12长生对照表数据结构
# 嵌套字典：{天干: {地支: 长生状态}}
CHANGSHENG_TABLE = {
    '甲': {
        '亥': '长生', '子': '沐浴', '丑': '冠带', '寅': '临官',
        '卯': '帝旺', '辰': '衰', '巳': '病', '午': '死',
        '未': '墓', '申': '绝', '酉': '胎', '戌': '养'
    },
    '乙': {
        '午': '长生', '巳': '沐浴', '辰': '冠带', '卯': '临官',
        '寅': '帝旺', '丑': '衰', '子': '病', '亥': '死',
        '戌': '墓', '酉': '绝', '申': '胎', '未': '养'
    },
    '丙': {
        '寅': '长生', '卯': '沐浴', '辰': '冠带', '巳': '临官',
        '午': '帝旺', '未': '衰', '申': '病', '酉': '死',
        '戌': '墓', '亥': '绝', '子': '胎', '丑': '养'
    },
    '丁': {
        '酉': '长生', '申': '沐浴', '未': '冠带', '午': '临官',
        '巳': '帝旺', '辰': '衰', '卯': '病', '寅': '死',
        '丑': '墓', '子': '绝', '亥': '胎', '戌': '养'
    },
    '戊': {
        '寅': '长生', '卯': '沐浴', '辰': '冠带', '巳': '临官',
        '午': '帝旺', '未': '衰', '申': '病', '酉': '死',
        '戌': '墓', '亥': '绝', '子': '胎', '丑': '养'
    },
    '己': {
        '酉': '长生', '申': '沐浴', '未': '冠带', '午': '临官',
        '巳': '帝旺', '辰': '衰', '卯': '病', '寅': '死',
        '丑': '墓', '子': '绝', '亥': '胎', '戌': '养'
    },
    '庚': {
        '巳': '长生', '午': '沐浴', '未': '冠带', '申': '临官',
        '酉': '帝旺', '戌': '衰', '亥': '病', '子': '死',
        '丑': '墓', '寅': '绝', '卯': '胎', '辰': '养'
    },
    '辛': {
        '子': '长生', '亥': '沐浴', '戌': '冠带', '酉': '临官',
        '申': '帝旺', '未': '衰', '午': '病', '巳': '死',
        '辰': '墓', '卯': '绝', '寅': '胎', '丑': '养'
    },
    '壬': {
        '申': '长生', '酉': '沐浴', '戌': '冠带', '亥': '临官',
        '子': '帝旺', '丑': '衰', '寅': '病', '卯': '死',
        '辰': '墓', '巳': '绝', '午': '胎', '未': '养'
    },
    '癸': {
        '卯': '长生', '寅': '沐浴', '丑': '冠带', '子': '临官',
        '亥': '帝旺', '戌': '衰', '酉': '病', '申': '死',
        '未': '墓', '午': '绝', '巳': '胎', '辰': '养'
    }
}

# 12长生状态说明
CHANGSHENG_DESC = {
    '长生': '初生萌芽，生机盎然',
    '沐浴': '初涉红尘，易受诱惑',
    '冠带': '身披华服，渐入佳境',
    '临官': '当官掌权，事业有成',
    '帝旺': '如日中天，巅峰时期',
    '衰': '盛极而衰，逐渐衰退',
    '病': '疾病缠身，身体欠佳',
    '死': '寿元将尽，生命终结',
    '墓': '归入墓地，安息之所',
    '绝': '生机断绝，彻底绝望',
    '胎': '孕育新生，转机出现',
    '养': '休养生息，积蓄力量'
}


def get_changsheng(tian_gan: str, di_zhi: str) -> str:
    """
    获取指定天干地支组合对应的12长生状态
    
    参数:
        tian_gan (str): 天干，如'甲','乙','丙'等
        di_zhi (str): 地支，如'子','丑','寅'等
    
    返回:
        str: 对应的12长生状态，如'长生','沐浴'等
             如果输入无效，返回"输入错误"
    
    异常处理:
        - 无效天干地支输入返回"输入错误"
        - 缺失参数返回"输入错误"
    """
    # 参数校验
    if not isinstance(tian_gan, str) or not isinstance(di_zhi, str):
        return "输入错误"
    
    # 去除前后空格
    tian_gan = tian_gan.strip()
    di_zhi = di_zhi.strip()
    
    # 检查是否为空
    if not tian_gan or not di_zhi:
        return "输入错误"
    
    # 检查天干是否有效
    if tian_gan not in CHANGSHENG_TABLE:
        return "输入错误"
    
    # 检查地支是否有效
    if di_zhi not in CHANGSHENG_TABLE[tian_gan]:
        return "输入错误"
    
    # 返回对应的长生状态
    return CHANGSHENG_TABLE[tian_gan][di_zhi]


def xingyun(ri_zhu: str, di_zhi_list: list) -> dict:
    """
    分析日主与各柱地支的星运关系
    
    星运分析：以日主天干为基准，分析它与各柱地支之间的12长生关系
    
    参数:
        ri_zhu (str): 日主天干，如'甲','乙','丙'等
        di_zhi_list (list): 地支列表，格式为[年柱地支, 月柱地支, 日柱地支, 时柱地支]
                           如['子','丑','寅','卯']
    
    返回:
        dict: 包含各柱位置及对应长生状态的字典
              格式: {'年柱': '长生', '月柱': '沐浴', '日柱': '冠带', '时柱': '临官'}
              如果输入无效，返回空字典{}
    
    异常处理:
        - 无效日主返回空字典
        - 地支列表长度不为4返回空字典
        - 无效地支返回"输入错误"
    """
    # 参数校验
    if not isinstance(ri_zhu, str):
        return {}
    
    if not isinstance(di_zhi_list, list):
        return {}
    
    # 去除日主前后空格
    ri_zhu = ri_zhu.strip()
    
    # 检查日主是否有效
    if not ri_zhu or ri_zhu not in CHANGSHENG_TABLE:
        return {}
    
    # 检查地支列表长度
    if len(di_zhi_list) != 4:
        return {}
    
    # 柱位名称
    zhu_names = ['年柱', '月柱', '日柱', '时柱']
    
    # 结果字典
    result = {}
    
    # 遍历地支列表
    for i, di_zhi in enumerate(di_zhi_list):
        # 检查地支类型
        if not isinstance(di_zhi, str):
            result[zhu_names[i]] = "输入错误"
            continue
        
        # 去除前后空格
        di_zhi = di_zhi.strip()
        
        # 检查是否为空
        if not di_zhi:
            result[zhu_names[i]] = "输入错误"
            continue
        
        # 获取长生状态
        changsheng = get_changsheng(ri_zhu, di_zhi)
        result[zhu_names[i]] = changsheng
    
    return result


def zizuo(si_zhu_data: dict) -> dict:
    """
    分析年/月/日/时四柱的自坐关系
    
    自坐分析：计算每柱天干与本柱地支的12长生关系
    
    参数:
        si_zhu_data (dict): 四柱数据字典
                           格式: {'年柱': (天干, 地支), '月柱': (天干, 地支),
                                  '日柱': (天干, 地支), '时柱': (天干, 地支)}
                           如: {'年柱': ('甲', '子'), '月柱': ('乙', '丑'),
                                '日柱': ('丙', '寅'), '时柱': ('丁', '卯')}
    
    返回:
        dict: 包含各柱自坐长生状态的字典
              格式: {'年柱': {'组合': '甲子', '长生': '长生'},
                     '月柱': {'组合': '乙丑', '长生': '沐浴'},
                     '日柱': {'组合': '丙寅', '长生': '冠带'},
                     '时柱': {'组合': '丁卯', '长生': '临官'}}
              如果输入无效，返回空字典{}
    
    异常处理:
        - 输入不是字典返回空字典
        - 柱位不完整返回空字典
        - 柱位数据格式错误返回空字典
    """
    # 参数校验
    if not isinstance(si_zhu_data, dict):
        return {}
    
    # 检查柱位完整性
    required_keys = ['年柱', '月柱', '日柱', '时柱']
    for key in required_keys:
        if key not in si_zhu_data:
            return {}
    
    # 结果字典
    result = {}
    
    # 遍历四柱
    for zhu_name in required_keys:
        zhu_data = si_zhu_data[zhu_name]
        
        # 检查数据格式
        if not isinstance(zhu_data, (tuple, list)) or len(zhu_data) != 2:
            result[zhu_name] = {}
            continue
        
        tian_gan, di_zhi = zhu_data
        
        # 检查天干地支类型
        if not isinstance(tian_gan, str) or not isinstance(di_zhi, str):
            result[zhu_name] = {}
            continue
        
        # 去除前后空格
        tian_gan = tian_gan.strip()
        di_zhi = di_zhi.strip()
        
        # 检查是否为空
        if not tian_gan or not di_zhi:
            result[zhu_name] = {}
            continue
        
        # 获取长生状态
        changsheng = get_changsheng(tian_gan, di_zhi)
        
        # 构建结果
        result[zhu_name] = {
            '组合': tian_gan + di_zhi,
            '长生': changsheng
        }
    
    return result


def explain_changsheng(changsheng: str) -> str:
    """
    获取12长生状态的说明文字
    
    参数:
        changsheng (str): 长生状态，如'长生','沐浴'等
    
    返回:
        str: 对应的说明文字
             如果输入无效，返回"未知状态"
    """
    return CHANGSHENG_DESC.get(changsheng, "未知状态")


def print_changsheng_table():
    """
    打印完整的12长生对照表
    """
    print("=" * 80)
    print("12长生对照表")
    print("=" * 80)
    
    # 表头
    print(f"{'天干':<4}", end='')
    zhis = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    for zhi in zhis:
        print(f"{zhi:<6}", end='')
    print()
    print("-" * 80)
    
    # 每个天干的对应关系
    for tian_gan in CHANGSHENG_TABLE:
        print(f"{tian_gan:<4}", end='')
        for zhi in zhis:
            status = CHANGSHENG_TABLE[tian_gan][zhi]
            print(f"{status:<6}", end='')
        print()
    
    print("=" * 80)


# ==================== 示例代码 ====================

if __name__ == "__main__":
    # 示例1：使用get_changsheng函数
    print("\n【示例1】获取天干地支的长生状态")
    print("-" * 50)
    test_cases = [('甲', '亥'), ('乙', '午'), ('丙', '寅'), ('甲', 'X')]
    for tian_gan, di_zhi in test_cases:
        result = get_changsheng(tian_gan, di_zhi)
        if result != "输入错误":
            desc = explain_changsheng(result)
            print(f"{tian_gan}{di_zhi} -> {result}：{desc}")
        else:
            print(f"{tian_gan}{di_zhi} -> {result}")
    
    # 示例2：使用xingyun函数
    print("\n【示例2】星运分析")
    print("-" * 50)
    ri_zhu = '甲'
    di_zhi_list = ['亥', '子', '丑', '寅']
    result = xingyun(ri_zhu, di_zhi_list)
    print(f"日主：{ri_zhu}")
    print("星运分析结果：")
    for zhu_name, changsheng in result.items():
        if changsheng != "输入错误":
            desc = explain_changsheng(changsheng)
            print(f"  {zhu_name}({di_zhi_list[list(result.keys()).index(zhu_name)]})：{changsheng} - {desc}")
        else:
            print(f"  {zhu_name}：{changsheng}")
    
    # 示例3：使用zizuo函数
    print("\n【示例3】自坐分析")
    print("-" * 50)
    si_zhu_data = {
        '年柱': ('甲', '亥'),
        '月柱': ('乙', '子'),
        '日柱': ('丙', '丑'),
        '时柱': ('丁', '寅')
    }
    result = zizuo(si_zhu_data)
    print("四柱自坐分析结果：")
    for zhu_name, info in result.items():
        if info:
            changsheng = info['长生']
            desc = explain_changsheng(changsheng)
            print(f"  {zhu_name}({info['组合']})：{changsheng} - {desc}")
        else:
            print(f"  {zhu_name}：数据格式错误")
    
    # 示例4：打印完整的12长生对照表
    print("\n【示例4】完整的12长生对照表")
    print_changsheng_table()
    
    # 示例5：综合示例 - 八字分析
    print("\n【示例5】综合示例 - 八字分析")
    print("=" * 80)
    
    # 示例八字：甲亥 乙子 丙丑 丁寅
    ba_zi = {
        '年柱': ('甲', '亥'),
        '月柱': ('乙', '子'),
        '日柱': ('丙', '丑'),
        '时柱': ('丁', '寅')
    }
    ri_zhu = ba_zi['日柱'][0]  # 丙
    
    print(f"八字：{ba_zi['年柱'][0]}{ba_zi['年柱'][1]} {ba_zi['月柱'][0]}{ba_zi['月柱'][1]} "
          f"{ba_zi['日柱'][0]}{ba_zi['日柱'][1]} {ba_zi['时柱'][0]}{ba_zi['时柱'][1]}")
    print(f"日主：{ri_zhu}\n")
    
    # 星运分析
    di_zhi_list = [ba_zi['年柱'][1], ba_zi['月柱'][1], ba_zi['日柱'][1], ba_zi['时柱'][1]]
    xingyun_result = xingyun(ri_zhu, di_zhi_list)
    print("【星运分析】日主与各柱地支的12长生关系：")
    for zhu_name, changsheng in xingyun_result.items():
        desc = explain_changsheng(changsheng)
        print(f"  {zhu_name}：{changsheng} - {desc}")
    
    # 自坐分析
    zizuo_result = zizuo(ba_zi)
    print("\n【自坐分析】各柱天干与本柱地支的12长生关系：")
    for zhu_name, info in zizuo_result.items():
        changsheng = info['长生']
        desc = explain_changsheng(changsheng)
        print(f"  {zhu_name}({info['组合']})：{changsheng} - {desc}")
    
    print("\n" + "=" * 80)
