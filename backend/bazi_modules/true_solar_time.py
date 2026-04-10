#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真太阳时计算模块

真太阳时 = 平太阳时 + 经度时差 + 均时差

经度时差：根据出生地经度与东经120度的差异计算
均时差：由于地球公转轨道为椭圆且自转轴倾斜造成的修正
"""

import math
from datetime import datetime, timedelta

# 均时差表（简化版，基于一年中不同日期的近似值）
# 格式：(月, 日, 均时差分钟)
# 均时差范围大约在 -14分钟 到 +16分钟 之间
EQUATION_OF_TIME_TABLE = [
    (1, 1, -3.0), (1, 15, -10.5), (2, 1, -13.5), (2, 15, -14.0),
    (3, 1, -12.5), (3, 15, -9.0), (4, 1, -4.0), (4, 15, 0.0),
    (5, 1, +3.0), (5, 15, +3.5), (6, 1, +2.5), (6, 15, -0.5),
    (7, 1, -3.5), (7, 15, -6.0), (8, 1, -6.5), (8, 15, -5.0),
    (9, 1, -1.0), (9, 15, +4.0), (10, 1, +10.0), (10, 15, +14.0),
    (11, 1, +16.0), (11, 15, +14.5), (12, 1, +10.5), (12, 15, +3.0),
]


def calculate_longitude_diff(longitude):
    """
    计算经度时差
    
    地球自转一周360度需要24小时，即每度4分钟
    东经120度为标准时间，其他经度按差值计算
    
    Args:
        longitude: 经度（东经为正，西经为负）
        
    Returns:
        经度时差（分钟），东加西减
    """
    # 每度4分钟时差
    diff_minutes = (longitude - 120.0) * 4.0
    return diff_minutes


def get_equation_of_time(month, day):
    """
    获取指定日期的均时差
    
    使用线性插值计算均时差
    
    Args:
        month: 月份 (1-12)
        day: 日期 (1-31)
        
    Returns:
        均时差（分钟），真太阳时减平太阳时
    """
    # 将当前日期转换为一年中的天数（近似）
    def day_of_year(m, d):
        days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return sum(days_in_month[:m]) + d
    
    target_doy = day_of_year(month, day)
    
    # 查找相邻的两个数据点
    prev_point = None
    next_point = None
    
    for i, (m, d, eq) in enumerate(EQUATION_OF_TIME_TABLE):
        point_doy = day_of_year(m, d)
        if point_doy <= target_doy:
            prev_point = (point_doy, eq)
        if point_doy >= target_doy and next_point is None:
            next_point = (point_doy, eq)
            break
    
    # 边界处理
    if prev_point is None:
        return EQUATION_OF_TIME_TABLE[0][2]
    if next_point is None:
        return EQUATION_OF_TIME_TABLE[-1][2]
    
    if prev_point[0] == next_point[0]:
        return prev_point[1]
    
    # 线性插值
    ratio = (target_doy - prev_point[0]) / (next_point[0] - prev_point[0])
    interpolated = prev_point[1] + ratio * (next_point[1] - prev_point[1])
    
    return interpolated


def calculate_true_solar_time(year, month, day, hour, minute, longitude, latitude=None, use_dst=False):
    """
    计算真太阳时
    
    Args:
        year, month, day: 年月日
        hour, minute: 时分（24小时制）
        longitude: 经度（东经为正）
        latitude: 纬度（可选，暂未使用）
        use_dst: 是否使用夏令时（中国1986-1991实行过夏令时）
        
    Returns:
        dict: {
            'original_time': '原始时间字符串',
            'true_solar_time': '真太阳时字符串',
            'longitude_diff': 经度时差分钟,
            'equation_of_time': 均时差分钟,
            'total_diff': 总时差分钟,
            'adjusted_datetime': 调整后的datetime对象,
            'year': 调整后年,
            'month': 调整后月,
            'day': 调整后日,
            'hour': 调整后小时,
            'minute': 调整后分钟
        }
    """
    # 原始时间
    original_dt = datetime(year, month, day, hour, minute)
    
    # 1. 计算经度时差（分钟）
    longitude_diff = calculate_longitude_diff(longitude)
    
    # 2. 获取均时差（分钟）
    equation_of_time = get_equation_of_time(month, day)
    
    # 3. 夏令时调整（如果启用）
    dst_offset = -60 if use_dst and is_dst_period(month, day) else 0
    
    # 4. 总时差
    total_diff_minutes = longitude_diff + equation_of_time + dst_offset
    
    # 5. 计算真太阳时
    true_solar_dt = original_dt + timedelta(minutes=total_diff_minutes)
    
    return {
        'original_time': original_dt.strftime('%Y年%m月%d日 %H:%M'),
        'true_solar_time': true_solar_dt.strftime('%Y年%m月%d日 %H:%M'),
        'longitude_diff': round(longitude_diff, 2),
        'equation_of_time': round(equation_of_time, 2),
        'total_diff': round(total_diff_minutes, 2),
        'adjusted_datetime': true_solar_dt,
        'year': true_solar_dt.year,
        'month': true_solar_dt.month,
        'day': true_solar_dt.day,
        'hour': true_solar_dt.hour,
        'minute': true_solar_dt.minute,
        'longitude': longitude,
        'latitude': latitude
    }


def is_dst_period(month, day):
    """
    判断是否在夏令时期间（中国1986-1991年实行）
    
    中国夏令时：每年4月中旬第一个星期日凌晨2时开始
              到9月中旬第一个星期日凌晨2时结束
    
    Args:
        month: 月份
        day: 日期
        
    Returns:
        bool: 是否在夏令时期间
    """
    # 简化的夏令时判断：4月中旬到9月中旬
    if month < 4 or month > 9:
        return False
    if month == 4 and day < 15:
        return False
    if month == 9 and day >= 15:
        return False
    return True


def get_time_diff_description(diff_minutes):
    """
    获取时差描述
    
    Args:
        diff_minutes: 时差分钟数
        
    Returns:
        str: 时差描述
    """
    if abs(diff_minutes) < 1:
        return "与标准时间基本一致"
    
    direction = "快" if diff_minutes > 0 else "慢"
    hours = int(abs(diff_minutes) // 60)
    minutes = int(abs(diff_minutes) % 60)
    
    if hours > 0:
        return f"比标准时间{direction}{hours}小时{minutes}分钟"
    else:
        return f"比标准时间{direction}{minutes}分钟"


def format_true_solar_time_result(result):
    """
    格式化真太阳时计算结果
    
    Args:
        result: calculate_true_solar_time返回的字典
        
    Returns:
        str: 格式化的结果字符串
    """
    lines = [
        "═" * 50,
        "真太阳时计算结果",
        "═" * 50,
        f"出生地经纬度: 东经{result['longitude']:.4f}°",
        "",
        f"【原时间】　　: {result['original_time']}",
        f"【真太阳时】　: {result['true_solar_time']}",
        "",
        "时差明细:",
        f"  • 经度时差　: {result['longitude_diff']:+.2f}分钟",
        f"  • 均时差　　: {result['equation_of_time']:+.2f}分钟",
        f"  • 总时差　　: {result['total_diff']:+.2f}分钟",
        "",
        f"说明: {get_time_diff_description(result['total_diff'])}",
        "═" * 50,
    ]
    return "\n".join(lines)


def convert_to_true_solar_time_for_bazi(year, month, day, hour, minute, province_city):
    """
    为八字排盘转换真太阳时
    
    Args:
        year, month, day: 年月日
        hour, minute: 时分
        province_city: 格式为"省份 城市"的字符串
        
    Returns:
        dict: 转换结果，如果找不到城市返回None
    """
    from city_database import get_city_coordinates
    
    coords = get_city_coordinates(province_city)
    if coords is None:
        return None
    
    longitude, latitude = coords
    result = calculate_true_solar_time(year, month, day, hour, minute, longitude, latitude)
    
    return result


if __name__ == "__main__":
    # 测试示例
    print("测试真太阳时计算\n")
    
    # 测试北京（东经116.4度，接近标准时）
    result = calculate_true_solar_time(2024, 6, 15, 12, 0, 116.4134, 39.9110)
    print(format_true_solar_time_result(result))
    print("\n")
    
    # 测试乌鲁木齐（东经87.6度，西部城市）
    result = calculate_true_solar_time(2024, 6, 15, 12, 0, 87.6244, 43.8308)
    print(format_true_solar_time_result(result))
    print("\n")
    
    # 测试哈尔滨（东经126.5度，东部城市）
    result = calculate_true_solar_time(2024, 6, 15, 12, 0, 126.5416, 45.8088)
    print(format_true_solar_time_result(result))
