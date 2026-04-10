#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字命理分析系统 - 命令行版本
整合 bazi_geju_refactored_v5.py 和 DeepSeek 报告生成

功能：
1. 根据用户输入的出生年月日时（支持多种格式）生成八字
2. 选项1：打印八字基础信息（默认）
3. 选项2：结合DeepSeek生成天赋与性格分析报告

支持格式：
- 年月日时: 1990 5 15 10
- 年月日: 1990 5 15 (无时柱)
- 带分隔符: 1990-05-15 10, 1990/5/15
- 紧凑格式: 1990051510
- 八字干支: 甲子 乙丑 丙寅 丁卯
- 八字干支(连写): 甲子乙丑丙寅丁卯

作者: Claude AI
创建日期: 2026-03-02
版本: 1.0
"""

import re
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple, Union

# DeepSeek API 默认密钥（用户可替换为自己的密钥）
DEFAULT_DEEPSEEK_API_KEY = "sk-99f76dba24a242d9b6b358365b356d79"


def parse_input(input_str: str) -> Optional[Tuple]:
    """
    解析用户输入的日期时间字符串
    
    支持格式:
    - 年月日时分开: 1990 5 15 10
    - 年月日: 1990 5 15
    - 带分隔符: 1990-05-15 10, 1990/5/15, 1990年5月15日
    - 紧凑格式: 1990051510
    - 八字干支: 甲子 乙丑 丙寅 丁卯
    - 八字干支(连写): 甲子乙丑丙寅丁卯
    
    返回:
        ('date', year, month, day, hour) 或 ('bazi', bazi_dict) 或 None
    """
    input_str = input_str.strip()
    if not input_str:
        return None
    
    # 尝试匹配带分隔符的格式: 1990-05-15 10, 1990/5/15, 1990年5月15日
    date_pattern = r'(\d{4})[-/\.年](\d{1,2})[-/\.月](\d{1,2})[日\s]*'
    date_match = re.search(date_pattern, input_str)
    
    if date_match:
        year = int(date_match.group(1))
        month = int(date_match.group(2))
        day = int(date_match.group(3))
        
        # 尝试匹配时间部分
        time_pattern = r'[\s:]*(\d{1,2})[\s:时]*'
        remaining = input_str[date_match.end():]
        time_match = re.search(time_pattern, remaining)
        hour = int(time_match.group(1)) if time_match else None
        
        return ('date', year, month, day, hour)
    
    # 尝试匹配空格分隔的格式: 1990 5 15 10
    parts = input_str.split()
    if len(parts) >= 3:
        try:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            hour = int(parts[3]) if len(parts) >= 4 else None
            return ('date', year, month, day, hour)
        except ValueError:
            pass
    
    # 尝试匹配紧凑格式: 1990051510
    if input_str.isdigit() and len(input_str) >= 8:
        year = int(input_str[:4])
        month = int(input_str[4:6])
        day = int(input_str[6:8])
        hour = int(input_str[8:10]) if len(input_str) >= 10 else None
        return ('date', year, month, day, hour)
    
    # 尝试匹配八字干支格式
    gans = "甲乙丙丁戊己庚辛壬癸"
    zhis = "子丑寅卯辰巳午未申酉戌亥"
    
    # 移除空格后检查: 甲子乙丑丙寅丁卯
    clean_str = input_str.replace(' ', '')
    if len(clean_str) >= 8:
        is_ganzhi = all(c in gans + zhis for c in clean_str)
        if is_ganzhi:
            bazi_dict = {
                'year_gan': clean_str[0],
                'year_zhi': clean_str[1],
                'month_gan': clean_str[2],
                'month_zhi': clean_str[3],
                'day_gan': clean_str[4],
                'day_zhi': clean_str[5],
                'time_gan': clean_str[6] if len(clean_str) >= 8 else '',
                'time_zhi': clean_str[7] if len(clean_str) >= 8 else ''
            }
            return ('bazi', bazi_dict)
    
    # 空格分隔的干支格式: 甲子 乙丑 丙寅 丁卯
    if len(parts) >= 4:
        if all(len(p) == 2 and p[0] in gans and p[1] in zhis for p in parts[:4]):
            bazi_dict = {
                'year_gan': parts[0][0],
                'year_zhi': parts[0][1],
                'month_gan': parts[1][0],
                'month_zhi': parts[1][1],
                'day_gan': parts[2][0],
                'day_zhi': parts[2][1],
                'time_gan': parts[3][0],
                'time_zhi': parts[3][1]
            }
            return ('bazi', bazi_dict)
    
    return None


def date_to_bazi(year: int, month: int, day: int, hour: Optional[int] = None) -> Dict[str, str]:
    """
    将公历日期转换为八字
    
    参数:
        year, month, day: 年月日
        hour: 时（可选），如果为None则不计算时柱
    
    返回:
        八字字典
    """
    try:
        from lunar_python import Solar
    except ImportError:
        raise ImportError("请先安装 lunar_python: pip install lunar_python")
    
    # 获取年月日三柱（必须）
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    ba = lunar.getEightChar()
    
    bazi_dict = {
        'year_gan': ba.getYearGan(),
        'year_zhi': ba.getYearZhi(),
        'month_gan': ba.getMonthGan(),
        'month_zhi': ba.getMonthZhi(),
        'day_gan': ba.getDayGan(),
        'day_zhi': ba.getDayZhi(),
        'time_gan': '',
        'time_zhi': ''
    }
    
    # 只有提供了小时才计算时柱
    if hour is not None:
        solar_with_time = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar_with_time = solar_with_time.getLunar()
        ba_with_time = lunar_with_time.getEightChar()
        bazi_dict['time_gan'] = ba_with_time.getTimeGan()
        bazi_dict['time_zhi'] = ba_with_time.getTimeZhi()
    
    return bazi_dict


def print_bazi_basic_info(bazi_dict: Dict[str, str], is_male: bool):
    """
    打印八字基础信息（使用 bazi_geju_refactored_v5.py 的分析结果）
    """
    try:
        from bazi_geju_refactored_v5 import GeJuAnalyzerV5
    except ImportError:
        print("错误: 无法导入 bazi_geju_refactored_v5 模块")
        print("请确保该文件在当前目录中")
        return
    
    print("\n" + "=" * 80)
    print("【八字基础信息】".center(80))
    print("=" * 80)
    
    # 创建分析器
    analyzer = GeJuAnalyzerV5(
        bazi_dict,
        liunian_year=datetime.now().year,
        is_male=is_male
    )
    
    # 执行分析
    result = analyzer.analyze()
    
    # 打印结果
    analyzer.print_analysis()
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)


def generate_deepseek_report(bazi_dict: Dict[str, str], is_male: bool, api_key: str):
    """
    调用 DeepSeek 生成详细报告
    """
    try:
        from bazi_to_deepseek_report import BaziDeepSeekAnalyzer
    except ImportError:
        print("错误: 无法导入 bazi_to_deepseek_report 模块")
        print("请确保该文件在当前目录中")
        return
    
    print("\n" + "=" * 80)
    print("【DeepSeek 天赋与性格分析报告】".center(80))
    print("=" * 80)
    
    # 创建分析器
    analyzer = BaziDeepSeekAnalyzer(api_key=api_key)
    
    # 生成报告
    try:
        print("\n正在分析八字...")
        print("正在生成提示词...")
        print("正在调用 DeepSeek API（这可能需要 10-30 秒）...")
        print("-" * 80)
        
        report = analyzer.generate_report(
            bazi_dict,
            liunian_year=datetime.now().year,
            api_key=api_key,
            save_to_file=True
        )
        
        if report:
            analyzer.print_report(report)
        else:
            print("生成报告失败，请检查 API 密钥和网络连接")
    
    except Exception as e:
        print(f"\n错误: {str(e)}")
        print("\n可能的原因：")
        print("1. API 密钥无效或已过期")
        print("2. 网络连接问题")
        print("3. DeepSeek 服务暂时不可用")
        print("\n建议：")
        print("- 检查 API 密钥是否正确")
        print("- 检查网络连接")
        print("- 稍后再试")


def get_user_input() -> Tuple[Dict[str, str], bool, str]:
    """
    获取用户输入并返回八字字典、性别和API密钥
    
    返回:
        (bazi_dict, is_male, api_key)
    """
    print("=" * 80)
    print("八字命理分析系统".center(80))
    print("=" * 80)
    print("\n支持输入格式:")
    print("  1. 年月日时: 1990 5 15 10")
    print("  2. 年月日: 1990 5 15 (无时柱)")
    print("  3. 带分隔符: 1990-05-15 10, 1990/5/15")
    print("  4. 紧凑格式: 1990051510")
    print("  5. 八字干支: 甲子 乙丑 丙寅 丁卯")
    print("  6. 八字干支(连写): 甲子乙丑丙寅丁卯")
    
    # 获取用户输入
    print("\n请输入出生信息（公历）或八字干支：")
    input_str = input("> ").strip()
    
    # 解析输入
    parsed = parse_input(input_str)
    
    if parsed is None:
        print("\n输入格式错误！请使用以下格式之一:")
        print("  - 1990 5 15 10 (年月日时)")
        print("  - 1990 5 15 (年月日)")
        print("  - 1990-05-15 10")
        print("  - 1990051510")
        print("  - 甲子 乙丑 丙寅 丁卯 (八字干支)")
        sys.exit(1)
    
    # 获取性别
    print("\n请输入性别：")
    gender_input = input("1-男, 0-女 (默认1): ").strip()
    is_male = gender_input != '0'
    gender_str = "男" if is_male else "女"
    print(f"性别: {gender_str}")
    
    # 处理输入数据
    if parsed[0] == 'date':
        _, year, month, day, hour = parsed
        try:
            bazi_dict = date_to_bazi(year, month, day, hour)
        except Exception as e:
            print(f"\n日期转换错误: {e}")
            sys.exit(1)
        
        print(f"\n根据出生日期计算得到八字：")
        print(f"  年柱: {bazi_dict['year_gan']}{bazi_dict['year_zhi']}")
        print(f"  月柱: {bazi_dict['month_gan']}{bazi_dict['month_zhi']}")
        print(f"  日柱: {bazi_dict['day_gan']}{bazi_dict['day_zhi']}")
        if hour:
            print(f"  时柱: {bazi_dict['time_gan']}{bazi_dict['time_zhi']}")
        else:
            print(f"  时柱: 无")
    else:
        _, bazi_dict = parsed
        print(f"\n输入的八字信息：")
        print(f"  年柱: {bazi_dict['year_gan']}{bazi_dict['year_zhi']}")
        print(f"  月柱: {bazi_dict['month_gan']}{bazi_dict['month_zhi']}")
        print(f"  日柱: {bazi_dict['day_gan']}{bazi_dict['day_zhi']}")
        has_time = bool(bazi_dict.get('time_gan'))
        if has_time:
            print(f"  时柱: {bazi_dict['time_gan']}{bazi_dict['time_zhi']}")
        else:
            print(f"  时柱: 无")
    
    return bazi_dict, is_male, DEFAULT_DEEPSEEK_API_KEY


def main():
    """主函数：交互式界面"""
    try:
        bazi_dict, is_male, api_key = get_user_input()
    except SystemExit:
        return
    except Exception as e:
        print(f"输入处理错误: {e}")
        return
    
    # 提供选项
    print("\n" + "=" * 80)
    print("请选择操作：")
    print("  1. 打印此用户八字基础信息（默认）")
    print("  2. 结合DeepSeek生成详细分析报告")
    print("=" * 80)
    
    choice = input("\n请输入选项 (1/2，直接回车默认选1): ").strip()
    
    if choice == '':
        choice = '1'
    
    while choice not in ['1', '2']:
        print("输入错误，请输入 1 或 2")
        choice = input("请输入选项 (1/2，直接回车默认选1): ").strip()
        if choice == '':
            choice = '1'
    
    if choice == '1':
        # 选项1：打印八字基础信息
        print("\n您选择了：打印八字基础信息")
        print_bazi_basic_info(bazi_dict, is_male)
    
    else:
        # 选项2：生成DeepSeek报告
        print("\n您选择了：生成DeepSeek详细分析报告")
        
        # 询问是否使用默认API密钥
        print(f"\n默认API密钥: {api_key[:20]}...")
        use_default = input("使用默认API密钥? (Y/n，默认Y): ").strip().upper()
        
        if use_default == 'N':
            custom_key = input("请输入您的DeepSeek API密钥: ").strip()
            if custom_key:
                api_key = custom_key
        
        generate_deepseek_report(bazi_dict, is_male, api_key)


if __name__ == '__main__':
    main()
