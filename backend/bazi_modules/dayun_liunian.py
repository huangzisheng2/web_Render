#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大运流年计算模块
实现八字大运、流年、小运的完整计算与展示
"""

import sys
import os
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# 导入项目相关模块
from lunar_python import Lunar, Solar
from changsheng import CHANGSHENG_TABLE, get_changsheng
from shensha_database import ShenShaDatabase, ShenShaCalculator
from ganzhi import Gan, Zhi, zhi5, zhi5_list, ten_deities, zhi_atts, zhi_3hes, zhi_6hes, ganzhi60
from datas import nayins, empties, zhi_half_3hes

# 天干列表
GANS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支列表
ZHIS = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
# 月份地支
MONTH_ZHI = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]

# 天干相克关系 (key克value，如甲克戊)
GAN_KE = {
    '甲': '戊',
    '乙': '己',
    '丙': '庚',
    '丁': '辛',
    '戊': '壬',
    '己': '癸',
    '庚': '甲',
    '辛': '乙',
    '壬': '丙',
    '癸': '丁'
}

# 地支六冲关系
ZHI_CHONG = {
    '子': '午',
    '午': '子',
    '丑': '未',
    '未': '丑',
    '寅': '申',
    '申': '寅',
    '卯': '酉',
    '酉': '卯',
    '辰': '戌',
    '戌': '辰',
    '巳': '亥',
    '亥': '巳'
}

# 原局四柱名称
YUANJU_PILLARS = ['年柱', '月柱', '日柱', '时柱']


class BaZiCalculator:
    """八字计算器核心类"""

    def __init__(self):
        """初始化计算器"""
        self.shensha_db = ShenShaDatabase()
        self.shensha_calc = ShenShaCalculator(self.shensha_db)
        self.birth_year = None  # 保存出生年份（如果有）

    def check_tian_ke_di_chong(self, liunian_gan: str, liunian_zhi: str, bazi: Dict) -> List[str]:
        """
        判断流年是否与原局某柱构成天克地冲
        
        判断标准：必须同时满足
        1. 流年天干与原局某柱天干相克（根据GAN_KE字典）
        2. 流年地支与原局某柱地支相冲（根据ZHI_CHONG字典）
        二者缺一不可
        
        参数:
            liunian_gan: 流年天干
            liunian_zhi: 流年地支
            bazi: 原局八字字典
            
        返回:
            构成天克地冲的柱位列表，如['年柱', '日柱']，如果没有则返回空列表
        """
        tian_ke_di_chong_pillars = []
        
        # 原局四柱
        yuanju_pillars = [
            ('year_gan', 'year_zhi', '年柱'),
            ('month_gan', 'month_zhi', '月柱'),
            ('day_gan', 'day_zhi', '日柱'),
            ('time_gan', 'time_zhi', '时柱')
        ]
        
        for gan_key, zhi_key, pillar_name in yuanju_pillars:
            yuanju_gan = bazi.get(gan_key, '')
            yuanju_zhi = bazi.get(zhi_key, '')
            
            # 跳过空柱（如无时柱）
            if not yuanju_gan or not yuanju_zhi:
                continue
            
            # 判断天干是否相克（检查双向相克）
            gan_ke = False
            # 流年干克原局干
            if GAN_KE.get(liunian_gan) == yuanju_gan:
                gan_ke = True
            # 原局干克流年干
            if GAN_KE.get(yuanju_gan) == liunian_gan:
                gan_ke = True
            
            # 判断地支是否相冲
            zhi_chong = False
            if ZHI_CHONG.get(liunian_zhi) == yuanju_zhi:
                zhi_chong = True
            
            # 必须同时满足天干相克和地支相冲
            if gan_ke and zhi_chong:
                tian_ke_di_chong_pillars.append(pillar_name)
        
        return tian_ke_di_chong_pillars
    
    def check_sui_yun_bing_lin(self, liunian_gan: str, liunian_zhi: str, dayun_gan: str, dayun_zhi: str) -> bool:
        """
        判断流年是否与当前大运构成岁运并临
        
        判断标准：
        - 流年干支与大运干支完全相同（天干相同且地支相同）
        - 两个条件必须同时满足，缺一不可
        
        参数:
            liunian_gan: 流年天干
            liunian_zhi: 流年地支
            dayun_gan: 大运天干
            dayun_zhi: 大运地支
            
        返回:
            True表示构成岁运并临，False表示不构成
        """
        return liunian_gan == dayun_gan and liunian_zhi == dayun_zhi

    def parse_bazi_input(self, bazi_str: str) -> Dict:
        """
        解析八字输入字符串

        支持格式:
        - 八字干支: 甲子 乙丑 丙寅 丁卯 (年月日时)
        - 出生日期: 1990 5 15 10 (年 月 日 时)
        - 出生日期(可选日时): 1990 5 (年 月)
        - 出生日期(可选时): 1990 5 15 (年 月 日)

        返回: {'year_gan': '甲', 'year_zhi': '子', ...}
        """
        bazi_str = bazi_str.strip()
        parts = bazi_str.split()

        # 判断是干支还是日期
        if all(len(p) == 2 and all(c in GANS + ZHIS for c in p) for p in parts[:min(len(parts), 4)]):
            # 干支格式: 甲子 乙丑 丙寅 丁卯
            return self._parse_ganzhi_input(parts)
        else:
            # 日期格式
            return self._parse_date_input(parts)

    def _parse_ganzhi_input(self, parts: List[str]) -> Dict:
        """解析八字干支输入"""
        if len(parts) >= 2:
            # 至少需要年柱和月柱
            bazi = {
                'year_gan': parts[0][0],
                'year_zhi': parts[0][1],
                'month_gan': parts[1][0],
                'month_zhi': parts[1][1],
                'day_gan': parts[2][0] if len(parts) > 2 else '',
                'day_zhi': parts[2][1] if len(parts) > 2 else '',
                'time_gan': parts[3][0] if len(parts) > 3 else '',
                'time_zhi': parts[3][1] if len(parts) > 3 else ''
            }

            # 如果提供了完整四柱，尝试反推出生日期
            if len(parts) >= 4:
                birth_dates = self._find_dates_from_bazi(bazi)
                if birth_dates:
                    # 让用户选择日期
                    print(f"\n根据八字 {parts[0]} {parts[1]} {parts[2]} {parts[3]} 找到以下可能的出生日期:")
                    for i, date_info in enumerate(birth_dates, 1):
                        print(f"{i}. {date_info['date_str']}")

                    if len(birth_dates) == 1:
                        # 只有一个结果，自动选择
                        selected_date = birth_dates[0]
                        print(f"\n自动选择: {selected_date['date_str']}")
                    else:
                        # 多个结果，让用户选择
                        while True:
                            try:
                                choice = input(f"\n请选择出生日期(1-{len(birth_dates)})，或按Enter跳过: ").strip()
                                if choice == '':
                                    selected_date = None
                                    break
                                choice_idx = int(choice) - 1
                                if 0 <= choice_idx < len(birth_dates):
                                    selected_date = birth_dates[choice_idx]
                                    break
                                print(f"请输入1-{len(birth_dates)}之间的数字")
                            except ValueError:
                                print("请输入有效的数字")

                    if selected_date:
                        # 使用选择的日期获取精确八字
                        return self.get_bazi_from_date(
                            selected_date['year'],
                            selected_date['month'],
                            selected_date['day'],
                            selected_date['hour']
                        )

            return bazi
        else:
            raise ValueError("输入格式错误，干支输入至少需要年柱和月柱(如:甲子 乙丑)")

    def _parse_date_input(self, parts: List[str]) -> Dict:
        """解析日期输入 - 支持无时柱（只提供年月日）"""
        try:
            year = int(parts[0])
            month = int(parts[1]) if len(parts) > 1 else 1
            day = int(parts[2]) if len(parts) > 2 else 1
            hour = int(parts[3]) if len(parts) > 3 else None  # 不再默认12时，None表示无时柱

            return self.get_bazi_from_date(year, month, day, hour)
        except ValueError:
            raise ValueError(f"输入格式错误，请使用: 八字干支(如:甲子 乙丑) 或 日期(如:1990 5 [15 [10]])")

    def _find_dates_from_bazi(self, bazi: Dict) -> List[Dict]:
        """
        从八字反推可能的出生日期

        范围: 2026年前后各100年 (1926-2126)

        返回: [{'year': 1990, 'month': 5, 'day': 15, 'hour': 10, 'date_str': '1990-05-15 10:00'}, ...]
        """
        year_ganzhi = bazi['year_gan'] + bazi['year_zhi']
        month_ganzhi = bazi['month_gan'] + bazi['month_zhi']
        day_ganzhi = bazi['day_gan'] + bazi['day_zhi']
        time_ganzhi = bazi['time_gan'] + bazi['time_zhi']

        # 查找年份
        year_candidates = self._get_years_from_ganzhi(year_ganzhi, 1926, 2126)

        # 遍历每个可能的年份，查找匹配的日期
        matching_dates = []

        for year in year_candidates:
            for month in range(1, 13):
                for day in range(1, 32):
                    try:
                        # 创建Solar对象
                        solar = Solar.fromYmdHms(year, month, day, 12, 0, 0)
                        lunar = solar.getLunar()
                        ba = lunar.getEightChar()

                        # 检查年月日柱是否匹配
                        if (ba.getYearGan() + ba.getYearZhi() == year_ganzhi and
                            ba.getMonthGan() + ba.getMonthZhi() == month_ganzhi and
                            ba.getDayGan() + ba.getDayZhi() == day_ganzhi):

                            # 检查时柱（如果提供了）
                            if time_ganzhi:
                                # 遍历12个时辰
                                for hour in range(0, 24, 2):
                                    if hour == 0:
                                        hour_start = 23
                                    else:
                                        hour_start = hour - 1
                                    solar_hour = Solar.fromYmdHms(year, month, day, hour_start, 0, 0)
                                    lunar_hour = solar_hour.getLunar()
                                    ba_hour = lunar_hour.getEightChar()

                                    if ba_hour.getTimeGan() + ba_hour.getTimeZhi() == time_ganzhi:
                                        matching_dates.append({
                                            'year': year,
                                            'month': month,
                                            'day': day,
                                            'hour': hour_start,
                                            'date_str': f"{year}-{month:02d}-{day:02d} {hour_start:02d}:00"
                                        })
                                        break
                            else:
                                # 没有提供时柱，只匹配年月日
                                matching_dates.append({
                                    'year': year,
                                    'month': month,
                                    'day': day,
                                    'hour': 12,
                                    'date_str': f"{year}-{month:02d}-{day:02d} 12:00"
                                })
                    except Exception:
                        continue

        return matching_dates

    def _get_years_from_ganzhi(self, ganzhi: str, min_year: int, max_year: int) -> List[int]:
        """
        从干支获取年份范围

        返回: [1984, 2044, 2104, ...]
        """
        # 获取干支在六十甲子中的序号
        seq = ganzhi60.inverse[ganzhi]

        # 1984年是甲子年（序号1）
        base_year = 1984
        first_year = base_year + (seq - 1)

        # 生成范围内所有可能的年份
        years = []
        current = first_year - 60  # 从更早开始
        while current <= max_year:
            if current >= min_year:
                years.append(current)
            current += 60

        return sorted(years)

    def get_bazi_from_date(self, year: int, month: int, day: int, hour: int = None) -> Dict:
        """
        从公历日期获取八字 - 支持无时柱（hour为None）

        参数:
            year: 年
            month: 月
            day: 日
            hour: 时（可选，None表示无时柱）

        返回: {'year_gan': '甲', 'year_zhi': '子', ...}
        """
        # 保存出生年份（用于后续计算）
        self.birth_year = year
        
        # 判断是否有时柱
        has_time_pillar = hour is not None
        self.has_time_pillar = has_time_pillar

        if has_time_pillar:
            # 完整四柱
            solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
            lunar = solar.getLunar()
            ba = lunar.getEightChar()
            
            # 保存lunar对象用于精确起运计算
            self.lunar = lunar
            
            return {
                'year_gan': ba.getYearGan(),
                'year_zhi': ba.getYearZhi(),
                'month_gan': ba.getMonthGan(),
                'month_zhi': ba.getMonthZhi(),
                'day_gan': ba.getDayGan(),
                'day_zhi': ba.getDayZhi(),
                'time_gan': ba.getTimeGan(),
                'time_zhi': ba.getTimeZhi()
            }
        else:
            # 只有年月日三柱，时柱为空
            # 使用默认时间12:00获取年月日三柱
            solar = Solar.fromYmdHms(year, month, day, 12, 0, 0)
            lunar = solar.getLunar()
            ba = lunar.getEightChar()
            
            # 保存lunar对象用于精确起运计算
            self.lunar = lunar
            
            return {
                'year_gan': ba.getYearGan(),
                'year_zhi': ba.getYearZhi(),
                'month_gan': ba.getMonthGan(),
                'month_zhi': ba.getMonthZhi(),
                'day_gan': ba.getDayGan(),
                'day_zhi': ba.getDayZhi(),
                'time_gan': '',  # 时柱为空
                'time_zhi': ''   # 时柱为空
            }

    def calculate_qiyun(self, bazi: Dict, is_male: bool = True) -> Tuple[int, int, int]:
        """
        计算起运岁数和月份（基于12节精确计算）

        返回: (起运岁数, 大运方向, 性别: 1男0女)
        """
        year_gan = bazi['year_gan']

        # 判断年干阴阳
        year_gan_seq = Gan.index(year_gan)
        is_yang_year = (year_gan_seq % 2 == 0)

        # 计算大运方向
        if is_male:
            direction = 1 if is_yang_year else -1
        else:
            direction = -1 if is_yang_year else 1

        # 精确计算起运岁数
        if hasattr(self, 'lunar'):
            # 有lunar对象，使用精确计算
            qiyun_years, qiyun_months, shichen_days = self._calculate_qiyun_age(self.lunar, is_male, is_yang_year)
            self._shichen_days = shichen_days  # 保存时辰转换天数S
        else:
            # 没有lunar对象（直接输入八字），使用简化计算
            qiyun_years, qiyun_months = 3, 0
            self._shichen_days = 0

        # 保存起运岁数和月份供后续使用
        self._qiyun_age = qiyun_years
        self._qiyun_months = qiyun_months

        return qiyun_years, direction, int(is_male), qiyun_months

    def _calculate_qiyun_age(self, lunar, is_male: bool, is_yang_year: bool) -> Tuple[int, int, int]:
        """
        基于12节计算起运岁数和月份

        参数:
            lunar: 农历对象
            is_male: 是否为男命
            is_yang_year: 是否为阳年

        返回:
            (起运岁数, 起运月份, 时辰转换天数S)
        """
        # 获取出生时间到上一个和下一个12节（主要12节）的时间
        prev_jie = lunar.getPrevJie()
        next_jie = lunar.getNextJie()

        prev_jie_solar = prev_jie.getSolar()
        next_jie_solar = next_jie.getSolar()
        birth_solar = lunar.getSolar()

        # 打印计算过程
        print("\n========== 起运计算过程 ==========")
        print(f"出生时间: {birth_solar.toYmdHms()}")
        print(f"上一个12节: {prev_jie.getName()} ({prev_jie_solar.toYmdHms()})")
        print(f"下一个12节: {next_jie.getName()} ({next_jie_solar.toYmdHms()})")

        # 判断大运方向
        is_shunxing = (is_male and is_yang_year) or (not is_male and not is_yang_year)
        direction_str = "顺行" if is_shunxing else "逆行"
        print(f"大运方向: {direction_str} (性别:{'男' if is_male else '女'}, 年年阴阳:{'阳' if is_yang_year else '阴'})")

        # 计算时间差（精确到小数）
        if is_shunxing:
            # 顺行大运：出生后到下一个12节的时间差
            birth_julian = birth_solar.getJulianDay()
            next_julian = next_jie_solar.getJulianDay()
            days_diff = next_julian - birth_julian
            print(f"计算方式: 下一个12节时间 - 出生时间")
        else:
            # 逆行大运：出生前到上一个12节的时间差
            birth_julian = birth_solar.getJulianDay()
            prev_julian = prev_jie_solar.getJulianDay()
            days_diff = birth_julian - prev_julian
            print(f"计算方式: 出生时间 - 上一个12节时间")

        print(f"时间差: {days_diff:.4f}天")

        # i. 计算到下一个12节的天数 = D（取整数部分，即节气天数）
        D = int(days_diff)
        print(f"i. 计算到下一个12节的天数: D = {D}天")

        # 计算时辰数：时间差的小数部分 × 12
        shichen_count = int((days_diff - D) * 12)
        print(f"   时间差小数部分: {days_diff - D:.4f}天")
        print(f"   对应时辰数: {shichen_count}个时辰")

        # ii. 计算时辰转换天数 = 时辰数 × 10 = S
        S = shichen_count * 10
        print(f"ii. 计算时辰转换天数: 时辰数({shichen_count}) × 10 = S = {S}天")

        # iii. 起运岁数 = D ÷ 3 = A（A即岁数）余B（仅用节气天数，不包含时辰天数）
        A = D // 3
        B = D % 3
        print(f"iii. 起运岁数: D({D}天) ÷ 3 = {A}岁 余 {B}天")

        # iv. 起运月份 = B（余数） × 4（仅用节气天数的余数）
        months = B * 4
        print(f"iv. 起运月份: B({B}天余数) × 4 = {months}个月")

        # v. 起运时间点 = A年+B月+S天（S为总天数，用于换算为年月日）
        print(f"v. 起运时间点: {A}年 + {months}个月 + {S}天")
        print("====================================\n")

        return A, months, S

    def estimate_birth_year(self, bazi: Dict) -> int:
        """
        根据八字估算出生年份

        返回: 估算的出生年份
        """
        # 使用年柱干支查找对应的年份
        year_ganzhi = bazi['year_gan'] + bazi['year_zhi']

        # 查找六十甲子对应的年份
        for num, gz in ganzhi60.items():
            if gz == year_ganzhi:
                # 计算大概的年份范围（1984年是甲子年）
                # 60年一轮回
                base_year = 1984  # 甲子年
                year_offset = num - 1
                # 找到最近的年份
                for year in range(1900, 2100):
                    if (year - base_year) % 60 == year_offset:
                        return year
        return 1990  # 默认值

    def generate_xiaoyuns(self, bazi: Dict, count: int = 20) -> List[Dict]:
        """
        生成小运列表

        小运: 从出生到起运年龄之间逐年的小运
        0岁小运与年柱相同，1岁及以后按六十甲子顺序推进

        返回: [{'age': 0, 'gan': '甲', 'zhi': '子', 'gan_zhi': '甲子'}, ...]
        """
        xiaoyuns = []
        year_gan_zhi = bazi['year_gan'] + bazi['year_zhi']
        gan_seq = Gan.index(year_gan_zhi[0])
        zhi_seq = Zhi.index(year_gan_zhi[1])

        for age in range(count):
            if age == 0:
                # 0岁小运与年柱相同
                xiaoyun = year_gan_zhi
            else:
                # 1岁及以上小运：从年柱开始，按六十甲子顺序向前推进
                gan_seq = (gan_seq + 1) % 10
                zhi_seq = (zhi_seq + 1) % 12
                xiaoyun = Gan[gan_seq] + Zhi[zhi_seq]

            xiaoyuns.append({
                'age': age,
                'gan': xiaoyun[0],
                'zhi': xiaoyun[1],
                'gan_zhi': xiaoyun
            })

        return xiaoyuns

    def generate_dayuns(self, bazi: Dict, direction: int, count: int = 12) -> List[Dict]:
        """
        生成大运列表

        大运: 从月柱开始，按顺行或逆行排列

        返回: [{'index': 1, 'gan': '己', 'zhi': '未', 'gan_zhi': '己未', 'start_date': 'YYYY-MM-DD'}, ...]
        """
        dayuns = []
        gan_seq = Gan.index(bazi['month_gan'])
        zhi_seq = Zhi.index(bazi['month_zhi'])

        # 计算第一个大运的精确起运日期
        first_dayun_start_date = self._calculate_first_dayun_start_date()
        qiyun_years = self._qiyun_age if hasattr(self, '_qiyun_age') else 3
        qiyun_months = self._qiyun_months if hasattr(self, '_qiyun_months') else 0

        for i in range(count):
            gan_seq += direction
            zhi_seq += direction
            gan_zhi = Gan[gan_seq % 10] + Zhi[zhi_seq % 12]

            dayun_data = {
                'index': i + 1,
                'gan': gan_zhi[0],
                'zhi': gan_zhi[1],
                'gan_zhi': gan_zhi
            }

            # 第一个大运设置精确起运日期
            if i == 0 and first_dayun_start_date:
                dayun_data['start_date'] = first_dayun_start_date
                dayun_data['age'] = f"{qiyun_years}岁{qiyun_months}个月"
            else:
                # 后续大运日期 = 第一个大运起运日期 + i*10年
                if first_dayun_start_date:
                    from datetime import datetime, timedelta
                    try:
                        base_date = datetime.strptime(first_dayun_start_date, "%Y-%m-%d")
                        future_date = base_date.replace(year=base_date.year + i * 10)
                        dayun_data['start_date'] = future_date.strftime("%Y-%m-%d")
                        age = qiyun_years + i * 10
                        dayun_data['age'] = f"{age}岁{qiyun_months}个月"
                    except Exception:
                        dayun_data['start_date'] = ''
                        dayun_data['age'] = f"{qiyun_years + i * 10}岁"
                else:
                    dayun_data['start_date'] = ''
                    dayun_data['age'] = f"{qiyun_years + i * 10}岁"

            dayuns.append(dayun_data)

        return dayuns

    def _calculate_first_dayun_start_date(self) -> str:
        """
        计算第一个大运的精确起运日期

        起运日期 = 出生日期 + A年 + B个月 + S天

        返回: 起运日期字符串 'YYYY-MM-DD'，如果无法计算则返回空字符串
        """
        if not hasattr(self, 'lunar') or not hasattr(self, '_shichen_days'):
            return ''

        try:
            birth_solar = self.lunar.getSolar()
            birth_year = birth_solar.getYear()
            birth_month = birth_solar.getMonth()
            birth_day = birth_solar.getDay()
            birth_hour = birth_solar.getHour()

            # 获取起运岁数、月份和时辰天数
            A = self._qiyun_age if hasattr(self, '_qiyun_age') else 3
            B = self._qiyun_months if hasattr(self, '_qiyun_months') else 0
            S = self._shichen_days if hasattr(self, '_shichen_days') else 0

            # 起运日期 = 出生日期 + A年 + B个月 + S天
            from datetime import datetime, timedelta
            from dateutil.relativedelta import relativedelta

            birth_date = datetime(birth_year, birth_month, birth_day, birth_hour, 0, 0)
            qiyun_date = birth_date + relativedelta(
                years=A,
                months=B,
                days=S
            )

            return qiyun_date.strftime("%Y-%m-%d")

        except Exception:
            # 如果dateutil不可用，使用简单计算
            try:
                birth_solar = self.lunar.getSolar()
                birth_year = birth_solar.getYear()
                birth_month = birth_solar.getMonth()
                birth_day = birth_solar.getDay()

                A = self._qiyun_age if hasattr(self, '_qiyun_age') else 3
                B = self._qiyun_months if hasattr(self, '_qiyun_months') else 0
                S = self._shichen_days if hasattr(self, '_shichen_days') else 0

                # 计算目标日期
                new_year = birth_year + A + (birth_month - 1 + B) // 12
                new_month = (birth_month - 1 + B) % 12 + 1
                new_day = birth_day + S

                # 处理月份溢出（可能由于S天数导致）
                from calendar import monthrange
                max_day = monthrange(new_year, new_month)[1]
                while new_day > max_day:
                    new_day -= max_day
                    new_month += 1
                    if new_month > 12:
                        new_month = 1
                        new_year += 1
                    max_day = monthrange(new_year, new_month)[1]

                return f"{new_year}-{new_month:02d}-{new_day:02d}"

            except Exception:
                return ''

    def generate_liunians_for_dayun(self, dayun: Dict, bazi: Dict, base_year: int, start_age: int, num_years: int = 10) -> List[Dict]:
        """
        生成某个大运对应的流年，并判断天克地冲、岁运并临

        流年干支从年柱开始，按实际年份推算

        返回: [{'year': 2006, 'gan': '丙', 'zhi': '戌', 'gan_zhi': '丙戌', 
                'tian_ke_di_chong': ['年柱'], 'sui_yun_bing_lin': False}, ...]
        """
        liunians = []

        # 获取年柱干支作为基准
        year_gan_zhi = bazi['year_gan'] + bazi['year_zhi']

        # 优先使用保存的出生年份，否则估算
        if hasattr(self, 'birth_year') and self.birth_year is not None:
            birth_year = self.birth_year
        else:
            birth_year = self.estimate_birth_year(bazi)

        # 计算年柱在六十甲子中的位置
        base_gan_seq = Gan.index(year_gan_zhi[0])
        base_zhi_seq = Zhi.index(year_gan_zhi[1])

        # 获取当前大运的干支
        dayun_gan = dayun.get('gan', '')
        dayun_zhi = dayun.get('zhi', '')

        for i in range(num_years):
            year = base_year + i

            # 计算该年份相对于出生年的偏移
            year_offset = year - birth_year

            # 从年柱开始推算流年干支
            gan_seq = (base_gan_seq + year_offset) % 10
            zhi_seq = (base_zhi_seq + year_offset) % 12
            gan_zhi = Gan[gan_seq] + Zhi[zhi_seq]
            liunian_gan = gan_zhi[0]
            liunian_zhi = gan_zhi[1]

            # 判断天克地冲
            tian_ke_di_chong_pillars = self.check_tian_ke_di_chong(liunian_gan, liunian_zhi, bazi)

            # 判断岁运并临
            sui_yun_bing_lin = self.check_sui_yun_bing_lin(liunian_gan, liunian_zhi, dayun_gan, dayun_zhi)

            liunians.append({
                'year': year,
                'age': start_age + i,
                'gan': liunian_gan,
                'zhi': liunian_zhi,
                'gan_zhi': gan_zhi,
                'tian_ke_di_chong': tian_ke_di_chong_pillars,
                'sui_yun_bing_lin': sui_yun_bing_lin
            })

        return liunians

    def get_ten_deities(self, day_gan: str, gan: str = None, zhi: str = None) -> Dict[str, str]:
        """
        获取天干地支相对于日主的十神关系

        返回: {'gan': '比', 'zhi': '官', 'canggan': ['甲(比)', '丙(食)']}
        """
        result = {}

        if gan:
            result['gan'] = ten_deities[day_gan][gan]

        if zhi:
            result['zhi'] = ten_deities[day_gan][zhi]

        if zhi and zhi in zhi5:
            canggan_list = []
            for canggan in zhi5[zhi]:
                shishen = ten_deities[day_gan][canggan]
                canggan_list.append(f"{canggan}{shishen}")
            result['canggan'] = canggan_list

        return result

    def get_xingyun(self, day_gan: str, zhi: str) -> str:
        """获取日主与地支的星运（12长生状态）"""
        return get_changsheng(day_gan, zhi)

    def get_zizuo(self, gan: str, zhi: str) -> str:
        """获取自坐（天干与本柱地支的12长生状态）"""
        return get_changsheng(gan, zhi)

    def get_empty(self, day_gan: str, day_zhi: str, target_zhi: str) -> str:
        """
        获取空亡

        根据日柱干支判断目标地支是否为空亡
        """
        day_ganzhi = (day_gan, day_zhi)
        if day_ganzhi in empties:
            empty_zhis = empties[day_ganzhi]
            return "*" if target_zhi in empty_zhis else ""
        return ""

    def get_nayin(self, gan: str, zhi: str) -> str:
        """获取纳音"""
        return nayins.get((gan, zhi), '')

    def calculate_zhi_relations(self, target_zhi: str, other_zhis: List[str]) -> Dict[str, str]:
        """
        计算地支与其他地支的关系

        返回: {'合': '寅,午', '冲': '申', '刑': '巳', ...}
        """
        relations = defaultdict(list)

        for other_zhi in other_zhis:
            if other_zhi == target_zhi:
                continue

            # 检查各种关系
            att = zhi_atts.get(target_zhi, {})

            # 冲
            if '冲' in att and att['冲'] == other_zhi:
                relations['冲'].append(other_zhi)

            # 刑
            if ('刑' in att and att['刑'] == other_zhi) or ('被刑' in att and att['被刑'] == other_zhi):
                relations['刑'].append(other_zhi)

            # 合
            if '合' in att and isinstance(att['合'], tuple) and other_zhi in att['合']:
                relations['合'].append(other_zhi)

            # 害
            if '害' in att and att['害'] == other_zhi:
                relations['害'].append(other_zhi)

            # 会
            if '会' in att and isinstance(att['会'], tuple) and other_zhi in att['会']:
                relations['会'].append(other_zhi)

            # 破
            if '破' in att and att['破'] == other_zhi:
                relations['破'].append(other_zhi)

            # 六合补充
            for zhi_he in zhi_6hes:
                if target_zhi in zhi_he and other_zhi in zhi_he:
                    if other_zhi not in relations.get('合', []):
                        relations['合'].append(other_zhi)

        return {k: ','.join(v) for k, v in relations.items() if v}

    def calculate_shensha_for_ganzhi(self, ganzhi: Dict, bazi: Dict, is_dayun_liunian: bool = False, is_male: bool = True) -> List[str]:
        """
        计算干支组合的神煞

        将该干支作为独立的柱来计算神煞，返回该柱的神煞列表

        参数:
            ganzhi: 干支字典 {'gan': '甲', 'zhi': '子'}
            bazi: 原局八字字典
            is_dayun_liunian: 是否为大运/流年神煞计算
            is_male: 是否为男性（用于勾绞煞判断）

        返回: 神煞列表
        """
        if is_dayun_liunian:
            # 大运/流年神煞计算：使用新方法，支持a-g类神煞
            shenshas = self.shensha_calc.calculate_dayun_liunian(
                ganzhi['gan'],
                ganzhi['zhi'],
                'dayun' if 'index' in ganzhi else 'liunian',
                bazi,
                is_male
            )
            return shenshas
        else:
            # 原局神煞计算：保持原有逻辑不变
            shensha_bazi = {
                'year_gan': ganzhi['gan'],
                'year_zhi': ganzhi['zhi'],
                'month_gan': bazi['month_gan'],
                'month_zhi': bazi['month_zhi'],
                'day_gan': bazi['day_gan'],
                'day_zhi': bazi['day_zhi'],
                'time_gan': bazi['time_gan'],
                'time_zhi': bazi['time_zhi']
            }
            all_shensha = self.shensha_calc.calculate(shensha_bazi)
            shenshas = all_shensha.get('年柱', [])
            return shenshas

    def calculate_comprehensive_shensha(self, all_zhis: List[str], day_gan: str, day_zhi: str) -> List[str]:
        """
        计算综合神煞（所有大运流年地支相对日主的神煞加起来）

        返回: 综合神煞列表
        """
        comprehensive = []

        # 构造临时八字用于神煞计算
        for zhi in all_zhis:
            temp_bazi = {
                'year_gan': day_gan,
                'year_zhi': zhi,
                'month_gan': '甲',
                'month_zhi': '子',
                'day_gan': day_gan,
                'day_zhi': day_zhi,
                'time_gan': '甲',
                'time_zhi': '子'
            }

            shensha_result = self.shensha_calc.calculate(temp_bazi)
            if '年柱' in shensha_result:
                comprehensive.extend(shensha_result['年柱'])

        return list(dict.fromkeys(comprehensive))


def print_table_header():
    """打印表格头部"""
    print("=" * 160)
    print(f"{'序号':<6}{'年份':<10}{'起运日期':<12}{'干支':<8}{'十二长生':<8}{'纳音':<10}{'十神':<6}{'天干':<6}{'地支':<6}{'藏干十神':<30}{'神煞':<30}{'特殊备注':<20}")
    print("=" * 160)


def print_table_row(data: Dict):
    """打印表格行"""
    # 获取神煞字符串
    shensha_str = ' '.join(data.get('shensha', []))
    # 获取起运日期
    start_date = data.get('start_date', '')
    
    # 获取特殊备注（天克地冲、岁运并临）
    remarks = []
    if data.get('tian_ke_di_chong'):
        pillars = '、'.join(data['tian_ke_di_chong'])
        remarks.append(f"天克地冲({pillars})")
    if data.get('sui_yun_bing_lin'):
        remarks.append("岁运并临")
    remark_str = ' '.join(remarks)

    row_str = f"{data.get('seq', ''):<6}{data.get('year', ''):<10}{start_date:<12}{data.get('gan_zhi', ''):<8}{data.get('changsheng', ''):<8}"
    row_str += f"{data.get('nayin', ''):<10}{data.get('shishen', ''):<6}{data.get('gan', ''):<6}{data.get('zhi', ''):<6}"
    row_str += f"{'　'.join(data.get('canggan', [])):<30}{shensha_str:<30}{remark_str:<20}"

    print(row_str)


def main():
    """主函数"""
    print("=" * 120)
    print("大运流年计算器")
    print("=" * 120)

    calc = BaZiCalculator()

    # 输入八字
    while True:
        bazi_input = input("\n请输入八字或出生日期(格式: 甲子 乙丑 丙寅 丁卯 或 1990 5 15 10): ").strip()
        try:
            bazi = calc.parse_bazi_input(bazi_input)
            break
        except ValueError as e:
            print(f"输入错误: {e}")
            print("请重新输入")

    # 输入性别
    gender_input = input("\n请输入性别(1-男, 0-女, 默认男): ").strip()
    is_male = True if gender_input != '0' else False

    # 计算起运信息
    qiyun_years, direction, sex, qiyun_months = calc.calculate_qiyun(bazi, is_male)
    sex_str = "男" if is_male else "女"

    # 显示起运时间
    qiyun_str = f"{qiyun_years}岁"
    if qiyun_months > 0:
        qiyun_str += f"{qiyun_months}个月"

    print(f"\n{'='*120}")
    print(f"八字: {bazi['year_gan']}{bazi['year_zhi']} {bazi['month_gan']}{bazi['month_zhi']} {bazi['day_gan']}{bazi['day_zhi']} {bazi['time_gan']}{bazi['time_zhi']}")
    print(f"日主: {bazi['day_gan']}")
    print(f"性别: {sex_str}")
    print(f"起运年龄: {qiyun_str}")
    print(f"大运方向: {'顺行' if direction > 0 else '逆行'}")
    print(f"{'='*120}")

    # 生成大运和流年
    dayuns = calc.generate_dayuns(bazi, direction, count=12)

    # 输入查看年份
    year_input = input("\n请输入要查看的年份(如2010，留空查看全部): ").strip()

    # 优先使用保存的出生年份，否则估算
    if hasattr(calc, 'birth_year') and calc.birth_year is not None:
        birth_year = calc.birth_year
    else:
        birth_year = calc.estimate_birth_year(bazi)

    if year_input:
        try:
            target_year = int(year_input)
        except ValueError:
            print("年份格式错误，将显示全部")
            target_year = None
    else:
        target_year = None

    # 计算要显示的大运范围
    if target_year:
        # 计算该年份所在的大运
        age = target_year - birth_year
        dayun_index = max(0, (age - qiyun_years) // 10)
        if dayun_index >= len(dayuns):
            dayun_index = len(dayuns) - 1
        display_dayuns = dayuns[:dayun_index + 1]
    else:
        display_dayuns = dayuns

    # 准备所有地支用于综合神煞计算
    all_dayun_liunian_zhis = []

    # 收集所有数据
    all_rows = []

    # 生成每个大运的流年
    for dayun_idx, dayun in enumerate(display_dayuns):
        # 使用大运的起运日期作为base_year，而不是简单计算
        start_date = dayun.get('start_date', '')
        if start_date:
            from datetime import datetime
            base_year = datetime.strptime(start_date, "%Y-%m-%d").year
            dayun_age_start = qiyun_years + dayun_idx * 10
        else:
            # 回退到简单计算
            dayun_age_start = qiyun_years + dayun_idx * 10
            base_year = birth_year + dayun_age_start

        # 获取大运的十神
        dayun_td = calc.get_ten_deities(bazi['day_gan'], dayun['gan'], dayun['zhi'])
        dayun_xingyun = calc.get_xingyun(bazi['day_gan'], dayun['zhi'])
        dayun_zizuo = calc.get_zizuo(dayun['gan'], dayun['zhi'])
        dayun_empty = calc.get_empty(bazi['day_gan'], bazi['day_zhi'], dayun['zhi'])
        dayun_nayin = calc.get_nayin(dayun['gan'], dayun['zhi'])

        # 计算大运地支与其他柱的关系
        other_zhis = [bazi['year_zhi'], bazi['month_zhi'], bazi['day_zhi'], bazi['time_zhi']]
        dayun_relations = calc.calculate_zhi_relations(dayun['zhi'], other_zhis)

        # 计算大运神煞
        dayun_shensha = calc.calculate_shensha_for_ganzhi(dayun, bazi, is_dayun_liunian=True, is_male=is_male)

        all_rows.append({
            'seq': f"大运{dayun_idx + 1}",
            'year': dayun.get('age', ''),
            'start_date': dayun.get('start_date', ''),
            'gan_zhi': dayun['gan_zhi'],
            'changsheng': dayun_xingyun,
            'nayin': dayun_nayin + dayun_empty,
            'shishen': dayun_td.get('zhi', ''),
            'gan': dayun['gan'],
            'zhi': dayun['zhi'],
            'canggan': [],
            'relations': dayun_relations,
            'shensha': dayun_shensha
        })

        all_dayun_liunian_zhis.append(dayun['zhi'])

        # 生成该大运的流年
        num_liunian_years = 10 if target_year else 10
        liunians = calc.generate_liunians_for_dayun(dayun, bazi, base_year, dayun_age_start, num_liunian_years)

        for liunian in liunians:
            # 如果指定了年份，只显示到该年份为止
            if target_year and liunian['year'] > target_year:
                continue

            # 获取流年的十神
            liunian_td = calc.get_ten_deities(bazi['day_gan'], liunian['gan'], liunian['zhi'])
            liunian_xingyun = calc.get_xingyun(bazi['day_gan'], liunian['zhi'])
            liunian_zizuo = calc.get_zizuo(liunian['gan'], liunian['zhi'])
            liunian_empty = calc.get_empty(bazi['day_gan'], bazi['day_zhi'], liunian['zhi'])
            liunian_nayin = calc.get_nayin(liunian['gan'], liunian['zhi'])

            # 计算流年地支与其他柱的关系
            liunian_relations = calc.calculate_zhi_relations(liunian['zhi'], other_zhis)

            # 计算流年神煞
            liunian_shensha = calc.calculate_shensha_for_ganzhi(liunian, bazi, is_dayun_liunian=True, is_male=is_male)

            all_rows.append({
                'seq': liunian['age'],
                'year': liunian['year'],
                'start_date': '',
                'gan_zhi': liunian['gan_zhi'],
                'changsheng': liunian_xingyun,
                'nayin': liunian_nayin + liunian_empty,
                'shishen': liunian_td.get('zhi', ''),
                'gan': liunian['gan'],
                'zhi': liunian['zhi'],
                'canggan': liunian_td.get('canggan', []),
                'relations': liunian_relations,
                'shensha': liunian_shensha,
                'tian_ke_di_chong': liunian.get('tian_ke_di_chong', []),
                'sui_yun_bing_lin': liunian.get('sui_yun_bing_lin', False)
            })

            all_dayun_liunian_zhis.append(liunian['zhi'])

    # 打印表格
    print_table_header()
    for row in all_rows:
        print_table_row(row)
    print("=" * 160)

    # 打印综合神煞
    comprehensive_shensha = calc.calculate_comprehensive_shensha(all_dayun_liunian_zhis, bazi['day_gan'], bazi['day_zhi'])
    if comprehensive_shensha:
        print("\n综合神煞:", ' '.join(comprehensive_shensha))
    print("=" * 160)


# 兼容性包装类 - 用于 bazi_geju_refactored_v5.py 等文件
class DaYunLiuNian:
    """
    DaYunLiuNian 包装类 - 封装 BaZiCalculator 以提供兼容接口

    该类提供了与旧版 DaYunLiuNian 类相同的接口，但底层使用 BaZiCalculator 实现
    """

    def __init__(self, day_gan: str, month_gan: str, month_zhi: str,
                 year_gan: str, year_zhi: str, day_zhi: str,
                 is_male: bool = True, birth_date: Optional[str] = None,
                 time_gan: str = '', time_zhi: str = ''):
        """
        初始化大运流年分析器

        参数:
            day_gan: 日干
            month_gan: 月干
            month_zhi: 月支
            year_gan: 年干
            year_zhi: 年支
            day_zhi: 日支
            is_male: 是否为男命
            birth_date: 出生日期 (格式: "YYYY-MM-DD" 或 "YYYY-MM-DD HH:MM")
            time_gan: 时干（可选，无时柱为空）
            time_zhi: 时支（可选，无时柱为空）
        """
        # 创建 BaZiCalculator 实例
        self.calc = BaZiCalculator()

        # 如果提供了出生日期，使用日期计算八字并初始化
        self._qiyun_age = None
        self._qiyun_months = None
        self._direction = None
        
        # 标记是否有时柱
        has_time_pillar = time_gan and time_zhi and time_gan.strip() and time_zhi.strip()

        if birth_date:
            try:
                if ' ' in birth_date:
                    from datetime import datetime
                    dt = datetime.strptime(birth_date, "%Y-%m-%d %H:%M")
                    year, month, day, hour = dt.year, dt.month, dt.day, dt.hour
                else:
                    from datetime import datetime
                    dt = datetime.strptime(birth_date, "%Y-%m-%d")
                    year, month, day, hour = dt.year, dt.month, dt.day, None  # 无时柱

                # 从日期获取八字（会设置 birth_year 和 lunar）
                # 支持无时柱的情况
                bazi_from_date = self.calc.get_bazi_from_date(year, month, day, hour)
                
                # 使用从日期计算的八字
                self.bazi = bazi_from_date
            except Exception as e:
                print(f"警告: 解析出生日期失败: {e}")
                # 使用传入的八字参数
                self.bazi = {
                    'year_gan': year_gan,
                    'year_zhi': year_zhi,
                    'month_gan': month_gan,
                    'month_zhi': month_zhi,
                    'day_gan': day_gan,
                    'day_zhi': day_zhi,
                    'time_gan': time_gan,
                    'time_zhi': time_zhi
                }
        else:
            # 使用传入的八字参数
            self.bazi = {
                'year_gan': year_gan,
                'year_zhi': year_zhi,
                'month_gan': month_gan,
                'month_zhi': month_zhi,
                'day_gan': day_gan,
                'day_zhi': day_zhi,
                'time_gan': time_gan,
                'time_zhi': time_zhi
            }

        # 计算起运信息
        qiyun_years, direction, sex, qiyun_months = self.calc.calculate_qiyun(self.bazi, is_male)
        self._qiyun_age = qiyun_years
        self._qiyun_months = qiyun_months
        self._direction = direction
        self._is_male = is_male

        # 生成大运和小运（生成15个大运以覆盖150岁）
        self._dayuns = self.calc.generate_dayuns(self.bazi, direction, count=15)
        self._xiaoyuns = self.calc.generate_xiaoyuns(self.bazi, count=self._qiyun_age if self._qiyun_age else 20)

    @property
    def dayuns(self) -> List[Dict]:
        """获取大运列表"""
        # 为每个大运添加年龄范围信息
        qiyun_age = self._qiyun_age if self._qiyun_age is not None else 3
        dayuns_with_age = []
        for dayun in self._dayuns:
            idx = dayun['index'] - 1
            start_age = qiyun_age + idx * 10
            end_age = start_age + 9
            dayuns_with_age.append({
                'gan_zhi': dayun['gan_zhi'],
                'index': dayun['index'],
                'gan': dayun['gan'],
                'zhi': dayun['zhi'],
                'start_age': start_age,
                'end_age': end_age,
                'start_date': dayun.get('start_date', '')
            })
        return dayuns_with_age

    @property
    def xiaoyuns(self) -> List[Dict]:
        """获取小运列表"""
        xiaoyuns_with_type = []
        for xy in self._xiaoyuns:
            xiaoyuns_with_type.append({
                'age': xy['age'],
                'gan_zhi': xy['gan_zhi'],
                'gan': xy['gan'],
                'zhi': xy['zhi'],
                'type': '小运'
            })
        return xiaoyuns_with_type

    @property
    def qiyun_age(self) -> int:
        """获取起运年龄"""
        return self._qiyun_age if self._qiyun_age is not None else 3

    def get_liunian_ganzhi_by_year(self, year: int) -> str:
        """
        根据年份计算流年干支

        返回: '甲子'
        """
        # 使用保存的出生年份，或估算
        if hasattr(self.calc, 'birth_year') and self.calc.birth_year is not None:
            birth_year = self.calc.birth_year
        else:
            birth_year = self.calc.estimate_birth_year(self.bazi)

        # 计算年柱在六十甲子中的位置
        year_ganzhi = self.bazi['year_gan'] + self.bazi['year_zhi']
        base_gan_seq = Gan.index(year_ganzhi[0])
        base_zhi_seq = Zhi.index(year_ganzhi[1])

        # 计算该年份相对于出生年的偏移
        year_offset = year - birth_year

        # 从年柱开始推算流年干支
        gan_seq = (base_gan_seq + year_offset) % 10
        zhi_seq = (base_zhi_seq + year_offset) % 12
        gan_zhi = Gan[gan_seq] + Zhi[zhi_seq]

        return gan_zhi

    def get_dayun_by_year(self, year: int) -> Optional[Dict]:
        """
        根据年份获取大运信息

        返回: {'gan_zhi': '己未', 'index': 1, 'start_age': 3, 'end_age': 12}
        """
        # 计算出生年份
        if hasattr(self.calc, 'birth_year') and self.calc.birth_year is not None:
            birth_year = self.calc.birth_year
        else:
            birth_year = self.calc.estimate_birth_year(self.bazi)

        # 计算该年份的年龄
        age = year - birth_year

        # 计算该年龄所在的大运
        qiyun_age = self._qiyun_age if self._qiyun_age is not None else 3
        dayun_index = max(0, (age - qiyun_age) // 10)

        # 检查是否在大运范围内
        if dayun_index >= len(self._dayuns):
            return None

        dayun = self._dayuns[dayun_index]
        return {
            'gan_zhi': dayun['gan_zhi'],
            'index': dayun['index'],
            'start_age': qiyun_age + dayun_index * 10,
            'end_age': qiyun_age + dayun_index * 10 + 9
        }

    def get_liunian_info(self, year: int) -> Optional[Dict]:
        """
        获取指定流年的详细信息，包括天克地冲、岁运并临判断

        参数:
            year: 年份

        返回: {
            'year': 2024,
            'gan_zhi': '甲辰',
            'gan': '甲',
            'zhi': '辰',
            'tian_ke_di_chong': ['年柱', '日柱'],  # 与原局构成天克地冲的柱位列表
            'sui_yun_bing_lin': False  # 是否岁运并临
        }
        """
        # 获取流年干支
        liunian_ganzhi = self.get_liunian_ganzhi_by_year(year)
        if not liunian_ganzhi:
            return None

        liunian_gan = liunian_ganzhi[0]
        liunian_zhi = liunian_ganzhi[1]

        # 判断天克地冲
        tian_ke_di_chong_pillars = self.calc.check_tian_ke_di_chong(liunian_gan, liunian_zhi, self.bazi)

        # 获取当前大运
        dayun_info = self.get_dayun_by_year(year)
        sui_yun_bing_lin = False
        if dayun_info:
            dayun_ganzhi = dayun_info['gan_zhi']
            sui_yun_bing_lin = self.calc.check_sui_yun_bing_lin(
                liunian_gan, liunian_zhi, dayun_ganzhi[0], dayun_ganzhi[1]
            )

        return {
            'year': year,
            'gan_zhi': liunian_ganzhi,
            'gan': liunian_gan,
            'zhi': liunian_zhi,
            'tian_ke_di_chong': tian_ke_di_chong_pillars,
            'sui_yun_bing_lin': sui_yun_bing_lin
        }

    def check_tian_ke_di_chong(self, liunian_gan: str, liunian_zhi: str) -> List[str]:
        """
        判断流年是否与原局构成天克地冲

        参数:
            liunian_gan: 流年天干
            liunian_zhi: 流年地支

        返回:
            构成天克地冲的柱位列表
        """
        return self.calc.check_tian_ke_di_chong(liunian_gan, liunian_zhi, self.bazi)

    def check_sui_yun_bing_lin(self, liunian_gan: str, liunian_zhi: str, dayun_gan: str, dayun_zhi: str) -> bool:
        """
        判断流年是否与大运构成岁运并临

        参数:
            liunian_gan: 流年天干
            liunian_zhi: 流年地支
            dayun_gan: 大运天干
            dayun_zhi: 大运地支

        返回:
            True表示构成岁运并临
        """
        return self.calc.check_sui_yun_bing_lin(liunian_gan, liunian_zhi, dayun_gan, dayun_zhi)


if __name__ == "__main__":
    main()