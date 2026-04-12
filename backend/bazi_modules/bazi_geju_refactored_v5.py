#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格局判定模块 - 重构版（包含第六论级）
严格按照《渊海子平》、《三命通会》、《子平真诠》等古籍理论
按照五级论级体系进行格局判定，并新增第六论级分析大运流年影响

作者: Claude AI
创建日期: 2026-02-03
版本: 6.0（新增第六论级）
"""

from typing import Dict, List, Optional, Set, Tuple
from collections import OrderedDict
from bidict import bidict
try:
    from lunar_python import Lunar, Solar
except ImportError:
    print("警告: 无法导入lunar_python模块")

# 导入基础数据
try:
    from ganzhi import (
        Gan, Zhi, zhi5, ten_deities, zhi_atts,
        zhi_hes, zhi_huis, zhi_3hes, zhi_half_3hes,
        zhi_chongs, gong_he, gong_hui, gan_hes, wuhangs, gan5, zhi5_list
    )
    from datas import tiaohous, jinbuhuan, jins, nayins, empties, day_shens, g_shens, shens_infos
    from changsheng import get_changsheng, CHANGSHENG_DESC
    from shensha_database import ShenShaDatabase, ShenShaCalculator
    from dayun_liunian import DaYunLiuNian
    from geju_database import GeJuDatabase, ShenQiangCalculator
except ImportError:
    print("警告: 无法导入基础模块,请确保在正确的目录下运行")
    # 定义默认值
    zhi5_list = {}
    zhi_atts = {}
    gan_hes = []
    zhi_hes = {}
    zhi_huis = {}
    zhi_3hes = {}
    GeJuDatabase = None
    ShenQiangCalculator = None


class GeJuAnalyzerV5:
    """
    格局分析器 - 五级论级体系 + 第六论级（大运流年分析）
    支持真太阳时计算
    
    第一论级: 月令与格局
    第二论级: 三会、三合、六合、刑冲破害
    第三论级: 五合、生克制
    第四论级: 特殊情况(从格、化气、战局)
    第五论级: 定喜忌、推岁运、辅助功能
    第六论级: 大运流年综合分析（将大运、流年带入原局重复第二、三、四论级的分析）
    """
    
    # 天干五合化气
    GAN_HE_HUA = {
        ('甲', '己'): {'化': '土', '中神': '戊', '条件': {'月令': ['辰', '戌', '丑', '未'], '地支': ['辰', '戌', '丑', '未', '午', '巳']}},
        ('己', '甲'): {'化': '土', '中神': '戊', '条件': {'月令': ['辰', '戌', '丑', '未'], '地支': ['辰', '戌', '丑', '未', '午', '巳']}},
        ('乙', '庚'): {'化': '金', '中神': '辛', '条件': {'月令': ['申', '酉', '辰', '戌'], '地支': ['申', '酉', '辰', '戌', '巳', '午']}},
        ('庚', '乙'): {'化': '金', '中神': '辛', '条件': {'月令': ['申', '酉', '辰', '戌'], '地支': ['申', '酉', '辰', '戌', '巳', '午']}},
        ('丙', '辛'): {'化': '水', '中神': '壬', '条件': {'月令': ['亥', '子', '申', '辰'], '地支': ['亥', '子', '申', '辰', '亥', '子']}},
        ('辛', '丙'): {'化': '水', '中神': '壬', '条件': {'月令': ['亥', '子', '申', '辰'], '地支': ['亥', '子', '申', '辰', '亥', '子']}},
        ('丁', '壬'): {'化': '木', '中神': '甲', '条件': {'月令': ['寅', '卯', '亥', '未'], '地支': ['寅', '卯', '亥', '未', '寅', '卯']}},
        ('壬', '丁'): {'化': '木', '中神': '甲', '条件': {'月令': ['寅', '卯', '亥', '未'], '地支': ['寅', '卯', '亥', '未', '寅', '卯']}},
        ('戊', '癸'): {'化': '火', '中神': '丙', '条件': {'月令': ['巳', '午', '寅', '未'], '地支': ['巳', '午', '寅', '未', '巳', '午']}},
        ('癸', '戊'): {'化': '火', '中神': '丙', '条件': {'月令': ['巳', '午', '寅', '未'], '地支': ['巳', '午', '寅', '未', '巳', '午']}}
    }

    # 地支五行映射
    ZHI_WUHANGS = {
        '子': '水', '亥': '水',
        '寅': '木', '卯': '木',
        '巳': '火', '午': '火',
        '申': '金', '酉': '金',
        '辰': '土', '戌': '土', '丑': '土', '未': '土'
    }

    # ==================== 统一评分标准 ====================
    # 适用于原局和大运流年五行十神能量计算的通用标准
    
    # 1. 地支关系评分标准
    SCORE_ZHI_RELATIONS = {
        # 三会局：五行+3，十神+0
        '三会': {'wuxing': 3, 'shishen': 0},
        # 半会：五行+1.5，十神+0
        '半会': {'wuxing': 1.5, 'shishen': 0},
        # 拱会：五行+1，藏干主气十神+1
        '拱会': {'wuxing': 1, 'shishen': 1, 'gong_zhi_canggan_shishen': True},
        # 三合局：五行+1，十神+0
        '三合': {'wuxing': 1, 'shishen': 0},
        # 半合：五行+0.5，十神+0
        '半合': {'wuxing': 0.5, 'shishen': 0},
        # 拱合：五行+1，藏干主气十神+1
        '拱合': {'wuxing': 1, 'shishen': 1, 'gong_zhi_canggan_shishen': True},
        # 六合：五行+1，十神+0
        '六合': {'wuxing': 1, 'shishen': 0},
    }
    
    # 2. 天干关系评分标准
    SCORE_GAN_RELATIONS = {
        # 天干五合：五行+2，十神+0
        '天干五合': {'wuxing': 2, 'shishen': 0},
        # 天干相克：被克方五行-1，十神-1
        '天干相克': {'wuxing': -1, 'shishen': -1, 'target': '被克方'},
    }
    
    # 3. 干支关系评分标准
    SCORE_GANZHI_RELATIONS = {
        # 盖头：地支五行-1，藏干主气十神-1
        '盖头': {'wuxing': -1, 'shishen': -1, 'target': '地支', 'canggan_shishen': True},
        # 截脚：天干五行-1，十神-1
        '截脚': {'wuxing': -1, 'shishen': -1, 'target': '天干'},
    }
    
    # 4. 基础评分标准
    SCORE_BASE = {
        # 天干基础分
        '天干': {'wuxing': 1, 'shishen': 1},
        # 地支藏干：本气+0.6，中气+0.3，余气+0.1
        '藏干本气': {'wuxing': 0.6, 'shishen': 0.6},
        '藏干中气': {'wuxing': 0.3, 'shishen': 0.3},
        '藏干余气': {'wuxing': 0.1, 'shishen': 0.1},
    }
    
    # 5. 通根透干评分标准（更新后）
    SCORE_TONGGEN_TOUGAN = {
        # 通根评分标准（根据位置不同）
        # a. 月令通根：本气+0.6，中气+0.3，余气+0.1（五行和十神相同）
        # b. 日支通根：本气+0.42，中气+0.21，余气+0.07
        # c. 时支通根：本气+0.3，中气+0.15，余气+0.05
        # d. 年支通根：本气+0.18，中气+0.09，余气+0.03
        # e. 通根透（干支一柱通根）则再+0.5
        '通根_月令_本气': {'wuxing': 0.6, 'shishen': 0.6},
        '通根_月令_中气': {'wuxing': 0.3, 'shishen': 0.3},
        '通根_月令_余气': {'wuxing': 0.1, 'shishen': 0.1},
        '通根_日支_本气': {'wuxing': 0.42, 'shishen': 0.42},
        '通根_日支_中气': {'wuxing': 0.21, 'shishen': 0.21},
        '通根_日支_余气': {'wuxing': 0.07, 'shishen': 0.07},
        '通根_时支_本气': {'wuxing': 0.3, 'shishen': 0.3},
        '通根_时支_中气': {'wuxing': 0.15, 'shishen': 0.15},
        '通根_时支_余气': {'wuxing': 0.05, 'shishen': 0.05},
        '通根_年支_本气': {'wuxing': 0.18, 'shishen': 0.18},
        '通根_年支_中气': {'wuxing': 0.09, 'shishen': 0.09},
        '通根_年支_余气': {'wuxing': 0.03, 'shishen': 0.03},
        '通根透': {'wuxing': 0.5, 'shishen': 0.5},  # 干支一柱通根额外加成
        # 透干不参与计算（已移除）
    }
    
    # 6. 月令评分标准（更新后：本气+1.8，中气+0.9，余气+0.3）
    SCORE_YUELING = {
        '月令藏干_本气': {'wuxing': 1.8, 'shishen': 1.8},
        '月令藏干_中气': {'wuxing': 0.9, 'shishen': 0.9},
        '月令藏干_余气': {'wuxing': 0.3, 'shishen': 0.3},
    }
    
    # 7. 大运评分标准（当做月令2处理，与月令相同）
    SCORE_DAYUN = {
        '大运藏干_本气': {'wuxing': 1.8, 'shishen': 1.8},
        '大运藏干_中气': {'wuxing': 0.9, 'shishen': 0.9},
        '大运藏干_余气': {'wuxing': 0.3, 'shishen': 0.3},
    }
    
    # 8. 盖头截脚评分标准（更新后）
    SCORE_GAITOU_JIEJIAO = {
        # 盖头：五行能量-0.5，藏干主气的十神能量-0.3
        '盖头_五行': -0.5,
        '盖头_主气十神': -0.3,
        # 截脚：五行能量-0.5，十神能量-0.5
        '截脚_五行': -0.5,
        '截脚_十神': -0.5,
    }
    
    # 盖头组合（天干克地支）
    GAITOU_COMBINATIONS = [
        ('甲', '辰'), ('甲', '戌'), ('乙', '丑'), ('乙', '未'),
        ('丙', '申'), ('丁', '酉'), ('戊', '子'), ('己', '亥'),
        ('庚', '寅'), ('辛', '卯'), ('壬', '午'), ('癸', '巳')
    ]
    
    # 截脚组合（地支克天干）
    JIEJIAO_COMBINATIONS = [
        ('甲', '申'), ('乙', '酉'), ('丙', '子'), ('丁', '亥'),
        ('戊', '寅'), ('己', '卯'), ('庚', '午'), ('辛', '巳'),
        ('壬', '辰'), ('癸', '丑'), ('癸', '未'), ('壬', '戌')
    ]

    def __init__(self, bazi: Dict[str, str], liunian_year: Optional[int] = None,
                 is_male: bool = True, birth_date: Optional[str] = None):
        """
        初始化格局分析器
        
        参数:
            bazi: 八字字典 {'year_gan': '甲', 'year_zhi': '子', ...}
            liunian_year: 流年年份，用于分析大运流年影响
            is_male: 是否为男命（默认True）
            birth_date: 出生日期，格式如 "2000-05-21" 或 "2000-05-21 14:30"
        """
        self.bazi = bazi
        self.liunian_year = liunian_year
        self.is_male = is_male
        self.birth_date = birth_date
        self.day_gan = bazi.get('day_gan', '')
        self.month_zhi = bazi.get('month_zhi', '')
        
        # 支持时柱为空的情况 - 如果时柱为空，则只分析年月日三柱
        time_gan = bazi.get('time_gan', '')
        time_zhi = bazi.get('time_zhi', '')
        
        # 检查时柱是否有效（非空且非None）
        has_time_pillar = time_gan and time_zhi and time_gan.strip() and time_zhi.strip()
        self.has_time_pillar = has_time_pillar
        
        if has_time_pillar:
            # 完整四柱
            self.gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''), 
                      self.day_gan, time_gan]
            self.zhis = [bazi.get('year_zhi', ''), self.month_zhi, 
                      bazi.get('day_zhi', ''), time_zhi]
        else:
            # 只有年月日三柱，时柱为空
            self.gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''), 
                      self.day_gan]
            self.zhis = [bazi.get('year_zhi', ''), self.month_zhi, 
                      bazi.get('day_zhi', '')]
        
        # 初始化神煞计算器
        self.shensha_db = ShenShaDatabase()
        self.shensha_calculator = ShenShaCalculator(self.shensha_db)

        # 初始化格局数据库
        self.geju_db = GeJuDatabase() if GeJuDatabase else None

        # 初始化身强身弱计算器
        self.shenqiang_calculator = ShenQiangCalculator(self.geju_db) if ShenQiangCalculator and self.geju_db else None

        # 初始化大运流年分析器
        self.dayun_liunian = None
        if self.liunian_year:
            try:
                # 传递时柱信息（可能为空）
                time_gan = self.gans[3] if self.has_time_pillar else ''
                time_zhi = self.zhis[3] if self.has_time_pillar else ''
                self.dayun_liunian = DaYunLiuNian(
                    day_gan=self.day_gan,
                    month_gan=self.gans[1],
                    month_zhi=self.month_zhi,
                    year_gan=self.gans[0],
                    year_zhi=self.zhis[0],
                    day_zhi=self.zhis[2],
                    is_male=self.is_male,
                    birth_date=self.birth_date,
                    time_gan=time_gan,
                    time_zhi=time_zhi
                )
            except Exception as e:
                print(f"警告: 初始化大运流年分析器失败: {e}")

        # 分析结果存储
        self.analysis_result = OrderedDict()

    def _add_shishen_to_gan(self, text: str) -> str:
        """为天干添加十神标注"""
        if not hasattr(self, 'day_gan') or not self.day_gan:
            return text
        try:
            from ganzhi import ten_deities
            result = text
            for gan in '甲乙丙丁戊己庚辛壬癸':
                if gan in result:
                    shishen = ten_deities[self.day_gan].get(gan, '')
                    if shishen:
                        result = result.replace(gan, f"{gan}({shishen})")
            return result
        except:
            return text

    def _add_shishen_to_zhi(self, text: str) -> str:
        """为地支添加十神标注（取藏干主气）"""
        if not hasattr(self, 'day_gan') or not self.day_gan:
            return text
        try:
            from ganzhi import ten_deities, zhi5
            result = text
            for zhi in '子丑寅卯辰巳午未申酉戌亥':
                if zhi in result:
                    # 获取地支藏干的主气
                    canggan_list = zhi5.get(zhi, [])
                    if canggan_list:
                        main_gan = canggan_list[0]  # 主气
                        shishen = ten_deities[self.day_gan].get(main_gan, '')
                        if shishen:
                            result = result.replace(zhi, f"{zhi}({shishen})")
            return result
        except:
            return text

    def _add_shishen_to_both(self, text: str) -> str:
        """为天干和地支都添加十神标注"""
        if not hasattr(self, 'day_gan') or not self.day_gan:
            return text
        try:
            from ganzhi import ten_deities, zhi5
            result = text
            # 先处理天干
            for gan in '甲乙丙丁戊己庚辛壬癸':
                if gan in result:
                    shishen = ten_deities[self.day_gan].get(gan, '')
                    if shishen:
                        result = result.replace(gan, f"{gan}({shishen})", 1)
            # 再处理地支
            for zhi in '子丑寅卯辰巳午未申酉戌亥':
                if zhi in result and '(' not in result[result.index(zhi):result.index(zhi)+3]:
                    canggan_list = zhi5.get(zhi, [])
                    if canggan_list:
                        main_gan = canggan_list[0]
                        shishen = ten_deities[self.day_gan].get(main_gan, '')
                        if shishen:
                            result = result.replace(zhi, f"{zhi}({shishen})", 1)
            return result
        except:
            return text

    def analyze(self) -> Dict:
        """
        执行完整的格局分析
        
        返回:
            包含五级论级分析结果的字典
        """
        # 第一论级: 月令与格局
        self.analysis_result['第一论级_月令与格局'] = self._analyze_month_yueling()
        
        # 第二论级: 地支关系
        self.analysis_result['第二论级_地支关系'] = self._analyze_zhi_relations()
        
        # 第三论级: 天干关系
        self.analysis_result['第三论级_天干关系'] = self._analyze_gan_relations()
        
        # 第四论级: 天干与地支的关系
        self.analysis_result['第四论级_天干与地支的关系'] = self._analyze_gan_zhi_relations()
        
        # 第五论级: 定喜忌、推岁运、辅助功能
        if self.liunian_year:
            self.analysis_result['第五论级_大运流年'] = self._analyze_suiyun()
            # 第六论级: 大运流年综合分析
            sixth_result = self._analyze_sixth_level()
            self.analysis_result['第六论级_大运流年'] = sixth_result
            # 同时保留旧键名用于兼容
            self.analysis_result['第六论级'] = sixth_result
        self.analysis_result['第五论级_定喜忌'] = self._analyze_xi_ji()
        self.analysis_result['第五论级_辅助信息'] = self._analyze_auxiliary_info()
        
        # 综合格局判定
        self.analysis_result['格局综合判定'] = self._determine_main_geju()
        
        return dict(self.analysis_result)
    
    def _analyze_month_yueling(self) -> Dict:
        """第一论级: 分析月令与格局"""
        result = {
            '月令': '',
            '月令藏干': [],
            '月令主气': '',
            '主要格局': '',
            '次要格局': [],
            '格局说明': ''
        }

        # 获取月令地支
        result['月令'] = self.month_zhi

        # 获取月令藏干
        canggan_list = zhi5_list.get(self.month_zhi, []) if zhi5_list else []
        result['月令藏干'] = canggan_list
        result['月令主气'] = canggan_list[0] if canggan_list else ''

        # 主要格局判定 - 调用 geju_database.py 中的 GeJuCalculator
        if result['月令主气'] and self.day_gan:
            try:
                from geju_database import GeJuCalculator
                calculator = GeJuCalculator()
                
                # 准备八字字典 - 支持无时柱的情况
                bazi_dict = {
                    'year_gan': self.gans[0],
                    'year_zhi': self.zhis[0],
                    'month_gan': self.gans[1],
                    'month_zhi': self.zhis[1],
                    'day_gan': self.day_gan,
                    'day_zhi': self.zhis[2],
                    'time_gan': self.gans[3] if self.has_time_pillar else '',
                    'time_zhi': self.zhis[3] if self.has_time_pillar else ''
                }
                
                # 调用 GeJuCalculator 计算格局
                geju_result = calculator.calculate(bazi_dict)
                main_geju_name = geju_result.get('主要格局', '未知格局')
                result['主要格局'] = main_geju_name
                result['格局列表'] = geju_result.get('格局列表', [])
                
                # 获取身强身弱信息
                shenqiang = geju_result.get('身强身弱', {})
                result['身强身弱'] = shenqiang.get('强弱判定', '')
                result['身强详情'] = {
                    '得令': shenqiang.get('得令', False),
                    '得地': shenqiang.get('得地', False),
                    '得势': shenqiang.get('得势', False),
                    '得令详情': shenqiang.get('得令详情', ''),
                    '得地详情': shenqiang.get('得地详情', ''),
                    '得势详情': shenqiang.get('得势详情', ''),
                    '详细说明': shenqiang.get('详细说明', [])
                }
                
                # 获取格局说明
                deity = ten_deities.get(self.day_gan, {}).get(result['月令主气'], '')
                result['格局说明'] = f"月令{self.month_zhi}主气为{result['月令主气']},对应{deity}神"
                
                # 如果格局数据库可用，获取详细的格局信息
                if self.geju_db:
                    # 格局名称映射（解决名称不一致问题）
                    geju_name_mapping = {
                        '七杀格': '七杀格（偏官格）',
                        '偏官格': '七杀格（偏官格）',
                        '正印格': '正印格（印绶格）',
                        '印绶格': '正印格（印绶格）',
                        '偏印格': '偏印格（枭神格）',
                        '枭神格': '偏印格（枭神格）',
                        '从儿格': '从儿格（食伤生财格）',
                    }
                    # 尝试直接获取，如果失败则尝试映射后的名称
                    geju_info = self.geju_db.get_geju_info(main_geju_name)
                    if not geju_info and main_geju_name in geju_name_mapping:
                        mapped_name = geju_name_mapping[main_geju_name]
                        geju_info = self.geju_db.get_geju_info(mapped_name)
                    if geju_info:
                        result['格局类别'] = geju_info.category
                        result['格局定义'] = geju_info.definition
                        result['格局喜忌'] = geju_info.preference
                        result['格局条件'] = geju_info.condition
                        result['格局古籍'] = geju_info.source
                        
            except Exception as e:
                # 如果调用失败，使用备用逻辑
                result['主要格局'] = '未知格局'
                result['格局说明'] = f"格局判定异常: {str(e)}"

        # 检查次要格局（已删除相关判定逻辑）
        result['次要格局'] = []

        # ==================== 五行旺相判断（旺相休囚死） ====================
        # 根据月令判断五行状态
        # 新逻辑：
        # 春季（寅卯）：木旺、火相、水休、金囚、土死
        # 夏季（巳午）：火旺、土相、木休、水囚、金死
        # 秋季（申酉）：金旺、水相、土休、火囚、木死
        # 冬季（亥子）：水旺、木相、金休、土囚、火死
        # 四季末（辰戌丑未）：土旺、金相、火休、木囚、水死
        month_zhi = self.month_zhi

        # 判断五行状态
        wuxing_status = {}

        # 春季（寅卯月）
        if month_zhi in ['寅', '卯']:
            # 木旺、火相、水休、金囚、土死
            wuxing_status['木'] = '旺'
            wuxing_status['火'] = '相'
            wuxing_status['水'] = '休'
            wuxing_status['金'] = '囚'
            wuxing_status['土'] = '死'

        # 夏季（巳午月）
        elif month_zhi in ['巳', '午']:
            # 火旺、土相、木休、水囚、金死
            wuxing_status['火'] = '旺'
            wuxing_status['土'] = '相'
            wuxing_status['木'] = '休'
            wuxing_status['水'] = '囚'
            wuxing_status['金'] = '死'

        # 秋季（申酉月）
        elif month_zhi in ['申', '酉']:
            # 金旺、水相、土休、火囚、木死
            wuxing_status['金'] = '旺'
            wuxing_status['水'] = '相'
            wuxing_status['土'] = '休'
            wuxing_status['火'] = '囚'
            wuxing_status['木'] = '死'

        # 冬季（亥子月）
        elif month_zhi in ['亥', '子']:
            # 水旺、木相、金休、土囚、火死
            wuxing_status['水'] = '旺'
            wuxing_status['木'] = '相'
            wuxing_status['金'] = '休'
            wuxing_status['土'] = '囚'
            wuxing_status['火'] = '死'

        # 四季末（辰戌丑未月）
        elif month_zhi in ['辰', '戌', '丑', '未']:
            # 土旺、金相、火休、木囚、水死
            wuxing_status['土'] = '旺'
            wuxing_status['金'] = '相'
            wuxing_status['火'] = '休'
            wuxing_status['木'] = '囚'
            wuxing_status['水'] = '死'
        else:
            # 默认情况,设置五行状态为空
            wuxing_status['木'] = ''
            wuxing_status['火'] = ''
            wuxing_status['土'] = ''
            wuxing_status['金'] = ''
            wuxing_status['水'] = ''

        # 构建输出字符串
        status_str = ', '.join([f"{wx}{status}" for wx, status in wuxing_status.items() if status])
        result['五行旺相'] = status_str

        return result


    def _analyze_zhi_relations(self) -> Dict:
        """第二论级: 分析地支关系"""
        result = {
            '三会': [],
            '拱会': [],
            '三合': [],
            '半合': [],
            '拱合': [],
            '六合': [],
            '六破': [],
            '六害': [],
            '三刑': [],
            '六冲': [],
            '自刑': [],
            '地支暗合': []
        }

        # 季节划分
        spring_zhis = ['寅', '卯', '辰']  # 春季地支
        summer_zhis = ['巳', '午', '未']  # 夏季地支
        autumn_zhis = ['申', '酉', '戌']  # 秋季地支
        winter_zhis = ['亥', '子', '丑']  # 冬季地支

        # ==================== 1. 检查三会局 ====================
        # 条件：三支齐全且同属一方季节
        sanhui_sets = {
            '寅卯辰': ('寅', '卯', '辰', '寅卯辰三会木局'),
            '巳午未': ('巳', '午', '未', '巳午未三会火局'),
            '申酉戌': ('申', '酉', '戌', '申酉戌三会金局'),
            '亥子丑': ('亥', '子', '丑', '亥子丑三会水局')
        }
        # 记录已形成的三会局，用于跳过半会、拱会
        formed_sanhui = set()
        for key, (z1, z2, z3, name) in sanhui_sets.items():
            if z1 in self.zhis and z2 in self.zhis and z3 in self.zhis:
                # 地支凑齐即构成三会局
                result['三会'].append(name)
                formed_sanhui.add(key)  # 记录已形成的三会局

        # ==================== 2. 检查拱会 ====================
        # 条件：三会局的地支隔一相拱
        # 寅辰供会卯木、巳未拱会午火、申戌拱会酉金、亥丑拱会子水
        # 如果已形成完整三会局，则不再分析对应的拱会
        gonghui = [
            ('寅', '辰', '卯', '木', '寅卯辰'), ('巳', '未', '午', '火', '巳午未'),
            ('申', '戌', '酉', '金', '申酉戌'), ('亥', '丑', '子', '水', '亥子丑')
        ]
        for z1, z2, gong_zhi, wuxing, sanhui_key in gonghui:
            # 跳过已形成完整三会局的拱会
            if sanhui_key in formed_sanhui:
                continue
            if z1 in self.zhis and z2 in self.zhis:
                result['拱会'].append(f"{z1}{z2}拱会{gong_zhi}{wuxing}")

        # ==================== 4. 检查三合局 ====================
        # 条件：生、旺、墓三支齐全；或两支有中神
        # 申子辰（水局）：申=长生，子=帝旺，辰=墓库
        # 亥卯未（木局）：亥=长生，卯=帝旺，未=墓库
        # 寅午戌（火局）：寅=长生，午=帝旺，戌=墓库
        # 巳酉丑（金局）：巳=长生，酉=帝旺，丑=墓库
        sanhe_sets = {
            '申子辰': ('申', '子', '辰', '水局'),
            '亥卯未': ('亥', '卯', '未', '木局'),
            '寅午戌': ('寅', '午', '戌', '火局'),
            '巳酉丑': ('巳', '酉', '丑', '金局')
        }

        # 检查完整三合局，记录已形成的三合局
        formed_sanhe = set()
        for key, (z1, z2, z3, name) in sanhe_sets.items():
            if z1 in self.zhis and z2 in self.zhis and z3 in self.zhis:
                # 地支凑齐即构成三合局，不需要考虑月令
                result['三合'].append(f"{key}合{name}")
                formed_sanhe.add(key)

        # ==================== 5. 检查半合 ====================
        # 条件：三合局中凑齐其中两个（有中神更佳）
        # 亥卯半合木、卯未半合木、寅午半合火、午戌半合火
        # 已酉半合金、酉丑半合金、申子半合水、子辰半合水
        # 如果已形成完整三合局，则不再分析对应的半合
        half_sanhe = [
            ('亥', '卯', '木', '亥卯未'), ('卯', '未', '木', '亥卯未'),
            ('寅', '午', '火', '寅午戌'), ('午', '戌', '火', '寅午戌'),
            ('巳', '酉', '金', '巳酉丑'), ('酉', '丑', '金', '巳酉丑'),
            ('申', '子', '水', '申子辰'), ('子', '辰', '水', '申子辰')
        ]
        for z1, z2, wuxing, sanhe_key in half_sanhe:
            # 跳过已形成完整三合局的半合
            if sanhe_key in formed_sanhe:
                continue
            if z1 in self.zhis and z2 in self.zhis:
                result['半合'].append(f"{z1}{z2}半合{wuxing}")

        # ==================== 6. 检查拱合 ====================
        # 条件：三合局的地支隔一相拱
        # 亥未拱合卯木、寅戌拱合午火、巳丑拱合酉金、申辰拱合子水
        # 如果已形成完整三合局，则不再分析对应的拱合
        gonghe = [
            ('亥', '未', '卯', '木', '亥卯未'), ('寅', '戌', '午', '火', '寅午戌'),
            ('巳', '丑', '酉', '金', '巳酉丑'), ('申', '辰', '子', '水', '申子辰')
        ]
        for z1, z2, gong_zhi, wuxing, sanhe_key in gonghe:
            # 跳过已形成完整三合局的拱合
            if sanhe_key in formed_sanhe:
                continue
            if z1 in self.zhis and z2 in self.zhis:
                result['拱合'].append(f"{z1}{z2}拱合{gong_zhi}{wuxing}")

        # ==================== 7. 检查六合 ====================
        # 条件：两支相邻；天干透化神；无强克干扰
        liuhe_data = {
            ('子', '丑'): ('子丑', '土'),
            ('丑', '子'): ('丑子', '土'),
            ('寅', '亥'): ('寅亥', '木'),
            ('亥', '寅'): ('亥寅', '木'),
            ('卯', '戌'): ('卯戌', '火'),
            ('戌', '卯'): ('戌卯', '火'),
            ('辰', '酉'): ('辰酉', '金'),
            ('酉', '辰'): ('酉辰', '金'),
            ('巳', '申'): ('巳申', '水'),
            ('申', '巳'): ('申巳', '水'),
            ('午', '未'): ('午未', '土'),
            ('未', '午'): ('未午', '土')
        }

        for zhi_pair, (he_name, wuxing) in liuhe_data.items():
            if zhi_pair[0] in self.zhis and zhi_pair[1] in self.zhis:
                # 检查天干是否透化神（与六合五行相同的天干）
                wuxing_gans = []
                if wuxing == '木':
                    wuxing_gans = ['甲', '乙']
                elif wuxing == '火':
                    wuxing_gans = ['丙', '丁']
                elif wuxing == '土':
                    wuxing_gans = ['戊', '己']
                elif wuxing == '金':
                    wuxing_gans = ['庚', '辛']
                elif wuxing == '水':
                    wuxing_gans = ['壬', '癸']

                has_hua_shen = any(gan in self.gans for gan in wuxing_gans)

                # 检查无强克干扰
                # 六冲对：子-午, 丑-未, 寅-申, 卯-酉, 辰-戌, 巳-亥
                # 如果六合的地支与第三个地支相冲，则六合减弱
                chong_map = {'子': '午', '午': '子', '丑': '未', '未': '丑',
                           '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
                           '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}

                zhi1, zhi2 = zhi_pair
                third_zhi = None
                for z in self.zhis:
                    if z != zhi1 and z != zhi2:
                        third_zhi = z
                        break

                has_chong = third_zhi is not None and chong_map.get(zhi1) == third_zhi

                if has_hua_shen and not has_chong:
                    result['六合'].append(f"{zhi1}{zhi2}合({wuxing})")
                elif has_hua_shen:
                    result['六合'].append(f"{zhi1}{zhi2}合({wuxing})受冲影响")
                elif not has_chong:
                    result['六合'].append(f"{zhi1}{zhi2}合({wuxing})弱")

        # ==================== 8. 检查六破 ====================
        # 条件：两支相破（标准顺序：子酉、寅亥、卯午、辰丑、巳申、未戌）
        liupo_pairs = [('子', '酉'), ('寅', '亥'), ('卯', '午'), ('辰', '丑'), ('巳', '申'), ('未', '戌')]
        for zhi_pair in liupo_pairs:
            if zhi_pair[0] in self.zhis and zhi_pair[1] in self.zhis:
                result['六破'].append(f"{zhi_pair[0]}{zhi_pair[1]}破")

        # ==================== 9. 检查三刑 ====================
        # 地支顺序：子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥
        zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

        # 无恩之刑：寅、巳、申三支全见
        # 不需要相邻，只要三者都在原局中即可
        if '寅' in self.zhis and '巳' in self.zhis and '申' in self.zhis:
            result['三刑'].append('寅巳申刑')

        # 无恩之刑的两两组合：寅巳刑、巳申刑、申寅刑
        # 不需要相邻，只要两个地支都在原局中即可
        if '寅' in self.zhis and '巳' in self.zhis:
            result['三刑'].append('寅巳刑')
        if '巳' in self.zhis and '申' in self.zhis:
            result['三刑'].append('巳申刑')
        if '申' in self.zhis and '寅' in self.zhis:
            result['三刑'].append('申寅刑')

        # 恃势之刑：丑、戌、未三支全见
        # 不需要相邻，只要三者都在原局中即可
        if '丑' in self.zhis and '戌' in self.zhis and '未' in self.zhis:
            result['三刑'].append('丑戌未刑')

        # 恃势之刑的两两组合：丑戌刑、戌未刑、未丑刑
        # 不需要相邻，只要两个地支都在原局中即可
        if '丑' in self.zhis and '戌' in self.zhis:
            result['三刑'].append('丑戌刑')
        if '戌' in self.zhis and '未' in self.zhis:
            result['三刑'].append('戌未刑')
        if '未' in self.zhis and '丑' in self.zhis:
            result['三刑'].append('未丑刑')

        # 无礼之刑：子、卯两支
        # 不需要相邻，只要两个地支都在原局中即可
        if '子' in self.zhis and '卯' in self.zhis:
            result['三刑'].append('子卯刑')

        # 自刑：自身重复且相邻（辰辰、午午、酉酉、亥亥）
        zhi_self_punish = ['辰', '午', '酉', '亥']
        for z in zhi_self_punish:
            if z in self.zhis:
                # 检查该地支是否重复且相邻
                for i in range(len(self.zhis) - 1):
                    if self.zhis[i] == z and self.zhis[i + 1] == z:
                        result['自刑'].append(f"{z}{z}自刑")
                        break  # 避免重复添加

        # ==================== 10. 检查六冲 ====================
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        for zhi_pair in chong_pairs:
            if zhi_pair[0] in self.zhis and zhi_pair[1] in self.zhis:
                result['六冲'].append(f"{zhi_pair[0]}{zhi_pair[1]}冲")

        # ==================== 11. 检查六害 ====================
        hai_pairs = [('子', '未'), ('丑', '午'), ('寅', '巳'), ('卯', '辰'), ('申', '亥'), ('酉', '戌')]
        for zhi_pair in hai_pairs:
            if zhi_pair[0] in self.zhis and zhi_pair[1] in self.zhis:
                result['六害'].append(f"{zhi_pair[0]}{zhi_pair[1]}害")

        # ==================== 12. 检查地支暗合 ====================
        # 条件：原局中出现对应地支即可成立，不需要相邻
        # 寅丑暗合：寅中甲木与丑中己土相合（甲己合）
        # 亥午暗合：亥中壬水与午中丁火相合（壬丁合）
        # 卯申暗合：卯中乙木与申中庚金相合（乙庚合）
        # 巳酉暗合：巳中丙火与酉中辛金相合（丙辛合）
        # 子戌暗合：子中癸水与戌中戊土相合（戊癸合）
        # 子巳暗合：子中癸水与巳中戊土相合（戊癸合）
        # 寅午暗合：寅中甲木与午中己土相合（甲己合）

        # 寅丑暗合：原局中出现地支寅、丑即可成立
        if '寅' in self.zhis and '丑' in self.zhis:
            result['地支暗合'].append('寅丑暗合(甲己合)')

        # 亥午暗合：原局中出现地支亥、午即可成立
        if '亥' in self.zhis and '午' in self.zhis:
            result['地支暗合'].append('亥午暗合(壬丁合)')

        # 卯申暗合：原局中出现地支卯、申即可成立
        if '卯' in self.zhis and '申' in self.zhis:
            result['地支暗合'].append('卯申暗合(乙庚合)')

        # 巳酉暗合：原局中出现地支巳、酉即可成立
        if '巳' in self.zhis and '酉' in self.zhis:
            result['地支暗合'].append('巳酉暗合(丙辛合)')

        # 子戌暗合：原局中出现地支子、戌即可成立
        if '子' in self.zhis and '戌' in self.zhis:
            result['地支暗合'].append('子戌暗合(戊癸合)')

        # 子巳暗合：原局中出现地支子、巳即可成立
        if '子' in self.zhis and '巳' in self.zhis:
            result['地支暗合'].append('子巳暗合(戊癸合)')

        # 寅午暗合：原局中出现地支寅、午即可成立
        if '寅' in self.zhis and '午' in self.zhis:
            result['地支暗合'].append('寅午暗合(甲己合)')

        return result
    
    def _analyze_gan_relations(self) -> Dict:
        """第三论级: 分析天干关系"""
        result = {
            '天干五合': [],
            '化气判定': '',
            '天干相冲': [],
            '天干相克': []
        }

        # 检查天干五合
        for gan_pair in gan_hes:
            if gan_pair[0] in self.gans and gan_pair[1] in self.gans:
                result['天干五合'].append(f"{gan_pair[0]}{gan_pair[1]}合")

        # 简单化气判定
        for he, hua_info in self.GAN_HE_HUA.items():
            if he[0] in self.gans and he[1] in self.gans:
                if self.month_zhi in hua_info['条件']['月令']:
                    result['化气判定'] = f"{he[0]}{he[1]}化{hua_info['化']}"
                    break

        # 检查天干相冲（单向）
        # 只存在：甲庚冲、乙辛冲、壬丙冲、癸丁冲
        gan_chong_pairs = [
            ('甲', '庚'),  # 甲庚相冲
            ('乙', '辛'),  # 乙辛相冲
            ('壬', '丙'),  # 壬丙相冲
            ('癸', '丁')   # 癸丁相冲
        ]
        for gan_pair in gan_chong_pairs:
            if gan_pair[0] in self.gans and gan_pair[1] in self.gans:
                result['天干相冲'].append(f"{gan_pair[0]}{gan_pair[1]}冲")

        # 检查天干相克（同性相斥，异性相吸）
        # 天干阴阳属性：阳干（甲丙戊庚壬），阴干（乙丁己辛癸）
        yang_gan = ['甲', '丙', '戊', '庚', '壬']
        yin_gan = ['乙', '丁', '己', '辛', '癸']

        # 木克土：阳木（甲）克阳土（戊），阴木（乙）克阴土（己）
        if '甲' in self.gans and '戊' in self.gans:
            result['天干相克'].append("甲戊相克")
        if '乙' in self.gans and '己' in self.gans:
            result['天干相克'].append("乙己相克")

        # 火克金：阳火（丙）克阳金（庚），阴火（丁）克阴金（辛）
        if '丙' in self.gans and '庚' in self.gans:
            result['天干相克'].append("丙庚相克")
        if '丁' in self.gans and '辛' in self.gans:
            result['天干相克'].append("丁辛相克")

        # 土克水：阳土（戊）克阳水（壬），阴土（己）克阴水（癸）
        if '戊' in self.gans and '壬' in self.gans:
            result['天干相克'].append("戊壬相克")
        if '己' in self.gans and '癸' in self.gans:
            result['天干相克'].append("己癸相克")

        # 金克木：阳金（庚）克阳木（甲），阴金（辛）克阴木（乙）
        if '庚' in self.gans and '甲' in self.gans:
            result['天干相克'].append("庚甲相克")
        if '辛' in self.gans and '乙' in self.gans:
            result['天干相克'].append("辛乙相克")

        # 水克火：阳水（壬）克阳火（丙），阴水（癸）克阴火（丁）
        if '壬' in self.gans and '丙' in self.gans:
            result['天干相克'].append("壬丙相克")
        if '癸' in self.gans and '丁' in self.gans:
            result['天干相克'].append("癸丁相克")

        return result

    
    def _analyze_gan_zhi_relations(self) -> Dict:
        """
        第四论级: 分析天干与地支的关系

        包括：
        1. 伏吟 - 干支重复
        2. 反吟 - 干支冲克
        3. 盖头 - 天干克地支
        4. 截脚 - 地支克天干
        """
        result = {
            '伏吟': [],      # 原局内部伏吟
            '反吟': [],      # 原局内部反吟
            '盖头': [],      # 天干克地支
            '截脚': []       # 地支克天干
        }

        # 构建干支柱列表 - 支持三柱或四柱
        pillars = ['年柱', '月柱', '日柱', '时柱']
        pillar_ganzhis = []

        # 构建干支柱（只包含非空的柱）
        for i in range(len(self.gans)):
            pillar_name = pillars[i] if i < len(pillars) else f'柱{i}'
            gan = self.gans[i] if i < len(self.gans) else ''
            zhi = self.zhis[i] if i < len(self.zhis) else ''
            if gan and zhi:  # 只添加有效的干支
                pillar_ganzhis.append((pillar_name, gan, zhi))

        # ==================== 1. 检查伏吟（原局内部） ====================
        # 条件：两柱或多柱的干支完全相同
        fuyin_pairs = []
        for i in range(len(pillar_ganzhis)):
            for j in range(i + 1, len(pillar_ganzhis)):
                if pillar_ganzhis[i][1] == pillar_ganzhis[j][1] and \
                   pillar_ganzhis[i][2] == pillar_ganzhis[j][2]:
                    # 两柱干支相同
                    fuyin_pairs.append(
                        f"{pillar_ganzhis[i][0]}({pillar_ganzhis[i][1]}{pillar_ganzhis[i][2]})与"
                        f"{pillar_ganzhis[j][0]}({pillar_ganzhis[j][1]}{pillar_ganzhis[j][2]})"
                    )
        result['伏吟'] = fuyin_pairs

        # ==================== 2. 检查反吟（原局内部） ====================
        # 条件：两柱地支相冲（天干可相克或不相克）
        # 天克地冲：天干相克且地支相冲（强烈反吟）
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        fanyin_pairs = []
        tian_ke_di_chong_pairs = []

        # 获取天干五行
        from ganzhi import gan5

        for i in range(len(pillar_ganzhis)):
            for j in range(i + 1, len(pillar_ganzhis)):
                gan1, zhi1 = pillar_ganzhis[i][1], pillar_ganzhis[i][2]
                gan2, zhi2 = pillar_ganzhis[j][1], pillar_ganzhis[j][2]

                # 检查地支是否相冲
                is_zhi_chong = False
                for chong_pair in chong_pairs:
                    if (zhi1 == chong_pair[0] and zhi2 == chong_pair[1]) or \
                       (zhi1 == chong_pair[1] and zhi2 == chong_pair[0]):
                        is_zhi_chong = True
                        break

                if is_zhi_chong:
                    # 地支相冲，检查天干是否相克
                    wuxing1 = gan5.get(gan1, '')
                    wuxing2 = gan5.get(gan2, '')

                    # 五行相克表
                    ke_map = {
                        '木': '土', '火': '金', '土': '水', '金': '木', '水': '火'
                    }

                    is_gan_ke = wuxing1 and wuxing2 and ke_map.get(wuxing1) == wuxing2

                    if is_gan_ke:
                        # 天克地冲（强烈反吟）
                        tian_ke_di_chong_pairs.append(
                            f"{pillar_ganzhis[i][0]}({gan1}{zhi1})与"
                            f"{pillar_ganzhis[j][0]}({gan2}{zhi2})天克地冲"
                        )
                    # 不再输出地支相冲的反吟

        # 只输出天克地冲
        result['反吟'] = tian_ke_di_chong_pairs

        # ==================== 3. 检查盖头和截脚 ====================
        # 条件：同柱干支五行相克
        # 固定组合判断

        # 盖头组合（天干克地支）：甲辰、甲戌、乙丑、乙未、丙申、丁酉、
        # 戊子、己亥、庚寅、辛卯、壬午、癸巳（共12组）
        gaitou_combinations = [
            ('甲', '辰'), ('甲', '戌'), ('乙', '丑'), ('乙', '未'),
            ('丙', '申'), ('丁', '酉'), ('戊', '子'), ('己', '亥'),
            ('庚', '寅'), ('辛', '卯'), ('壬', '午'), ('癸', '巳')
        ]

        # 截脚组合（地支克天干）：甲申、乙酉、丙子、丁亥、戊寅、己卯、
        # 庚午、辛巳、壬辰、癸丑、癸未、壬戌（共12组）
        jiejiao_combinations = [
            ('甲', '申'), ('乙', '酉'), ('丙', '子'), ('丁', '亥'),
            ('戊', '寅'), ('己', '卯'), ('庚', '午'), ('辛', '巳'),
            ('壬', '辰'), ('癸', '丑'), ('癸', '未'), ('壬', '戌')
        ]

        for i, (pillar_name, gan, zhi) in enumerate(pillar_ganzhis):
            # 检查盖头
            if (gan, zhi) in gaitou_combinations:
                result['盖头'].append(f"{pillar_name}({gan}{zhi})盖头")
            # 检查截脚
            if (gan, zhi) in jiejiao_combinations:
                result['截脚'].append(f"{pillar_name}({gan}{zhi})截脚")

        return result
    
    def _check_xiao_duo_shi(self) -> bool:
        """检查枭印夺食"""
        has_xiao = '枭' in [ten_deities[self.day_gan].get(gan, '') for gan in self.gans if gan]
        has_shi = '食' in [ten_deities[self.day_gan].get(gan, '') for gan in self.gans if gan]
        return has_xiao and has_shi
    
    def _check_shang_guan(self) -> bool:
        """检查伤官见官"""
        has_shang = '伤' in [ten_deities[self.day_gan].get(gan, '') for gan in self.gans if gan]
        has_guan = '官' in [ten_deities[self.day_gan].get(gan, '') for gan in self.gans if gan]
        return has_shang and has_guan
    
    def _check_guan_sha_hun(self) -> bool:
        """检查官杀混杂"""
        has_guan = '官' in [ten_deities[self.day_gan].get(gan, '') for gan in self.gans if gan]
        has_sha = '杀' in [ten_deities[self.day_gan].get(gan, '') for gan in self.gans if gan]
        return has_guan and has_sha
    
    def _calculate_wuxing_shishen_scores(self, include_dayun_liunian=False) -> Dict:
        """
        计算五行和十神能量评分 - 使用更新后的评分标准（2026-03-19更新）
        
        更新后的评分规则：
        1. 基础分：天干+1，地支藏干本气+0.6/中气+0.3/余气+0.1
        2. 地支关系：三会+3/半会+1.5/拱会+1/三合+1/半合+0.5/拱合+1/六合+1
        3. 天干关系：五合+2/相克-1
        4. 干支关系：盖头（五行-0.5，主气十神-0.3）/截脚（五行-0.5，十神-0.5）
        5. 通根：根据位置不同加分（月令本气+0.6/中气+0.3/余气+0.1，日支本气+0.42等，通根透额外+0.5）
        6. 透干：不参与计算
        7. 月令/大运地支：本气+1.8，中气+0.9，余气+0.3
        8. 日主不参与比肩计算、不参与通根透干计算
        
        数据来源：
        - 原局：基于第二、三、四论级的分析结果
        - 大运流年：基于第六论级的分析结果
        """
        from ganzhi import gan5, zhi5_list, ten_deities

        day_gan = self.day_gan
        month_zhi = self.month_zhi

        # 初始化五行和十神得分
        wuxing_scores = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        shishen_scores = {'比': 0, '劫': 0, '食': 0, '伤': 0, '财': 0, '才': 0, '官': 0, '杀': 0, '印': 0, '枭': 0}
        wuxing_details = {'木': [], '火': [], '土': [], '金': [], '水': []}
        shishen_details = {'比': [], '劫': [], '食': [], '伤': [], '财': [], '才': [], '官': [], '杀': [], '印': [], '枭': []}

        # 如果包含大运流年，需要获取大运流年信息
        # 注意：日主（日干，index=2）不参与通根、透干计算
        all_gans = self.gans.copy()  # 包含年干、月干、日干、时干
        all_zhis = self.zhis.copy()  # 包含年支、月支、日支、时支
        dayun_zhi = None
        liunian_zhi = None
        dayun_gan = None
        liunian_gan = None
        
        if include_dayun_liunian and self.dayun_liunian and hasattr(self.dayun_liunian, 'current_dayun_gan'):
            dayun_gan = self.dayun_liunian.current_dayun_gan
            liunian_gan = self.dayun_liunian.current_liunian_gan
            if dayun_gan:
                all_gans.append(dayun_gan)
            if liunian_gan:
                all_gans.append(liunian_gan)
            # 添加大运和流年地支到列表
            if hasattr(self.dayun_liunian, 'current_dayun_zhi') and self.dayun_liunian.current_dayun_zhi:
                dayun_zhi = self.dayun_liunian.current_dayun_zhi
                all_zhis.append(dayun_zhi)
            if hasattr(self.dayun_liunian, 'current_liunian_zhi') and self.dayun_liunian.current_liunian_zhi:
                liunian_zhi = self.dayun_liunian.current_liunian_zhi
                all_zhis.append(liunian_zhi)

        # ==================== 基础评分 ====================
        base_score = self.SCORE_BASE

        # 1. 天干基础评分（每个天干+1）
        # 原局天干 - 支持三柱或四柱
        gan_names = ['年干', '月干', '日干', '时干']
        for i, gan in enumerate(self.gans):
            if not gan:  # 跳过空天干
                continue
            gan_name = gan_names[i] if i < len(gan_names) else f'干{i}'
            wuxing = gan5.get(gan, '')
            if wuxing:
                wuxing_scores[wuxing] += base_score['天干']['wuxing']
                wuxing_details[wuxing].append(f'{gan_name}{gan}: +{base_score["天干"]["wuxing"]}')

            shishen = ten_deities.get(day_gan, {}).get(gan, '')
            # 规则1：日主不参与比肩的计算（日干不计算比肩/劫财）
            if shishen and not (i == 2 and shishen in ['比', '劫']):
                shishen_scores[shishen] += base_score['天干']['shishen']
                shishen_details[shishen].append(f'{gan_name}{gan}为{shishen}: +{base_score["天干"]["shishen"]}')
        
        # 大运天干（作为月干2）和流年天干（作为年干2）
        if include_dayun_liunian and self.dayun_liunian:
            # 大运天干 - 作为月干2，五行+1，十神+1
            if dayun_gan:
                wuxing = gan5.get(dayun_gan, '')
                shishen = ten_deities.get(day_gan, {}).get(dayun_gan, '')
                if wuxing:
                    wuxing_scores[wuxing] += base_score['天干']['wuxing']
                    wuxing_details[wuxing].append(f'大运天干{dayun_gan}五行{wuxing}+1')
                if shishen:
                    shishen_scores[shishen] += base_score['天干']['shishen']
                    shishen_details[shishen].append(f'大运天干{dayun_gan}十神{shishen}+1')
            
            # 流年天干 - 作为年干2，五行+1，十神+1
            if liunian_gan:
                wuxing = gan5.get(liunian_gan, '')
                shishen = ten_deities.get(day_gan, {}).get(liunian_gan, '')
                if wuxing:
                    wuxing_scores[wuxing] += base_score['天干']['wuxing']
                    wuxing_details[wuxing].append(f'流年天干{liunian_gan}五行{wuxing}+1')
                if shishen:
                    shishen_scores[shishen] += base_score['天干']['shishen']
                    shishen_details[shishen].append(f'流年天干{liunian_gan}十神{shishen}+1')

        # 2. 地支藏干评分（原局地支）
        zhi_names = ['年支', '月支', '日支', '时支']
        for i, zhi in enumerate(self.zhis):
            if not zhi:  # 跳过空地支
                continue
            zhi_name = zhi_names[i] if i < len(zhi_names) else f'支{i}'
            canggan_list = zhi5_list.get(zhi, [])
            if canggan_list:
                for j, canggan in enumerate(canggan_list):
                    if j == 0:  # 本气
                        score_wx = base_score['藏干本气']['wuxing']
                        score_ss = base_score['藏干本气']['shishen']
                        qi_type = '本气'
                    elif j == 1:  # 中气
                        score_wx = base_score['藏干中气']['wuxing']
                        score_ss = base_score['藏干中气']['shishen']
                        qi_type = '中气'
                    else:  # 余气
                        score_wx = base_score['藏干余气']['wuxing']
                        score_ss = base_score['藏干余气']['shishen']
                        qi_type = '余气'

                    wuxing = gan5.get(canggan, '')
                    if wuxing:
                        wuxing_scores[wuxing] += score_wx
                        wuxing_details[wuxing].append(f'{zhi_name}{zhi}藏干{canggan}({qi_type}): +{score_wx}')

                    shishen = ten_deities.get(day_gan, {}).get(canggan, '')
                    if shishen:
                        shishen_scores[shishen] += score_ss
                        shishen_details[shishen].append(f'{zhi_name}{zhi}藏干{canggan}({qi_type})为{shishen}: +{score_ss}')
        
        # 处理大运地支（月令2）和流年地支（年支2）
        if include_dayun_liunian and self.dayun_liunian:
            # 大运地支 - 作为月令2，本气+1.8，中气+0.9，余气+0.3
            if dayun_zhi:
                canggan_list = zhi5_list.get(dayun_zhi, [])
                for j, canggan in enumerate(canggan_list):
                    qi_type = '本气' if j == 0 else ('中气' if j == 1 else '余气')
                    dayun_score = self.SCORE_DAYUN
                    if j == 0:  # 本气
                        score_wx = dayun_score['大运藏干_本气']['wuxing']
                        score_ss = dayun_score['大运藏干_本气']['shishen']
                    elif j == 1:  # 中气
                        score_wx = dayun_score['大运藏干_中气']['wuxing']
                        score_ss = dayun_score['大运藏干_中气']['shishen']
                    else:  # 余气
                        score_wx = dayun_score['大运藏干_余气']['wuxing']
                        score_ss = dayun_score['大运藏干_余气']['shishen']
                    
                    wuxing = gan5.get(canggan, '')
                    shishen = ten_deities.get(day_gan, {}).get(canggan, '')
                    if wuxing:
                        wuxing_scores[wuxing] += score_wx
                        wuxing_details[wuxing].append(f'大运地支{dayun_zhi}藏干{canggan}({qi_type})五行{wuxing}+{score_wx}')
                    if shishen:
                        shishen_scores[shishen] += score_ss
                        shishen_details[shishen].append(f'大运地支{dayun_zhi}藏干{canggan}({qi_type})十神{shishen}+{score_ss}')
            
            # 流年地支 - 作为年支2，基础分
            if liunian_zhi:
                canggan_list = zhi5_list.get(liunian_zhi, [])
                for j, canggan in enumerate(canggan_list):
                    if j == 0:  # 本气
                        score_wx = base_score['藏干本气']['wuxing']
                        score_ss = base_score['藏干本气']['shishen']
                        qi_type = '本气'
                    elif j == 1:  # 中气
                        score_wx = base_score['藏干中气']['wuxing']
                        score_ss = base_score['藏干中气']['shishen']
                        qi_type = '中气'
                    else:  # 余气
                        score_wx = base_score['藏干余气']['wuxing']
                        score_ss = base_score['藏干余气']['shishen']
                        qi_type = '余气'
                    
                    wuxing = gan5.get(canggan, '')
                    shishen = ten_deities.get(day_gan, {}).get(canggan, '')
                    if wuxing:
                        wuxing_scores[wuxing] += score_wx
                        wuxing_details[wuxing].append(f'流年地支{liunian_zhi}藏干{canggan}({qi_type})五行{wuxing}+{score_wx}')
                    if shishen:
                        shishen_scores[shishen] += score_ss
                        shishen_details[shishen].append(f'流年地支{liunian_zhi}藏干{canggan}({qi_type})十神{shishen}+{score_ss}')

        # ==================== 使用已有分析结果进行评分 ====================
        # 获取分析结果（原局用第二、三、四论级，大运流年用第六论级）
        if include_dayun_liunian:
            # 大运流年模式：使用第六论级的分析结果
            sixth_level = self.analysis_result.get('第六论级', {})
            zhi_analysis = sixth_level.get('岁运地支分析', {})
            gan_analysis = sixth_level.get('岁运天干分析', {})
            ganzhi_analysis = sixth_level.get('岁运干支分析', {})
            
            # 处理地支关系
            self._apply_zhi_relation_scores(
                zhi_analysis, wuxing_scores, wuxing_details, 
                shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, gan5,
                prefix='大运流年'
            )
            
            # 处理天干关系
            self._apply_gan_relation_scores(
                gan_analysis, wuxing_scores, wuxing_details,
                shishen_scores, shishen_details, day_gan, ten_deities, gan5,
                prefix='大运流年'
            )
            
            # 处理干支关系
            self._apply_ganzhi_relation_scores(
                ganzhi_analysis, wuxing_scores, wuxing_details,
                shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, gan5,
                prefix='大运流年'
            )
        else:
            # 原局模式：使用第二、三、四论级的分析结果
            second_level = self.analysis_result.get('第二论级_地支关系', {})
            third_level = self.analysis_result.get('第三论级_天干关系', {})
            fourth_level = self.analysis_result.get('第四论级_天干与地支的关系', {})
            
            # 处理地支关系
            self._apply_zhi_relation_scores_direct(
                second_level, wuxing_scores, wuxing_details,
                shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, gan5
            )
            
            # 处理天干关系
            self._apply_gan_relation_scores_direct(
                third_level, wuxing_scores, wuxing_details,
                shishen_scores, shishen_details, day_gan, ten_deities, gan5
            )
            
            # 处理干支关系
            self._apply_ganzhi_relation_scores_direct(
                fourth_level, wuxing_scores, wuxing_details,
                shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, gan5
            )

        # ==================== 通根计算（更新后规则）====================
        # 规则2：日主不参与通根的计算
        # 规则3：透干不参与能量计算
        tonggen_scores = self.SCORE_TONGGEN_TOUGAN
        
        # 非日主天干列表（排除日干，index=2）
        non_day_gans = [g for i, g in enumerate(self.gans) if g and i != 2]
        if include_dayun_liunian:
            if dayun_gan:
                non_day_gans.append(dayun_gan)
            if liunian_gan:
                non_day_gans.append(liunian_gan)
        
        # 通根计算：只看地支藏干，不看地支本气五行
        # 天干在地支藏干中有同五行，根据地支位置加分
        for gan in non_day_gans:  # 排除日主
            gan_wuxing = gan5.get(gan, '')
            if not gan_wuxing:
                continue

            # 检查各柱地支藏干（不包括地支本身的五行）
            zhi_names = ['年支', '月支', '日支', '时支']
            zhi_list = self.zhis.copy()
            
            if include_dayun_liunian:
                zhi_names.extend(['大运支', '流年支'])
                if dayun_zhi:
                    zhi_list.append(dayun_zhi)
                if liunian_zhi:
                    zhi_list.append(liunian_zhi)
            
            for i, zhi in enumerate(zhi_list):
                if not zhi:
                    continue
                zhi_name = zhi_names[i] if i < len(zhi_names) else f'支{i}'
                canggan_list = zhi5_list.get(zhi, [])
                
                # 检查地支藏干是否与天干同五行
                for j, canggan in enumerate(canggan_list):
                    canggan_wuxing = gan5.get(canggan, '')
                    if canggan_wuxing != gan_wuxing:
                        continue
                    
                    qi_type = '本气' if j == 0 else ('中气' if j == 1 else '余气')
                    
                    # 根据地支位置确定通根分数
                    if i == 1:  # 月令
                        score_key = f'通根_月令_{qi_type}'
                    elif i == 2:  # 日支
                        score_key = f'通根_日支_{qi_type}'
                    elif i == 3:  # 时支
                        score_key = f'通根_时支_{qi_type}'
                    elif i == 0:  # 年支
                        score_key = f'通根_年支_{qi_type}'
                    else:  # 大运/流年
                        score_key = f'通根_月令_{qi_type}'  # 大运作为月令2
                    
                    if score_key in tonggen_scores:
                        score_wx = tonggen_scores[score_key]['wuxing']
                        score_ss = tonggen_scores[score_key]['shishen']
                        
                        wuxing_scores[gan_wuxing] += score_wx
                        wuxing_details[gan_wuxing].append(f'{gan}通根{zhi_name}{zhi}藏干{canggan}({qi_type}): +{score_wx}')
                        
                        shishen = ten_deities.get(day_gan, {}).get(gan, '')
                        if shishen:
                            shishen_scores[shishen] += score_ss
                            shishen_details[shishen].append(f'{gan}通根{zhi_name}{zhi}藏干{canggan}({qi_type}): +{score_ss}')
                        
                        # 检查是否为通根透（干支一柱）
                        gan_pillar_idx = -1
                        for idx, g in enumerate(self.gans):
                            if g == gan:
                                gan_pillar_idx = idx
                                break
                        
                        if gan_pillar_idx == i and i < 4:  # 原局四柱内的通根透
                            extra_score_wx = tonggen_scores['通根透']['wuxing']
                            extra_score_ss = tonggen_scores['通根透']['shishen']
                            wuxing_scores[gan_wuxing] += extra_score_wx
                            wuxing_details[gan_wuxing].append(f'{gan}通根透（干支一柱）: +{extra_score_wx}')
                            if shishen:
                                shishen_scores[shishen] += extra_score_ss
                                shishen_details[shishen].append(f'{gan}通根透（干支一柱）: +{extra_score_ss}')

        # ==================== 月令加成（更新后规则）====================
        yueling_score = self.SCORE_YUELING
        
        # 月令的藏干本气+1.8，中气+0.9，余气+0.3
        month_canggan_list = zhi5_list.get(month_zhi, [])
        for i, canggan in enumerate(month_canggan_list):
            wuxing = gan5.get(canggan, '')
            shishen = ten_deities.get(day_gan, {}).get(canggan, '')
            qi_type = '本气' if i == 0 else ('中气' if i == 1 else '余气')
            
            if i == 0:  # 本气
                score_wx = yueling_score['月令藏干_本气']['wuxing']
                score_ss = yueling_score['月令藏干_本气']['shishen']
            elif i == 1:  # 中气
                score_wx = yueling_score['月令藏干_中气']['wuxing']
                score_ss = yueling_score['月令藏干_中气']['shishen']
            else:  # 余气
                score_wx = yueling_score['月令藏干_余气']['wuxing']
                score_ss = yueling_score['月令藏干_余气']['shishen']
            
            if wuxing:
                wuxing_scores[wuxing] += score_wx
                wuxing_details[wuxing].append(f'月令{month_zhi}藏干{canggan}({qi_type}){wuxing}: +{score_wx}')

            if shishen:
                shishen_scores[shishen] += score_ss
                shishen_details[shishen].append(f'月令{month_zhi}藏干{canggan}({qi_type})为{shishen}: +{score_ss}')

        # ==================== 计算综合得分 ====================

        return {
            '五行得分': wuxing_scores,
            '五行详情': wuxing_details,
            '十神得分': shishen_scores,
            '十神详情': shishen_details
        }

    def _apply_zhi_relation_scores_direct(self, second_level, wuxing_scores, wuxing_details, 
                                           shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, gan5):
        """应用地支关系评分 - 原局模式（直接使用第二论级结果）"""
        scores = self.SCORE_ZHI_RELATIONS
        
        # 三会局
        for item in second_level.get('三会', []):
            self._add_wuxing_score_by_text(item, wuxing_scores, wuxing_details, scores['三会']['wuxing'])
        
        # 半会
        for item in second_level.get('半会', []):
            self._add_wuxing_score_by_text(item, wuxing_scores, wuxing_details, scores['半会']['wuxing'])
        
        # 拱会（藏干主气十神+1）
        for item in second_level.get('拱会', []):
            self._add_wuxing_score_by_text(item, wuxing_scores, wuxing_details, scores['拱会']['wuxing'])
            self._add_gonghui_shishen(item, shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities)
        
        # 三合局
        for item in second_level.get('三合', []):
            self._add_wuxing_score_by_text(item, wuxing_scores, wuxing_details, scores['三合']['wuxing'])
        
        # 半合
        for item in second_level.get('半合', []):
            self._add_wuxing_score_by_text(item, wuxing_scores, wuxing_details, scores['半合']['wuxing'])
        
        # 拱合（藏干主气十神+1）
        for item in second_level.get('拱合', []):
            self._add_wuxing_score_by_text(item, wuxing_scores, wuxing_details, scores['拱合']['wuxing'])
            self._add_gonghe_shishen(item, shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities)
        
        # 六合
        for item in second_level.get('六合', []):
            self._add_wuxing_score_by_text(item, wuxing_scores, wuxing_details, scores['六合']['wuxing'])
    
    def _apply_gan_relation_scores_direct(self, third_level, wuxing_scores, wuxing_details,
                                           shishen_scores, shishen_details, day_gan, ten_deities, gan5):
        """应用天干关系评分 - 原局模式"""
        scores = self.SCORE_GAN_RELATIONS
        
        # 天干五合
        wuhe_map = {
            '甲己': '土', '己甲': '土',
            '乙庚': '金', '庚乙': '金',
            '丙辛': '水', '辛丙': '水',
            '丁壬': '木', '壬丁': '木',
            '戊癸': '火', '癸戊': '火'
        }
        for item in third_level.get('天干五合', []):
            for pair, wuxing in wuhe_map.items():
                if pair in item:
                    wuxing_scores[wuxing] += scores['天干五合']['wuxing']
                    wuxing_details[wuxing].append(f'{item}化{wuxing}: +{scores["天干五合"]["wuxing"]}')
                    break
        
        # 天干相克
        ke_map = {
            '甲戊': '戊', '己癸': '癸', '乙己': '己', '庚甲': '甲',
            '丙庚': '庚', '辛乙': '乙', '丁辛': '辛', '壬丙': '丙',
            '戊壬': '壬', '癸丁': '丁'
        }
        for item in third_level.get('天干相克', []):
            for pair, beike in ke_map.items():
                if pair in item:
                    wuxing = gan5.get(beike, '')
                    shishen = ten_deities.get(day_gan, {}).get(beike, '')
                    if wuxing:
                        wuxing_scores[wuxing] += scores['天干相克']['wuxing']
                        wuxing_details[wuxing].append(f'{item}({beike}被克): {scores["天干相克"]["wuxing"]}')
                    # 规则：日干不参与比肩计算（被克方是日干时，其十神不计算）
                    if shishen and beike != day_gan:
                        shishen_scores[shishen] += scores['天干相克']['shishen']
                        shishen_details[shishen].append(f'{item}({beike}为{shishen}被克): {scores["天干相克"]["shishen"]}')
                    break
    
    def _apply_ganzhi_relation_scores_direct(self, fourth_level, wuxing_scores, wuxing_details,
                                              shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, gan5):
        """应用干支关系评分 - 原局模式（使用更新后的盖头截脚评分）"""
        gaitou_jiejiao_score = self.SCORE_GAITOU_JIEJIAO
        
        # 盖头：五行能量-0.5，藏干主气的十神能量-0.3
        for item in fourth_level.get('盖头', []):
            zhi_char = self._extract_zhi_from_ganzhi_item(item)
            if zhi_char:
                wuxing = self.ZHI_WUHANGS.get(zhi_char, '')
                if wuxing:
                    score_wx = gaitou_jiejiao_score['盖头_五行']
                    wuxing_scores[wuxing] += score_wx
                    wuxing_details[wuxing].append(f'{item}: {zhi_char}{wuxing}{score_wx}')
                # 藏干主气十神-0.3
                canggan_list = zhi5_list.get(zhi_char, [])
                if canggan_list:
                    main_canggan = canggan_list[0]
                    shishen = ten_deities.get(day_gan, {}).get(main_canggan, '')
                    if shishen:
                        score_ss = gaitou_jiejiao_score['盖头_主气十神']
                        shishen_scores[shishen] += score_ss
                        shishen_details[shishen].append(f'{item}{zhi_char}藏干主气{main_canggan}为{shishen}: {score_ss}')
        
        # 截脚：五行能量-0.5，十神能量-0.5
        for item in fourth_level.get('截脚', []):
            gan_char = self._extract_gan_from_ganzhi_item(item)
            if gan_char:
                wuxing = gan5.get(gan_char, '')
                if wuxing:
                    score_wx = gaitou_jiejiao_score['截脚_五行']
                    wuxing_scores[wuxing] += score_wx
                    wuxing_details[wuxing].append(f'{item}: {gan_char}{wuxing}{score_wx}')
                shishen = ten_deities.get(day_gan, {}).get(gan_char, '')
                # 规则：日柱截脚不计算十神（因为截脚天干就是日主本身）
                if shishen and '日柱' not in item:
                    score_ss = gaitou_jiejiao_score['截脚_十神']
                    shishen_scores[shishen] += score_ss
                    shishen_details[shishen].append(f'{item}{gan_char}为{shishen}: {score_ss}')
    
    def _apply_zhi_relation_scores(self, zhi_analysis, wuxing_scores, wuxing_details, 
                                    shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, gan5, prefix=''):
        """应用地支关系评分 - 大运流年模式
        
        处理第六论级的嵌套数据结构：
        {
            '大运地支影响': {'年柱': [{'类型': '三会', '描述': '...'}, ...], ...},
            '流年地支影响': {...},
            '大运流年地支关系': {...}
        }
        """
        scores = self.SCORE_ZHI_RELATIONS
        
        # 遍历所有影响类别（大运地支影响、流年地支影响、大运流年地支关系）
        for impact_category, pillar_impacts in zhi_analysis.items():
            if not isinstance(pillar_impacts, dict):
                continue
            # 遍历各柱的影响列表
            for pillar_name, impacts in pillar_impacts.items():
                if not isinstance(impacts, list):
                    continue
                for impact in impacts:
                    # 跳过非字典类型的数据（兼容字符串格式）
                    if not isinstance(impact, dict):
                        continue
                    impact_type = impact.get('类型', '')
                    desc = impact.get('描述', '')
                    
                    if impact_type in scores:
                        score_wx = scores[impact_type]['wuxing']
                        # 根据描述提取五行并加分
                        full_prefix = f'{prefix}{impact_category}-{pillar_name}'
                        self._add_wuxing_score_by_text(desc, wuxing_scores, wuxing_details, score_wx, full_prefix)
                        
                        # 拱会/拱合需要额外加十神
                        if impact_type in ['拱会', '拱合'] and scores[impact_type].get('gong_zhi_canggan_shishen'):
                            if impact_type == '拱会':
                                self._add_gonghui_shishen(desc, shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, full_prefix)
                            else:
                                self._add_gonghe_shishen(desc, shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, full_prefix)
    
    def _apply_gan_relation_scores(self, gan_analysis, wuxing_scores, wuxing_details,
                                    shishen_scores, shishen_details, day_gan, ten_deities, gan5, prefix=''):
        """应用天干关系评分 - 大运流年模式
        
        处理第六论级的嵌套数据结构：
        {
            '大运天干影响': {'年柱': [{'类型': '天干五合', '描述': '...'}, ...], ...},
            '流年天干影响': {...},
            '大运流年天干关系': {...}
        }
        """
        scores = self.SCORE_GAN_RELATIONS
        
        # 遍历所有影响类别（大运天干影响、流年天干影响、大运流年天干关系）
        for impact_category, pillar_impacts in gan_analysis.items():
            if not isinstance(pillar_impacts, dict):
                continue
            # 遍历各柱的影响列表
            for pillar_name, impacts in pillar_impacts.items():
                if not isinstance(impacts, list):
                    continue
                for impact in impacts:
                    # 跳过非字典类型的数据（兼容字符串格式）
                    if not isinstance(impact, dict):
                        continue
                    impact_type = impact.get('类型', '')
                    desc = impact.get('描述', '')
                    full_prefix = f'{prefix}{impact_category}-{pillar_name}'
                    
                    if impact_type == '天干五合':
                        wuhe_map = {
                            '甲己': '土', '己甲': '土',
                            '乙庚': '金', '庚乙': '金',
                            '丙辛': '水', '辛丙': '水',
                            '丁壬': '木', '壬丁': '木',
                            '戊癸': '火', '癸戊': '火'
                        }
                        for pair, wuxing in wuhe_map.items():
                            if pair in desc:
                                wuxing_scores[wuxing] += scores['天干五合']['wuxing']
                                wuxing_details[wuxing].append(f'{full_prefix}{desc}化{wuxing}: +{scores["天干五合"]["wuxing"]}')
                                break
                    
                    elif impact_type == '天干相克':
                        ke_map = {
                            '甲戊': '戊', '己癸': '癸', '乙己': '己', '庚甲': '甲',
                            '丙庚': '庚', '辛乙': '乙', '丁辛': '辛', '壬丙': '丙',
                            '戊壬': '壬', '癸丁': '丁'
                        }
                        for pair, beike in ke_map.items():
                            if pair in desc:
                                wuxing = gan5.get(beike, '')
                                shishen = ten_deities.get(day_gan, {}).get(beike, '')
                                if wuxing:
                                    wuxing_scores[wuxing] += scores['天干相克']['wuxing']
                                    wuxing_details[wuxing].append(f'{full_prefix}{desc}({beike}被克): {scores["天干相克"]["wuxing"]}')
                                if shishen:
                                    shishen_scores[shishen] += scores['天干相克']['shishen']
                                    shishen_details[shishen].append(f'{full_prefix}{desc}({beike}为{shishen}被克): {scores["天干相克"]["shishen"]}')
                                break
    
    def _apply_ganzhi_relation_scores(self, ganzhi_analysis, wuxing_scores, wuxing_details,
                                       shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, gan5, prefix=''):
        """应用干支关系评分 - 大运流年模式
        
        处理第六论级的嵌套数据结构：
        {
            '岁运原局干支关系': {'大运与年柱': [{'类型': '盖头', '描述': '...'}, ...], ...},
            '大运干支关系': [{'类型': '盖头', '描述': '...'}, ...],
            '流年干支关系': [...]
        }
        """
        scores = self.SCORE_GANZHI_RELATIONS
        
        # 处理不同类型的干支关系
        for relation_category, relation_data in ganzhi_analysis.items():
            if isinstance(relation_data, dict):
                # '岁运原局干支关系' 是字典结构
                for relation_name, impacts in relation_data.items():
                    if not isinstance(impacts, list):
                        continue
                    for impact in impacts:
                        # 跳过非字典类型的数据（兼容字符串格式）
                        if not isinstance(impact, dict):
                            continue
                        impact_type = impact.get('类型', '')
                        desc = impact.get('描述', '')
                        full_prefix = f'{prefix}{relation_category}-{relation_name}'
                        
                        if impact_type == '盖头':
                            zhi_char = self._extract_zhi_from_ganzhi_item(desc)
                            if zhi_char:
                                wuxing = self.ZHI_WUHANGS.get(zhi_char, '')
                                if wuxing:
                                    wuxing_scores[wuxing] += scores['盖头']['wuxing']
                                    wuxing_details[wuxing].append(f'{full_prefix}{desc}: {zhi_char}{wuxing}{scores["盖头"]["wuxing"]}')
                                canggan_list = zhi5_list.get(zhi_char, [])
                                if canggan_list:
                                    main_canggan = canggan_list[0]
                                    shishen = ten_deities.get(day_gan, {}).get(main_canggan, '')
                                    if shishen:
                                        shishen_scores[shishen] += scores['盖头']['shishen']
                                        shishen_details[shishen].append(f'{full_prefix}{desc}{zhi_char}藏干主气{main_canggan}为{shishen}: {scores["盖头"]["shishen"]}')
                        
                        elif impact_type == '截脚':
                            gan_char = self._extract_gan_from_ganzhi_item(desc)
                            if gan_char:
                                wuxing = gan5.get(gan_char, '')
                                if wuxing:
                                    wuxing_scores[wuxing] += scores['截脚']['wuxing']
                                    wuxing_details[wuxing].append(f'{full_prefix}{desc}: {gan_char}{wuxing}{scores["截脚"]["wuxing"]}')
                                shishen = ten_deities.get(day_gan, {}).get(gan_char, '')
                                if shishen:
                                    shishen_scores[shishen] += scores['截脚']['shishen']
                                    shishen_details[shishen].append(f'{full_prefix}{desc}{gan_char}为{shishen}: {scores["截脚"]["shishen"]}')
            
            elif isinstance(relation_data, list):
                # '大运干支关系' 和 '流年干支关系' 是列表结构
                for impact in relation_data:
                    # 跳过非字典类型的数据（兼容字符串格式）
                    if not isinstance(impact, dict):
                        continue
                    impact_type = impact.get('类型', '')
                    desc = impact.get('描述', '')
                    full_prefix = f'{prefix}{relation_category}'
                    
                    if impact_type == '盖头':
                        zhi_char = self._extract_zhi_from_ganzhi_item(desc)
                        if zhi_char:
                            wuxing = self.ZHI_WUHANGS.get(zhi_char, '')
                            if wuxing:
                                wuxing_scores[wuxing] += scores['盖头']['wuxing']
                                wuxing_details[wuxing].append(f'{full_prefix}{desc}: {zhi_char}{wuxing}{scores["盖头"]["wuxing"]}')
                            canggan_list = zhi5_list.get(zhi_char, [])
                            if canggan_list:
                                main_canggan = canggan_list[0]
                                shishen = ten_deities.get(day_gan, {}).get(main_canggan, '')
                                if shishen:
                                    shishen_scores[shishen] += scores['盖头']['shishen']
                                    shishen_details[shishen].append(f'{full_prefix}{desc}{zhi_char}藏干主气{main_canggan}为{shishen}: {scores["盖头"]["shishen"]}')
                    
                    elif impact_type == '截脚':
                        gan_char = self._extract_gan_from_ganzhi_item(desc)
                        if gan_char:
                            wuxing = gan5.get(gan_char, '')
                            if wuxing:
                                wuxing_scores[wuxing] += scores['截脚']['wuxing']
                                wuxing_details[wuxing].append(f'{full_prefix}{desc}: {gan_char}{wuxing}{scores["截脚"]["wuxing"]}')
                            shishen = ten_deities.get(day_gan, {}).get(gan_char, '')
                            if shishen:
                                shishen_scores[shishen] += scores['截脚']['shishen']
                                shishen_details[shishen].append(f'{full_prefix}{desc}{gan_char}为{shishen}: {scores["截脚"]["shishen"]}')
    
    def _add_wuxing_score_by_text(self, text, wuxing_scores, wuxing_details, score, prefix=''):
        """根据文本内容判断五行并加分"""
        wuxing_map = {'木': '木', '火': '火', '土': '土', '金': '金', '水': '水'}
        for wx_name, wx_key in wuxing_map.items():
            if wx_name in text:
                wuxing_scores[wx_key] += score
                sign = '+' if score > 0 else ''
                wuxing_details[wx_key].append(f'{prefix}{text}: {sign}{score}')
                return
    
    def _add_gonghui_shishen(self, text, shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, prefix=''):
        """添加拱会藏干主气十神分"""
        gonghui_info = {
            '卯': ('木', '乙'), '午': ('火', '丙'),
            '酉': ('金', '辛'), '子': ('水', '癸')
        }
        for gong_zhi, (wuxing, canggan) in gonghui_info.items():
            if gong_zhi in text and wuxing in text:
                shishen = ten_deities.get(day_gan, {}).get(canggan, '')
                if shishen:
                    shishen_scores[shishen] += 1
                    shishen_details[shishen].append(f'{prefix}拱会{gong_zhi}藏干主气{canggan}为{shishen}: +1')
                return
    
    def _add_gonghe_shishen(self, text, shishen_scores, shishen_details, day_gan, zhi5_list, ten_deities, prefix=''):
        """添加拱合藏干主气十神分"""
        gonghe_info = {
            '卯': ('木', '乙'), '午': ('火', '丙'),
            '酉': ('金', '辛'), '子': ('水', '癸')
        }
        for gong_zhi, (wuxing, canggan) in gonghe_info.items():
            if gong_zhi in text and wuxing in text:
                shishen = ten_deities.get(day_gan, {}).get(canggan, '')
                if shishen:
                    shishen_scores[shishen] += 1
                    shishen_details[shishen].append(f'{prefix}拱合{gong_zhi}藏干主气{canggan}为{shishen}: +1')
                return
    
    def _extract_zhi_from_ganzhi_item(self, item):
        """从干支关系项中提取地支"""
        for zhi in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
            if zhi in item:
                return zhi
        return None
    
    def _extract_gan_from_ganzhi_item(self, item):
        """从干支关系项中提取天干"""
        for gan in ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
            if gan in item:
                return gan
        return None


    def _determine_main_geju(self) -> Dict:
        """综合格局判定"""
        result = {
            '主格局': '',
            '次要格局': [],
            '格局说明': '',
            '判定依据': []
        }

        # 使用第一论级的格局判定
        first_level = self.analysis_result.get('第一论级_月令与格局', {})

        # 主格局：取主要格局
        result['主格局'] = first_level.get('主要格局', '')

        # 次要格局：使用第一论级的次要格局
        secondary = first_level.get('次要格局', [])

        # 去重
        all_secondary = list(set(secondary))
        result['次要格局'] = all_secondary

        # 格局说明
        if result['主格局']:
            result['格局说明'] = first_level.get('格局说明', '')
            result['判定依据'].append(f'第一论级主要格局: {result["主格局"]}')

        # 如果有次要格局，添加判定依据
        if result['次要格局']:
            result['判定依据'].append(f'次要格局: {", ".join(result["次要格局"])}')

        # ==================== 计算原局五行和十神能量评分 ====================
        energy_scores = self._calculate_wuxing_shishen_scores(include_dayun_liunian=False)
        result['五行能量分析'] = energy_scores['五行得分']
        result['五行详情'] = energy_scores['五行详情']
        result['十神能量分析'] = energy_scores['十神得分']
        result['十神详情'] = energy_scores['十神详情']

        # ==================== 计算结合大运流年后的五行和十神能量评分 ====================
        if self.dayun_liunian and hasattr(self.dayun_liunian, 'current_dayun_gan'):
            energy_scores_with_dayun = self._calculate_wuxing_shishen_scores(include_dayun_liunian=True)
            result['大运流年五行能量分析'] = energy_scores_with_dayun['五行得分']
            result['大运流年五行详情'] = energy_scores_with_dayun['五行详情']
            result['大运流年十神能量分析'] = energy_scores_with_dayun['十神得分']
            result['大运流年十神详情'] = energy_scores_with_dayun['十神详情']

            # 计算大运流年对原局的影响（增加的能量）
            dayun_impact = self._calculate_energy_impact_with_unified_scoring(
                self.analysis_result.get('第六论级', {})
            )
            result['大运流年五行影响'] = dayun_impact['五行影响']['大运流年增加']
            result['大运流年五行影响详情'] = dayun_impact['五行影响']['大运流年增加详情']
            result['大运流年十神影响'] = dayun_impact['十神影响']['大运流年增加']
            result['大运流年十神影响详情'] = dayun_impact['十神影响']['大运流年增加详情']

        return result
    
    # ==================== 第五论级实现 ====================

    def _analyze_xi_ji(self) -> Dict:
        """
        第五论级: 定喜忌（优化版 - 喜用四步法）

        根据以下步骤判断喜神、用神、忌神：
        第一步：诊断核心矛盾 - 定旺衰，辨格局
        第二步：开具药方 - 取用神，定喜忌
        第三步：考虑特殊情况 - 论调候
        第四步：化解内部冲突 - 寻通关
        """
        result = {
            '旺衰判定': '',
            '用神': [],
            '喜神': [],
            '忌神': [],
            '调候用神': [],
            '调候分析': '',
            '调候提要': '',
            '调候优先级': '',
            '通关神': [],
            '喜忌依据': [],
            '其余十神': []
        }

        day_gan = self.day_gan
        month_zhi = self.month_zhi

        # ==================== 第一步：定旺衰 ====================
        strength_info = self._calculate_day_master_strength()
        result['旺衰判定'] = strength_info['状态']
        result['旺衰得分'] = strength_info['总分']
        result['旺衰详情'] = strength_info['详情']
        result['喜忌依据'].append(f"旺衰判定: {strength_info['状态']} (得分: {strength_info['总分']})")

        # ==================== 第二步：取用神、定喜忌 ====================
        yong_xi_info = self._determine_yong_xi(strength_info)
        result['用神'] = yong_xi_info['用神']
        result['喜神'] = yong_xi_info['喜神']
        result['忌神'] = yong_xi_info['忌神']
        result['喜忌依据'].extend(yong_xi_info['依据'])

        # ==================== 第三步：论调候 ====================
        diahou_info = self._analyze_tiaohou()
        result['调候用神'] = diahou_info['调候用神']
        result['调候分析'] = diahou_info['调候说明']
        result['调候提要'] = diahou_info['调候提要']
        result['调候优先级'] = diahou_info['优先级']
        result['喜忌依据'].extend(diahou_info['依据'])
        # 添加其余十神分析
        result['其余十神'] = diahou_info.get('其余十神', [])

        # ==================== 第四步：寻通关 ====================
        tongguan_info = self._analyze_tongguan()
        result['通关神'] = tongguan_info['通关神']
        result['喜忌依据'].extend(tongguan_info['依据'])

        return result

    def _calculate_day_master_strength(self) -> Dict:
        """
        计算日主旺衰（第一步：诊断核心矛盾）

        评分体系：
        - 月令权重: ±40分（最重要依据）
        - 地支根气: ±30分（禄、旺、墓库）
        - 天干生扶: ±20分（印星、比劫）
        - 克泄耗: ±10分（官杀、食伤、财星）

        得分范围: -100 ~ +100
        - > 30: 身旺/强
        - -30 ~ 30: 身中和
        - < -30: 身弱/衰
        """
        day_gan = self.day_gan
        month_zhi = self.month_zhi

        # 获取日主五行
        from ganzhi import gan5
        day_wuxing = gan5.get(day_gan, '')
        if not day_wuxing:
            return {'状态': '未知', '总分': 0, '详情': '无法确定日主五行'}

        total_score = 0
        details = []

        # 1. 月令判断（权重±40）
        month_wuxing = self.ZHI_WUHANGS.get(month_zhi, '')

        # 月令旺相休囚死表
        wuxing_season = {
            '木': {'春(寅卯辰)': '旺', '夏(巳午未)': '休', '秋(申酉戌)': '囚', '冬(亥子丑)': '相'},
            '火': {'春': '相', '夏': '旺', '秋': '囚', '冬': '休'},
            '土': {'春': '囚', '夏': '相', '秋': '休', '冬': '囚'},
            '金': {'春': '囚', '夏': '死', '秋': '旺', '冬': '相'},
            '水': {'春': '休', '夏': '囚', '秋': '相', '冬': '旺'}
        }

        # 判断季节
        season = ''
        if month_zhi in ['寅', '卯', '辰']:
            season = '春(寅卯辰)'
        elif month_zhi in ['巳', '午', '未']:
            season = '夏(巳午未)'
        elif month_zhi in ['申', '酉', '戌']:
            season = '秋(申酉戌)'
        elif month_zhi in ['亥', '子', '丑']:
            season = '冬(亥子丑)'

        if season:
            season_status = wuxing_season.get(day_wuxing, {}).get(season, '未知')
            if season_status == '旺':
                total_score += 40
                details.append(f'月令得旺: +40分')
            elif season_status == '相':
                total_score += 30
                details.append(f'月令得相: +30分')
            elif season_status == '休':
                total_score -= 10
                details.append(f'月令休: -10分')
            elif season_status == '囚':
                total_score -= 20
                details.append(f'月令囚: -20分')
            elif season_status == '死':
                total_score -= 40
                details.append(f'月令死: -40分')

        # 2. 地支根气（权重±30）
        # 禄、旺地支
        lu_wang_map = {
            '甲': {'禄': '寅', '旺': '卯', '墓库': '未'},
            '乙': {'禄': '卯', '旺': '寅', '墓库': '辰'},
            '丙': {'禄': '巳', '旺': '午', '墓库': '戌'},
            '丁': {'禄': '午', '旺': '巳', '墓库': '未'},
            '戊': {'禄': '巳', '旺': '午', '墓库': '戌'},
            '己': {'禄': '午', '旺': '巳', '墓库': '丑'},
            '庚': {'禄': '申', '旺': '酉', '墓库': '丑'},
            '辛': {'禄': '酉', '旺': '申', '墓库': '辰'},
            '壬': {'禄': '亥', '旺': '子', '墓库': '辰'},
            '癸': {'禄': '子', '旺': '亥', '墓库': '未'}
        }

        root_score = 0
        root_info = lu_wang_map.get(day_gan, {})
        if root_info:
            # 检查地支中是否有禄、旺、墓库
            for zhi in self.zhis:
                if zhi == root_info.get('禄'):
                    root_score += 15
                    details.append(f'地支得禄{zhi}: +15分')
                elif zhi == root_info.get('旺'):
                    root_score += 10
                    details.append(f'地支得旺{zhi}: +10分')
                elif zhi == root_info.get('墓库'):
                    root_score += 5
                    details.append(f'地支得墓库{zhi}: +5分')

        total_score += root_score

        # 3. 天干生扶（权重±20）
        # 印星（生我者）和比劫（同我者）
        gan_score = 0
        for gan in self.gans:
            deity = ten_deities.get(day_gan, {}).get(gan, '')
            if deity == '印' or deity == '枭':
                gan_score += 5
                details.append(f'天干{gan}为{deity}星: +5分')
            elif deity == '比' or deity == '劫':
                gan_score += 3
                details.append(f'天干{gan}为{deity}星: +3分')

        total_score += gan_score

        # 4. 克泄耗（权重-10）
        # 官杀（克我者）、食伤（我生者）、财星（我克者）
        consume_score = 0
        for gan in self.gans:
            deity = ten_deities.get(day_gan, {}).get(gan, '')
            if deity == '官' or deity == '杀':
                consume_score -= 3
                details.append(f'天干{gan}为{deity}星: -3分')
            elif deity == '食' or deity == '伤':
                consume_score -= 2
                details.append(f'天干{gan}为{deity}星: -2分')
            elif deity == '财':
                consume_score -= 2
                details.append(f'天干{gan}为财星: -2分')

        total_score += consume_score

        # 判定状态（调整阈值，使判断更准确）
        if total_score > 20:
            status = '身旺'
        elif total_score < -20:
            status = '身弱'
        else:
            # 身中和时，需要结合月令强弱和整体力量来判断
            # 如果得分在-20~20之间，检查月令是否支持
            if month_zhi in ['寅', '卯', '辰'] and day_wuxing == '木':
                status = '身弱'  # 木生春季但失令，可能偏弱
            elif month_zhi in ['巳', '午', '未'] and day_wuxing == '火':
                status = '身弱'
            elif month_zhi in ['申', '酉', '戌'] and day_wuxing == '金':
                status = '身弱'
            elif month_zhi in ['亥', '子', '丑'] and day_wuxing == '水':
                status = '身弱'
            else:
                status = '身中和'

        return {
            '状态': status,
            '总分': total_score,
            '详情': '; '.join(details)
        }

    def _determine_yong_xi(self, strength_info: Dict) -> Dict:
        """
        取用神、定喜忌（第二步：开具药方）

        根据"损有余而补不足"原则：
        - 身旺：用神=官杀/食伤/财星，喜神=生扶用神的五行，忌神=印星/比劫
        - 身弱：用神=印星/比劫，喜神=生扶用神的五行，忌神=官杀/食伤/财星
        """
        day_gan = self.day_gan
        status = strength_info['状态']

        yong_shen = []
        xi_shen = []
        ji_shen = []
        reasons = []

        # 获取日主五行
        from ganzhi import gan5, wuhangs
        day_wuxing = gan5.get(day_gan, '')

        # 五行相生相克关系
        sheng_ke = {
            '木': {'生': '火', '被生': '水', '克': '土', '被克': '金'},
            '火': {'生': '土', '被生': '木', '克': '金', '被克': '水'},
            '土': {'生': '金', '被生': '火', '克': '水', '被克': '木'},
            '金': {'生': '水', '被生': '土', '克': '木', '被克': '火'},
            '水': {'生': '木', '被生': '金', '克': '火', '被克': '土'}
        }

        # 五行对应天干
        wuxing_to_gan = {
            '木': ['甲', '乙'],
            '火': ['丙', '丁'],
            '土': ['戊', '己'],
            '金': ['庚', '辛'],
            '水': ['壬', '癸']
        }

        if status == '身旺':
            # 身旺：核心病根是印星、比劫
            # 用神：克制日主的官杀、泄秀的食伤、消耗能量的财星
            # 首选官杀（克制），次选食伤（泄秀），再次选财星（消耗）

            # 首选：官杀（克我者）
            guan_sha_wuxing = sheng_ke[day_wuxing]['被克']  # 被克者克我
            for gan in wuxing_to_gan.get(guan_sha_wuxing, []):
                if gan not in yong_shen:
                    yong_shen.append(gan)
            if guan_sha_wuxing:
                reasons.append(f'身旺首选官杀({guan_sha_wuxing})克制日主')

            # 次选：食伤（我生者，泄秀）
            shi_shang_wuxing = sheng_ke[day_wuxing]['生']
            for gan in wuxing_to_gan.get(shi_shang_wuxing, []):
                if gan not in yong_shen:
                    yong_shen.append(gan)
            if shi_shang_wuxing:
                reasons.append(f'身旺次选食伤({shi_shang_wuxing})泄秀')

            # 再次：财星（我克者，消耗）
            cai_wuxing = sheng_ke[day_wuxing]['克']
            for gan in wuxing_to_gan.get(cai_wuxing, []):
                if gan not in yong_shen:
                    yong_shen.append(gan)
            if cai_wuxing:
                reasons.append(f'身旺再次财星({cai_wuxing})消耗')

            # 忌神：印星、比劫
            yin_wuxing = sheng_ke[day_wuxing]['被生']  # 印星（生我者）
            bi_wuxing = day_wuxing  # 比劫（同我者）

            ji_wuxing_list = [yin_wuxing, bi_wuxing]
            for jwx in ji_wuxing_list:
                if jwx:
                    for gan in wuxing_to_gan.get(jwx, []):
                        if gan not in ji_shen and gan not in yong_shen:
                            ji_shen.append(gan)
            reasons.append(f'身旺忌印星({yin_wuxing})、比劫({bi_wuxing})')

            # 喜神：生扶用神的五行（不能是用神，也不能是忌神）
            # 如果用神是官杀（金），喜神就是生金的财星（土）
            if yong_shen:
                first_yong_gan = yong_shen[0]
                first_yong_wuxing = gan5.get(first_yong_gan, '')
                if first_yong_wuxing:
                    xi_wuxing = sheng_ke[first_yong_wuxing]['被生']  # 生用神的五行
                    for gan in wuxing_to_gan.get(xi_wuxing, []):
                        if gan not in xi_shen and gan not in yong_shen and gan not in ji_shen:
                            xi_shen.append(gan)
                    if xi_wuxing:
                        reasons.append(f'喜神({xi_wuxing})生扶用神({first_yong_wuxing})')

        elif status == '身弱':
            # 身弱：核心病根是官杀、食伤、财星
            # 用神：印星、比劫
            # 首选印星（化杀），次选比劫（助身）

            # 首选：印星（生我者）
            yin_wuxing = sheng_ke[day_wuxing]['被生']
            for gan in wuxing_to_gan.get(yin_wuxing, []):
                if gan not in yong_shen:
                    yong_shen.append(gan)
            if yin_wuxing:
                reasons.append(f'身弱首选印星({yin_wuxing})生扶')

            # 次选：比劫（同我者）
            bi_wuxing = day_wuxing
            for gan in wuxing_to_gan.get(bi_wuxing, []):
                if gan not in yong_shen:
                    yong_shen.append(gan)
            if bi_wuxing:
                reasons.append(f'身弱次选比劫({bi_wuxing})助身')

            # 忌神：官杀、食伤、财星（不能是用神）
            guan_sha_wuxing = sheng_ke[day_wuxing]['被克']
            shi_shang_wuxing = sheng_ke[day_wuxing]['生']
            cai_wuxing = sheng_ke[day_wuxing]['克']

            ji_wuxings = [guan_sha_wuxing, shi_shang_wuxing, cai_wuxing]
            for jw in ji_wuxings:
                if jw:
                    for gan in wuxing_to_gan.get(jw, []):
                        if gan not in ji_shen and gan not in yong_shen:
                            ji_shen.append(gan)
            reasons.append(f'身弱忌官杀({guan_sha_wuxing})、食伤({shi_shang_wuxing})、财星({cai_wuxing})')

            # 喜神：生扶用神的五行（不能是用神，也不能是忌神）
            # 如果用神是印星（水），喜神就是生水的官杀（金）
            # 但要注意：如果喜神与忌神冲突，则不取该喜神
            if yong_shen:
                first_yong_gan = yong_shen[0]
                first_yong_wuxing = gan5.get(first_yong_gan, '')
                if first_yong_wuxing:
                    xi_wuxing = sheng_ke[first_yong_wuxing]['被生']  # 生用神的五行
                    # 检查喜神五行是否与忌神五行冲突
                    if xi_wuxing not in [guan_sha_wuxing, shi_shang_wuxing, cai_wuxing]:
                        for gan in wuxing_to_gan.get(xi_wuxing, []):
                            if gan not in xi_shen and gan not in yong_shen and gan not in ji_shen:
                                xi_shen.append(gan)
                        if xi_wuxing:
                            reasons.append(f'喜神({xi_wuxing})生扶用神({first_yong_wuxing})')
                    else:
                        reasons.append(f'喜神({xi_wuxing})与忌神冲突，不取')

        elif status == '身中和':
            # 身中和：需要综合判断，暂不取用神
            reasons.append('身中和状态，需结合格局和调候综合判断')

        return {
            '用神': yong_shen,
            '喜神': xi_shen,
            '忌神': ji_shen,
            '依据': reasons
        }

    def _analyze_tiaohou(self) -> Dict:
        """
        论调候（第三步：考虑特殊情况）

        根据《穷通宝鉴》十干调候用神提要的核心思想：
        - 调候用神：根据日主和月令，确定调候用神及其优先级
        - 寒局：生于亥子丑月，八字金水多，用火暖局，喜木生火
        - 燥局：生于巳午未月，八字木火多，用水润局，喜金生水
        - 特殊说明：根据穷通宝鉴提要中的详细说明进行补充分析
        """
        day_gan = self.day_gan
        month_zhi = self.month_zhi
        day_month_key = day_gan + month_zhi

        result = {
            '调候用神': [],
            '调候说明': '',
            '调候提要': '',
            '优先级': '一般',
            '依据': [],
            '其余十神': []
        }

        # 穷通宝鉴调候用神提要（详细说明）
        tiaohou_notes = {
            # 甲木
            '甲寅': '调和气候为要，丙火为主，癸水为佐',
            '甲卯': '阳刃驾煞，专用庚金，以戊己滋煞为佐。无庚用丙丁泄秀，不取制煞',
            '甲辰': '用庚金必须丁火制之，为伤官制煞。无庚用壬',
            '甲巳': '调和气候，癸水为主。原局气润，庚丁为用',
            '甲午': '木性虚焦，癸为主要，无癸用丁，亦宜运行北方。木盛先庚，庚盛先丁',
            '甲未': '上半月同五月，用癸；下半月用庚丁',
            '甲申': '伤官制煞。无丁用壬，富而不贵',
            '甲酉': '用丁制煞，用丙调候，丁丙并用为佐',
            '甲戌': '土旺者用木，木旺者用庚金，丁壬癸为佐',
            '甲亥': '用庚金，取丁火制之。丙火调候。水旺用戊',
            '甲子': '木性生寒。丁先庚后，丙火为佐，必须支见巳寅，方为贵格',
            '甲丑': '丁火必不可少，通根巳寅，甲木为助，用庚劈甲引丁',
            # 乙木
            '乙寅': '取丙火解寒，略取癸水滋润，不宜困丙。火多用癸',
            '乙卯': '以癸滋木，以丙泄秀，不宜见金',
            '乙辰': '若支成水局，取戊为佐',
            '乙巳': '月令丙火得禄，专用癸水，调候为急',
            '乙午': '上半月专用癸水，下半月丙癸并用',
            '乙未': '润土滋木，喜用癸水。柱多金水，先用丙火。夏月壬癸，切记戊己杂乱',
            '乙申': '月垣庚金司令，取丙火制之，或癸水化之。不论用丙用癸，皆己土为佐',
            '乙酉': '上半月癸先丙后，下半月丙先癸后。无癸用壬。支成金局，又宜用丁',
            '乙戌': '以金发水之源。见甲，名藤萝系甲',
            '乙亥': '乙木向阳，专用丙火，水多以戊为佐',
            '乙子': '寒木向阳，专用丙火，忌见癸水',
            '乙丑': '寒谷回春，专用丙火',
            # 丙火
            '丙寅': '壬水为用，庚金发水之源为佐',
            '丙卯': '专用壬水，水多用戊制之。身弱用印化之。无壬用己',
            '丙辰': '专用壬水。土重，以甲为佐',
            '丙巳': '以庚为佐。忌戊制壬。无壬用癸',
            '丙午': '壬庚以通根申宫为妙',
            '丙未': '以庚为佐',
            '丙申': '壬水通根申宫，壬多必取戊制',
            '丙酉': '四柱多丙，一壬高透为奇。无壬用癸',
            '丙戌': '忌土晦光，先取甲疏土，次用壬水',
            '丙亥': '月垣壬水秉令，水旺用甲木化之。身煞两旺，用戊制之。火旺用壬，木旺宜庚',
            '丙子': '气进二阳，丙火弱中复强，用壬水，取戊制之。无戊用己',
            '丙丑': '喜壬为用。土多，不可少甲',
            # 丁火
            '丁寅': '用庚金劈甲引丁',
            '丁卯': '以庚去乙，以甲引丁',
            '丁辰': '用甲木引丁制土，次看庚金。木盛用庚，水盛用土',
            '丁巳': '取甲引丁，甲多又取庚为先',
            '丁午': '火多，以庚壬两透为贵。无壬用癸，为独煞当权',
            '丁未': '以甲木化壬引丁为用。用甲木不能无庚，取庚为佐',
            '丁申': '取庚劈甲，无甲用乙。用丙暖金晒甲。无庚甲而用乙者，见丙为杜草引灯。水旺用戊',
            '丁酉': '取庚劈甲，无甲用乙。用丙暖金晒甲。无庚甲而用乙者，见丙为枯草引灯。水旺用戊',
            '丁戌': '一派戊土无甲，为伤官伤尽',
            '丁亥': '庚金劈甲引丁，甲木为尊，庚金为佐。戊癸权宜酌用',
            '丁子': '庚金劈甲引丁，甲木为尊，庚金为佐。戊癸权宜酌用',
            '丁丑': '庚金劈甲引丁，甲木为尊，庚金为佐。戊癸权宜酌用',
            # 戊土
            '戊寅': '无丙照暖，戊土不生。无甲疏劈，戊土不灵。无癸滋润，万物不长。先丙、次甲次癸',
            '戊卯': '无丙照暖，戊土不生。无甲疏劈，戊土不灵。无癸滋润，万物不长。先丙、次甲次癸',
            '戊辰': '戊土司令，先用甲疏、次丙、次癸',
            '戊巳': '戊土建禄，先用甲疏劈，次取丙癸',
            '戊午': '调候为急，先用壬水，次取甲木，丙火配用',
            '戊未': '调候为急，癸不可缺。丙火配用。土重不能无甲',
            '戊申': '寒气渐增，先用丙火。水多，用甲泄之',
            '戊酉': '赖丙照暖，喜水滋润',
            '戊戌': '戊土当权，先用甲木，次取丙火。见金，先用癸水，后取丙火',
            '戊亥': '非甲不灵，非丙不暖',
            '戊子': '丙火为尚，甲木为佐',
            '戊丑': '丙火为尚，甲木为佐',
            # 己土
            '己寅': '取丙解寒，忌见壬水。如水多，须以戊土为佐。土多用甲，甲多用庚',
            '己卯': '用甲，忌与己土合化。次用癸水润之',
            '己辰': '先丙后癸，土暖而润，随用甲疏',
            '己巳': '调候不能无癸，土润不能无丙',
            '己午': '调候不能无癸，土润不能无丙',
            '己未': '调候不能无癸，土润不能无丙',
            '己申': '丙火温土，癸水润土。七月庚金司权，丙能制金，癸以泄金',
            '己酉': '取辛辅癸',
            '己戌': '九月土盛，宜甲木疏之，次用丙癸',
            '己亥': '三冬己土，非丙暖不生。初冬壬旺，取戊土制之。土多，取甲木疏之',
            '己子': '三冬己土，非丙暖不生。壬水太旺，取戊土制之。土多，取甲木疏之',
            '己丑': '三冬己土，非丙暖不生。壬水太旺，取戊土制之。土多，取甲木疏之',
            # 庚金
            '庚寅': '用丙暖庚性。虑土厚埋金，须甲泄秀。火多用土，支成火局用壬',
            '庚卯': '庚金暗强，专用丁火。借甲引丁，用庚劈甲。无丁用丙',
            '庚辰': '顽金宜丁。土旺用甲，不用庚劈。支火宜癸，干火宜壬',
            '庚巳': '丙不熔金，惟喜壬制，次取戊土，丙火为佐。支成金局，变弱为强，须用丁火',
            '庚午': '专用壬水，癸次之。须支见庚、辛为助。无壬癸，用戊己泄火之气',
            '庚未': '若支会土局，甲先丁后',
            '庚申': '专用丁火，甲木引丁',
            '庚酉': '用丁甲煅金，兼用丙火调候',
            '庚戌': '土厚先用甲疏，次用壬洗。忌见己土浊壬',
            '庚亥': '水冷金寒爱丙丁。甲木辅丁',
            '庚子': '仍取丁甲，次取丙火照暖。一派金水，不入和暖之乡，孤贫。丙丁须寅巳午未戌支，方为有力',
            '庚丑': '仍取丁甲，次取丙火照暖。一派金水，不入和暖之乡，孤贫。丙丁须寅巳午未戌支，方为有力',
            # 辛金
            '辛寅': '辛金失令，取己土为生身之本。欲得辛金发用，全赖壬水之功。壬己并用，以庚为助',
            '辛卯': '与正月同',
            '辛辰': '若见丙火合辛，须有癸制丙。支见亥子申，为贵',
            '辛巳': '壬水淘洗，兼有调候之用。更有甲木制戊，一清澈底',
            '辛午': '己无壬不湿，辛无巳不生，故壬己并用。无壬用癸',
            '辛未': '先用壬水，取庚为佐。忌戊出，得甲制之，方吉',
            '辛申': '壬水为尊，甲戊酌用。不可用癸水',
            '辛酉': '壬水淘洗，如见戊己，须甲制土。支成金局，无壬，须用丁火',
            '辛戌': '九月辛金，火土为病，水木为药',
            '辛亥': '先壬后丙，名金白水清。余皆酌用',
            '辛子': '冬月辛金，不能缺丙火温暖。余皆酌用',
            '辛丑': '同上。丙先壬后，戊己次之。总之，丙火不可少也',
            # 壬水
            '壬寅': '无比劫者，不必用戊，专用庚金，以丙为佐。如比劫多，宜制之，一戊出干，名"一将当关，群邪自伏"',
            '壬卯': '三春壬水绝地，取庚辛发水之源。水多用戊',
            '壬辰': '甲疏季土，次取庚金发水源；金多，须丙制为妙',
            '壬巳': '壬水弱极，取庚辛为源，壬癸比助',
            '壬午': '取庚为源，取癸为佐。无庚用辛',
            '壬未': '以辛金发水源，甲木疏土',
            '壬申': '取丁火佐戊制庚。戊土通根辰戌，丁火通根午戌，方可为用',
            '壬酉': '无甲，用金发水源，名"浊水三犯庚辛，体全之象"',
            '壬戌': '以甲制戌中戊土，丙火为佐',
            '壬亥': '如甲出制戊，须以庚金为救',
            '壬子': '水旺宜戊，调候宜丙，丙戊必须兼用',
            '壬丑': '上半月专用丙火；下半月用丙，甲木为佐',
            # 癸水
            '癸寅': '用辛生癸水为源，无辛用庚，丙不可少',
            '癸卯': '乙木司令，专用庚金，辛金次之',
            '癸辰': '上半月专用丙火；下半月虽用丙火，辛甲佐之',
            '癸巳': '无辛用庚',
            '癸午': '庚辛为生身之本。但丁火司权，金难敌火，宜兼用比劫，方得庚辛之用',
            '癸未': '上半月金神衰弱，火气炎热，宜比劫帮身，同五月。下半月无比劫亦可',
            '癸申': '庚金得禄，必丁火制金为用。丁火以通根午戌未为妙',
            '癸酉': '辛金为用，丙火佐之，名水暖金温，须隔位同透为妙',
            '癸戌': '专用辛金，忌戊土。要比劫滋甲，制戊为妙',
            '癸亥': '亥中甲木长生，泄散元神，宜用庚辛。水多用戊，金多用丁',
            '癸子': '丙火解冻，辛金滋扶',
            '癸丑': '丙火解冻，通根寅巳午未戌方妙。癸巳会党，年透丁火，名雪后灯光，夜生者贵。支成火局，又宜用庚辛'
        }

        # 解析调候用神
        if day_month_key in tiaohous:
            tiaohou_str = tiaohous[day_month_key]
            yongshen_list = []

            # 解析格式: '1丙2_癸3丁' 或 '1庚2_丙3丁4戊'
            # 提取所有用神（1、2、3、4、5）
            import re
            # 匹配 1-5 后可能跟下划线，然后是天干的模式
            matches = re.findall(r'[1-5]_?([甲乙丙丁戊己庚辛壬癸])', tiaohou_str)

            # 十神完整名称映射
            deity_full_names = {
                '比': '比肩',
                '劫': '劫财',
                '食': '食神',
                '伤': '伤官',
                '财': '正财',
                '杀': '七杀',
                '官': '正官',
                '印': '正印',
                '枭': '偏印'
            }

            if matches:
                # 为每个用神添加十神信息
                from ganzhi import gan5
                for gan in matches:
                    deity = ten_deities.get(day_gan, {}).get(gan, '')
                    wuxing = gan5.get(gan, '')
                    # 转换为完整名称
                    deity_full = deity_full_names.get(deity, deity)
                    yongshen_list.append(f'{gan}{wuxing}（{deity_full}）')

            result['调候用神'] = yongshen_list

        # 添加穷通宝鉴提要说明
        if day_month_key in tiaohou_notes:
            result['调候提要'] = tiaohou_notes[day_month_key]

        # ==================== 寒燥局判定（四大类）====================
        from ganzhi import gan5
        month_wuxing = self.ZHI_WUHANGS.get(month_zhi, '')

        # 统计八字五行数量
        wuxing_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        for gan in self.gans:
            wx = gan5.get(gan, '')
            if wx:
                wuxing_count[wx] += 1
        for zhi in self.zhis:
            wx = self.ZHI_WUHANGS.get(zhi, '')
            if wx:
                wuxing_count[wx] += 1

        # 检查天干地支是否有特定五行
        def has_wuxing_in_ganzhi(wuxing):
            """检查天干地支中是否有指定五行"""
            for gan in self.gans:
                if gan5.get(gan, '') == wuxing:
                    return True
            for zhi in self.zhis:
                if self.ZHI_WUHANGS.get(zhi, '') == wuxing:
                    return True
            return False

        def has_gan(gan_name):
            """检查是否有指定天干"""
            return gan_name in self.gans

        # （一）极寒局（生于亥、子、丑月）
        if month_zhi in ['亥', '子', '丑']:
            jinshui_count = wuxing_count['金'] + wuxing_count['水']
            muhuo_count = wuxing_count['木'] + wuxing_count['火']

            # 判断是否为极寒局：金水过旺或无火（降低阈值）
            if jinshui_count >= muhuo_count + 1 or not has_wuxing_in_ganzhi('火'):
                result['寒燥分析'] = {
                    '局型': '极寒局',
                    '核心原则': '寒则暖之（以火暖局）',
                    '病症': '生于冬令，命局冰冷生机闭',
                    '主用神': [],
                    '辅用神': [],
                    '忌神': ['金', '水']
                }

                # 主用神：丙火（第一）、丁火（第二）
                if has_gan('丙'):
                    result['寒燥分析']['主用神'].append('丙火（太阳火，暖局力强）')
                elif has_gan('丁'):
                    result['寒燥分析']['主用神'].append('丁火（灯烛火，辅助暖局）')
                else:
                    result['寒燥分析']['主用神'].append('丙火（太阳火，第一用神）')
                    result['寒燥分析']['主用神'].append('丁火（灯烛火，第二用神）')

                # 辅用神：戊土/己土（稳固火势）、甲木（生火助暖）
                if has_wuxing_in_ganzhi('土'):
                    result['寒燥分析']['辅用神'].append('戊土/己土（稳固火势，防水克火）')
                if has_wuxing_in_ganzhi('木'):
                    result['寒燥分析']['辅用神'].append('甲木（生火助暖，火弱时用）')

                result['调候说明'] = f"极寒局：生于{month_zhi}月冬令，命局冰冷，以火暖局为急"
                result['优先级'] = '高（调候优先）'
                result['依据'].append(f'极寒局：金水{jinshui_count}个，木火{muhuo_count}个，需火暖局')

        # （二）极燥局（生于巳、午、未月）
        elif month_zhi in ['巳', '午', '未']:
            muhuo_count = wuxing_count['木'] + wuxing_count['火']
            jinshui_count = wuxing_count['金'] + wuxing_count['水']

            # 判断是否为极燥局：木火过旺或无水（降低阈值）
            if muhuo_count >= jinshui_count + 1 or not has_wuxing_in_ganzhi('水'):
                result['寒燥分析'] = {
                    '局型': '极燥局',
                    '核心原则': '燥则润之（以水润局）',
                    '病症': '生于夏令，命局燥热耗损重',
                    '主用神': [],
                    '辅用神': [],
                    '忌神': ['火', '土']
                }

                # 主用神：癸水（第一）、辛金（第二）
                if has_gan('癸'):
                    result['寒燥分析']['主用神'].append('癸水（雨露水，第一用神）')
                else:
                    result['寒燥分析']['主用神'].append('癸水（雨露水，雨露润局）')

                if has_gan('辛'):
                    result['寒燥分析']['主用神'].append('辛金（阴金，生水护水）')

                # 辅用神：壬水（需辛金生助）、乙木
                if has_gan('壬'):
                    result['寒燥分析']['辅用神'].append('壬水（阳水，需辛金生助防水被土克）')
                if has_wuxing_in_ganzhi('木'):
                    result['寒燥分析']['辅用神'].append('乙木（阴木，泄水生火平衡燥气）')

                result['调候说明'] = f"极燥局：生于{month_zhi}月夏令，命局燥热，以水润局为急"
                result['优先级'] = '高（调候优先）'
                result['依据'].append(f'极燥局：木火{muhuo_count}个，金水{jinshui_count}个，需水润局')

        # （三）过湿局（生于寅、卯、辰月）
        elif month_zhi in ['寅', '卯', '辰']:
            mushui_count = wuxing_count['木'] + wuxing_count['水']
            tu_count = wuxing_count['土']

            # 判断是否为过湿局：木旺水助湿气重（降低阈值）
            if mushui_count >= 3 or (mushui_count >= 2 and tu_count <= 2):
                result['寒燥分析'] = {
                    '局型': '过湿局',
                    '核心原则': '湿则燥之（以土燥局、火暖局）',
                    '病症': '生于春令木旺，命局湿气重困顿',
                    '主用神': [],
                    '辅用神': [],
                    '忌神': ['水', '木']
                }

                # 主用神：戌土/未土（燥土，第一）、丙火（第二）
                zhi_has_xu_wei = '戌' in self.zhis or '未' in self.zhis
                if zhi_has_xu_wei:
                    result['寒燥分析']['主用神'].append('戌土/未土（燥土，燥湿固气第一用神）')
                else:
                    result['寒燥分析']['主用神'].append('戌土/未土（燥土，燥湿固气）')

                if has_gan('丙'):
                    result['寒燥分析']['主用神'].append('丙火（太阳火，暖局化湿）')
                else:
                    result['寒燥分析']['主用神'].append('丙火（太阳火，暖局化湿第二用神）')

                # 辅用神：庚金/辛金（伐木防湿）、戊土
                if has_wuxing_in_ganzhi('金'):
                    result['寒燥分析']['辅用神'].append('庚金/辛金（伐木防湿，减少木生湿）')
                if has_gan('戊'):
                    result['寒燥分析']['辅用神'].append('戊土（阳土，辅助燥湿）')

                result['调候说明'] = f"过湿局：生于{month_zhi}月春令，木旺湿重，以土燥之、火暖之"
                result['优先级'] = '高（调候优先）'
                result['依据'].append(f'过湿局：木水{mushui_count}个，土{tu_count}个，需燥土暖局')

        # （四）过凉局（生于申、酉、戌月）
        elif month_zhi in ['申', '酉', '戌']:
            jinshui_count = wuxing_count['金'] + wuxing_count['水']
            muhuo_count = wuxing_count['木'] + wuxing_count['火']

            # 判断是否为过凉局：金旺水助凉意过盛（降低阈值）
            if jinshui_count >= 3 or (jinshui_count >= 2 and muhuo_count <= 2):
                result['寒燥分析'] = {
                    '局型': '过凉局',
                    '核心原则': '凉则暖之（以火暖局）',
                    '病症': '生于秋令金旺，命局凉意过盛收敛过度',
                    '主用神': [],
                    '辅用神': [],
                    '忌神': ['金', '水']
                }

                # 主用神：丁火（第一，温和暖局）、丙火（第二，凉极时用）
                if has_gan('丁'):
                    result['寒燥分析']['主用神'].append('丁火（灯烛火，温和暖局第一用神）')
                else:
                    result['寒燥分析']['主用神'].append('丁火（灯烛火，温和暖局）')

                if has_gan('丙') and jinshui_count >= 4:
                    result['寒燥分析']['主用神'].append('丙火（太阳火，凉极时强暖）')

                # 辅用神：乙木/甲木（生火助暖）、己土
                if has_wuxing_in_ganzhi('木'):
                    result['寒燥分析']['辅用神'].append('乙木/甲木（生火助暖）')
                if has_gan('己'):
                    result['寒燥分析']['辅用神'].append('己土（阴土，稳固火势防暖局被冲）')

                result['调候说明'] = f"过凉局：生于{month_zhi}月秋令，金旺凉重，以火暖局"
                result['优先级'] = '高（调候优先）'
                result['依据'].append(f'过凉局：金水{jinshui_count}个，木火{muhuo_count}个，需火暖局')

        # （五）四季末平和局（生于辰、戌、丑、未月）
        elif month_zhi in ['辰', '戌', '丑', '未']:
            tu_count = wuxing_count['土']
            jinshui_count = wuxing_count['金'] + wuxing_count['水']
            muhuo_count = wuxing_count['木'] + wuxing_count['火']

            # 四季末土旺，根据其他五行旺相判断偏向
            if tu_count >= 3:
                # 土旺局
                result['寒燥分析'] = {
                    '局型': '土旺局（四季末）',
                    '核心原则': '土重则疏之（以木疏土）或泄之（以金泄土）',
                    '病症': f'生于{month_zhi}月四季末，土气厚重',
                    '主用神': [],
                    '辅用神': [],
                    '忌神': ['土']
                }

                # 主用神：甲木（疏土）、庚金（泄土）
                if has_gan('甲'):
                    result['寒燥分析']['主用神'].append('甲木（阳木，疏土第一用神）')
                else:
                    result['寒燥分析']['主用神'].append('甲木（阳木，疏土之力）')

                if has_gan('庚'):
                    result['寒燥分析']['主用神'].append('庚金（阳金，泄土之气）')

                # 辅用神：丙火（暖局生土，调和寒湿）、壬水（润土）
                if month_zhi in ['辰', '丑']:  # 湿土
                    if has_gan('丙'):
                        result['寒燥分析']['辅用神'].append('丙火（太阳火，暖局化湿）')
                elif month_zhi in ['戌', '未']:  # 燥土
                    if has_gan('壬'):
                        result['寒燥分析']['辅用神'].append('壬水（阳水，润燥润土）')

                result['调候说明'] = f"土旺局：生于{month_zhi}月四季末，土旺当令，宜疏宜泄"
                result['优先级'] = '一般'
                result['依据'].append(f'土旺局：土{tu_count}个，需木疏之或金泄之')
            else:
                # 一般四季末情况
                result['寒燥分析'] = {
                    '局型': '四季末平和局',
                    '核心原则': '平和调候（根据具体五行偏枯调候）',
                    '病症': f'生于{month_zhi}月四季末，土旺金相',
                    '主用神': [],
                    '辅用神': [],
                    '忌神': []
                }

                # 根据其他五行旺相判断
                if jinshui_count >= 3:
                    result['寒燥分析']['主用神'].append('火（暖局制金水）')
                    result['寒燥分析']['忌神'] = ['金', '水']
                elif muhuo_count >= 3:
                    result['寒燥分析']['主用神'].append('水（润局制木火）')
                    result['寒燥分析']['忌神'] = ['火', '木']
                else:
                    result['寒燥分析']['主用神'].append('根据具体格局取用神')

                result['调候说明'] = f"四季末：生于{month_zhi}月，土旺金相，平和调候"
                result['优先级'] = '一般'
                result['依据'].append(f'四季末：土{tu_count}个，金{wuxing_count["金"]}个，水{wuxing_count["水"]}个，木{wuxing_count["木"]}个，火{wuxing_count["火"]}个')

        # 如果没有特殊寒燥局，但有调候用神，则给出一般性说明
        if '寒燥分析' not in result and result['调候用神']:
            result['调候说明'] = f'根据《穷通宝鉴》调候用神：{", ".join(result["调候用神"])}'

        # 参考《穷通宝鉴》jinbuhuan数据
        if day_month_key in jinbuhuan:
            jin_info = jinbuhuan[day_month_key]
            if '调候：' in jin_info:
                diahou = jin_info.split('调候：')[1].split(' 大运：')[0]
                if not result['依据']:
                    result['依据'].append(f"《穷通宝鉴》调候参考: {diahou}")
                else:
                    result['依据'].append(f"《穷通宝鉴》: {diahou}")

        # ==================== 统计其余十神 ====================
        # 统计原局中各十神出现的次数，排除调候用神
        from ganzhi import gan5
        deity_count = {}

        # 获取调候用神的天干列表（排除下划线）
        tiaohou_gans = set()
        if day_month_key in tiaohous:
            import re
            tiaohou_str = tiaohous[day_month_key]
            matches = re.findall(r'[1-5]_?([甲乙丙丁戊己庚辛壬癸])', tiaohou_str)
            tiaohou_gans = set(matches)

        # 统计天干十神
        for gan in self.gans:
            if not gan:
                continue
            # 获取十神（日主 vs 当前天干）
            deity = ten_deities.get(day_gan, {}).get(gan, '')
            # 只有当十神不为空且该天干不是调候用神时才统计
            if deity:
                if gan not in tiaohou_gans:
                    deity_count[deity] = deity_count.get(deity, 0) + 1

        # 统计地支藏干十神
        for zhi in self.zhis:
            if not zhi:
                continue
            # 获取地支的藏干
            canggan_list = zhi5_list.get(zhi, [])
            for canggan in canggan_list:
                # 获取藏干的十神
                deity = ten_deities.get(day_gan, {}).get(canggan, '')
                # 只有当十神不为空且该藏干不是调候用神时才统计
                if deity:
                    if canggan not in tiaohou_gans:
                        deity_count[deity] = deity_count.get(deity, 0) + 1

        # 十神完整名称映射
        deity_full_names = {
            '比': '比肩',
            '劫': '劫财',
            '食': '食神',
            '伤': '伤官',
            '才': '正财',
            '财': '偏财',
            '杀': '七杀',
            '官': '正官',
            '印': '正印',
            '枭': '偏印'
        }

        # 按次数从多到少排序
        sorted_deities = sorted(deity_count.items(), key=lambda x: -x[1])
        # 转换为完整名称并格式化
        other_deities = [f"{deity_full_names.get(d, d)}({count})" for d, count in sorted_deities]
        result['其余十神'] = other_deities

        return result

    def _analyze_tongguan(self) -> Dict:
        """
        寻通关（第四步：化解内部冲突）

        当命局中出现两种五行激烈冲克时，需要引入"和事佬"：
        - 金木相战：喜水通关（金生水→水生木）
        - 水火相冲：喜木通关（水生木→木生火）
        - 木土相战：喜火通关（木生火→火生土）
        - 土水相战：喜金通关（土生金→金生水）
        - 火金相战：喜土通关（火生土→土生金）
        """
        result = {
            '通关神': [],
            '依据': []
        }

        # 统计五行力量
        from ganzhi import gan5
        wuxing_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        for gan in self.gans:
            wx = gan5.get(gan, '')
            if wx:
                wuxing_count[wx] += 1
        for zhi in self.zhis:
            wx = self.ZHI_WUHANGS.get(zhi, '')
            if wx:
                wuxing_count[wx] += 1

        # 五行相生相克
        sheng = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }
        ke = {
            '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
        }

        # 检查相冲（两方力量都较强）
        threshold = 3  # 至少3个才算较强

        # 金木相战
        if wuxing_count['金'] >= threshold and wuxing_count['木'] >= threshold:
            tong_gan = '水'
            result['通关神'].append(tong_gan)
            result['依据'].append(f'金木相战（金{wuxing_count["金"]}，木{wuxing_count["木"]}），喜水通关：金生水→水生木')

        # 水火相冲
        if wuxing_count['水'] >= threshold and wuxing_count['火'] >= threshold:
            tong_gan = '木'
            result['通关神'].append(tong_gan)
            result['依据'].append(f'水火相冲（水{wuxing_count["水"]}，火{wuxing_count["火"]}），喜木通关：水生木→木生火')

        # 木土相战
        if wuxing_count['木'] >= threshold and wuxing_count['土'] >= threshold:
            tong_gan = '火'
            result['通关神'].append(tong_gan)
            result['依据'].append(f'木土相战（木{wuxing_count["木"]}，土{wuxing_count["土"]}），喜火通关：木生火→火生土')

        # 土水相战
        if wuxing_count['土'] >= threshold and wuxing_count['水'] >= threshold:
            tong_gan = '金'
            result['通关神'].append(tong_gan)
            result['依据'].append(f'土水相战（土{wuxing_count["土"]}，水{wuxing_count["水"]}），喜金通关：土生金→金生水')

        # 火金相战
        if wuxing_count['火'] >= threshold and wuxing_count['金'] >= threshold:
            tong_gan = '土'
            result['通关神'].append(tong_gan)
            result['依据'].append(f'火金相战（火{wuxing_count["火"]}，金{wuxing_count["金"]}），喜土通关：火生土→土生金')

        return result
    
    def _analyze_auxiliary_info(self) -> Dict:
        """
        第五论级: 辅助功能
        
        计算并显示12长生、空亡、纳音、神煞等辅助信息
        """
        result = {
            '十二长生': {},
            '空亡': {},
            '纳音': {},
            '神煞': {}
        }
        
        # 1. 计算十二长生
        # 根据是否有时间柱决定遍历哪些柱子
        if self.has_time_pillar:
            pillars = ['年柱', '月柱', '日柱', '时柱']
        else:
            pillars = ['年柱', '月柱', '日柱']
        
        for i, pillar_name in enumerate(pillars):
            gan = self.gans[i] if i < len(self.gans) else ''
            zhi = self.zhis[i] if i < len(self.zhis) else ''
            
            if not zhi:  # 跳过空的地支
                continue
            
            # 星运（以日主为基准）
            xingyun_status = get_changsheng(self.day_gan, zhi)
            result['十二长生'][pillar_name] = {
                '星运': xingyun_status,
                '自坐': get_changsheng(gan, zhi) if gan else ''
            }
        
        # 2. 计算空亡
        # 优化空亡判定逻辑：先查【年支、日支】确定旬，再看【其余三柱地支】
        # 六十甲子旬空亡：
        # 甲子旬：戌、亥空
        # 甲戌旬：申、酉空
        # 甲申旬：午、未空
        # 甲午旬：辰、巳空
        # 甲辰旬：寅、卯空
        # 甲寅旬：子、丑空

        # 定义各旬及其空亡地支
        xunkong_data = [
            # (旬名, 旬中的所有干支组合, 空亡地支)
            ('甲子旬', ['甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉'], ('戌', '亥')),
            ('甲戌旬', ['甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午', '癸未'], ('申', '酉')),
            ('甲申旬', ['甲申', '乙酉', '丙戌', '丁亥', '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳'], ('午', '未')),
            ('甲午旬', ['甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子', '辛丑', '壬寅', '癸卯'], ('辰', '巳')),
            ('甲辰旬', ['甲辰', '乙巳', '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑'], ('寅', '卯')),
            ('甲寅旬', ['甲寅', '乙卯', '丙辰', '丁巳', '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥'], ('子', '丑'))
        ]

        # 分别判断年柱和日柱所在的旬，以及对应的空亡地支
        year_xun = None
        year_kongwang_zhis = None
        day_xun = None
        day_kongwang_zhis = None

        # 查年柱所在的旬
        year_ganzhi = self.gans[0] + self.zhis[0]
        for xun_name, ganzhi_list, empty_zhis in xunkong_data:
            if year_ganzhi in ganzhi_list:
                year_xun = xun_name
                year_kongwang_zhis = empty_zhis
                break

        # 查日柱所在的旬
        day_ganzhi = self.gans[2] + self.zhis[2]
        for xun_name, ganzhi_list, empty_zhis in xunkong_data:
            if day_ganzhi in ganzhi_list:
                day_xun = xun_name
                day_kongwang_zhis = empty_zhis
                break

        # 判断各柱是否为空亡
        result['空亡'] = {}
        # 根据是否有时间柱决定遍历哪些柱子
        if self.has_time_pillar:
            pillars = ['年柱', '月柱', '日柱', '时柱']
        else:
            pillars = ['年柱', '月柱', '日柱']

        for i, pillar_name in enumerate(pillars):
            pillar_zhi = self.zhis[i] if i < len(self.zhis) else ''
            if not pillar_zhi:  # 跳过空的地支
                continue
            
            is_kong = False
            kong_sources = []
            kong_zhis_list = []

            # 检查是否在年柱确定的旬空亡中
            if year_xun and year_kongwang_zhis:
                if pillar_zhi in year_kongwang_zhis:
                    is_kong = True
                    kong_sources.append('年柱')
                    kong_zhis_list.append(f"{pillar_zhi}({year_xun})")

            # 检查是否在日柱确定的旬空亡中
            if day_xun and day_kongwang_zhis:
                if pillar_zhi in day_kongwang_zhis:
                    is_kong = True
                    kong_sources.append('日柱')
                    kong_zhis_list.append(f"{pillar_zhi}({day_xun})")

            # 设置结果
            if is_kong:
                result['空亡'][pillar_name] = {
                    '空亡': True,
                    '地支': pillar_zhi,
                    '旬来源': '、'.join(kong_sources),
                    '空亡详情': '、'.join(kong_zhis_list)
                }
            else:
                result['空亡'][pillar_name] = {'空亡': False}
        
        # 3. 计算纳音
        for i, pillar_name in enumerate(pillars):
            gan = self.gans[i] if i < len(self.gans) else ''
            zhi = self.zhis[i] if i < len(self.zhis) else ''
            if gan and zhi:
                result['纳音'][pillar_name] = nayins.get((gan, zhi), '未知')
        
        # 4. 计算神煞
        bazi_dict = {
            'year_gan': self.gans[0], 'year_zhi': self.zhis[0],
            'month_gan': self.gans[1], 'month_zhi': self.zhis[1],
            'day_gan': self.gans[2], 'day_zhi': self.zhis[2],
        }
        # 只有有时柱时才添加
        if self.has_time_pillar and len(self.gans) > 3 and len(self.zhis) > 3:
            bazi_dict['time_gan'] = self.gans[3]
            bazi_dict['time_zhi'] = self.zhis[3]
        else:
            bazi_dict['time_gan'] = ''
            bazi_dict['time_zhi'] = ''
        
        shensha_result = self.shensha_calculator.calculate(bazi_dict)
        result['神煞'] = shensha_result
        
        return result
    
    def _analyze_suiyun(self) -> Dict:
        """
        第五论级: 推岁运
        
        分析指定流年及其所属大运对原局的影响
        使用 DaYunLiuNian 正确计算大运
        """
        result = {
            '流年年份': self.liunian_year,
            '流年干支': '',
            '大运干支': '',
            '当前大运': '',
            '大运序号': 0,
            '大运年龄范围': '',
            '起运年龄': '',
            '大运序列': [],
            '原局格局': self.analysis_result.get('格局综合判定', {}).get('主格局', ''),
            '影响分析': ''
        }
        
        if not self.liunian_year or not self.dayun_liunian:
            return result
        
        # 使用 DaYunLiuNian 获取大运信息
        dayuns = self.dayun_liunian.dayuns

        # 生成大运序列
        result['大运序列'] = [dayun['gan_zhi'] for dayun in dayuns]
        
        # 获取起运年龄
        result['起运年龄'] = self.dayun_liunian.qiyun_age

        # 计算流年干支（使用 dayun_liunian.py 中的方法）
        try:
            result['流年干支'] = self.dayun_liunian.get_liunian_ganzhi_by_year(self.liunian_year)
        except Exception as e:
            result['流年干支'] = f'计算失败({e})'

        # 确定流年所属的大运（使用 dayun_liunian.py 中的方法）
        target_dayun = self.dayun_liunian.get_dayun_by_year(self.liunian_year)

        if target_dayun:
            result['大运干支'] = target_dayun['gan_zhi']
            result['当前大运'] = target_dayun['gan_zhi']
            result['大运序号'] = target_dayun['index']
            result['大运年龄范围'] = f"{target_dayun['start_age']}-{target_dayun['end_age']}岁"
        else:
            # 如果找不到，使用默认计算
            result['大运干支'] = ''
            result['当前大运'] = ''
            result['大运序号'] = 0
            result['大运年龄范围'] = '无法确定'
        
        # 分析影响
        liunian_gan = result['流年干支'][0] if result['流年干支'] else ''
        liunian_zhi = result['流年干支'][1] if result['流年干支'] else ''
        dayun_gan = result['大运干支'][0] if result['大运干支'] else ''
        dayun_zhi = result['大运干支'][1] if result['大运干支'] else ''
        
        impact_analysis = []
        
        # 1. 检查岁运伏吟
        # 根据是否有时间柱决定遍历哪些柱子
        if self.has_time_pillar:
            pillars = ['年柱', '月柱', '日柱', '时柱']
        else:
            pillars = ['年柱', '月柱', '日柱']
        
        fuyin_found = []
        
        for i, pillar_name in enumerate(pillars):
            if i < len(self.gans) and i < len(self.zhis):
                if liunian_gan == self.gans[i] and liunian_zhi == self.zhis[i]:
                    fuyin_found.append(f"流年{liunian_gan}{liunian_zhi}与{pillar_name}伏吟")
        
        for i, pillar_name in enumerate(pillars):
            if i < len(self.gans) and i < len(self.zhis):
                if dayun_gan == self.gans[i] and dayun_zhi == self.zhis[i]:
                    fuyin_found.append(f"大运{dayun_gan}{dayun_zhi}与{pillar_name}伏吟")
        
        if liunian_gan == dayun_gan and liunian_zhi == dayun_zhi and liunian_gan:
            fuyin_found.append(f"岁运并临：流年{liunian_gan}{liunian_zhi}与大运相同，伏吟力量最强")
        
        if fuyin_found:
            impact_analysis.extend(fuyin_found)
        
        # 2. 检查岁运反吟（天克地冲）
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        gan_chong_pairs = [('甲', '庚'), ('乙', '辛'), ('壬', '丙'), ('癸', '丁')]
        fanyin_found = []
        
        from ganzhi import gan5
        ke_map = {
            '木': '土', '火': '金', '土': '水', '金': '木', '水': '火'
        }
        
        # 流年反吟
        for i, pillar_name in enumerate(pillars):
            if i >= len(self.zhis) or i >= len(self.gans):
                continue
            is_zhi_chong = any(
                (liunian_zhi == cp[0] and self.zhis[i] == cp[1]) or
                (liunian_zhi == cp[1] and self.zhis[i] == cp[0])
                for cp in chong_pairs
            )
            if is_zhi_chong:
                wuxing1 = gan5.get(liunian_gan, '')
                wuxing2 = gan5.get(self.gans[i], '')
                is_gan_chong = any(
                    (liunian_gan == gcp[0] and self.gans[i] == gcp[1]) or
                    (liunian_gan == gcp[1] and self.gans[i] == gcp[0])
                    for gcp in gan_chong_pairs
                )
                is_gan_ke = wuxing1 and wuxing2 and ke_map.get(wuxing1) == wuxing2
                if is_gan_ke:
                    fanyin_found.append(f"流年{liunian_gan}{liunian_zhi}与{pillar_name}天克地冲")
        
        # 大运反吟
        for i, pillar_name in enumerate(pillars):
            if i >= len(self.zhis) or i >= len(self.gans):
                continue
            is_zhi_chong = any(
                (dayun_zhi == cp[0] and self.zhis[i] == cp[1]) or
                (dayun_zhi == cp[1] and self.zhis[i] == cp[0])
                for cp in chong_pairs
            )
            if is_zhi_chong:
                wuxing1 = gan5.get(dayun_gan, '')
                wuxing2 = gan5.get(self.gans[i], '')
                is_gan_chong = any(
                    (dayun_gan == gcp[0] and self.gans[i] == gcp[1]) or
                    (dayun_gan == gcp[1] and self.gans[i] == gcp[0])
                    for gcp in gan_chong_pairs
                )
                is_gan_ke = wuxing1 and wuxing2 and ke_map.get(wuxing1) == wuxing2
                if is_gan_ke:
                    fanyin_found.append(f"大运{dayun_gan}{dayun_zhi}与{pillar_name}天克地冲")
        
        if fanyin_found:
            impact_analysis.extend(fanyin_found)
        
        # 3. 检查大运流年本身的盖头和截脚
        gaitou_combinations = [
            ('甲', '辰'), ('甲', '戌'), ('乙', '丑'), ('乙', '未'),
            ('丙', '申'), ('丁', '酉'), ('戊', '子'), ('己', '亥'),
            ('庚', '寅'), ('辛', '卯'), ('壬', '午'), ('癸', '巳')
        ]
        jiejiao_combinations = [
            ('甲', '申'), ('乙', '酉'), ('丙', '子'), ('丁', '亥'),
            ('戊', '寅'), ('己', '卯'), ('庚', '午'), ('辛', '巳'),
            ('壬', '辰'), ('癸', '丑'), ('癸', '未'), ('壬', '戌')
        ]
        
        if liunian_gan and liunian_zhi:
            if (liunian_gan, liunian_zhi) in gaitou_combinations:
                impact_analysis.append(f"流年{liunian_gan}{liunian_zhi}为盖头")
            if (liunian_gan, liunian_zhi) in jiejiao_combinations:
                impact_analysis.append(f"流年{liunian_gan}{liunian_zhi}为截脚")
        
        if dayun_gan and dayun_zhi:
            if (dayun_gan, dayun_zhi) in gaitou_combinations:
                impact_analysis.append(f"大运{dayun_gan}{dayun_zhi}为盖头")
            if (dayun_gan, dayun_zhi) in jiejiao_combinations:
                impact_analysis.append(f"大运{dayun_gan}{dayun_zhi}为截脚")
        
        # 4. 检查与原局的合冲
        for gan_pair in gan_hes:
            if gan_pair[0] in [liunian_gan, dayun_gan] and gan_pair[1] in self.gans:
                impact_analysis.append(f"天干相合: {gan_pair[0]}{gan_pair[1]}合")
        
        for zhi_pair in chong_pairs:
            if (zhi_pair[0] in [liunian_zhi, dayun_zhi] and zhi_pair[1] in self.zhis) or \
               (zhi_pair[1] in [liunian_zhi, dayun_zhi] and zhi_pair[0] in self.zhis):
                impact_analysis.append(f"地支相冲: {zhi_pair[0]}{zhi_pair[1]}冲")
        
        # 5. 检查是否引动原局格局
        xi_ji_info = self.analysis_result.get('第五论级_定喜忌', {})
        xi_yong = xi_ji_info.get('喜用神', [])
        ji_shen = xi_ji_info.get('忌神', [])
        
        # 流年、大运天干是否为喜用神
        if liunian_gan in xi_yong:
            impact_analysis.append(f"流年天干{liunian_gan}为喜用神，大吉")
        if dayun_gan in xi_yong:
            impact_analysis.append(f"大运天干{dayun_gan}为喜用神，大吉")
        
        # 流年、大运天干是否为忌神
        if liunian_gan in ji_shen:
            impact_analysis.append(f"流年天干{liunian_gan}为忌神，需谨慎")
        if dayun_gan in ji_shen:
            impact_analysis.append(f"大运天干{dayun_gan}为忌神，需化解")
        
        result['影响分析'] = '; '.join(impact_analysis) if impact_analysis else '无明显影响'
        
        return result
    
    # ==================== 第六论级实现 ====================
    
    def _analyze_sixth_level(self) -> Dict:
        """
        第六论级: 大运流年综合分析
        
        分析流程:
        i. 先分析大运与流年的十二长生、空亡、纳音、神煞信息，给出分析结论
        ii. 将大运天干、流年天干和地支分别代入到年、月、日、时柱天干地支中分析大运、流年、年柱、月柱、日柱、时柱之间的相互影响
        iii. 最后给出大运流年综合总结性分析说明
        
        新增：分析大运流年作用后，对原局五行能量和十神能量的影响
        - 大运地支当做月令2处理
        - 藏干本气中气余气五行能量和十神能量都+2
        """
        result = {
            '大运流年基本信息': {},
            '大运流年特征分析': {},
            '岁运天干分析': {},
            '岁运地支分析': {},
            '岁运特殊格局分析': {},
            '岁运干支分析': {},
            '影响分析': {},
            '综合评语': '',
            '大运流年对原局能量影响': {}
        }
        
        # 获取流年和大运信息
        liunian_info = self.analysis_result.get('第五论级_大运流年', {})
        liunian_gan = liunian_info.get('流年干支', '')[0] if liunian_info.get('流年干支') else ''
        liunian_zhi = liunian_info.get('流年干支', '')[1] if liunian_info.get('流年干支') else ''
        dayun_gan = liunian_info.get('大运干支', '')[0] if liunian_info.get('大运干支') else ''
        dayun_zhi = liunian_info.get('大运干支', '')[1] if liunian_info.get('大运干支') else ''
        
        # 设置大运流年属性，供 _calculate_wuxing_shishen_scores 使用
        if self.dayun_liunian:
            self.dayun_liunian.current_dayun_gan = dayun_gan
            self.dayun_liunian.current_dayun_zhi = dayun_zhi
            self.dayun_liunian.current_liunian_gan = liunian_gan
            self.dayun_liunian.current_liunian_zhi = liunian_zhi
        
        # i. 基本信息与特征分析
        # 计算大运列表（包含时间范围）
        dayun_list = []
        if self.dayun_liunian:
            for dayun in self.dayun_liunian.dayuns:
                # 使用start_date获取精确的起运年份
                start_date = dayun.get('start_date', '')
                if start_date:
                    from datetime import datetime
                    try:
                        start_year = datetime.strptime(start_date, "%Y-%m-%d").year
                        end_year = start_year + 10
                        dayun_list.append(f"{dayun['gan_zhi']}（{start_year}~{end_year}）")
                    except Exception:
                        # 如果解析失败，使用简单计算
                        birth_year = self._get_birth_year()
                        qiyun_age = self.dayun_liunian.qiyun_age if hasattr(self.dayun_liunian, 'qiyun_age') else 3
                        start_year = birth_year + qiyun_age + (dayun['index'] - 1) * 10
                        end_year = start_year + 10
                        dayun_list.append(f"{dayun['gan_zhi']}（{start_year}~{end_year}）")
                else:
                    # 如果没有start_date，使用简单计算
                    birth_year = self._get_birth_year()
                    qiyun_age = self.dayun_liunian.qiyun_age if hasattr(self.dayun_liunian, 'qiyun_age') else 3
                    start_year = birth_year + qiyun_age + (dayun['index'] - 1) * 10
                    end_year = start_year + 10
                    dayun_list.append(f"{dayun['gan_zhi']}（{start_year}~{end_year}）")
        
        result['大运流年基本信息'] = {
            '流年干支': liunian_info.get('流年干支', ''),
            '流年年份': liunian_info.get('流年年份', ''),
            '大运干支': liunian_info.get('大运干支', ''),
            '大运序号': liunian_info.get('大运序号', 0),
            '大运年龄范围': liunian_info.get('大运年龄范围', ''),
            '大运列表': dayun_list
        }
        
        # i. 分析大运流年的十二长生、空亡、纳音、神煞
        result['大运流年特征分析'] = self._analyze_suiyuan_features(
            dayun_gan, dayun_zhi, liunian_gan, liunian_zhi
        )
        
        # ii. 将大运流年天干地支代入原局分析相互影响
        # 1. 岁运天干分析（按第三论级规则）
        result['岁运天干分析'] = self._analyze_suiyuan_gan_relations(
            dayun_gan, liunian_gan
        )
        
        # 2. 岁运地支分析（按第二论级规则）
        result['岁运地支分析'] = self._analyze_suiyuan_zhi_relations(
            dayun_zhi, liunian_zhi
        )
        
        # 3. 岁运干支分析（按第四论级规则）
        result['岁运干支分析'] = self._analyze_suiyuan_ganzhi_relations(
            dayun_gan, dayun_zhi, liunian_gan, liunian_zhi
        )
        
        # 5. 天克地冲、岁运并临、伏吟分析
        result['特殊流年分析'] = self._analyze_special_liunian_patterns(
            dayun_gan, dayun_zhi, liunian_gan, liunian_zhi
        )
        
        # iii. 综合影响分析
        result['影响分析'] = self._analyze_suiyuan_impact(
            self.analysis_result,
            result,
            dayun_gan, dayun_zhi, liunian_gan, liunian_zhi
        )
        
        # iv. 分析大运流年对原局五行和十神能量的影响
        # 使用统一的评分标准 _calculate_wuxing_shishen_scores(include_dayun_liunian=True)
        # 注意：需要先临时存储第六论级结果，以便 _calculate_wuxing_shishen_scores 能获取到
        self.analysis_result['第六论级'] = result
        result['大运流年对原局能量影响'] = self._calculate_energy_impact_with_unified_scoring(result)
        
        # v. 分析历史大运对原局能量影响
        result['历史大运对原局能量影响'] = self._calculate_historical_dayun_impact(liunian_info.get('流年年份', 0))
        
        # vi. 生成综合评语
        result['综合评语'] = self._generate_sixth_level_summary(result)
        
        return result
    
    def _analyze_suiyuan_features(self, dayun_gan: str, dayun_zhi: str,
                                   liunian_gan: str, liunian_zhi: str) -> Dict:
        """
        i. 分析大运与流年的十二长生、空亡、纳音、神煞信息

        参数:
            dayun_gan: 大运天干
            dayun_zhi: 大运地支
            liunian_gan: 流年天干
            liunian_zhi: 流年地支
        """
        from changsheng import get_changsheng, CHANGSHENG_DESC
        from shensha_database import ShenShaCalculator

        result = {
            '大运': {
                '十二长生': {},
                '空亡': False,
                '纳音': '',
                '神煞': []
            },
            '流年': {
                '十二长生': {},
                '空亡': False,
                '纳音': '',
                '神煞': []
            },
            '特征总结': []
        }
        
        # 初始化 day_gan_zhi 变量，避免未定义错误
        day_gan_zhi = ''

        # 准备八字字典（用于神煞计算）
        # 大运作为年柱，流年作为月柱的模拟八字
        bazi_dict = {
            'year_gan': dayun_gan if dayun_gan else self.gans[0],
            'year_zhi': dayun_zhi if dayun_zhi else self.zhis[0],
            'month_gan': liunian_gan if liunian_gan else self.gans[1],
            'month_zhi': liunian_zhi if liunian_zhi else self.zhis[1],
            'day_gan': self.day_gan,
            'day_zhi': self.zhis[2],
            'time_gan': self.gans[3] if self.has_time_pillar and len(self.gans) > 3 else '',
            'time_zhi': self.zhis[3] if self.has_time_pillar and len(self.zhis) > 3 else ''
        }

        # 分析大运
        if dayun_gan and dayun_zhi:
            # 十二长生分析
            if self.day_gan:
                # 星运：日主天干 → 大运地支
                changsheng_xingyun = get_changsheng(self.day_gan, dayun_zhi)
                # 自坐：大运天干 → 大运地支
                changsheng_zizuo = get_changsheng(dayun_gan, dayun_zhi)
                if changsheng_xingyun or changsheng_zizuo:
                    result['大运']['十二长生'] = {
                        '星运': changsheng_xingyun,
                        '星运解释': CHANGSHENG_DESC.get(changsheng_xingyun, ''),
                        '自坐': changsheng_zizuo,
                        '自坐解释': CHANGSHENG_DESC.get(changsheng_zizuo, '')
                    }

            # 空亡判定
            day_gan_zhi = self.day_gan + self.zhis[2] if self.day_gan and self.zhis[2] else ''
            if day_gan_zhi and empties and day_gan_zhi in empties:
                kongwang_zhis = empties[day_gan_zhi]
                if dayun_zhi in kongwang_zhis:
                    result['大运']['空亡'] = True
                    result['特征总结'].append(f"大运地支{dayun_zhi}落空亡")

            # 纳音
            dayun_ganzhi = dayun_gan + dayun_zhi
            if nayins and dayun_ganzhi in nayins:
                result['大运']['纳音'] = nayins[dayun_ganzhi]

            # 神煞 - 使用 ShenShaCalculator.calculate_dayun_liunian 计算大运神煞
            try:
                calculator = ShenShaCalculator()
                # 准备原局八字字典
                original_bazi = {
                    'year_gan': self.gans[0],
                    'year_zhi': self.zhis[0],
                    'month_gan': self.gans[1],
                    'month_zhi': self.zhis[1],
                    'day_gan': self.day_gan,
                    'day_zhi': self.zhis[2],
                    'time_gan': self.gans[3] if self.has_time_pillar and len(self.gans) > 3 else '',
                    'time_zhi': self.zhis[3] if self.has_time_pillar and len(self.zhis) > 3 else ''
                }
                # 使用大运流年神煞计算方法
                result['大运']['神煞'] = calculator.calculate_dayun_liunian(
                    dayun_gan, dayun_zhi, 'dayun', original_bazi, self.is_male
                )
                if result['大运']['神煞']:
                    result['特征总结'].append(f"大运带神煞: {', '.join(result['大运']['神煞'])}")
                # 调试输出
                # print(f"[调试] 大运神煞计算: 原局={original_bazi}, 大运={dayun_gan}{dayun_zhi}, 神煞={result['大运']['神煞']}")
            except Exception as e:
                result['特征总结'].append(f"大运神煞计算异常: {str(e)}")
                import traceback
                result['特征总结'].append(f"异常详情: {traceback.format_exc()}")

        # 分析流年
        if liunian_gan and liunian_zhi:
            # 十二长生分析
            if self.day_gan:
                # 星运：日主天干 → 流年地支
                changsheng_xingyun = get_changsheng(self.day_gan, liunian_zhi)
                # 自坐：流年天干 → 流年地支
                changsheng_zizuo = get_changsheng(liunian_gan, liunian_zhi)
                if changsheng_xingyun or changsheng_zizuo:
                    result['流年']['十二长生'] = {
                        '星运': changsheng_xingyun,
                        '星运解释': CHANGSHENG_DESC.get(changsheng_xingyun, ''),
                        '自坐': changsheng_zizuo,
                        '自坐解释': CHANGSHENG_DESC.get(changsheng_zizuo, '')
                    }

            # 空亡判定
            if day_gan_zhi and empties and day_gan_zhi in empties:
                kongwang_zhis = empties[day_gan_zhi]
                if liunian_zhi in kongwang_zhis:
                    result['流年']['空亡'] = True
                    result['特征总结'].append(f"流年地支{liunian_zhi}落空亡")

            # 纳音
            liunian_ganzhi = liunian_gan + liunian_zhi
            if nayins and liunian_ganzhi in nayins:
                result['流年']['纳音'] = nayins[liunian_ganzhi]

            # 神煞 - 使用 ShenShaCalculator.calculate_dayun_liunian 计算流年神煞
            try:
                calculator = ShenShaCalculator()
                # 准备原局八字字典
                original_bazi = {
                    'year_gan': self.gans[0],
                    'year_zhi': self.zhis[0],
                    'month_gan': self.gans[1],
                    'month_zhi': self.zhis[1],
                    'day_gan': self.day_gan,
                    'day_zhi': self.zhis[2],
                    'time_gan': self.gans[3] if self.has_time_pillar and len(self.gans) > 3 else '',
                    'time_zhi': self.zhis[3] if self.has_time_pillar and len(self.zhis) > 3 else ''
                }
                # 使用大运流年神煞计算方法
                result['流年']['神煞'] = calculator.calculate_dayun_liunian(
                    liunian_gan, liunian_zhi, 'liunian', original_bazi, self.is_male
                )
                if result['流年']['神煞']:
                    result['特征总结'].append(f"流年带神煞: {', '.join(result['流年']['神煞'])}")
                # 调试输出
                # print(f"[调试] 流年神煞计算: 原局={original_bazi}, 流年={liunian_gan}{liunian_zhi}, 神煞={result['流年']['神煞']}")
            except Exception as e:
                result['特征总结'].append(f"流年神煞计算异常: {str(e)}")
                import traceback
                result['特征总结'].append(f"异常详情: {traceback.format_exc()}")

        # 生成特征总结
        if not result['特征总结']:
            result['特征总结'].append('大运流年无明显特殊特征')

        return result
    
    def _analyze_suiyuan_gan_relations(self, dayun_gan: str, liunian_gan: str) -> Dict:
        """
        ii.1. 岁运天干分析命名（按第三论级规则）
        
        将大运天干、流年天干分别代入到年、月、日、时柱天干中分析
        """
        result = {
            '大运天干影响': {},
            '流年天干影响': {},
            '大运流年天干关系': {}
        }
        
        # 根据是否有时间柱决定遍历哪些柱子
        if self.has_time_pillar:
            pillar_names = ['年柱', '月柱', '日柱', '时柱']
        else:
            pillar_names = ['年柱', '月柱', '日柱']
        
        # 大运天干对各柱的影响
        for i, pillar_name in enumerate(pillar_names):
            if i < len(self.gans):
                impacts = self._analyze_gan_impact_detailed(
                    dayun_gan, self.gans[i], f'大运天干', pillar_name
                )
                if impacts:
                    result['大运天干影响'][pillar_name] = impacts
        
        # 流年天干对各柱的影响
        for i, pillar_name in enumerate(pillar_names):
            if i < len(self.gans):
                impacts = self._analyze_gan_impact_detailed(
                    liunian_gan, self.gans[i], f'流年天干', pillar_name
                )
                if impacts:
                    result['流年天干影响'][pillar_name] = impacts
        
        # 大运与流年天干之间的关系
        if dayun_gan and liunian_gan:
            impacts_dy_ll = self._analyze_gan_impact_detailed(
                dayun_gan, liunian_gan, '大运天干', '流年天干'
            )
            if impacts_dy_ll:
                result['大运流年天干关系']['大运对流年'] = impacts_dy_ll
        
        return result
    
    def _analyze_gan_impact_detailed(self, source_gan: str, target_gan: str,
                                     source_type: str, target_name: str) -> List[Dict]:
        """
        详细分析天干影响（按第三论级规则）
        
        分析项目:
        1. 天干五合
        2. 化气判定
        3. 天干相冲
        4. 天干相克
        """
        impacts = []
        
        if not source_gan or not target_gan:
            return impacts
        
        # 1. 天干五合
        for gan_pair in gan_hes:
            if source_gan == gan_pair[0] and target_gan == gan_pair[1]:
                impacts.append({
                    '类型': '天干五合',
                    '描述': f"{source_gan}{target_gan}合"
                })
            elif source_gan == gan_pair[1] and target_gan == gan_pair[0]:
                impacts.append({
                    '类型': '天干五合',
                    '描述': f"{target_gan}{source_gan}合"
                })
        
        # 2. 化气判定（基于第三论级规则）
        for he, hua_info in self.GAN_HE_HUA.items():
            if (source_gan == he[0] and target_gan == he[1]) or \
               (source_gan == he[1] and target_gan == he[0]):
                if self.month_zhi in hua_info['条件']['月令']:
                    impacts.append({
                        '类型': '化气判定',
                        '描述': f"{he[0]}{he[1]}化{hua_info['化']}"
                    })
                    break
        
        # 3. 天干相冲（只存在甲庚冲、乙辛冲、丙壬冲、丁癸冲）
        gan_chong_pairs = [('甲', '庚'), ('乙', '辛'), ('丙', '壬'), ('丁', '癸')]
        for gan_pair in gan_chong_pairs:
            if (source_gan == gan_pair[0] and target_gan == gan_pair[1]) or \
               (source_gan == gan_pair[1] and target_gan == gan_pair[0]):
                impacts.append({
                    '类型': '天干相冲',
                    '描述': f"{gan_pair[0]}{gan_pair[1]}冲"
                })
        
        # 4. 天干相克（同性相克，异性不相克）
        # 阳干（甲丙戊庚壬），阴干（乙丁己辛癸）
        yang_gan = ['甲', '丙', '戊', '庚', '壬']
        yin_gan = ['乙', '丁', '己', '辛', '癸']
        
        # 判断阴阳属性
        source_yang = source_gan in yang_gan
        target_yang = target_gan in yang_gan
        
        # 只同性才相克，检查双向关系
        if source_yang == target_yang:
            # 木克土：阳木（甲）克阳土（戊），阴木（乙）克阴土（己）
            if (source_gan == '甲' and target_gan == '戊') or (source_gan == '戊' and target_gan == '甲'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '甲戊克'
                })
            elif (source_gan == '乙' and target_gan == '己') or (source_gan == '己' and target_gan == '乙'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '乙己克'
                })
            # 火克金：阳火（丙）克阳金（庚），阴火（丁）克阴金（辛）
            elif (source_gan == '丙' and target_gan == '庚') or (source_gan == '庚' and target_gan == '丙'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '丙庚克'
                })
            elif (source_gan == '丁' and target_gan == '辛') or (source_gan == '辛' and target_gan == '丁'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '丁辛克'
                })
            # 土克水：阳土（戊）克阳水（壬），阴土（己）克阴水（癸）
            elif (source_gan == '戊' and target_gan == '壬') or (source_gan == '壬' and target_gan == '戊'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '戊壬克'
                })
            elif (source_gan == '己' and target_gan == '癸') or (source_gan == '癸' and target_gan == '己'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '己癸克'
                })
            # 金克木：阳金（庚）克阳木（甲），阴金（辛）克阴木（乙）
            elif (source_gan == '庚' and target_gan == '甲') or (source_gan == '甲' and target_gan == '庚'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '庚甲克'
                })
            elif (source_gan == '辛' and target_gan == '乙') or (source_gan == '乙' and target_gan == '辛'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '辛乙克'
                })
            # 水克火：阳水（壬）克阳火（丙），阴水（癸）克阴火（丁）
            elif (source_gan == '壬' and target_gan == '丙') or (source_gan == '丙' and target_gan == '壬'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '壬丙克'
                })
            elif (source_gan == '癸' and target_gan == '丁') or (source_gan == '丁' and target_gan == '癸'):
                impacts.append({
                    '类型': '天干相克',
                    '描述': '癸丁克'
                })
        
        return impacts
    
    def _analyze_suiyuan_zhi_relations(self, dayun_zhi: str, liunian_zhi: str) -> Dict:
        """
        ii.2. 岁运地支分析命名（按第二论级规则）
        
        将大运地支、流年地支分别代入到年、月、日、时柱地支中分析
        """
        result = {
            '大运地支影响': {},
            '流年地支影响': {},
            '大运流年地支关系': {}
        }
        
        # 根据是否有时间柱决定遍历哪些柱子
        if self.has_time_pillar:
            pillar_names = ['年柱', '月柱', '日柱', '时柱']
        else:
            pillar_names = ['年柱', '月柱', '日柱']
        
        # 大运地支对各柱的影响
        for i, pillar_name in enumerate(pillar_names):
            if i < len(self.zhis):
                impacts = self._analyze_zhi_impact_detailed(
                    dayun_zhi, self.zhis[i], f'大运地支', pillar_name
                )
                if impacts:
                    result['大运地支影响'][pillar_name] = impacts
        
        # 流年地支对各柱的影响
        for i, pillar_name in enumerate(pillar_names):
            if i < len(self.zhis):
                impacts = self._analyze_zhi_impact_detailed(
                    liunian_zhi, self.zhis[i], f'流年地支', pillar_name
                )
                if impacts:
                    result['流年地支影响'][pillar_name] = impacts
        
        # 大运与流年地支之间的关系
        if dayun_zhi and liunian_zhi:
            impacts_dy_ll = self._analyze_zhi_impact_detailed(
                dayun_zhi, liunian_zhi, '大运地支', '流年地支'
            )
            if impacts_dy_ll:
                result['大运流年地支关系']['大运对流年'] = impacts_dy_ll
        
        return result
    
    def _analyze_zhi_impact_detailed(self, source_zhi: str, target_zhi: str,
                                     source_type: str, target_name: str) -> List[Dict]:
        """
        详细分析地支影响（按第二论级规则）

        分析项目:
        1. 三会
        2. 拱会
        3. 三合
        4. 半合
        5. 拱合
        6. 六合
        7. 六破
        8. 六害
        9. 三刑
        10. 六冲
        11. 自刑
        12. 地支暗合
        """
        impacts = []
        
        if not source_zhi or not target_zhi:
            return impacts
        
        # 1. 三会 & 检查是否形成完整三会（用于跳过半会、拱会）
        sanhui_sets = {
            '寅卯辰': ['寅', '卯', '辰'],
            '巳午未': ['巳', '午', '未'],
            '申酉戌': ['申', '酉', '戌'],
            '亥子丑': ['亥', '子', '丑']
        }
        
        formed_sanhui = None  # 记录是否形成完整三会
        for sanhui_name, sanhui_zhis in sanhui_sets.items():
            if source_zhi in sanhui_zhis and target_zhi in sanhui_zhis:
                if source_zhi != target_zhi:
                    # 检查是否形成完整三会（使用所有有效的地支）
                    zhis_in_set = [z for z in self.zhis if z] + [source_zhi, target_zhi]
                    complete = all(z in zhis_in_set for z in sanhui_zhis)
                    if complete:
                        impacts.append({
                            '类型': '三会',
                            '描述': f"形成{sanhui_name}"
                        })
                        formed_sanhui = sanhui_name  # 记录形成的三会局
        
        # 2. 拱会：寅辰拱会卯木、巳未拱会午火、申戌拱会酉金、亥丑拱会子水
        # 如果已形成完整三会局，则不再分析对应的拱会
        gonghui_pairs = [
            (('寅', '辰'), '卯', '木', '寅卯辰'),
            (('巳', '未'), '午', '火', '巳午未'),
            (('申', '戌'), '酉', '金', '申酉戌'),
            (('亥', '丑'), '子', '水', '亥子丑')
        ]
        for (z1, z2), gong_zhi, wuxing, sanhui_key in gonghui_pairs:
            # 跳过已形成完整三会局的拱会
            if formed_sanhui == sanhui_key:
                continue
            if (source_zhi == z1 and target_zhi == z2) or (source_zhi == z2 and target_zhi == z1):
                impacts.append({
                    '类型': '拱会',
                    '描述': f"{z1}{z2}拱会{gong_zhi}{wuxing}"
                })
        
        # 3. 三合 & 检查是否形成完整三合（用于跳过半合、拱合）
        sanhe_sets = {
            '申子辰': ['申', '子', '辰'],
            '亥卯未': ['亥', '卯', '未'],
            '寅午戌': ['寅', '午', '戌'],
            '巳酉丑': ['巳', '酉', '丑']
        }

        formed_sanhe = None  # 记录是否形成完整三合
        for sanhe_name, sanhe_zhis in sanhe_sets.items():
            if source_zhi in sanhe_zhis and target_zhi in sanhe_zhis:
                if source_zhi != target_zhi:
                    # 检查是否形成完整三合（使用所有有效的地支）
                    zhis_in_set = [z for z in self.zhis if z] + [source_zhi, target_zhi]
                    complete = all(z in zhis_in_set for z in sanhe_zhis)
                    if complete:
                        impacts.append({
                            '类型': '三合',
                            '描述': f"形成{sanhe_name}"
                        })
                        formed_sanhe = sanhe_name  # 记录形成的三合局

        # 4. 半合：亥卯/卯未半合木、寅午/午戌半合火、巳酉/酉丑半合金、申子/子辰半合水
        # 如果已形成完整三合局，则不再分析对应的半合
        banhe_pairs = [
            (('亥', '卯'), '木', '亥卯未'), (('卯', '未'), '木', '亥卯未'),
            (('寅', '午'), '火', '寅午戌'), (('午', '戌'), '火', '寅午戌'),
            (('巳', '酉'), '金', '巳酉丑'), (('酉', '丑'), '金', '巳酉丑'),
            (('申', '子'), '水', '申子辰'), (('子', '辰'), '水', '申子辰')
        ]
        for (z1, z2), wuxing, sanhe_key in banhe_pairs:
            # 跳过已形成完整三合局的半合
            if formed_sanhe == sanhe_key:
                continue
            if (source_zhi == z1 and target_zhi == z2) or (source_zhi == z2 and target_zhi == z1):
                impacts.append({
                    '类型': '半合',
                    '描述': f"{z1}{z2}半合{wuxing}"
                })
        
        # 5. 拱合：亥未拱合卯(木)、寅戌拱合午(火)、巳丑拱合酉(金)、申辰拱合子(水)
        # 如果已形成完整三合局，则不再分析对应的拱合
        gonghe_pairs = [
            (('亥', '未'), '卯', '木', '亥卯未'),
            (('寅', '戌'), '午', '火', '寅午戌'),
            (('巳', '丑'), '酉', '金', '巳酉丑'),
            (('申', '辰'), '子', '水', '申子辰')
        ]
        for (z1, z2), gong_zhi, wuxing, sanhe_key in gonghe_pairs:
            # 跳过已形成完整三合局的拱合
            if formed_sanhe == sanhe_key:
                continue
            if (source_zhi == z1 and target_zhi == z2) or (source_zhi == z2 and target_zhi == z1):
                impacts.append({
                    '类型': '拱合',
                    '描述': f"{z1}{z2}拱合{gong_zhi}({wuxing})"
                })

        # 6. 六合（标准顺序：子丑、寅亥、卯戌、辰酉、巳申、午未）
        liuhe_pairs = [('子', '丑', '土'), ('寅', '亥', '木'), ('卯', '戌', '火'),
                       ('辰', '酉', '金'), ('巳', '申', '水'), ('午', '未', '土')]
        for z1, z2, wuxing in liuhe_pairs:
            if (source_zhi, target_zhi) == (z1, z2) or (target_zhi, source_zhi) == (z1, z2):
                impacts.append({
                    '类型': '六合',
                    '描述': f"{z1}{z2}合({wuxing})"
                })

        # 7. 六破（标准顺序：子酉、寅亥、卯午、辰丑、巳申、未戌）
        lipo_pairs = [
            ('子', '酉'), ('寅', '亥'), ('卯', '午'), ('辰', '丑'), ('巳', '申'), ('未', '戌')
        ]
        for po_pair in lipo_pairs:
            if (source_zhi, target_zhi) == po_pair or (target_zhi, source_zhi) == po_pair:
                impacts.append({
                    '类型': '六破',
                    '描述': f"{po_pair[0]}{po_pair[1]}破"
                })

        # 8. 六害（标准顺序：子未、丑午、寅巳、申亥、卯辰、酉戌）
        hai_pairs = [
            ('子', '未'), ('丑', '午'), ('寅', '巳'), ('申', '亥'), ('卯', '辰'), ('酉', '戌')
        ]
        for hai_pair in hai_pairs:
            if (source_zhi, target_zhi) == hai_pair or (target_zhi, source_zhi) == hai_pair:
                impacts.append({
                    '类型': '六害',
                    '描述': f"{hai_pair[0]}{hai_pair[1]}害"
                })

        # 9. 三刑 - 打印具体组合（如丑未刑，而非丑戌未刑）
        # 无恩之刑：寅、巳、申
        yin_si_shen = ['寅', '巳', '申']
        if source_zhi in yin_si_shen and target_zhi in yin_si_shen and source_zhi != target_zhi:
            impacts.append({
                '类型': '三刑',
                '描述': f"{source_zhi}{target_zhi}刑"
            })
        
        # 恃势之刑：丑、戌、未
        chou_xu_wei = ['丑', '戌', '未']
        if source_zhi in chou_xu_wei and target_zhi in chou_xu_wei and source_zhi != target_zhi:
            impacts.append({
                '类型': '三刑',
                '描述': f"{source_zhi}{target_zhi}刑"
            })

        # 10. 六冲（标准顺序：子午、丑未、寅申、卯酉、辰戌、巳亥）
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        for chong_pair in chong_pairs:
            if (source_zhi, target_zhi) == chong_pair or (target_zhi, source_zhi) == chong_pair:
                impacts.append({
                    '类型': '六冲',
                    '描述': f"{chong_pair[0]}{chong_pair[1]}冲"
                })

        # 11. 自刑（打印形式：午午自刑）
        zixing_pairs = [('辰', '辰'), ('午', '午'), ('酉', '酉'), ('亥', '亥')]
        for zx_pair in zixing_pairs:
            if source_zhi == zx_pair[0] and target_zhi == zx_pair[1]:
                impacts.append({
                    '类型': '自刑',
                    '描述': f"{source_zhi}{target_zhi}自刑"
                })
        
        # 13. 地支暗合（按原局定义）
        # 寅丑暗合：寅中甲木与丑中己土相合（甲己合）
        # 亥午暗合：亥中壬水与午中丁火相合（壬丁合）
        # 卯申暗合：卯中乙木与申中庚金相合（乙庚合）
        # 巳酉暗合：巳中丙火与酉中辛金相合（丙辛合）
        # 子戌暗合：子中癸水与戌中戊土相合（戊癸合）
        # 子巳暗合：子中癸水与巳中戊土相合（戊癸合）
        # 寅午暗合：寅中甲木与午中己土相合（甲己合）
        
        anhe_pairs = [
            ('寅', '丑', '甲己合'),
            ('亥', '午', '壬丁合'),
            ('卯', '申', '乙庚合'),
            ('巳', '酉', '丙辛合'),
            ('子', '戌', '戊癸合'),
            ('子', '巳', '戊癸合'),
            ('寅', '午', '甲己合')
        ]
        
        for anhe_pair in anhe_pairs:
            z1, z2, tianhe = anhe_pair
            if (source_zhi, target_zhi) == (z1, z2) or (target_zhi, source_zhi) == (z1, z2):
                impacts.append({
                    '类型': '地支暗合',
                    '描述': f"{z1}{z2}暗合({tianhe})"
                })
        
        return impacts
    
    def _analyze_suiyuan_ganzhi_relations(self, dayun_gan: str, dayun_zhi: str,
                                         liunian_gan: str, liunian_zhi: str) -> Dict:
        """
        ii.4. 岁运干支分析命名（按第四论级_天干地支的关系规则）
        
        分析项目:
        1. 伏吟
        2. 反吟
        3. 盖头
        4. 截脚
        """
        result = {
            '大运干支关系': {},
            '流年干支关系': {},
            '岁运原局干支关系': {}
        }
        
        # 根据是否有时间柱决定遍历哪些柱子
        if self.has_time_pillar:
            pillar_names = ['年柱', '月柱', '日柱', '时柱']
        else:
            pillar_names = ['年柱', '月柱', '日柱']
        
        # 1-4. 分析大运本身的干支关系
        if dayun_gan and dayun_zhi:
            dayun_rels = self._analyze_single_ganzhi_relations(
                dayun_gan, dayun_zhi, self.gans, self.zhis, '大运'
            )
            result['大运干支关系'] = dayun_rels
        
        # 1-4. 分析流年本身的干支关系
        if liunian_gan and liunian_zhi:
            liunian_rels = self._analyze_single_ganzhi_relations(
                liunian_gan, liunian_zhi, self.gans, self.zhis, '流年'
            )
            result['流年干支关系'] = liunian_rels
        
        # 分析岁运与原局的干支关系
        for i, pillar_name in enumerate(pillar_names):
            if i >= len(self.gans) or i >= len(self.zhis):
                continue
            # 大运与该柱的关系
            if dayun_gan and dayun_zhi:
                dy_rel = self._analyze_ganzhi_pair_relations(
                    dayun_gan, dayun_zhi, self.gans[i], self.zhis[i], f'大运', pillar_name
                )
                if dy_rel:
                    result['岁运原局干支关系'][f'大运与{pillar_name}'] = dy_rel
            
            # 流年与该柱的关系
            if liunian_gan and liunian_zhi:
                ll_rel = self._analyze_ganzhi_pair_relations(
                    liunian_gan, liunian_zhi, self.gans[i], self.zhis[i], f'流年', pillar_name
                )
                if ll_rel:
                    result['岁运原局干支关系'][f'流年与{pillar_name}'] = ll_rel
        
        return result
    
    def _analyze_special_liunian_patterns(self, dayun_gan: str, dayun_zhi: str,
                                         liunian_gan: str, liunian_zhi: str) -> Dict:
        """
        分析特殊流年格局：天克地冲、岁运并临、伏吟
        
        判断标准：
        - 天克地冲：流年干支与原局某柱同时满足天干相克、地支相冲
        - 岁运并临：流年干支与大运干支完全相同
        - 伏吟：流年干支与原局某柱完全相同
        
        参数:
            dayun_gan: 大运天干
            dayun_zhi: 大运地支
            liunian_gan: 流年天干
            liunian_zhi: 流年地支
            
        返回:
            {
                '流年天克地冲': [{'柱位': '年柱', '原局干支': '甲子', '流年干支': '庚午', '说明': '...'}, ...],
                '岁运并临': {'发生': True/False, '干支': '甲子', '说明': '...'},
                '流年伏吟': [{'柱位': '年柱', '干支': '甲子'}, ...],
                '大运伏吟': [{'柱位': '年柱', '干支': '甲子'}, ...],
                '岁运伏吟': {'发生': True/False, '说明': '...'}
            }
        """
        # 天干相克关系 (key克value)
        GAN_KE = {
            '甲': '戊', '乙': '己', '丙': '庚', '丁': '辛', '戊': '壬',
            '己': '癸', '庚': '甲', '辛': '乙', '壬': '丙', '癸': '丁'
        }
        
        # 地支六冲关系
        ZHI_CHONG = {
            '子': '午', '午': '子', '丑': '未', '未': '丑',
            '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'
        }
        
        result = {
            '流年天克地冲': [],
            '岁运并临': {'发生': False, '干支': '', '说明': ''},
            '流年伏吟': [],
            '大运伏吟': [],
            '岁运伏吟': {'发生': False, '说明': ''}
        }
        
        # 原局四柱（从self.gans和self.zhis列表获取）
        yuanju_pillars = [
            (0, '年柱'),
            (1, '月柱'),
            (2, '日柱'),
            (3, '时柱')
        ]
        
        # ========== 1. 判断流年天克地冲 ==========
        for idx, pillar_name in yuanju_pillars:
            # 检查索引是否有效
            if idx >= len(self.gans) or idx >= len(self.zhis):
                continue
                
            yuanju_gan = self.gans[idx]
            yuanju_zhi = self.zhis[idx]
            
            # 跳过空柱
            if not yuanju_gan or not yuanju_zhi:
                continue
            
            # 判断天干是否相克（双向检查）
            gan_ke = False
            if GAN_KE.get(liunian_gan) == yuanju_gan or GAN_KE.get(yuanju_gan) == liunian_gan:
                gan_ke = True
            
            # 判断地支是否相冲
            zhi_chong = ZHI_CHONG.get(liunian_zhi) == yuanju_zhi
            
            # 必须同时满足天干相克和地支相冲
            if gan_ke and zhi_chong:
                result['流年天克地冲'].append({
                    '柱位': pillar_name,
                    '原局干支': f"{yuanju_gan}{yuanju_zhi}",
                    '流年干支': f"{liunian_gan}{liunian_zhi}",
                    '说明': f"流年{liunian_gan}{liunian_zhi}与原局{pillar_name}{yuanju_gan}{yuanju_zhi}构成天克地冲"
                })
        
        # ========== 2. 判断岁运并临 ==========
        if liunian_gan == dayun_gan and liunian_zhi == dayun_zhi:
            result['岁运并临'] = {
                '发生': True,
                '干支': f"{liunian_gan}{liunian_zhi}",
                '说明': f"流年{liunian_gan}{liunian_zhi}与大运{dayun_gan}{dayun_zhi}干支完全相同，构成岁运并临"
            }
        
        # ========== 3. 判断流年伏吟 ==========
        for idx, pillar_name in yuanju_pillars:
            # 检查索引是否有效
            if idx >= len(self.gans) or idx >= len(self.zhis):
                continue
                
            yuanju_gan = self.gans[idx]
            yuanju_zhi = self.zhis[idx]
            
            if not yuanju_gan or not yuanju_zhi:
                continue
            
            # 伏吟：干支完全相同
            if liunian_gan == yuanju_gan and liunian_zhi == yuanju_zhi:
                result['流年伏吟'].append({
                    '柱位': pillar_name,
                    '干支': f"{liunian_gan}{liunian_zhi}"
                })
        
        # ========== 4. 判断大运伏吟 ==========
        for idx, pillar_name in yuanju_pillars:
            # 检查索引是否有效
            if idx >= len(self.gans) or idx >= len(self.zhis):
                continue
                
            yuanju_gan = self.gans[idx]
            yuanju_zhi = self.zhis[idx]
            
            if not yuanju_gan or not yuanju_zhi:
                continue
            
            # 伏吟：干支完全相同
            if dayun_gan == yuanju_gan and dayun_zhi == yuanju_zhi:
                result['大运伏吟'].append({
                    '柱位': pillar_name,
                    '干支': f"{dayun_gan}{dayun_zhi}"
                })
        
        # ========== 5. 判断岁运伏吟（大运与流年之间） ==========
        if liunian_gan == dayun_gan and liunian_zhi == dayun_zhi:
            result['岁运伏吟'] = {
                '发生': True,
                '说明': f"大运{dayun_gan}{dayun_zhi}与流年{liunian_gan}{liunian_zhi}干支相同"
            }
        
        return result
    
    def _analyze_single_ganzhi_relations(self, gan: str, zhi: str,
                                       orig_gans: List[str], orig_zhis: List[str],
                                       source_type: str) -> Dict:
        """分析单个干柱的关系"""
        relations = {
            '伏吟': [],
            '反吟': [],
            '盖头': False,
            '截脚': False
        }
        
        if not gan or not zhi:
            return relations
        
        # 检查与原局各柱的伏吟
        for i in range(len(orig_gans)):
            if gan == orig_gans[i] and zhi == orig_zhis[i]:
                relations['伏吟'].append(f'与{"年月日时"[i]}柱{gan}{zhi}伏吟')
        
        # 检查与原局各柱的反吟
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        gan_chong_pairs = [('甲', '庚'), ('乙', '辛'), ('壬', '丙'), ('癸', '丁')]
        
        for i in range(len(orig_gans)):
            is_zhi_chong = any(
                (zhi == cp[0] and orig_zhis[i] == cp[1]) or (zhi == cp[1] and orig_zhis[i] == cp[0])
                for cp in chong_pairs
            )
            is_gan_chong = any(
                (gan == gcp[0] and orig_gans[i] == gcp[1]) or (gan == gcp[1] and orig_gans[i] == gcp[0])
                for gcp in gan_chong_pairs
            )
            if is_zhi_chong and is_gan_chong:
                relations['反吟'].append(f'与{"年月日时"[i]}柱{gan}{zhi}反吟（天克地冲）')
        
        # 检查盖头和截脚
        gaitou_combinations = [
            ('甲', '辰'), ('甲', '戌'), ('乙', '丑'), ('乙', '未'),
            ('丙', '申'), ('丁', '酉'), ('戊', '子'), ('己', '亥'),
            ('庚', '寅'), ('辛', '卯'), ('壬', '午'), ('癸', '巳')
        ]
        jiejiao_combinations = [
            ('甲', '申'), ('乙', '酉'), ('丙', '子'), ('丁', '亥'),
            ('戊', '寅'), ('己', '卯'), ('庚', '午'), ('辛', '巳'),
            ('壬', '辰'), ('癸', '丑'), ('癸', '未'), ('壬', '戌')
        ]
        
        if (gan, zhi) in gaitou_combinations:
            relations['盖头'] = True
        if (gan, zhi) in jiejiao_combinations:
            relations['截脚'] = True
        
        return relations
    
    def _analyze_ganzhi_pair_relations(self, gan1: str, zhi1: str,
                                     gan2: str, zhi2: str,
                                     name1: str, name2: str) -> List[str]:
        """分析两个干柱之间的关系"""
        relations = []
        
        if not gan1 or not zhi1 or not gan2 or not zhi2:
            return relations
        
        # 伏吟
        if gan1 == gan2 and zhi1 == zhi2:
            relations.append(f'{gan1}{zhi1}与{gan2}{zhi2}伏吟')
        
        # 反吟（天克地冲）
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        gan_chong_pairs = [('甲', '庚'), ('乙', '辛'), ('壬', '丙'), ('癸', '丁')]
        
        is_zhi_chong = any(
            (zhi1 == cp[0] and zhi2 == cp[1]) or (zhi1 == cp[1] and zhi2 == cp[0])
            for cp in chong_pairs
        )
        is_gan_chong = any(
            (gan1 == gcp[0] and gan2 == gcp[1]) or (gan1 == gcp[1] and gan2 == gcp[0])
            for gcp in gan_chong_pairs
        )
        
        if is_zhi_chong and is_gan_chong:
            relations.append(f'{gan1}{zhi1}与{gan2}{zhi2}反吟（天克地冲）')
        
        return relations
    
    def _analyze_extended_zhi_relations(self, extended_zhis: List[str]) -> Dict:
        """分析扩展地支关系（含大运流年）"""
        result = {
            '三会': [],
            '三合': [],
            '六合': [],
            '半会': [],
            '半合': [],
            '拱会': [],
            '拱合': [],
            '六冲': [],
            '六害': [],
            '三刑': []
        }
        
        # 来源标记
        result['来源标记'] = {
            '三会': [],
            '三合': [],
            '六合': [],
            '六冲': [],
            '三刑': []
        }
        
        # 季节划分
        spring_zhis = ['寅', '卯', '辰']
        summer_zhis = ['巳', '午', '未']
        autumn_zhis = ['申', '酉', '戌']
        winter_zhis = ['亥', '子', '丑']
        
        # 检查三会局
        sanhui_sets = {
            '寅卯辰': ('寅', '卯', '辰', '寅卯辰三会木局'),
            '巳午未': ('巳', '午', '未', '巳午未三会火局'),
            '申酉戌': ('申', '酉', '戌', '申酉戌三会金局'),
            '亥子丑': ('亥', '子', '丑', '亥子丑三会水局')
        }
        for key, (z1, z2, z3, name) in sanhui_sets.items():
            if z1 in extended_zhis and z2 in extended_zhis and z3 in extended_zhis:
                result['三会'].append(name)
                # 标记来源
                sources = []
                for z in [z1, z2, z3]:
                    idx = extended_zhis.index(z)
                    sources.append(self._get_extended_source_name(idx))
                result['来源标记']['三会'].append((name, '+'.join(sources)))
        
        # 检查三合局
        sanhe_sets = {
            '申子辰': ('申', '子', '辰', '水局'),
            '亥卯未': ('亥', '卯', '未', '木局'),
            '寅午戌': ('寅', '午', '戌', '火局'),
            '巳酉丑': ('巳', '酉', '丑', '金局')
        }
        for key, (z1, z2, z3, name) in sanhe_sets.items():
            if z1 in extended_zhis and z2 in extended_zhis and z3 in extended_zhis:
                # 地支凑齐即构成三合局，不需要考虑月令
                result['三合'].append(f"{key}合{name}")
                # 标记来源
                sources = []
                for z in [z1, z2, z3]:
                    idx = extended_zhis.index(z)
                    sources.append(self._get_extended_source_name(idx))
                result['来源标记']['三合'].append((f"{key}合{name}", '+'.join(sources)))
        
        # 检查六合（标准顺序：子丑、寅亥、卯戌、辰酉、巳申、午未）
        liuhe_pairs = [('子', '丑', '土'), ('寅', '亥', '木'), ('卯', '戌', '火'),
                       ('辰', '酉', '金'), ('巳', '申', '水'), ('午', '未', '土')]
        for z1, z2, wuxing in liuhe_pairs:
            if z1 in extended_zhis and z2 in extended_zhis:
                idx1 = extended_zhis.index(z1)
                idx2 = extended_zhis.index(z2)
                source = f"{self._get_extended_source_name(idx1)}+{self._get_extended_source_name(idx2)}"
                result['六合'].append(f"{z1}{z2}合({wuxing})")
                result['来源标记']['六合'].append((f"{z1}{z2}合", source))
        
        # 检查六冲
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        for z1, z2 in chong_pairs:
            if z1 in extended_zhis and z2 in extended_zhis:
                idx1 = extended_zhis.index(z1)
                idx2 = extended_zhis.index(z2)
                source = f"{self._get_extended_source_name(idx1)}+{self._get_extended_source_name(idx2)}"
                result['六冲'].append(f"{z1}{z2}冲")
                result['来源标记']['六冲'].append((f"{z1}{z2}冲", source))
        
        # 检查三刑
        san_xing = [('寅', '巳', '申'), ('丑', '戌', '未')]
        for xing in san_xing:
            if all(z in extended_zhis for z in xing):
                sources = []
                for z in xing:
                    idx = extended_zhis.index(z)
                    sources.append(self._get_extended_source_name(idx))
                result['三刑'].append(f"{xing[0]}{xing[1]}{xing[2]}刑")
                result['来源标记']['三刑'].append((f"{xing[0]}{xing[1]}{xing[2]}刑", '+'.join(sources)))
        
        return result
    
    def _analyze_extended_gan_relations(self, extended_gans: List[str]) -> Dict:
        """分析扩展天干关系（含大运流年）"""
        result = {
            '天干五合': [],
            '化气判定': '',
            '天干相冲': [],
            '天干相克': []
        }
        
        # 来源标记
        result['来源标记'] = {
            '天干五合': [],
            '天干相冲': []
        }
        
        # 分析天干五合
        for gan_pair in gan_hes:
            if gan_pair[0] in extended_gans and gan_pair[1] in extended_gans:
                idx1 = extended_gans.index(gan_pair[0])
                idx2 = extended_gans.index(gan_pair[1])
                source = f"{self._get_extended_source_name(idx1)}+{self._get_extended_source_name(idx2)}"
                result['天干五合'].append(f"{gan_pair[0]}{gan_pair[1]}合")
                result['来源标记']['天干五合'].append((f"{gan_pair[0]}{gan_pair[1]}合", source))
        
        # 分析天干相冲
        gan_chong_pairs = [
            ('甲', '庚'), ('乙', '辛'), ('壬', '丙'), ('癸', '丁')
        ]
        for gan_pair in gan_chong_pairs:
            if gan_pair[0] in extended_gans and gan_pair[1] in extended_gans:
                idx1 = extended_gans.index(gan_pair[0])
                idx2 = extended_gans.index(gan_pair[1])
                source = f"{self._get_extended_source_name(idx1)}+{self._get_extended_source_name(idx2)}"
                result['天干相冲'].append(f"{gan_pair[0]}{gan_pair[1]}冲")
                result['来源标记']['天干相冲'].append((f"{gan_pair[0]}{gan_pair[1]}冲", source))
        
        # 简单化气判定
        for he, hua_info in self.GAN_HE_HUA.items():
            if he[0] in extended_gans and he[1] in extended_gans:
                if self.month_zhi in hua_info['条件']['月令']:
                    result['化气判定'] = f"{he[0]}{he[1]}化{hua_info['化']}"
                    break
        
        return result
    
    def _analyze_extended_gan_zhi_relations(self, extended_gans: List[str], extended_zhis: List[str]) -> Dict:
        """分析扩展天干与地支的关系（含大运流年）"""
        result = {
            '伏吟': [],
            '反吟': [],
            '盖头': [],
            '截脚': []
        }
        
        # 来源标记
        result['来源标记'] = {
            '伏吟': [],
            '反吟': [],
            '盖头': [],
            '截脚': []
        }
        
        # 分析所有柱的干支关系
        pillar_names = ['年柱', '月柱', '日柱', '时柱', '大运', '流年']
        
        # 检查伏吟（干支重复）
        for i in range(len(extended_gans)):
            for j in range(i + 1, len(extended_gans)):
                if extended_gans[i] == extended_gans[j] and extended_zhis[i] == extended_zhis[j]:
                    ganzhi = f"{extended_gans[i]}{extended_zhis[i]}"
                    result['伏吟'].append(f"{pillar_names[i]}{ganzhi}与{pillar_names[j]}{ganzhi}伏吟")
                    source = f"{pillar_names[i]}+{pillar_names[j]}"
                    result['来源标记']['伏吟'].append((f"{pillar_names[i]}{ganzhi}与{pillar_names[j]}{ganzhi}伏吟", source))
        
        # 检查反吟（天干相冲且地支相冲）
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        gan_chong_pairs = [('甲', '庚'), ('乙', '辛'), ('壬', '丙'), ('癸', '丁')]
        
        for i in range(len(extended_gans)):
            for j in range(i + 1, len(extended_gans)):
                # 检查地支是否相冲
                is_zhi_chong = False
                zhi_chong_str = ''
                for chong_pair in chong_pairs:
                    if (extended_zhis[i] == chong_pair[0] and extended_zhis[j] == chong_pair[1]) or \
                       (extended_zhis[i] == chong_pair[1] and extended_zhis[j] == chong_pair[0]):
                        is_zhi_chong = True
                        zhi_chong_str = f"{extended_zhis[i]}{extended_zhis[j]}地冲"
                        break
                
                # 检查天干是否相冲
                is_gan_chong = False
                gan_chong_str = ''
                for gan_pair in gan_chong_pairs:
                    if (extended_gans[i] == gan_pair[0] and extended_gans[j] == gan_pair[1]) or \
                       (extended_gans[i] == gan_pair[1] and extended_gans[j] == gan_pair[0]):
                        is_gan_chong = True
                        gan_chong_str = f"{extended_gans[i]}{extended_gans[j]}天冲"
                        break
                
                if is_zhi_chong and is_gan_chong:
                    result['反吟'].append(f"{pillar_names[i]}与{pillar_names[j]}反吟（{gan_chong_str}+{zhi_chong_str}）")
                    source = f"{pillar_names[i]}+{pillar_names[j]}"
                    result['来源标记']['反吟'].append((f"{pillar_names[i]}与{pillar_names[j]}反吟（{gan_chong_str}+{zhi_chong_str}）", source))
        
        # 检查盖头和截脚
        gaitou_combinations = [
            ('甲', '辰'), ('甲', '戌'), ('乙', '丑'), ('乙', '未'),
            ('丙', '申'), ('丁', '酉'), ('戊', '子'), ('己', '亥'),
            ('庚', '寅'), ('辛', '卯'), ('壬', '午'), ('癸', '巳')
        ]
        
        jiejiao_combinations = [
            ('甲', '申'), ('乙', '酉'), ('丙', '子'), ('丁', '亥'),
            ('戊', '寅'), ('己', '卯'), ('庚', '午'), ('辛', '巳'),
            ('壬', '辰'), ('癸', '丑'), ('癸', '未'), ('壬', '戌')
        ]
        
        for i in range(len(extended_gans)):
            gan, zhi = extended_gans[i], extended_zhis[i]
            if (gan, zhi) in gaitou_combinations:
                result['盖头'].append(f"{pillar_names[i]}({gan}盖{zhi})盖头")
                result['来源标记']['盖头'].append((f"{pillar_names[i]}({gan}盖{zhi})盖头", pillar_names[i]))
            if (gan, zhi) in jiejiao_combinations:
                result['截脚'].append(f"{pillar_names[i]}({zhi}截{gan})截脚")
                result['来源标记']['截脚'].append((f"{pillar_names[i]}({zhi}截{gan})截脚", pillar_names[i]))
        
        return result
    
    def _analyze_yuesui_relations(self, dayun_gan: str, dayun_zhi: str, 
                                   liunian_gan: str, liunian_zhi: str) -> Dict:
        """
        分析原局与大运流年的关系
        
        按照要求分别分析：
        1. 岁运天干分析（结合第三、四论级）：对大运天干、流年天干分别对原局年、月、日、时柱的影响，以及大运流年天干之间的影响
        2. 岁运地支分析（结合第二、四论级）：对大运地支、流年地支分别对原局年、月、日、时柱的影响，以及大运流年地支之间的影响
        """
        result = {
            '岁运并临': False,
            '岁运天干分析': {
                '大运天干影响': {'对年柱': [], '对月柱': [], '对日柱': [], '对时柱': [], '对流年天干': []},
                '流年天干影响': {'对年柱': [], '对月柱': [], '对日柱': [], '对时柱': [], '对大运天干': []}
            },
            '岁运地支分析': {
                '大运地支影响': {'对年柱': [], '对月柱': [], '对日柱': [], '对时柱': [], '对流年地支': []},
                '流年地支影响': {'对年柱': [], '对月柱': [], '对日柱': [], '对时柱': [], '对大运地支': []}
            }
        }
        
        from ganzhi import gan5
        pillar_names = ['年柱', '月柱', '日柱', '时柱']
        
        # ==================== 岁运天干分析 ====================
        
        # 大运天干对原局各柱的影响
        for i, pillar_name in enumerate(pillar_names):
            impacts = self._analyze_gan_impact_on_pillar(
                dayun_gan, self.gans[i], pillar_name, '大运天干'
            )
            if impacts:
                result['岁运天干分析']['大运天干影响'][f'对{pillar_name}'] = impacts
        
        # 流年天干对原局各柱的影响
        for i, pillar_name in enumerate(pillar_names):
            impacts = self._analyze_gan_impact_on_pillar(
                liunian_gan, self.gans[i], pillar_name, '流年天干'
            )
            if impacts:
                result['岁运天干分析']['流年天干影响'][f'对{pillar_name}'] = impacts
        
        # 大运天干与流年天干之间的影响
        gan_impact_dy_ll = self._analyze_gan_impact_on_pillar(
            dayun_gan, liunian_gan, '流年天干', '大运天干'
        )
        if gan_impact_dy_ll:
            result['岁运天干分析']['大运天干影响']['对流年天干'] = gan_impact_dy_ll
        
        # 流年天干与大运天干之间的影响（双向，但避免重复）
        gan_impact_ll_dy = self._analyze_gan_impact_on_pillar(
            liunian_gan, dayun_gan, '大运天干', '流年天干'
        )
        if gan_impact_ll_dy and not gan_impact_dy_ll:
            result['岁运天干分析']['流年天干影响']['对大运天干'] = gan_impact_ll_dy
        
        # ==================== 岁运地支分析 ====================
        
        # 大运地支对原局各柱的影响
        for i, pillar_name in enumerate(pillar_names):
            impacts = self._analyze_zhi_impact_on_pillar(
                dayun_zhi, self.zhis[i], pillar_name, '大运地支'
            )
            if impacts:
                result['岁运地支分析']['大运地支影响'][f'对{pillar_name}'] = impacts
        
        # 流年地支对原局各柱的影响
        for i, pillar_name in enumerate(pillar_names):
            impacts = self._analyze_zhi_impact_on_pillar(
                liunian_zhi, self.zhis[i], pillar_name, '流年地支'
            )
            if impacts:
                result['岁运地支分析']['流年地支影响'][f'对{pillar_name}'] = impacts
        
        # 大运地支与流年地支之间的影响
        zhi_impact_dy_ll = self._analyze_zhi_impact_on_pillar(
            dayun_zhi, liunian_zhi, '流年地支', '大运地支'
        )
        if zhi_impact_dy_ll:
            result['岁运地支分析']['大运地支影响']['对流年地支'] = zhi_impact_dy_ll
        
        # 流年地支与大运地支之间的影响（双向，但避免重复）
        zhi_impact_ll_dy = self._analyze_zhi_impact_on_pillar(
            liunian_zhi, dayun_zhi, '大运地支', '流年地支'
        )
        if zhi_impact_ll_dy and not zhi_impact_dy_ll:
            result['岁运地支分析']['流年地支影响']['对大运地支'] = zhi_impact_ll_dy
        
        # 检查岁运并临（大运与流年相同）
        if dayun_gan == liunian_gan and dayun_zhi == liunian_zhi:
            result['岁运并临'] = True
        
        return result
    
    def _analyze_gan_impact_on_pillar(self, source_gan: str, target_gan: str, 
                                     pillar_name: str, source_type: str) -> List[Dict]:
        """
        分析天干对某柱的影响（结合第三、四论级逻辑）
        
        参数:
            source_gan: 来源天干（大运或流年）
            target_gan: 目标天干
            pillar_name: 柱名称
            source_type: 来源类型（大运天干或流年天干）
        返回:
            字典列表，每个字典包含'类型'和'描述'键
        """
        impacts = []
        
        if not source_gan or not target_gan:
            return impacts
        
        # 第三论级：天干五合（标准顺序：甲己合、乙庚合、丙辛合、丁壬合、戊癸合）
        for gan_pair in gan_hes:
            if (source_gan, target_gan) == gan_pair or (target_gan, source_gan) == gan_pair:
                impacts.append({
                    '类型': '天干五合',
                    '描述': f"{gan_pair[0]}{gan_pair[1]}合"
                })
        
        # 第三论级：天干相冲（标准顺序：甲庚冲、乙辛冲、丙壬冲、丁癸冲）
        gan_chong_pairs = [('甲', '庚'), ('乙', '辛'), ('丙', '壬'), ('丁', '癸')]
        for gan_pair in gan_chong_pairs:
            if source_gan == gan_pair[0] and target_gan == gan_pair[1]:
                impacts.append({
                    '类型': '天干相冲',
                    '描述': f"{gan_pair[0]}{gan_pair[1]}冲"
                })
            elif source_gan == gan_pair[1] and target_gan == gan_pair[0]:
                impacts.append({
                    '类型': '天干相冲',
                    '描述': f"{gan_pair[0]}{gan_pair[1]}冲"
                })
        
        # 第三论级：天干相克
        from ganzhi import gan5
        ke_map = {
            '木': '土', '火': '金', '土': '水', '金': '木', '水': '火'
        }
        
        source_wuxing = gan5.get(source_gan, '')
        target_wuxing = gan5.get(target_gan, '')
        
        if source_wuxing and target_wuxing and ke_map.get(source_wuxing) == target_wuxing:
            impacts.append({
                '类型': '天干相克',
                '描述': f"{source_wuxing}克{target_wuxing}（{source_gan}克{target_gan}）"
            })
        
        # 第三论级：天干相生
        sheng_map = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }
        
        if source_wuxing and target_wuxing and sheng_map.get(source_wuxing) == target_wuxing:
            impacts.append({
                '类型': '天干相生',
                '描述': f"{source_wuxing}生{target_wuxing}（{source_gan}生{target_gan}）"
            })
        
        # 第四论级：同柱伏吟（如果是在分析同柱的干支）
        # 这里假设外部已经处理了伏吟，所以主要关注跨柱的影响
        
        return impacts
    
    def _analyze_zhi_impact_on_pillar(self, source_zhi: str, target_zhi: str, 
                                     pillar_name: str, source_type: str) -> List[Dict]:
        """
        分析地支对某柱的影响（结合第二、四论级逻辑）
        
        参数:
            source_zhi: 来源地支（大运或流年）
            target_zhi: 目标地支
            pillar_name: 柱名称
            source_type: 来源类型（大运地支或流年地支）
        返回:
            字典列表，每个字典包含'类型'和'描述'键
        """
        impacts = []
        
        if not source_zhi or not target_zhi:
            return impacts
        
        # 第二论级：六合（标准顺序：子丑、寅亥、卯戌、辰酉、巳申、午未）
        liuhe_data = {
            ('子', '丑'): ('子丑', '土'), ('丑', '子'): ('子丑', '土'),
            ('寅', '亥'): ('寅亥', '木'), ('亥', '寅'): ('寅亥', '木'),
            ('卯', '戌'): ('卯戌', '火'), ('戌', '卯'): ('卯戌', '火'),
            ('辰', '酉'): ('辰酉', '金'), ('酉', '辰'): ('辰酉', '金'),
            ('巳', '申'): ('巳申', '水'), ('申', '巳'): ('巳申', '水'),
            ('午', '未'): ('午未', '土'), ('未', '午'): ('午未', '土')
        }

        for zhi_pair, (he_name, wuxing) in liuhe_data.items():
            if (source_zhi == zhi_pair[0] and target_zhi == zhi_pair[1]) or \
               (source_zhi == zhi_pair[1] and target_zhi == zhi_pair[0]):
                impacts.append({
                    '类型': '六合',
                    '描述': f"{he_name}合({wuxing})"
                })
        
        # 第二论级：六冲（标准顺序：子午、丑未、寅申、卯酉、辰戌、巳亥）
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        for chong_pair in chong_pairs:
            if (source_zhi == chong_pair[0] and target_zhi == chong_pair[1]) or \
               (source_zhi == chong_pair[1] and target_zhi == chong_pair[0]):
                impacts.append({
                    '类型': '六冲',
                    '描述': f"{chong_pair[0]}{chong_pair[1]}冲"
                })
        
        # 第二论级：三合（如果两个地支可以形成三合的一部分）
        sanhe_sets = {
            '申子辰': ['申', '子', '辰'],
            '亥卯未': ['亥', '卯', '未'],
            '寅午戌': ['寅', '午', '戌'],
            '巳酉丑': ['巳', '酉', '丑']
        }
        
        for sanhe_name, sanhe_zhis in sanhe_sets.items():
            if source_zhi in sanhe_zhis and target_zhi in sanhe_zhis:
                impacts.append({
                    '类型': '三合',
                    '描述': f"可形成三合：{sanhe_name}"
                })
        
        # 第二论级：三刑
        san_xing = [('寅', '巳', '申'), ('丑', '戌', '未')]
        for xing in san_xing:
            if source_zhi in xing and target_zhi in xing:
                impacts.append({
                    '类型': '三刑',
                    '描述': f"可形成三刑：{xing[0]}{xing[1]}{xing[2]}刑"
                })
        
        # 第二论级：六害（标准顺序：子未、丑午、寅巳、申亥、卯辰、酉戌）
        hai_pairs = [('子', '未'), ('丑', '午'), ('寅', '巳'), ('申', '亥'), ('卯', '辰'), ('酉', '戌')]
        for hai_pair in hai_pairs:
            if (source_zhi == hai_pair[0] and target_zhi == hai_pair[1]) or \
               (source_zhi == hai_pair[1] and target_zhi == hai_pair[0]):
                impacts.append({
                    '类型': '六害',
                    '描述': f"{hai_pair[0]}{hai_pair[1]}害"
                })
        
        # 第四论级：地支冲克（天克地冲的前提）
        # 这里已经通过六冲覆盖了
        
        return impacts
    
    def _analyze_suiyuan_impact(self, original: Dict, sixth_result: Dict,
                                dayun_gan: str, dayun_zhi: str,
                                liunian_gan: str, liunian_zhi: str) -> Dict:
        """
        iii. 分析大运流年对原局的综合影响
        
        参数:
            original: 原局分析结果
            sixth_result: 第六论级分析结果（包含岁运分析）
        """
        result = {
            '引发': [],
            '加强': [],
            '破坏': [],
            '喜神用神判定': [],
            '综合影响': []
        }
        
        # 获取喜忌信息
        xi_ji_info = original.get('第五论级_定喜忌', {})
        yong_shen = xi_ji_info.get('用神', [])
        xi_shen = xi_ji_info.get('喜神', [])
        ji_shen = xi_ji_info.get('忌神', [])
        xi_yong = yong_shen + xi_shen
        
        # 判断大运流年是否为喜用神或忌神
        if dayun_gan in xi_yong:
            result['喜神用神判定'].append(f"大运天干{dayun_gan}为喜用神，大吉")
        elif dayun_gan in ji_shen:
            result['喜神用神判定'].append(f"大运天干{dayun_gan}为忌神，需化解")
        
        if liunian_gan in xi_yong:
            result['喜神用神判定'].append(f"流年天干{liunian_gan}为喜用神，大吉")
        elif liunian_gan in ji_shen:
            result['喜神用神判定'].append(f"流年天干{liunian_gan}为忌神，需谨慎")
        
        # 分析天干影响
        gan_analysis = sixth_result.get('岁运天干分析', {})
        
        # 统计引发的新组合
        new_combinations = []
        
        # 大运天干引发的新关系
        for pillar_name, impacts in gan_analysis.get('大运天干影响', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干五合':
                    new_combinations.append(f"大运天干引发天干五合: {impact['描述']}")
                    result['引发'].append(f"大运天干引发天干五合: {impact['描述']}")
                elif impact['类型'] == '化气判定':
                    new_combinations.append(f"大运天干引发化气: {impact['描述']}")
                    result['引发'].append(f"大运天干引发化气: {impact['描述']}")
                elif impact['类型'] == '天干相冲':
                    result['破坏'].append(f"大运天干冲克: {impact['描述']}")
        
        # 流年天干引发的新关系
        for pillar_name, impacts in gan_analysis.get('流年天干影响', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干五合':
                    result['引发'].append(f"流年天干引发天干五合: {impact['描述']}")
                elif impact['类型'] == '化气判定':
                    result['引发'].append(f"流年天干引发化气: {impact['描述']}")
                elif impact['类型'] == '天干相冲':
                    result['破坏'].append(f"流年天干冲克: {impact['描述']}")
        
        # 分析地支影响
        zhi_analysis = sixth_result.get('岁运地支分析', {})
        
        # 大运地支引发的新关系
        for pillar_name, impacts in zhi_analysis.get('大运地支影响', {}).items():
            for impact in impacts:
                if impact['类型'] in ['三合', '三会', '六合']:
                    result['引发'].append(f"大运地支引发{impact['类型']}: {impact['描述']}")
                elif impact['类型'] == '六冲':
                    result['破坏'].append(f"大运地支冲克: {impact['描述']}")
                elif impact['类型'] == '三刑':
                    result['破坏'].append(f"大运地支引动三刑: {impact['描述']}")
        
        # 流年地支引发的新关系
        for pillar_name, impacts in zhi_analysis.get('流年地支影响', {}).items():
            for impact in impacts:
                if impact['类型'] in ['三合', '三会', '六合']:
                    result['引发'].append(f"流年地支引发{impact['类型']}: {impact['描述']}")
                elif impact['类型'] == '六冲':
                    result['破坏'].append(f"流年地支冲克: {impact['描述']}")
                elif impact['类型'] == '三刑':
                    result['破坏'].append(f"流年地支引动三刑: {impact['描述']}")
        
        # 分析特殊格局
        special_patterns = sixth_result.get('岁运特殊格局分析', {})
        if special_patterns.get('引发的特殊格局'):
            result['引发'].extend(special_patterns['引发的特殊格局'])
        
        # 分析干支关系
        ganzhi_analysis = sixth_result.get('岁运干支分析', {})
        for relation_name, relations in ganzhi_analysis.get('岁运原局干支关系', {}).items():
            for relation in relations:
                if '伏吟' in relation:
                    result['引发'].append(f"{relation_name}伏吟")
                elif '反吟' in relation:
                    result['破坏'].append(f"{relation_name}反吟")
        
        # 生成综合影响评语
        count_yinfa = len(result['引发'])
        count_pohuai = len(result['破坏'])
        
        if count_yinfa > 0 and count_pohuai == 0:
            result['综合影响'].append(f"大运流年引发{count_yinfa}项新格局，运势上升")
        elif count_pohuai > 0 and count_yinfa == 0:
            result['综合影响'].append(f"大运流年造成{count_pohuai}项破坏，运势下降")
        elif count_yinfa > 0 and count_pohuai > 0:
            result['综合影响'].append(f"大运流年引发{count_yinfa}项新格局，同时造成{count_pohuai}项破坏，喜忧参半")
        else:
            result['综合影响'].append("大运流年对原局影响平稳")
        
        return result
    
    def _calculate_energy_impact_with_unified_scoring(self, sixth_result: Dict) -> Dict:
        """
        使用统一评分标准计算大运流年对原局能量影响
        
        规则：
        - 只计算大运流年干支本身的基础能量（天干+1，地支藏干基础分+月令2加成）
        - 不计算关系评分（如合、冲等），避免两次计算使用不同数据源导致的误差
        """
        import re
        from ganzhi import gan5, zhi5_list, ten_deities
        
        day_gan = self.day_gan
        base_score = self.SCORE_BASE
        
        # 初始化增加的能量
        wuxing_add = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        wuxing_add_details = {'木': [], '火': [], '土': [], '金': [], '水': []}
        shishen_add = {'比': 0, '劫': 0, '食': 0, '伤': 0, '财': 0, '才': 0, '官': 0, '杀': 0, '印': 0, '枭': 0}
        shishen_add_details = {'比': [], '劫': [], '食': [], '伤': [], '财': [], '才': [], '官': [], '杀': [], '印': [], '枭': []}
        
        # 获取大运流年干支
        dayun_gan = getattr(self.dayun_liunian, 'current_dayun_gan', '') if self.dayun_liunian else ''
        dayun_zhi = getattr(self.dayun_liunian, 'current_dayun_zhi', '') if self.dayun_liunian else ''
        liunian_gan = getattr(self.dayun_liunian, 'current_liunian_gan', '') if self.dayun_liunian else ''
        liunian_zhi = getattr(self.dayun_liunian, 'current_liunian_zhi', '') if self.dayun_liunian else ''
        
        # ========== 计算大运天干能量贡献 ==========
        if dayun_gan:
            wuxing = gan5.get(dayun_gan, '')
            shishen = ten_deities.get(day_gan, {}).get(dayun_gan, '')
            if wuxing:
                wuxing_add[wuxing] += base_score['天干']['wuxing']
                wuxing_add_details[wuxing].append(f'大运天干{dayun_gan}五行{wuxing}+{base_score["天干"]["wuxing"]}')
            if shishen:
                shishen_add[shishen] += base_score['天干']['shishen']
                shishen_add_details[shishen].append(f'大运天干{dayun_gan}十神{shishen}+{base_score["天干"]["shishen"]}')
        
        # ========== 计算流年天干能量贡献 ==========
        if liunian_gan:
            wuxing = gan5.get(liunian_gan, '')
            shishen = ten_deities.get(day_gan, {}).get(liunian_gan, '')
            if wuxing:
                wuxing_add[wuxing] += base_score['天干']['wuxing']
                wuxing_add_details[wuxing].append(f'流年天干{liunian_gan}五行{wuxing}+{base_score["天干"]["wuxing"]}')
            if shishen:
                shishen_add[shishen] += base_score['天干']['shishen']
                shishen_add_details[shishen].append(f'流年天干{liunian_gan}十神{shishen}+{base_score["天干"]["shishen"]}')
        
        # ========== 计算大运地支能量贡献（月令2：本气+0.6+2，中气+0.3+2，余气+0.1+2） ==========
        if dayun_zhi:
            canggan_list = zhi5_list.get(dayun_zhi, [])
            for j, canggan in enumerate(canggan_list):
                qi_type = '本气' if j == 0 else ('中气' if j == 1 else '余气')
                base_wx = base_score['藏干本气']['wuxing'] if j == 0 else (base_score['藏干中气']['wuxing'] if j == 1 else base_score['藏干余气']['wuxing'])
                base_ss = base_score['藏干本气']['shishen'] if j == 0 else (base_score['藏干中气']['shishen'] if j == 1 else base_score['藏干余气']['shishen'])
                total_add = 2 + base_wx  # 月令2(+2) + 基础分
                
                wuxing = gan5.get(canggan, '')
                shishen = ten_deities.get(day_gan, {}).get(canggan, '')
                if wuxing:
                    wuxing_add[wuxing] += total_add
                    wuxing_add_details[wuxing].append(f'大运地支{dayun_zhi}藏干{canggan}({qi_type})五行{wuxing}+{base_wx}+2={total_add}')
                if shishen:
                    shishen_add[shishen] += total_add
                    shishen_add_details[shishen].append(f'大运地支{dayun_zhi}藏干{canggan}({qi_type})十神{shishen}+{base_ss}+2={total_add}')
        
        # ========== 计算流年地支能量贡献（年支2：本气+0.6，中气+0.3，余气+0.1） ==========
        if liunian_zhi:
            canggan_list = zhi5_list.get(liunian_zhi, [])
            for j, canggan in enumerate(canggan_list):
                if j == 0:  # 本气
                    score_wx = base_score['藏干本气']['wuxing']
                    score_ss = base_score['藏干本气']['shishen']
                    qi_type = '本气'
                elif j == 1:  # 中气
                    score_wx = base_score['藏干中气']['wuxing']
                    score_ss = base_score['藏干中气']['shishen']
                    qi_type = '中气'
                else:  # 余气
                    score_wx = base_score['藏干余气']['wuxing']
                    score_ss = base_score['藏干余气']['shishen']
                    qi_type = '余气'
                
                wuxing = gan5.get(canggan, '')
                shishen = ten_deities.get(day_gan, {}).get(canggan, '')
                if wuxing:
                    wuxing_add[wuxing] += score_wx
                    wuxing_add_details[wuxing].append(f'流年地支{liunian_zhi}藏干{canggan}({qi_type})五行{wuxing}+{score_wx}')
                if shishen:
                    shishen_add[shishen] += score_ss
                    shishen_add_details[shishen].append(f'流年地支{liunian_zhi}藏干{canggan}({qi_type})十神{shishen}+{score_ss}')
        
        # ========== 计算地支关系带来的能量贡献 ==========
        # 从 sixth_result 获取岁运地支分析结果
        zhi_analysis = sixth_result.get('岁运地支分析', {})
        
        # 定义地支关系评分标准
        zhi_relation_scores = {
            '三会': 3.0,
            '半会': 1.5,
            '拱会': 1.0,
            '三合': 1.0,
            '半合': 0.5,
            '拱合': 1.0,
            '六合': 1.0,
        }
        
        # 收集所有地支关系影响
        all_zhi_impacts = []
        
        # 收集大运地支影响
        for pillar_name, impacts in zhi_analysis.get('大运地支影响', {}).items():
            for impact in impacts:
                if impact['类型'] in zhi_relation_scores:
                    all_zhi_impacts.append({
                        '来源': f'大运地支-{pillar_name}',
                        '类型': impact['类型'],
                        '描述': impact['描述'],
                        '分数': zhi_relation_scores[impact['类型']]
                    })
        
        # 收集流年地支影响
        for pillar_name, impacts in zhi_analysis.get('流年地支影响', {}).items():
            for impact in impacts:
                if impact['类型'] in zhi_relation_scores:
                    all_zhi_impacts.append({
                        '来源': f'流年地支-{pillar_name}',
                        '类型': impact['类型'],
                        '描述': impact['描述'],
                        '分数': zhi_relation_scores[impact['类型']]
                    })
        
        # 收集大运流年地支之间关系
        for relation_name, impacts in zhi_analysis.get('大运流年地支关系', {}).items():
            for impact in impacts:
                if impact['类型'] in zhi_relation_scores:
                    all_zhi_impacts.append({
                        '来源': relation_name,
                        '类型': impact['类型'],
                        '描述': impact['描述'],
                        '分数': zhi_relation_scores[impact['类型']]
                    })
        
        # 处理每个地支关系，提取五行并加分
        for impact in all_zhi_impacts:
            desc = impact['描述']
            rel_type = impact['类型']
            score = impact['分数']
            source = impact['来源']
            
            # 从描述中提取五行
            # 格式如："申酉半会金"、"寅辰拱会卯木"、"辰酉合(金)"
            wuxing = None
            
            # 尝试从描述末尾提取五行（金、木、水、火、土）
            for wx in ['金', '木', '水', '火', '土']:
                if wx in desc:
                    wuxing = wx
                    break
            
            if wuxing:
                wuxing_add[wuxing] += score
                wuxing_add_details[wuxing].append(f'{source}-{desc}:{rel_type}+{score}')
                
                # 对于拱会/拱合，还需要给拱出的中神藏干十神加分
                if rel_type in ['拱会', '拱合']:
                    # 提取中神（如"寅辰拱会卯木"中的卯）
                    import re
                    match = re.search(r'拱会(\w)|拱合(\w)', desc)
                    if match:
                        gong_zhi = match.group(1) or match.group(2)
                        if gong_zhi:
                            # 获取中神的藏干（本气）
                            canggan_list = zhi5_list.get(gong_zhi, [])
                            if canggan_list:
                                main_canggan = canggan_list[0]  # 本气
                                shishen = ten_deities.get(day_gan, {}).get(main_canggan, '')
                                if shishen:
                                    shishen_add[shishen] += score
                                    shishen_add_details[shishen].append(f'{source}-{desc}:{rel_type}中神{gong_zhi}藏干{main_canggan}十神{shishen}+{score}')
                elif rel_type == '六合':
                    # 六合有化气，需要给对应十神加分
                    # 从描述中提取合化五行，如"辰酉合(金)"
                    match = re.search(r'\((\w)\)', desc)
                    if match:
                        he_wuxing = match.group(1)
                        # 六合的十神由合化五行决定（根据日主）
                        # 这里简化处理，给对应五行的藏干十神加分
                        pass
        
        # 获取原局能量和计算大运流年后总能量
        original_energy = self._calculate_wuxing_shishen_scores(include_dayun_liunian=False)
        
        # 计算大运流年后能量 = 原局能量 + 大运流年增加的能量
        wuxing_final = {}
        shishen_final = {}
        for wuxing in ['木', '火', '土', '金', '水']:
            wuxing_final[wuxing] = original_energy['五行得分'].get(wuxing, 0) + wuxing_add[wuxing]
        
        for shishen in ['比', '劫', '食', '伤', '财', '才', '官', '杀', '印', '枭']:
            shishen_final[shishen] = original_energy['十神得分'].get(shishen, 0) + shishen_add[shishen]
        
        # 构建结果
        result = {
            '五行影响': {
                '原局能量': original_energy['五行得分'],
                '大运流年增加': wuxing_add,
                '大运流年增加详情': wuxing_add_details,
                '大运流年后能量': wuxing_final
            },
            '十神影响': {
                '原局能量': original_energy['十神得分'],
                '大运流年增加': shishen_add,
                '大运流年增加详情': shishen_add_details,
                '大运流年后能量': shishen_final
            }
        }
        
        return result
    
    def _generate_sixth_level_summary(self, sixth_result: Dict) -> str:
        """
        iii. 生成大运流年综合总结性分析说明
        """
        features = sixth_result.get('大运流年特征分析', {})
        gan_analysis = sixth_result.get('岁运天干分析', {})
        zhi_analysis = sixth_result.get('岁运地支分析', {})
        special_patterns = sixth_result.get('岁运特殊格局分析', {})
        ganzhi_analysis = sixth_result.get('岁运干支分析', {})
        impact = sixth_result.get('影响分析', {})
        
        summary_parts = []
        
        # 1. 大运流年特征总结
        feature_summary = features.get('特征总结', [])
        if feature_summary:
            summary_parts.append(f"大运流年特征: {'; '.join(feature_summary)}")
        
        # 2. 喜神用神判定
        xiyong_judgments = impact.get('喜神用神判定', [])
        if xiyong_judgments:
            summary_parts.append(f"喜忌判定: {'; '.join(xiyong_judgments)}")
        
        # 3. 天干影响总结
        gan_impact_count = 0
        for pillar, impacts in gan_analysis.get('大运天干影响', {}).items():
            gan_impact_count += len(impacts)
        for pillar, impacts in gan_analysis.get('流年天干影响', {}).items():
            gan_impact_count += len(impacts)
        
        if gan_impact_count > 0:
            summary_parts.append(f"天干影响: 大运流年天干与原局产生{gan_impact_count}项相互作用")
        
        # 4. 地支影响总结
        zhi_impact_count = 0
        for pillar, impacts in zhi_analysis.get('大运地支影响', {}).items():
            zhi_impact_count += len(impacts)
        for pillar, impacts in zhi_analysis.get('流年地支影响', {}).items():
            zhi_impact_count += len(impacts)
        
        if zhi_impact_count > 0:
            summary_parts.append(f"地支影响: 大运流年地支与原局产生{zhi_impact_count}项相互作用")
        
        # 5. 特殊格局总结
        triggered_patterns = special_patterns.get('引发的特殊格局', [])
        if triggered_patterns:
            summary_parts.append(f"特殊格局: {'; '.join(triggered_patterns[:3])}")
        
        # 6. 综合影响
        comprehensive_impacts = impact.get('综合影响', [])
        if comprehensive_impacts:
            summary_parts.append(f"综合影响: {'; '.join(comprehensive_impacts)}")
        
        # 7. 总体建议
        count_yinfa = len(impact.get('引发', []))
        count_pohuai = len(impact.get('破坏', []))
        
        if count_pohuai > count_yinfa * 2:
            summary_parts.append("建议: 本年需谨慎应对，注意规避风险")
        elif count_yinfa > count_pohuai * 2:
            summary_parts.append("建议: 本年运势较好，可积极进取")
        else:
            summary_parts.append("建议: 本年运势平稳，宜稳中求进")
        
        return '。'.join(summary_parts)
    
    def _get_extended_source_name(self, idx: int) -> str:
        """获取扩展来源名称"""
        if idx < 4:
            return ['年柱', '月柱', '日柱', '时柱'][idx]
        elif idx == 4:
            return '大运'
        else:
            return '流年'
    
    def print_sixth_level(self):
        """
        打印第六论级分析结果
        
        按照要求的结构输出:
        i. 先分析大运与流年的十二长生、空亡、纳音、神煞信息，给出分析结论
        ii. 将大运天干、流年天干和地支分别代入到年、月、日、时柱天干地支中分析大运、流年、年柱、月柱、日柱、时柱之间的相互影响
        iii. 最后给出大运流年综合总结性分析说明
        """
        from ganzhi import ten_deities, zhi5_list
        
        sixth_result = self.analysis_result.get('第六论级', {})
        if not sixth_result:
            print("\n【第六论级】未执行（需要指定流年年份）")
            return
        
        print("\n" + "=" * 80)
        print("【第六论级】大运流年综合分析")
        print("=" * 80)
        
        # ==================== i. 大运流年基本信息与特征分析 ====================
        basic_info = sixth_result.get('大运流年基本信息', {})
        print(f"\n【基本信息】")
        print(f"  流年: {basic_info.get('流年年份', '')}年 ({basic_info.get('流年干支', '')})")
        print(f"  当前大运: {basic_info.get('大运干支', '')} (第{basic_info.get('大运序号', 0)}运)")
        print(f"  大运年龄范围: {basic_info.get('大运年龄范围', '')}")
        
        # 打印大运列表
        dayun_list = basic_info.get('大运列表', [])
        if dayun_list:
            print(f"  大运列表: {', '.join(dayun_list)}")
        
        # 大运流年特征分析（十二长生、空亡、纳音、神煞）
        print(f"\n【大运流年特征分析】")
        features = sixth_result.get('大运流年特征分析', {})
        
        # 大运特征
        print(f"\n  大运特征:")
        dayun_features = features.get('大运', {})
        if dayun_features.get('十二长生'):
            cs = dayun_features['十二长生']
            print(f"    十二长生: 星运={cs.get('星运', '')}, 自坐={cs.get('自坐', '')}")
        if dayun_features.get('空亡'):
            print(f"    空亡: 是")
        if dayun_features.get('纳音'):
            print(f"    纳音: {dayun_features['纳音']}")
        if dayun_features.get('神煞'):
            print(f"    神煞: {', '.join(dayun_features['神煞'])}")
        
        # 流年特征
        print(f"\n  流年特征:")
        liunian_features = features.get('流年', {})
        if liunian_features.get('十二长生'):
            cs = liunian_features['十二长生']
            print(f"    十二长生: 星运={cs.get('星运', '')}, 自坐={cs.get('自坐', '')}")
        if liunian_features.get('空亡'):
            print(f"    空亡: 是")
        if liunian_features.get('纳音'):
            print(f"    纳音: {liunian_features['纳音']}")
        if liunian_features.get('神煞'):
            print(f"    神煞: {', '.join(liunian_features['神煞'])}")
        
        # 特征总结
        feature_summary = features.get('特征总结', [])
        if feature_summary:
            print(f"\n  【特征分析结论】")
            for summary in feature_summary:
                print(f"    - {summary}")
        
        # 岁运与原局相互影响分析
        print(f"\n【大运流年与原局相互影响分析】")

        # 岁运天干分析（按第三论级规则：天干五合、化气判定、天干相冲、天干相克）
        print(f"\n  【岁运天干分析】（按第三论级规则）")
        gan_analysis = sixth_result.get('岁运天干分析', {})
        
        # 收集所有天干五合
        wuhe_list = []
        for pillar_name, impacts in gan_analysis.get('大运天干影响', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干五合':
                    desc = self._add_shishen_to_gan(impact['描述'])
                    wuhe_list.append(desc)
        for pillar_name, impacts in gan_analysis.get('流年天干影响', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干五合':
                    desc = self._add_shishen_to_gan(impact['描述'])
                    wuhe_list.append(desc)
        for relation_name, impacts in gan_analysis.get('大运流年天干关系', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干五合':
                    desc = self._add_shishen_to_gan(impact['描述'])
                    wuhe_list.append(desc)
        if wuhe_list:
            print(f"    天干五合: {', '.join(wuhe_list)}")
        else:
            print(f"    天干五合: 无")
        
        # 收集所有天干相冲
        chong_list = []
        for pillar_name, impacts in gan_analysis.get('大运天干影响', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干相冲':
                    desc = self._add_shishen_to_gan(impact['描述'])
                    chong_list.append(desc)
        for pillar_name, impacts in gan_analysis.get('流年天干影响', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干相冲':
                    desc = self._add_shishen_to_gan(impact['描述'])
                    chong_list.append(desc)
        for relation_name, impacts in gan_analysis.get('大运流年天干关系', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干相冲':
                    desc = self._add_shishen_to_gan(impact['描述'])
                    chong_list.append(desc)
        if chong_list:
            print(f"    天干相冲: {', '.join(chong_list)}")
        else:
            print(f"    天干相冲: 无")
        
        # 收集所有天干相克
        ke_list = []
        for pillar_name, impacts in gan_analysis.get('大运天干影响', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干相克':
                    desc = self._add_shishen_to_gan(impact['描述'])
                    ke_list.append(desc)
        for pillar_name, impacts in gan_analysis.get('流年天干影响', {}).items():
            for impact in impacts:
                if impact['类型'] == '天干相克':
                    desc = self._add_shishen_to_gan(impact['描述'])
                    ke_list.append(desc)
        if ke_list:
            print(f"    天干相克: {', '.join(ke_list)}")
        else:
            print(f"    天干相克: 无")
        
        # 岁运地支分析（按第二论级规则：三会、拱会、三合、半合、拱合、六合、六破、六害、三刑、六冲、自刑、地支暗合）
        print(f"\n  【岁运地支分析】（按第二论级规则）")
        zhi_analysis = sixth_result.get('岁运地支分析', {})
        
        # 按类型分类收集所有地支关系（使用独立类型）
        rel_types = ['三会', '拱会', '三合', '半合', '拱合', '六合', '六破', '六害', '三刑', '六冲', '自刑', '地支暗合']
        all_rels = {rel_type: [] for rel_type in rel_types}
        
        # 收集大运地支影响
        for pillar_name, impacts in zhi_analysis.get('大运地支影响', {}).items():
            for impact in impacts:
                rel_type = impact['类型']
                if rel_type in all_rels:
                    desc = self._add_shishen_to_zhi(impact['描述'])
                    all_rels[rel_type].append(desc)

        # 收集流年地支影响
        for pillar_name, impacts in zhi_analysis.get('流年地支影响', {}).items():
            for impact in impacts:
                rel_type = impact['类型']
                if rel_type in all_rels:
                    desc = self._add_shishen_to_zhi(impact['描述'])
                    all_rels[rel_type].append(desc)

        # 收集大运流年地支之间关系
        for relation_name, impacts in zhi_analysis.get('大运流年地支关系', {}).items():
            for impact in impacts:
                rel_type = impact['类型']
                if rel_type in all_rels:
                    desc = self._add_shishen_to_zhi(impact['描述'])
                    all_rels[rel_type].append(desc)
        
        # 打印结果（去重后显示）
        for rel_type in rel_types:
            if all_rels[rel_type]:
                # 去重
                unique_rels = list(set(all_rels[rel_type]))
                print(f"    {rel_type}: {', '.join(unique_rels)}")
            else:
                print(f"    {rel_type}: 无")
        
        # ii.4 岁运干支分析（按第四论级规则：伏吟、反吟、盖头、截脚，以及天克地冲、岁运并临、伏吟）
        print(f"\n  【岁运干支分析】（按第四论级规则）")
        ganzhi_analysis = sixth_result.get('岁运干支分析', {})
        
        # 大运干支关系
        print(f"\n    大运干支关系:")
        dayun_rels = ganzhi_analysis.get('大运干支关系', {})
        for rel_type, value in dayun_rels.items():
            if isinstance(value, list) and value:
                value_with_shishen = [self._add_shishen_to_both(item) for item in value]
                print(f"      {rel_type}: {', '.join(value_with_shishen)}")
            elif isinstance(value, bool) and value:
                print(f"      {rel_type}: 是")

        # 流年干支关系
        print(f"\n    流年干支关系:")
        liunian_rels = ganzhi_analysis.get('流年干支关系', {})
        for rel_type, value in liunian_rels.items():
            if isinstance(value, list) and value:
                value_with_shishen = [self._add_shishen_to_both(item) for item in value]
                print(f"      {rel_type}: {', '.join(value_with_shishen)}")
            elif isinstance(value, bool) and value:
                print(f"      {rel_type}: 是")

        # 岁运与原局干支关系
        print(f"\n    岁运与原局干支关系:")
        ganzhi_pair_rels = ganzhi_analysis.get('岁运原局干支关系', {})
        for relation_name, relations in ganzhi_pair_rels.items():
            if relations:
                print(f"      {relation_name}:")
                for relation in relations:
                    relation_with_shishen = self._add_shishen_to_both(relation)
                    print(f"        - {relation_with_shishen}")
        
        # 岁运特殊格局分析（天克地冲、岁运并临、伏吟）- 并入岁运干支分析
        special_patterns = sixth_result.get('特殊流年分析', {})
        
        # 获取喜用神信息用于判断
        xiji_info = self.analysis_result.get('第五论级_定喜忌', {})
        xiyong_list = []
        jishen_list = []
        # 从调候用神、格局用神、日主强弱用神获取喜用神
        for key in ['调候用神', '格局用神', '日主强弱用神']:
            if key in xiji_info:
                yongshen = xiji_info[key]
                if isinstance(yongshen, list):
                    xiyong_list.extend(yongshen)
                elif isinstance(yongshen, str) and yongshen:
                    xiyong_list.extend(yongshen.split('、'))
        xiyong_list = list(set(xiyong_list))
        
        # 辅助函数：判断某柱对日主来说是喜用还是忌神
        def get_pillar_xi_ji(pillar_gan, pillar_zhi):
            """判断柱位对日主来说是喜用还是忌神"""
            # 天干十神
            gan_shishen = ten_deities.get(self.day_gan, {}).get(pillar_gan, '')
            # 地支十神（取本气）
            zhi_canggan = zhi5_list.get(pillar_zhi, []) if zhi5_list and pillar_zhi else []
            zhi_shishen = ten_deities.get(self.day_gan, {}).get(zhi_canggan[0], '') if zhi_canggan else ''
            
            # 判断天干是喜用还是忌
            gan_is_xiyong = any(xy in gan_shishen for xy in xiyong_list) if gan_shishen and xiyong_list else False
            zhi_is_xiyong = any(xy in zhi_shishen for xy in xiyong_list) if zhi_shishen and xiyong_list else False
            
            return {
                'gan_shishen': gan_shishen,
                'zhi_shishen': zhi_shishen,
                'gan_is_xiyong': gan_is_xiyong,
                'zhi_is_xiyong': zhi_is_xiyong,
                'is_xiyong': gan_is_xiyong or zhi_is_xiyong
            }
        
        # 辅助函数：获取柱位十神描述
        def get_pillar_shishen_desc(pillar_gan, pillar_zhi):
            """获取柱位十神描述，如戊午财杀"""
            info = get_pillar_xi_ji(pillar_gan, pillar_zhi)
            gan_shi = info['gan_shishen']
            zhi_shi = info['zhi_shishen']
            return f"{pillar_gan}{pillar_zhi}{gan_shi}{zhi_shi}"
        
        # 辅助函数：格式化喜忌神显示（如"比为喜用神，杀为忌神"）
        def format_xi_ji(gan_shishen, zhi_shishen, gan_is_xiyong, zhi_is_xiyong):
            """格式化喜忌神显示"""
            gan_xi_ji = "喜用神" if gan_is_xiyong else "忌神"
            zhi_xi_ji = "喜用神" if zhi_is_xiyong else "忌神"
            
            # 如果天干地支都是喜用神或都是忌神，简化显示
            if gan_is_xiyong and zhi_is_xiyong:
                return f"{gan_shishen}{zhi_shishen}为喜用神"
            elif not gan_is_xiyong and not zhi_is_xiyong:
                return f"{gan_shishen}{zhi_shishen}为忌神"
            else:
                # 分别显示
                return f"{gan_shishen}为{gan_xi_ji}，{zhi_shishen}为{zhi_xi_ji}"
        
        # 导入流年运势数据库用于打印详细信息
        try:
            from zonghe_database import LiuNianYunShiDatabase
            liunian_db = LiuNianYunShiDatabase()
        except:
            liunian_db = None
        
        # 天克地冲（打印基本信息和详细信息）
        tiankedichong_list = special_patterns.get('流年天克地冲', [])
        if tiankedichong_list:
            print(f"\n    ⚠️ 天克地冲（反吟）:")
            for item in tiankedichong_list:
                pillar = item['柱位']
                yuanju_gan = item['原局干支'][0]
                yuanju_zhi = item['原局干支'][1]
                
                # 获取原局柱位十神描述
                yuanju_desc = get_pillar_shishen_desc(yuanju_gan, yuanju_zhi)
                # 判断是喜用还是忌神
                yuanju_info = get_pillar_xi_ji(yuanju_gan, yuanju_zhi)
                xi_ji_desc = format_xi_ji(yuanju_info['gan_shishen'], yuanju_info['zhi_shishen'], 
                                          yuanju_info['gan_is_xiyong'], yuanju_info['zhi_is_xiyong'])
                
                print(f"      - 天克地冲：流年与{pillar}（{yuanju_desc}）天克地冲，冲克{yuanju_info['gan_shishen']}{yuanju_info['zhi_shishen']}（{xi_ji_desc}）")
                
                # 打印详细信息（从数据库获取）
                if liunian_db:
                    try:
                        # 获取天克地冲解析
                        tkdc_info = liunian_db.get_dict('天克地冲（反吟）', '整体定义')
                        tkdc_pillar = liunian_db.get_dict('天克地冲（反吟）', f'作用于{pillar}')
                        tkdc_strategy = liunian_db.get_dict('天克地冲（反吟）', f'分柱对应策略-{pillar}')
                        
                        if tkdc_info:
                            print(f"        【天克地冲整体定义】{tkdc_info.get('核心内容', '')}")
                        if tkdc_pillar:
                            print(f"        【作用于{pillar}】{tkdc_pillar.get('核心内容', '')}")
                        if tkdc_strategy:
                            print(f"        【对应策略】{tkdc_strategy.get('核心内容', '')}")
                    except Exception as e:
                        pass
        
        # 岁运并临（打印基本信息和详细信息）
        suiyun_binglin = special_patterns.get('岁运并临', {})
        if suiyun_binglin.get('发生'):
            print(f"\n    ⚠️ 岁运并临:")
            gan_zhi = suiyun_binglin['干支']
            # 判断岁运并临干支是喜用还是忌
            liunian_info = get_pillar_xi_ji(gan_zhi[0], gan_zhi[1])
            xi_ji_desc = format_xi_ji(liunian_info['gan_shishen'], liunian_info['zhi_shishen'], 
                                      liunian_info['gan_is_xiyong'], liunian_info['zhi_is_xiyong'])
            print(f"      - 岁运并临：流年大运干支{gan_zhi}（{liunian_info['gan_shishen']}{liunian_info['zhi_shishen']}，{xi_ji_desc}）")
            
            # 打印详细信息（从数据库获取，使用伏吟的定义）
            if liunian_db:
                try:
                    # 判断是喜用神还是忌神
                    xi_ji_type = "喜用神" if liunian_info['is_xiyong'] else "忌神"
                    
                    fuyin_info = liunian_db.get_dict('伏吟', '整体定义')
                    fuyin_xi_ji = liunian_db.get_dict('伏吟', f'作用于{xi_ji_type}')
                    
                    if fuyin_info:
                        print(f"        【岁运并临整体定义】{fuyin_info.get('核心内容', '')}")
                    if fuyin_xi_ji:
                        print(f"        【作用于{xi_ji_type}】{fuyin_xi_ji.get('核心内容', '')}")
                except Exception as e:
                    pass
        
        # 流年伏吟（打印基本信息和详细信息）
        liunian_fuyin = special_patterns.get('流年伏吟', [])
        if liunian_fuyin:
            print(f"\n    ⚠️ 流年伏吟:")
            for item in liunian_fuyin:
                pillar = item['柱位']
                fuyin_gan = item['干支'][0]
                fuyin_zhi = item['干支'][1]
                # 获取原局柱位十神描述
                yuanju_desc = get_pillar_shishen_desc(fuyin_gan, fuyin_zhi)
                # 判断是喜用还是忌神
                yuanju_info = get_pillar_xi_ji(fuyin_gan, fuyin_zhi)
                xi_ji_desc = format_xi_ji(yuanju_info['gan_shishen'], yuanju_info['zhi_shishen'], 
                                          yuanju_info['gan_is_xiyong'], yuanju_info['zhi_is_xiyong'])
                print(f"      - 流年伏吟：流年与{pillar}（{yuanju_desc}）伏吟，重叠{yuanju_info['gan_shishen']}{yuanju_info['zhi_shishen']}（{xi_ji_desc}）")
                
                # 打印详细信息（从数据库获取）
                if liunian_db:
                    try:
                        # 判断是喜用神还是忌神
                        xi_ji_type = "喜用神" if yuanju_info['is_xiyong'] else "忌神"
                        
                        fuyin_info = liunian_db.get_dict('伏吟', '整体定义')
                        fuyin_pillar = liunian_db.get_dict('伏吟', f'作用于{pillar}')
                        fuyin_xi_ji = liunian_db.get_dict('伏吟', f'作用于{xi_ji_type}')
                        fuyin_strategy = liunian_db.get_dict('伏吟', f'分柱对应策略-{pillar}')
                        
                        if fuyin_info:
                            print(f"        【伏吟整体定义】{fuyin_info.get('核心内容', '')}")
                        if fuyin_xi_ji:
                            print(f"        【作用于{xi_ji_type}】{fuyin_xi_ji.get('核心内容', '')}")
                        if fuyin_pillar:
                            print(f"        【作用于{pillar}】{fuyin_pillar.get('核心内容', '')}")
                        if fuyin_strategy:
                            print(f"        【对应策略】{fuyin_strategy.get('核心内容', '')}")
                    except Exception as e:
                        pass
        
        # 大运伏吟（仅打印基本信息）
        dayun_fuyin = special_patterns.get('大运伏吟', [])
        if dayun_fuyin:
            print(f"\n    ⚠️ 大运伏吟:")
            for item in dayun_fuyin:
                pillar = item['柱位']
                fuyin_gan = item['干支'][0]
                fuyin_zhi = item['干支'][1]
                # 获取原局柱位十神描述
                yuanju_desc = get_pillar_shishen_desc(fuyin_gan, fuyin_zhi)
                # 判断是喜用还是忌神
                yuanju_info = get_pillar_xi_ji(fuyin_gan, fuyin_zhi)
                xi_ji_type = "喜用神" if yuanju_info['is_xiyong'] else "忌神"
                print(f"      - 大运伏吟：大运与{pillar}（{yuanju_desc}）伏吟，重叠{yuanju_info['gan_shishen']}{yuanju_info['zhi_shishen']}（{xi_ji_type}）")
        
        # ==================== iii. 综合影响分析 ====================
        print(f"\n【综合影响分析】")
        impact = sixth_result.get('影响分析', {})
        
        # 喜神用神判定
        xiyong_judgments = impact.get('喜神用神判定', [])
        if xiyong_judgments:
            print(f"\n  喜神用神判定:")
            for judgment in xiyong_judgments:
                print(f"    - {judgment}")
        
        # 引发的新格局
        yinfa_items = impact.get('引发', [])
        if yinfa_items:
            print(f"\n  引发的新格局（共{len(yinfa_items)}项）:")
            for item in yinfa_items:
                print(f"    - {item}")
        
        # 破坏的格局
        pohuai_items = impact.get('破坏', [])
        if pohuai_items:
            print(f"\n  破坏的格局（共{len(pohuai_items)}项）:")
            for item in pohuai_items:
                print(f"    - {item}")
        
        # 综合影响
        comprehensive_impacts = impact.get('综合影响', [])
        if comprehensive_impacts:
            print(f"\n  综合影响:")
            for impact_item in comprehensive_impacts:
                print(f"    - {impact_item}")
        
        # ==================== iii. 大运流年综合总结性分析说明 ====================
        print(f"\n【大运流年综合总结性分析说明】")
        summary = sixth_result.get('综合评语', '')
        if summary:
            # 将长总结分段显示
            sentences = summary.split('。')
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    print(f"  {i+1}. {sentence.strip()}")
        else:
            print(f"  （未生成综合总结）")
        
        # ==================== iv. 大运流年对原局能量影响分析 ====================
        print(f"\n【大运流年对原局能量影响分析】")
        energy_impact = sixth_result.get('大运流年对原局能量影响', {})
        
        # 打印五行能量影响（按最终能量从高到低排序，标注占比）
        wuxing_impact = energy_impact.get('五行影响', {})
        if wuxing_impact:
            print(f"\n  五行能量影响:")
            original_wuxing = wuxing_impact.get('原局能量', {})
            added_wuxing = wuxing_impact.get('大运流年增加', {})
            added_wuxing_details = wuxing_impact.get('大运流年增加详情', {})
            final_wuxing = wuxing_impact.get('大运流年后能量', {})
            
            wuxing_order = ['木', '火', '土', '金', '水']
            
            # 按最终能量从高到低排序
            wuxing_sorted = sorted(wuxing_order, key=lambda w: final_wuxing.get(w, 0), reverse=True)
            
            # 计算总能量和占比
            total_final_score = sum(final_wuxing.get(w, 0) for w in wuxing_order)
            
            for wuxing in wuxing_sorted:
                orig = original_wuxing.get(wuxing, 0)
                added = added_wuxing.get(wuxing, 0)
                final = final_wuxing.get(wuxing, 0)
                details = added_wuxing_details.get(wuxing, [])
                # 计算占比
                if total_final_score > 0:
                    percentage = (final / total_final_score * 100) if final > 0 else 0
                else:
                    percentage = 0
                print(f"    {wuxing}: 原局{orig:.1f}分 → 增加{added:+.1f}分 → 大运流年后{final:.1f}分 (占比{percentage:.1f}%)")
                if details:
                    for detail in details:
                        print(f"      - {detail}")
        
        # 打印十神能量影响（按最终能量从高到低排序，标注占比）
        shishen_impact = energy_impact.get('十神影响', {})
        if shishen_impact:
            print(f"\n  十神能量影响:")
            original_shishen = shishen_impact.get('原局能量', {})
            added_shishen = shishen_impact.get('大运流年增加', {})
            added_shishen_details = shishen_impact.get('大运流年增加详情', {})
            final_shishen = shishen_impact.get('大运流年后能量', {})
            
            shishen_full_names = {
                '比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官',
                '财': '正财', '才': '偏财', '官': '正官', '杀': '七杀',
                '印': '正印', '枭': '偏印'
            }
            shishen_order = ['比', '劫', '食', '伤', '财', '才', '官', '杀', '印', '枭']
            
            # 按最终能量从高到低排序
            shishen_sorted = sorted(shishen_order, key=lambda s: final_shishen.get(s, 0), reverse=True)
            
            # 计算总能量和占比
            total_final_shishen_score = sum(final_shishen.get(s, 0) for s in shishen_order)
            
            for shishen in shishen_sorted:
                orig = original_shishen.get(shishen, 0)
                added = added_shishen.get(shishen, 0)
                final = final_shishen.get(shishen, 0)
                details = added_shishen_details.get(shishen, [])
                full_name = shishen_full_names.get(shishen, shishen)
                # 计算占比
                if total_final_shishen_score > 0:
                    percentage = (final / total_final_shishen_score * 100) if final > 0 else 0
                else:
                    percentage = 0
                print(f"    {full_name}({shishen}): 原局{orig:.1f}分 → 增加{added:+.1f}分 → 大运流年后{final:.1f}分 (占比{percentage:.1f}%)")
                if details:
                    for detail in details:
                        print(f"      - {detail}")
        
        # ==================== v. 历史大运对原局能量影响分析 ====================
        print(f"\n【历史大运对原局能量影响分析】")
        historical_impact = sixth_result.get('历史大运对原局能量影响', {})
        
        if historical_impact.get('历史大运', []):
            print(f"  {historical_impact.get('分析说明', '')}\n")
            
            shishen_full_names = {
                '比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官',
                '财': '正财', '才': '偏财', '官': '正官', '杀': '七杀',
                '印': '正印', '枭': '偏印'
            }
            
            for dayun_data in historical_impact['历史大运']:
                print(f"  ▶ {dayun_data['大运干支']} ({dayun_data['时间范围']})")
                
                # 打印五行能量
                wuxing_energy = dayun_data.get('五行能量', {})
                if wuxing_energy:
                    print(f"    五行能量影响:")
                    wuxing_original = wuxing_energy.get('原局能量', {})
                    wuxing_added = wuxing_energy.get('大运增加', {})
                    wuxing_final = wuxing_energy.get('大运后能量', {})
                    wuxing_percentages = wuxing_energy.get('占比', {})
                    wuxing_details_map = wuxing_energy.get('详情', {})
                    
                    for wuxing in dayun_data.get('五行排序', []):
                        orig = wuxing_original.get(wuxing, 0)
                        added = wuxing_added.get(wuxing, 0)
                        final = wuxing_final.get(wuxing, 0)
                        percentage = wuxing_percentages.get(wuxing, 0)
                        details = wuxing_details_map.get(wuxing, [])
                        
                        if final > 0 or added != 0:  # 显示有变化或最终有能量的
                            print(f"      {wuxing}: 原局{orig:.1f}分 → 增加{added:+.1f}分 → 大运后{final:.1f}分 (占比{percentage:.1f}%)")
                            if details:
                                for detail in details:
                                    print(f"        - {detail}")
                
                # 打印十神能量
                shishen_energy = dayun_data.get('十神能量', {})
                if shishen_energy:
                    print(f"    十神能量影响:")
                    shishen_original = shishen_energy.get('原局能量', {})
                    shishen_added = shishen_energy.get('大运增加', {})
                    shishen_final = shishen_energy.get('大运后能量', {})
                    shishen_percentages = shishen_energy.get('占比', {})
                    shishen_details_map = shishen_energy.get('详情', {})
                    
                    for shishen in dayun_data.get('十神排序', []):
                        orig = shishen_original.get(shishen, 0)
                        added = shishen_added.get(shishen, 0)
                        final = shishen_final.get(shishen, 0)
                        percentage = shishen_percentages.get(shishen, 0)
                        full_name = shishen_full_names.get(shishen, shishen)
                        details = shishen_details_map.get(shishen, [])
                        
                        if final > 0 or added != 0:  # 显示有变化或最终有能量的
                            print(f"      {full_name}({shishen}): 原局{orig:.1f}分 → 增加{added:+.1f}分 → 大运后{final:.1f}分 (占比{percentage:.1f}%)")
                            if details:
                                for detail in details:
                                    print(f"        - {detail}")
                print()
        else:
            print(f"  {historical_impact.get('分析说明', '无历史大运数据')}")
        
        print("\n" + "=" * 80)
    
    def _get_birth_year(self) -> int:
        """获取出生年份（简化版，实际需要从输入解析）"""
        # 这里简化处理，实际应该从八字输入中解析
        year_gan = self.gans[0]
        year_zhi = self.zhis[0]
        
        # 粗略估算（假设在2000年左右）
        ganzhi_order = ['甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', 
                        '庚午', '辛未', '壬申', '癸酉', '甲戌', '乙亥',
                        '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳',
                        '壬午', '癸未', '甲申', '乙酉', '丙戌', '丁亥',
                        '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳',
                        '甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥',
                        '庚子', '辛丑', '壬寅', '癸卯', '甲辰', '乙巳',
                        '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥',
                        '壬子', '癸丑', '甲寅', '乙卯', '丙辰', '丁巳',
                        '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥']
        
        year_ganzhi = year_gan + year_zhi
        try:
            idx = ganzhi_order.index(year_ganzhi)
            # 1984年是甲子
            base_year = 1984
            offset = idx - (0 % 60)  # 甲子在索引0
            return base_year + offset
        except ValueError:
            return 1984  # 默认值
    
    def _calculate_historical_dayun_impact(self, current_year: int) -> Dict:
        """
        计算历史大运对原局能量影响
        
        分析用户当前大运及之前的所有大运（根据当前流年年份判断），
        计算每个大运对原局五行能量和十神能量的影响
        
        参数:
            current_year: 当前流年年份
            
        返回:
            {
                '历史大运': [
                    {
                        '大运干支': '己未',
                        '时间范围': '2006~2016',
                        '五行能量': {
                            '原局能量': {...},
                            '大运增加': {...},
                            '大运后能量': {...},
                            '占比': {...},
                            '详情': {...}
                        },
                        '十神能量': {...}
                    },
                    ...
                ],
                '当前大运': '辛酉',
                '分析说明': '...'
            }
        """
        from ganzhi import gan5, zhi5_list, ten_deities
        
        result = {
            '历史大运': [],
            '当前大运': '',
            '分析说明': ''
        }
        
        if not self.dayun_liunian or not current_year:
            return result
        
        day_gan = self.day_gan
        
        # 获取原局能量分数（不包含大运流年）
        original_energy = self._calculate_wuxing_shishen_scores(include_dayun_liunian=False)
        original_wuxing = original_energy['五行得分']
        original_shishen = original_energy['十神得分']
        
        # 先确定当前运行的大运
        current_dayun_info = None
        for dayun in self.dayun_liunian.dayuns:
            start_date = dayun.get('start_date', '')
            if start_date:
                from datetime import datetime
                try:
                    start_year = datetime.strptime(start_date, "%Y-%m-%d").year
                except Exception:
                    birth_year = self._get_birth_year()
                    qiyun_age = self.dayun_liunian.qiyun_age if hasattr(self.dayun_liunian, 'qiyun_age') else 3
                    start_year = birth_year + qiyun_age + (dayun['index'] - 1) * 10
            else:
                birth_year = self._get_birth_year()
                qiyun_age = self.dayun_liunian.qiyun_age if hasattr(self.dayun_liunian, 'qiyun_age') else 3
                start_year = birth_year + qiyun_age + (dayun['index'] - 1) * 10
            
            end_year = start_year + 10
            
            # 判断是否为当前运行的大运（当前年份在该大运的时间范围内）
            if start_year <= current_year < end_year:
                current_dayun_info = {
                    '大运干支': dayun['gan_zhi'],
                    '大运天干': dayun['gan'],
                    '大运地支': dayun['zhi'],
                    '时间范围': f"{start_year}~{end_year}",
                    '开始年份': start_year,
                    '结束年份': end_year,
                    '序号': dayun['index']
                }
                result['当前大运'] = dayun['gan_zhi']
                break
        
        # 获取当前大运之前的所有历史大运（不包括当前大运）
        historical_dayuns = []
        current_dayun_index = current_dayun_info['序号'] if current_dayun_info else 999
        
        for dayun in self.dayun_liunian.dayuns:
            start_date = dayun.get('start_date', '')
            if start_date:
                from datetime import datetime
                try:
                    start_year = datetime.strptime(start_date, "%Y-%m-%d").year
                except Exception:
                    birth_year = self._get_birth_year()
                    qiyun_age = self.dayun_liunian.qiyun_age if hasattr(self.dayun_liunian, 'qiyun_age') else 3
                    start_year = birth_year + qiyun_age + (dayun['index'] - 1) * 10
            else:
                birth_year = self._get_birth_year()
                qiyun_age = self.dayun_liunian.qiyun_age if hasattr(self.dayun_liunian, 'qiyun_age') else 3
                start_year = birth_year + qiyun_age + (dayun['index'] - 1) * 10
            
            end_year = start_year + 10
            
            # 只取当前大运之前的大运（序号 < 当前大运序号），不包括当前大运
            if dayun['index'] < current_dayun_index:
                historical_dayuns.append({
                    '大运干支': dayun['gan_zhi'],
                    '大运天干': dayun['gan'],
                    '大运地支': dayun['zhi'],
                    '时间范围': f"{start_year}~{end_year}",
                    '开始年份': start_year,
                    '结束年份': end_year,
                    '序号': dayun['index']
                })
        
        if not historical_dayuns:
            result['分析说明'] = f'根据当前流年{current_year}年，尚未有已完成的大运'
            return result
        
        # 计算每个已过大运的能量影响
        wuxing_order = ['木', '火', '土', '金', '水']
        shishen_order = ['比', '劫', '食', '伤', '财', '才', '官', '杀', '印', '枭']
        
        for dayun_info in historical_dayuns:
            dayun_gan = dayun_info['大运天干']
            dayun_zhi = dayun_info['大运地支']
            
            # 初始化大运增加的能量得分
            wuxing_added = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
            shishen_added = {'比': 0, '劫': 0, '食': 0, '伤': 0, '财': 0, '才': 0, '官': 0, '杀': 0, '印': 0, '枭': 0}
            wuxing_details = {'木': [], '火': [], '土': [], '金': [], '水': []}
            shishen_details = {'比': [], '劫': [], '食': [], '伤': [], '财': [], '才': [], '官': [], '杀': [], '印': [], '枭': []}
            
            # 1. 大运天干能量（五行+1，十神+1）
            if dayun_gan:
                wuxing = gan5.get(dayun_gan, '')
                shishen = ten_deities.get(day_gan, {}).get(dayun_gan, '')
                if wuxing:
                    wuxing_added[wuxing] += 1
                    wuxing_details[wuxing].append(f'大运天干{dayun_gan}五行{wuxing}+1')
                if shishen:
                    shishen_added[shishen] += 1
                    shishen_details[shishen].append(f'大运天干{dayun_gan}十神{shishen}+1')
            
            # 2. 大运地支能量（本气+1.8，中气+0.9，余气+0.3）
            if dayun_zhi:
                canggan_list = zhi5_list.get(dayun_zhi, [])
                for i, canggan in enumerate(canggan_list):
                    qi_type = '本气' if i == 0 else ('中气' if i == 1 else '余气')
                    dayun_score = self.SCORE_DAYUN
                    if i == 0:  # 本气
                        score_wx = dayun_score['大运藏干_本气']['wuxing']
                        score_ss = dayun_score['大运藏干_本气']['shishen']
                    elif i == 1:  # 中气
                        score_wx = dayun_score['大运藏干_中气']['wuxing']
                        score_ss = dayun_score['大运藏干_中气']['shishen']
                    else:  # 余气
                        score_wx = dayun_score['大运藏干_余气']['wuxing']
                        score_ss = dayun_score['大运藏干_余气']['shishen']
                    
                    wuxing = gan5.get(canggan, '')
                    shishen = ten_deities.get(day_gan, {}).get(canggan, '')
                    if wuxing:
                        wuxing_added[wuxing] += score_wx
                        wuxing_details[wuxing].append(f'大运地支{dayun_zhi}藏干{canggan}({qi_type})五行{wuxing}+{score_wx}')
                    if shishen:
                        shishen_added[shishen] += score_ss
                        shishen_details[shishen].append(f'大运地支{dayun_zhi}藏干{canggan}({qi_type})十神{shishen}+{score_ss}')
                
                # 计算大运地支与原局地支的关系
                for i, zhi in enumerate(self.zhis):
                    zhi_name = ['年支', '月支', '日支', '时支'][i]
                    # 六合
                    liuhe_pairs = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), ('辰', '酉'), ('巳', '申'), ('午', '未')]
                    for z1, z2 in liuhe_pairs:
                        if (dayun_zhi == z1 and zhi == z2) or (dayun_zhi == z2 and zhi == z1):
                            # 六合对应五行
                            liuhe_wuxing = {'子丑': '土', '寅亥': '木', '卯戌': '火', '辰酉': '金', '巳申': '水', '午未': '土'}
                            wuxing = liuhe_wuxing.get(f'{z1}{z2}', liuhe_wuxing.get(f'{z2}{z1}', ''))
                            if wuxing:
                                wuxing_added[wuxing] += 1
                                wuxing_details[wuxing].append(f'大运{dayun_zhi}与原局{zhi_name}{zhi}六合{wuxing}+1')
                            break
                    
                    # 六冲
                    chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
                    for z1, z2 in chong_pairs:
                        if (dayun_zhi == z1 and zhi == z2) or (dayun_zhi == z2 and zhi == z1):
                            wuxing = gan5.get(zhi, '')
                            if wuxing:
                                wuxing_added[wuxing] -= 0.5
                                wuxing_details[wuxing].append(f'大运{dayun_zhi}与原局{zhi_name}{zhi}六冲{wuxing}-0.5')
                            break
            
            # 计算大运后的能量 = 原局能量 + 大运增加
            wuxing_final = {w: original_wuxing[w] + wuxing_added[w] for w in wuxing_order}
            shishen_final = {s: original_shishen[s] + shishen_added[s] for s in shishen_order}
            
            # 计算大运后五行占比
            total_wuxing_final = sum(max(wuxing_final[w], 0) for w in wuxing_order)
            wuxing_percentages = {}
            for w in wuxing_order:
                if total_wuxing_final > 0 and wuxing_final[w] > 0:
                    wuxing_percentages[w] = (wuxing_final[w] / total_wuxing_final * 100)
                else:
                    wuxing_percentages[w] = 0
            
            # 计算大运后十神占比
            total_shishen_final = sum(max(shishen_final[s], 0) for s in shishen_order)
            shishen_percentages = {}
            for s in shishen_order:
                if total_shishen_final > 0 and shishen_final[s] > 0:
                    shishen_percentages[s] = (shishen_final[s] / total_shishen_final * 100)
                else:
                    shishen_percentages[s] = 0
            
            # 按大运后能量排序
            wuxing_sorted = sorted(wuxing_order, key=lambda w: wuxing_final[w], reverse=True)
            shishen_sorted = sorted(shishen_order, key=lambda s: shishen_final[s], reverse=True)
            
            result['历史大运'].append({
                '大运干支': dayun_info['大运干支'],
                '时间范围': dayun_info['时间范围'],
                '是否当前大运': dayun_info.get('是否当前大运', False),
                '五行能量': {
                    '原局能量': original_wuxing,
                    '大运增加': wuxing_added,
                    '大运后能量': wuxing_final,
                    '占比': wuxing_percentages,
                    '详情': wuxing_details
                },
                '十神能量': {
                    '原局能量': original_shishen,
                    '大运增加': shishen_added,
                    '大运后能量': shishen_final,
                    '占比': shishen_percentages,
                    '详情': shishen_details
                },
                '五行排序': wuxing_sorted,
                '十神排序': shishen_sorted
            })
        
        result['分析说明'] = f'已分析当前大运之前的共{len(historical_dayuns)}个历史大运对原局的影响'
        return result
    
    def print_analysis(self):
        """打印完整的分析结果（支持三柱或四柱）"""
        from ganzhi import ten_deities, zhi5_list
        
        # 辅助函数：给文本中的天干添加十神
        def add_shishen_to_gan(text):
            if not text or text == '无':
                return text
            result = text
            for gan in ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
                if gan in result:
                    shishen = ten_deities.get(self.day_gan, {}).get(gan, '')
                    if shishen:
                        result = result.replace(gan, f"{gan}（{shishen}）", 1)
            return result
        
        # 辅助函数：给文本中的地支添加十神
        def add_shishen_to_zhi(text):
            if not text or text == '无':
                return text
            result = text
            for zhi in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
                if zhi in result:
                    canggan = zhi5_list.get(zhi, [])
                    if canggan and self.day_gan in ten_deities:
                        shishen = ten_deities[self.day_gan].get(canggan[0], '')
                        if shishen:
                            result = result.replace(zhi, f"{zhi}（{shishen}）", 1)
            return result
        
        # 辅助函数：给文本中的天干和地支都添加十神
        def add_shishen_to_both(text):
            if not text or text == '无':
                return text
            result = add_shishen_to_gan(text)
            result = add_shishen_to_zhi(result)
            return result
        
        print("=" * 80)
        print("八字格局分析结果 - 五级论级体系 + 第六论级（大运流年）")
        print("=" * 80)
        
        # 打印基本信息
        print(f"\n【八字】")
        print(f"年柱: {self.gans[0]}{self.zhis[0]}")
        print(f"月柱: {self.gans[1]}{self.zhis[1]}")
        print(f"日柱: {self.gans[2]}{self.zhis[2]}")
        if self.has_time_pillar and len(self.gans) > 3 and len(self.zhis) > 3:
            print(f"时柱: {self.gans[3]}{self.zhis[3]}")
        else:
            print(f"时柱: (未提供)")
        
        # 打印第一论级
        print(f"\n【第一论级_月令与格局】")
        first_level = self.analysis_result.get('第一论级_月令与格局', {})
        print(f"月令: {first_level.get('月令', '')}")
        print(f"月令藏干: {first_level.get('月令藏干', [])}")
        print(f"月令主气: {first_level.get('月令主气', '')}")
        print(f"主要格局: {first_level.get('主要格局', '')}")
        if first_level.get('格局类别'):
            print(f"格局类别: {first_level.get('格局类别', '')}")
        if first_level.get('格局定义'):
            print(f"格局定义: {first_level.get('格局定义', '')}")
        if first_level.get('格局条件'):
            print(f"格局条件: {first_level.get('格局条件', '')}")
        if first_level.get('格局喜忌'):
            print(f"格局喜忌: {first_level.get('格局喜忌', '')}")
        if first_level.get('格局古籍'):
            print(f"格局古籍: {first_level.get('格局古籍', '')}")

        secondary_gejus = first_level.get('次要格局', [])
        if secondary_gejus:
            print(f"次要格局: {', '.join(secondary_gejus)}")
        else:
            print(f"次要格局: 无")
        if first_level.get('格局说明'):
            print(f"格局说明: {first_level.get('格局说明', '')}")
        print(f"五行旺相: {first_level.get('五行旺相', '')}")
        
        # 打印第二论级
        print(f"\n【第二论级_地支关系】")
        second_level = self.analysis_result.get('第二论级_地支关系', {})
        for key, value in second_level.items():
            if key == '刑冲克害说明':
                print(f"{key}: {value if value else '无'}")
            else:
                # 给地支添加十神
                if isinstance(value, list):
                    value_with_shishen = [add_shishen_to_zhi(item) for item in value]
                    print(f"{key}: {value_with_shishen if value_with_shishen else '无'}")
                else:
                    print(f"{key}: {add_shishen_to_zhi(value) if value else '无'}")
        
        # 打印第三论级
        print(f"\n【第三论级_天干关系】")
        third_level = self.analysis_result.get('第三论级_天干关系', {})
        for key, value in third_level.items():
            # 给天干添加十神
            if isinstance(value, list):
                value_with_shishen = [add_shishen_to_gan(item) for item in value]
                print(f"{key}: {value_with_shishen if value_with_shishen else '无'}")
            else:
                print(f"{key}: {add_shishen_to_gan(value) if value else '无'}")
        


        # 打印第四论级 - 天干与地支的关系
        print(f"\n【第四论级_天干与地支的关系】")
        gan_zhi_level = self.analysis_result.get('第四论级_天干与地支的关系', {})
        for key, value in gan_zhi_level.items():
            if value:
                print(f"{key}:")
                for item in value:
                    # 给干支关系添加十神
                    item_with_shishen = add_shishen_to_both(item)
                    print(f"  - {item_with_shishen}")
            else:
                print(f"{key}: 无")

        # 打印第五论级 - 大运流年（已删除详细打印）
        
        # 打印第五论级 - 定喜忌
        print(f"\n【第五论级_定喜忌】")
        xiji = self.analysis_result.get('第五论级_定喜忌', {})

        # 打印喜用神（衰旺论）- 参考geju_database.py实现
        print(f"\n喜用神（衰旺论）：")
        # 获取原局和综合强弱判定
        first_level = self.analysis_result.get('第一论级_月令与格局', {})
        # 身强身弱信息直接存储在'身强身弱'键下
        yuanju_qiangruo = first_level.get('身强身弱', '')
        day_gan = self.day_gan if hasattr(self, 'day_gan') else ''

        # 判断是否为均衡格
        if yuanju_qiangruo == '均衡':
            # 均衡格统一按照身弱来分析
            print(f"  原局判定: 均衡格（按身弱分析）")
            final_qiangruo = '偏弱'  # 均衡格按身弱处理
        elif yuanju_qiangruo:
            # 非均衡格直接使用原局判定
            final_qiangruo = yuanju_qiangruo
            print(f"  强弱判定: {final_qiangruo}")
        else:
            print(f"  强弱判定: 未判定")
            final_qiangruo = ''

        # 使用GeJuDatabase获取喜用神
        if GeJuDatabase:
            try:
                db = GeJuDatabase()
                xiyongshen = db.get_xiyongshen(day_gan, final_qiangruo)
                if 'error' not in xiyongshen:
                    print(f"  日主: {xiyongshen.get('日主', day_gan)}")
                    print(f"  喜用神: {xiyongshen.get('喜神', '无')}")
                    print(f"  忌神: {xiyongshen.get('忌神', '无')}")
                    if '成长建议' in xiyongshen and xiyongshen['成长建议']:
                        print(f"\n  【成长建议】")
                        for line in xiyongshen['成长建议'].split('\n'):
                            if line.strip():
                                print(f"  {line}")
                else:
                    # 使用内部方法获取喜用神
                    xi_shen = xiji.get('喜神', [])
                    yong_shen = xiji.get('用神', [])
                    ji_shen_list = xiji.get('忌神', [])
                    print(f"  日主: {day_gan}")
                    print(f"  喜神: {'、'.join(xi_shen) if xi_shen else '无'}")
                    print(f"  用神: {'、'.join(yong_shen) if yong_shen else '无'}")
                    print(f"  忌神: {'、'.join(ji_shen_list) if ji_shen_list else '无'}")
            except Exception as e:
                # 使用内部方法获取喜用神
                xi_shen = xiji.get('喜神', [])
                yong_shen = xiji.get('用神', [])
                ji_shen_list = xiji.get('忌神', [])
                print(f"  日主: {day_gan}")
                print(f"  喜神: {'、'.join(xi_shen) if xi_shen else '无'}")
                print(f"  用神: {'、'.join(yong_shen) if yong_shen else '无'}")
                print(f"  忌神: {'、'.join(ji_shen_list) if ji_shen_list else '无'}")
        else:
            # 使用内部方法获取喜用神
            xi_shen = xiji.get('喜神', [])
            yong_shen = xiji.get('用神', [])
            ji_shen_list = xiji.get('忌神', [])
            print(f"  日主: {day_gan}")
            print(f"  喜神: {'、'.join(xi_shen) if xi_shen else '无'}")
            print(f"  用神: {'、'.join(yong_shen) if yong_shen else '无'}")
            print(f"  忌神: {'、'.join(ji_shen_list) if ji_shen_list else '无'}")

        # 打印调候派用神
        print(f"\n调候派：")
        tiaohou_yongshen = xiji.get('调候用神', [])
        if tiaohou_yongshen:
            # 将多个用神用顿号连接打印在同一行
            print(f"  {'、'.join(tiaohou_yongshen)}")
        else:
            print(f"  无")

        # 打印调候说明（合并调候提要）
        diahou_shuoming = xiji.get('调候分析', '')
        tiaohou_tiyao = xiji.get('调候提要', '')
        if diahou_shuoming and tiaohou_tiyao:
            print(f"\n调候说明: {diahou_shuoming}。{tiaohou_tiyao}")
        elif diahou_shuoming:
            print(f"\n调候说明: {diahou_shuoming}")
        elif tiaohou_tiyao:
            print(f"\n调候说明: {tiaohou_tiyao}")
        else:
            print(f"\n调候说明: 无")

        # 打印寒燥分析
        hanzao_analysis = xiji.get('寒燥分析', {})
        if hanzao_analysis:
            print(f"\n寒燥分析：")
            print(f"  {hanzao_analysis.get('局型', '')}，{hanzao_analysis.get('核心原则', '')}")
            print(f"  病症：{hanzao_analysis.get('病症', '')}")
            zhu_yongshen = hanzao_analysis.get('主用神', [])
            if zhu_yongshen:
                print(f"  主用神：{'；'.join(zhu_yongshen)}")
            fu_yongshen = hanzao_analysis.get('辅用神', [])
            if fu_yongshen:
                print(f"  辅用神：{'；'.join(fu_yongshen)}")
            ji_shen = hanzao_analysis.get('忌神', [])
            if ji_shen:
                print(f"  忌神：{'、'.join(ji_shen)}")

        # 打印第五论级 - 辅助信息
        print(f"\n【第五论级_辅助信息】")
        aux_info = self.analysis_result.get('第五论级_辅助信息', {})
        
        # 打印十二长生
        print("\n十二长生:")
        changsheng_data = aux_info.get('十二长生', {})
        for pillar, data in changsheng_data.items():
            print(f"  {pillar}: 星运-{data.get('星运', '')} 自坐-{data.get('自坐', '')}")
        
        # 打印空亡
        print("\n空亡:")
        kongwang_data = aux_info.get('空亡', {})
        for pillar, kong_info in kongwang_data.items():
            if isinstance(kong_info, dict):
                is_kong = kong_info.get('空亡', False)
                if is_kong:
                    zhi = kong_info.get('地支', '')
                    source = kong_info.get('旬来源', '')
                    detail = kong_info.get('空亡详情', '')
                    status = f'空亡({zhi}) - {detail}，由{source}确定'
                else:
                    status = ''
            else:
                status = '空' if kong_info else ''  # 兼容旧格式
            print(f"  {pillar}: {status}")
        
        # 打印纳音
        print("\n纳音:")
        nayin_data = aux_info.get('纳音', {})
        for pillar, nayin in nayin_data.items():
            print(f"  {pillar}: {nayin}")
        
        # 打印神煞
        print("\n神煞:")
        shensha_data = aux_info.get('神煞', {})
        for pillar, shensha_list in shensha_data.items():
            if shensha_list:
                print(f"  {pillar}: {', '.join(shensha_list)}")
        
        # 打印综合格局判定
        print(f"\n【格局综合判定】")
        final_geju = self.analysis_result.get('格局综合判定', {})
        print(f"主格局: {final_geju.get('主格局', '')}")

        # 打印原局五行能量分析（按能量高低排序，标注占比）
        print(f"\n【原局五行能量分析】")
        wuxing_scores = final_geju.get('五行能量分析', {})
        wuxing_details = final_geju.get('五行详情', {})

        wuxing_order = ['木', '火', '土', '金', '水']
        
        # 计算总能量（取正值总和）
        total_wuxing_score = sum(max(wuxing_scores.get(w, 0), 0) for w in wuxing_order)
        
        # 按能量从高到低排序
        wuxing_sorted = sorted(wuxing_order, key=lambda w: wuxing_scores.get(w, 0), reverse=True)
        
        for wuxing in wuxing_sorted:
            score = wuxing_scores.get(wuxing, 0)
            details = wuxing_details.get(wuxing, [])
            # 计算占比
            if total_wuxing_score > 0:
                percentage = (max(score, 0) / total_wuxing_score * 100) if score > 0 else 0
            else:
                percentage = 0
            
            if score != 0 or details:
                print(f"  {wuxing} ({score:.1f}分, 占比{percentage:.1f}%):")
                if details:
                    for detail in details:
                        print(f"    - {detail}")
                else:
                    print(f"    无加分/减分")
            else:
                print(f"  {wuxing}: 无 (占比0.0%)")

        # 打印原局十神能量分析（按能量高低排序，标注占比，不省略任何十神）
        print(f"\n【原局十神能量分析】")
        shishen_scores = final_geju.get('十神能量分析', {})
        shishen_details = final_geju.get('十神详情', {})

        # 十神完整名称映射
        shishen_full_names = {
            '比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官',
            '财': '正财', '才': '偏财', '官': '正官', '杀': '七杀',
            '印': '正印', '枭': '偏印'
        }
        shishen_order = ['比', '劫', '食', '伤', '财', '才', '官', '杀', '印', '枭']
        
        # 计算总能量（取正值总和）
        total_shishen_score = sum(max(shishen_scores.get(s, 0), 0) for s in shishen_order)
        
        # 按能量从高到低排序
        shishen_sorted = sorted(shishen_order, key=lambda s: shishen_scores.get(s, 0), reverse=True)
        
        for shishen in shishen_sorted:
            score = shishen_scores.get(shishen, 0)
            details = shishen_details.get(shishen, [])
            full_name = shishen_full_names.get(shishen, shishen)
            # 计算占比
            if total_shishen_score > 0:
                percentage = (max(score, 0) / total_shishen_score * 100) if score > 0 else 0
            else:
                percentage = 0
            
            if score != 0 or details:
                print(f"  {full_name}({shishen}) ({score:.1f}分, 占比{percentage:.1f}%):")
                if details:
                    for detail in details:
                        print(f"    - {detail}")
                else:
                    print(f"    无加分/减分")
            else:
                print(f"  {full_name}({shishen}): 无 (占比0.0%)")



        # 打印其余十神分析（按原局十神能量高低排序，包含不存在的十神）
        xiji = self.analysis_result.get('第五论级_定喜忌', {})
        original_shishen_scores = final_geju.get('十神能量分析', {})

        # 按原局十神能量从高到低排序（包括不存在的十神，能量为0）
        shishen_sorted_by_score = sorted(shishen_order, key=lambda s: original_shishen_scores.get(s, 0), reverse=True)

        # 格式化输出（所有十神都显示，不存在的标注为0）
        shishen_result_list = []
        for shishen in shishen_sorted_by_score:
            score = original_shishen_scores.get(shishen, 0)
            full_name = shishen_full_names.get(shishen, shishen)
            shishen_result_list.append(f"{full_name}({score:.1f})")

        if shishen_result_list:
            print(f"其余十神分析: {'、'.join(shishen_result_list)}")
        else:
            print(f"其余十神分析: 无")
        print(f"格局说明: {final_geju.get('格局说明', '')}")
        print(f"判定依据:")
        for basis in final_geju.get('判定依据', []):
            print(f"  - {basis}")
        
        # 打印第六论级（大运流年分析）
        self.print_sixth_level()
        
        # 打印基础信息综合分析
        self._print_basic_info_analysis()
        
        # 打印命盘综合信息分析（调用zonghe_database）
        self._print_mingpan_zonghe_analysis()
        
        print("\n" + "=" * 80)
    
    def _print_basic_info_analysis(self):
        """
        打印基础信息综合分析，并将数据存储到analysis_result
        """
        print("\n" + "=" * 80)
        print("【基础信息综合分析】")
        print("=" * 80)
        
        from ganzhi import ten_deities, zhi5_list, gan5, zhi_wuhangs
        from datetime import datetime
        
        # 初始化数据结构
        basic_info_analysis = {
            "性别": "",
            "年龄": "",
            "出生阳历": "",
            "出生农历": "",
            "四柱": [],
            "十二长生": {},
            "纳音": {},
            "日元": "",
            "日支": "",
            "月令": "",
            "五行旺相": "",
            "身强身弱判定": "",
            "格局类型": [],
            "旺衰类型": "",
            "最旺五行": "",
            "调候用神": [],
            "原局天干关系": [],
            "原局地支关系": [],
            "原局干支关系": [],
            "岁运天干关系": [],
            "岁运地支关系": [],
            "当前流年": "",
            "当前大运": "",
            "未来五年流年": []
        }
        
        # 获取基本信息
        is_male = getattr(self, 'is_male', True)
        gender = "男" if is_male else "女"
        basic_info_analysis["性别"] = gender
        
        # 计算年龄
        age = ""
        if hasattr(self, 'birth_date') and self.birth_date:
            try:
                birth_year = int(self.birth_date.split('-')[0])
                current_year = datetime.now().year
                age = f"{current_year - birth_year}岁（实岁）"
                basic_info_analysis["年龄"] = age
            except:
                pass
        
        # 获取阳历和农历
        solar_date = getattr(self, 'solar_date', '')
        lunar_date = getattr(self, 'lunar_date', '')
        basic_info_analysis["出生阳历"] = solar_date
        basic_info_analysis["出生农历"] = lunar_date
        
        # 获取四柱十神信息
        pillars = ['年柱', '月柱', '日柱', '时柱']
        sizhu_info = []
        for i, pillar in enumerate(pillars):
            if i >= len(self.gans) or i >= len(self.zhis):
                continue
            gan = self.gans[i]
            zhi = self.zhis[i]
            
            # 获取天干十神
            if i == 2:  # 日柱
                gan_shishen = "元"
            elif gan and self.day_gan in ten_deities:
                gan_shishen = ten_deities[self.day_gan].get(gan, '')
            else:
                gan_shishen = ''
            
            # 获取地支十神（取主气/第一个藏干）
            canggan_list = zhi5_list.get(zhi, []) if zhi5_list and zhi else []
            if canggan_list and self.day_gan in ten_deities:
                zhi_shishen = ten_deities[self.day_gan].get(canggan_list[0], '')
            else:
                zhi_shishen = ''
            
            sizhu_info.append(f"{gan}{zhi}{pillar[0]}（{gan_shishen}{zhi_shishen}）")
        
        # 获取辅助信息
        aux_info = self.analysis_result.get('第五论级_辅助信息', {})
        changsheng_data = aux_info.get('十二长生', {})
        nayin_data = aux_info.get('纳音', {})
        
        # 获取第一论级信息
        first_level = self.analysis_result.get('第一论级_月令与格局', {})
        yueling = first_level.get('月令', '')
        yueling_zhuqi = first_level.get('月令主气', '')
        zhugeju = first_level.get('主要格局', '')
        cigeju = first_level.get('次要格局', [])
        wuxing_qiangruo = first_level.get('五行旺相', '')
        
        # 获取第五论级_定喜忌
        xiji_info = self.analysis_result.get('第五论级_定喜忌', {})
        tiaohou_yongshen = xiji_info.get('调候用神', [])
        
        # 获取格局综合判定信息
        final_geju = self.analysis_result.get('格局综合判定', {})
        wangshuai_type = final_geju.get('旺衰类型', '')
        strongest_wuxing = final_geju.get('最旺五行', '')
        
        # 获取身强身弱分析结果 - 从第一论级中获取
        rizhu_wangshuai = first_level.get('身强身弱', '')
        
        # 获取第二论级_地支关系
        second_level = self.analysis_result.get('第二论级_地支关系', {})
        
        # 获取第三论级_天干关系
        third_level = self.analysis_result.get('第三论级_天干关系', {})
        
        # 获取第四论级_天干与地支的关系
        fourth_level = self.analysis_result.get('第四论级_天干与地支的关系', {})
        
        # 打印基础信息
        print(f"性别：{gender}")
        if age:
            print(f"年龄：{age}")
        if solar_date:
            print(f"出生阳历：{solar_date}")
        if lunar_date:
            print(f"出生农历：{lunar_date}")
        
        # 打印四柱
        if sizhu_info:
            print(f"四柱：{ '、'.join(sizhu_info) }")
        
        # 打印十二长生
        print(f"十二长生：")
        for pillar in pillars:
            if pillar in changsheng_data:
                data = changsheng_data[pillar]
                print(f"  {pillar}: 星运-{data.get('星运', '')} 自坐-{data.get('自坐', '')}")
        
        # 打印纳音
        print(f"纳音：")
        for pillar in pillars:
            if pillar in nayin_data:
                print(f"  {pillar}: {nayin_data[pillar]}")
        
        # 打印第一论级信息
        print(f"\n")
        # 自动适配日主五行
        if self.day_gan:
            day_gan_wuxing = gan5.get(self.day_gan, '')
            print(f"日元：{self.day_gan}{day_gan_wuxing}")
        else:
            print("日元：")
        # 自动适配日支五行
        if len(self.zhis) > 2:
            rizhi = self.zhis[2]
            rizhi_wuxing = zhi_wuhangs.get(rizhi, '')
            print(f"日支：{rizhi}{rizhi_wuxing}")
        print(f"月令：{yueling}月")
        if wuxing_qiangruo:
            print(f"五行旺相：{wuxing_qiangruo}")
        # 新增：身强身弱分析 
        if rizhu_wangshuai:
            print(f"身强身弱判定：{rizhu_wangshuai}")
        geju_list = [zhugeju] if zhugeju else []
        if cigeju:
            geju_list.extend(cigeju)
        if geju_list:
            print(f"格局类型：{'、'.join(geju_list)}")
        print(f"")
        
        # 打印旺衰类型和最旺五行
        if wangshuai_type:
            print(f"\n旺衰类型：{wangshuai_type}")
        if strongest_wuxing:
            print(f"最旺五行（不算藏干）：{strongest_wuxing}")
        
        # 打印调候用神
        if tiaohou_yongshen:
            print(f"调候用神：{'、'.join(tiaohou_yongshen)}")
        
        # 辅助函数：给文本中的天干地支添加十神
        def add_shishen_to_text(text):
            """给文本中的天干地支添加十神，如：丙（偏财）壬（日主）冲"""
            # 如果不是字符串类型，直接返回原值
            if not isinstance(text, str) or not text or text == '无':
                return text
            result = text
            # 处理天干（按常见顺序匹配，避免重复）
            for gan in ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
                if gan in result:
                    shishen = ten_deities.get(self.day_gan, {}).get(gan, '')
                    if shishen:
                        # 使用临时标记避免重复替换
                        result = result.replace(gan, f"{gan}（{shishen}）", 1)
            return result
        
        def add_shishen_to_zhi_text(text):
            """给文本中的地支添加十神，如：寅（食神）辰（七杀）拱会卯木（伤官）"""
            # 如果不是字符串类型，直接返回原值
            if not isinstance(text, str) or not text or text == '无':
                return text
            result = text
            # 处理地支（按常见顺序匹配，避免重复）
            for zhi in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
                if zhi in result:
                    canggan = zhi5_list.get(zhi, [])
                    if canggan and self.day_gan in ten_deities:
                        shishen = ten_deities[self.day_gan].get(canggan[0], '')
                        if shishen:
                            result = result.replace(zhi, f"{zhi}（{shishen}）", 1)
            return result
        
        # 打印原局天干关系
        print(f"\n原局天干（冲克合等）：", end='')
        gan_relations = []
        for key, value in third_level.items():
            if value and value != '无':
                if isinstance(value, list):
                    for item in value:
                        gan_relations.append(add_shishen_to_text(item))
                else:
                    gan_relations.append(add_shishen_to_text(value))
        if gan_relations:
            print(f"{'、'.join(gan_relations)}")
        else:
            print("无")
        
        # 打印原局地支关系
        print(f"原局地支（刑冲合害等）：", end='')
        zhi_relations = []
        for key, value in second_level.items():
            if value and value != '无' and key != '刑冲克害说明':
                if isinstance(value, list):
                    for item in value:
                        zhi_relations.append(add_shishen_to_zhi_text(item))
                else:
                    zhi_relations.append(add_shishen_to_zhi_text(value))
        if zhi_relations:
            print(f"{'、'.join(zhi_relations)}")
        else:
            print("无")
        
        # 打印原局干支关系
        print(f"原局干支：", end='')
        ganzhi_relations = []
        for key, value in fourth_level.items():
            if value and value != '无':
                if isinstance(value, list):
                    for item in value:
                        # 干支关系需要同时处理天干和地支
                        item_with_shishen = add_shishen_to_text(item)
                        item_with_shishen = add_shishen_to_zhi_text(item_with_shishen)
                        ganzhi_relations.append(item_with_shishen)
                else:
                    item_with_shishen = add_shishen_to_text(value)
                    item_with_shishen = add_shishen_to_zhi_text(item_with_shishen)
                    ganzhi_relations.append(item_with_shishen)
        if ganzhi_relations:
            print(f"{'、'.join(ganzhi_relations)}")
        else:
            print("无")
        # 新增：岁运分析（需要第六论级数据）
        if self.liunian_year:
            sixth_level = self.analysis_result.get('第六论级', {})
            # 岁运天干
            print(f"\n岁运天干（冲克合等）：", end='')
            suiyun_gan_analysis = sixth_level.get('岁运天干分析', {})
            suiyun_tian_gan = []
            for pillar, impacts in suiyun_gan_analysis.get('大运天干影响', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        desc = add_shishen_to_text(impact['描述'])
                        suiyun_tian_gan.append(desc)
            for pillar, impacts in suiyun_gan_analysis.get('流年天干影响', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        desc = add_shishen_to_text(impact['描述'])
                        suiyun_tian_gan.append(desc)
            for relation, impacts in suiyun_gan_analysis.get('大运流年天干关系', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        desc = add_shishen_to_text(impact['描述'])
                        suiyun_tian_gan.append(desc)
            if suiyun_tian_gan:
                print(f"{'、'.join(suiyun_tian_gan)}")
            else:
                print("无")
            
            # 岁运地支
            print(f"岁运地支（刑冲合害等）：", end='')
            suiyun_zhi_analysis = sixth_level.get('岁运地支分析', {})
            suiyun_di_zhi = []
            for pillar, impacts in suiyun_zhi_analysis.get('大运地支影响', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        desc = add_shishen_to_zhi_text(impact['描述'])
                        suiyun_di_zhi.append(desc)
            for pillar, impacts in suiyun_zhi_analysis.get('流年地支影响', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        desc = add_shishen_to_zhi_text(impact['描述'])
                        suiyun_di_zhi.append(desc)
            for relation, impacts in suiyun_zhi_analysis.get('大运流年地支关系', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        desc = add_shishen_to_zhi_text(impact['描述'])
                        suiyun_di_zhi.append(desc)
            if suiyun_di_zhi:
                print(f"{'、'.join(suiyun_di_zhi)}")
            else:
                print("无")
            
            # 岁运干支（包含岁运并临、天克地冲、伏吟等特殊流年分析）
            print(f"岁运干支：", end='')
            suiyun_ganzhi_analysis = sixth_level.get('岁运干支分析', {})
            special_liunian = sixth_level.get('特殊流年分析', {})
            suiyun_ganzhi = []

            # 辅助函数：获取柱位十神信息（提前定义）
            def get_pillar_shishen_info(pillar_gan, pillar_zhi):
                gan_shishen = ten_deities.get(self.day_gan, {}).get(pillar_gan, '')
                zhi_canggan = zhi5_list.get(pillar_zhi, []) if zhi5_list and pillar_zhi else []
                zhi_shishen = ten_deities.get(self.day_gan, {}).get(zhi_canggan[0], '') if zhi_canggan else ''
                return gan_shishen, zhi_shishen

            # 获取喜用神列表
            xiji_info = self.analysis_result.get('第五论级_定喜忌', {})
            xiyong_list = []
            for key in ['调候用神', '格局用神', '日主强弱用神']:
                if key in xiji_info:
                    yongshen = xiji_info[key]
                    if isinstance(yongshen, list):
                        xiyong_list.extend(yongshen)
                    elif isinstance(yongshen, str) and yongshen:
                        xiyong_list.extend(yongshen.split('、'))
            xiyong_list = list(set(xiyong_list))

            # 添加岁运并临信息
            if special_liunian.get('岁运并临', {}).get('发生', False):
                gan_zhi = special_liunian['岁运并临']['干支']
                gan_shi, zhi_shi = get_pillar_shishen_info(gan_zhi[0], gan_zhi[1])
                is_xiyong = any(xy in gan_shi or xy in zhi_shi for xy in xiyong_list) if xiyong_list else False
                xi_ji = "喜用神" if is_xiyong else "忌神"
                suiyun_ganzhi.append(f"岁运并临：{gan_zhi}（{gan_shi}{zhi_shi}，{xi_ji}）")

            # 添加天克地冲信息
            for item in special_liunian.get('流年天克地冲', []):
                pillar = item['柱位']
                gan = item['原局干支'][0]
                zhi = item['原局干支'][1]
                gan_shi, zhi_shi = get_pillar_shishen_info(gan, zhi)
                is_xiyong = any(xy in gan_shi or xy in zhi_shi for xy in xiyong_list) if xiyong_list else False
                xi_ji = "喜用神" if is_xiyong else "忌神"
                suiyun_ganzhi.append(f"天克地冲：流年与{pillar}（{gan}{zhi}{gan_shi}{zhi_shi}）相冲（{xi_ji}）")

            # 添加流年伏吟信息
            for item in special_liunian.get('流年伏吟', []):
                pillar = item['柱位']
                gan = item['干支'][0]
                zhi = item['干支'][1]
                gan_shi, zhi_shi = get_pillar_shishen_info(gan, zhi)
                is_xiyong = any(xy in gan_shi or xy in zhi_shi for xy in xiyong_list) if xiyong_list else False
                xi_ji = "喜用神" if is_xiyong else "忌神"
                suiyun_ganzhi.append(f"流年伏吟：流年与{pillar}（{gan}{zhi}{gan_shi}{zhi_shi}）伏吟（{xi_ji}）")

            # 添加大运伏吟信息
            for item in special_liunian.get('大运伏吟', []):
                pillar = item['柱位']
                gan = item['干支'][0]
                zhi = item['干支'][1]
                gan_shi, zhi_shi = get_pillar_shishen_info(gan, zhi)
                is_xiyong = any(xy in gan_shi or xy in zhi_shi for xy in xiyong_list) if xiyong_list else False
                xi_ji = "喜用神" if is_xiyong else "忌神"
                suiyun_ganzhi.append(f"大运伏吟：大运与{pillar}（{gan}{zhi}{gan_shi}{zhi_shi}）伏吟（{xi_ji}）")

            dayun_ganzhi = suiyun_ganzhi_analysis.get('大运干支关系', {})
            for rel_type, items in dayun_ganzhi.items():
                if items and items != '无':
                    if isinstance(items, list):
                        for item in items:
                            if item and item != '无':
                                item_with_shishen = add_shishen_to_text(item)
                                item_with_shishen = add_shishen_to_zhi_text(item_with_shishen)
                                if isinstance(item_with_shishen, str):
                                    suiyun_ganzhi.append(item_with_shishen)
                    else:
                        item_with_shishen = add_shishen_to_text(items)
                        item_with_shishen = add_shishen_to_zhi_text(item_with_shishen)
                        if isinstance(item_with_shishen, str):
                            suiyun_ganzhi.append(item_with_shishen)
            liunian_ganzhi = suiyun_ganzhi_analysis.get('流年干支关系', {})
            for rel_type, items in liunian_ganzhi.items():
                if items and items != '无':
                    if isinstance(items, list):
                        for item in items:
                            if item and item != '无':
                                item_with_shishen = add_shishen_to_text(item)
                                item_with_shishen = add_shishen_to_zhi_text(item_with_shishen)
                                if isinstance(item_with_shishen, str):
                                    suiyun_ganzhi.append(item_with_shishen)
                    else:
                        item_with_shishen = add_shishen_to_text(items)
                        item_with_shishen = add_shishen_to_zhi_text(item_with_shishen)
                        if isinstance(item_with_shishen, str):
                            suiyun_ganzhi.append(item_with_shishen)
            for relation, items in suiyun_ganzhi_analysis.get('岁运原局干支关系', {}).items():
                if items and items != '无':
                    if isinstance(items, list):
                        for item in items:
                            if item and item != '无':
                                item_with_shishen = add_shishen_to_text(item)
                                item_with_shishen = add_shishen_to_zhi_text(item_with_shishen)
                                if isinstance(item_with_shishen, str):
                                    suiyun_ganzhi.append(item_with_shishen)
                    else:
                        item_with_shishen = add_shishen_to_text(items)
                        item_with_shishen = add_shishen_to_zhi_text(item_with_shishen)
                        if isinstance(item_with_shishen, str):
                            suiyun_ganzhi.append(item_with_shishen)
            if suiyun_ganzhi:
                print(f"{'、'.join(suiyun_ganzhi)}")
            else:
                print("无")
        
        # 新增：当前大运流年分析
        if self.liunian_year and hasattr(self, 'dayun_liunian') and self.dayun_liunian:
            
            # 获取当前流年
            liunian_gan = getattr(self.dayun_liunian, 'current_liunian_gan', '')
            liunian_zhi = getattr(self.dayun_liunian, 'current_liunian_zhi', '')
            
            # 获取当前大运
            dayun_gan = getattr(self.dayun_liunian, 'current_dayun_gan', '')
            dayun_zhi = getattr(self.dayun_liunian, 'current_dayun_zhi', '')
            
            # 辅助函数：获取地支藏干主气十神
            def get_zhi_shishen(day_gan, zhi):
                canggan = zhi5_list.get(zhi, [])
                if canggan and day_gan in ten_deities:
                    return ten_deities[day_gan].get(canggan[0], '')
                return ''
            
            # 流年
            if liunian_gan and liunian_zhi:
                liunian_gan_shi = ten_deities.get(self.day_gan, {}).get(liunian_gan, '')
                liunian_zhi_shi = get_zhi_shishen(self.day_gan, liunian_zhi)
                print(f"当前流年：{liunian_gan}{liunian_zhi}（{liunian_gan_shi}{liunian_zhi_shi}）")
            
            # 大运
            if dayun_gan and dayun_zhi:
                dayun_gan_shi = ten_deities.get(self.day_gan, {}).get(dayun_gan, '')
                dayun_zhi_shi = get_zhi_shishen(self.day_gan, dayun_zhi)
                print(f"当前大运：{dayun_gan}{dayun_zhi}（{dayun_gan_shi}{dayun_zhi_shi}）")
            
            # 检查并打印特殊流年格局（天克地冲、岁运并临、伏吟）
            sixth_level = self.analysis_result.get('第六论级', {})
            if sixth_level:
                special_liunian = sixth_level.get('特殊流年分析', {})
                
                # 天克地冲（已在岁运干支中打印，这里只打印⚠️标记的详细信息）
                tiankedichong_list = special_liunian.get('流年天克地冲', [])
                if tiankedichong_list:
                    for item in tiankedichong_list:
                        pillar = item['柱位']
                        yuanju_gan = item['原局干支'][0]
                        yuanju_zhi = item['原局干支'][1]
                        gan_shi, zhi_shi = get_pillar_shishen_info(yuanju_gan, yuanju_zhi)
                        # 判断喜忌
                        is_xiyong = any(xy in gan_shi or xy in zhi_shi for xy in xiyong_list) if xiyong_list else False
                        xi_ji = "喜用神" if is_xiyong else "忌神"
                        print(f"  ⚠️ 天克地冲（反吟）：流年与{pillar}（{yuanju_gan}{yuanju_zhi}{gan_shi}{zhi_shi}）天克地冲，冲克{gan_shi}{zhi_shi}（{xi_ji}）")
                
                # 岁运并临
                suiyun_binglin = special_liunian.get('岁运并临', {})
                if suiyun_binglin.get('发生'):
                    gan_zhi = suiyun_binglin['干支']
                    gan_shi, zhi_shi = get_pillar_shishen_info(gan_zhi[0], gan_zhi[1])
                    # 判断喜忌
                    is_xiyong = any(xy in gan_shi or xy in zhi_shi for xy in xiyong_list) if xiyong_list else False
                    xi_ji = "喜用神" if is_xiyong else "忌神"
                    print(f"  ⚠️ 岁运并临：流年大运干支{gan_zhi}（{gan_shi}{zhi_shi}，{xi_ji}）")
                
                # 流年伏吟
                liunian_fuyin = special_liunian.get('流年伏吟', [])
                if liunian_fuyin:
                    for item in liunian_fuyin:
                        pillar = item['柱位']
                        gan_zhi = item['干支']
                        gan_shi, zhi_shi = get_pillar_shishen_info(gan_zhi[0], gan_zhi[1])
                        # 判断喜忌
                        is_xiyong = any(xy in gan_shi or xy in zhi_shi for xy in xiyong_list) if xiyong_list else False
                        xi_ji = "喜用神" if is_xiyong else "忌神"
                        print(f"  ⚠️ 流年伏吟：流年与{pillar}（{gan_zhi}{gan_shi}{zhi_shi}）伏吟，重叠{gan_shi}{zhi_shi}（{xi_ji}）")
                
                # 大运伏吟
                dayun_fuyin = special_liunian.get('大运伏吟', [])
                if dayun_fuyin:
                    for item in dayun_fuyin:
                        pillar = item['柱位']
                        gan_zhi = item['干支']
                        gan_shi, zhi_shi = get_pillar_shishen_info(gan_zhi[0], gan_zhi[1])
                        # 判断喜忌
                        is_xiyong = any(xy in gan_shi or xy in zhi_shi for xy in xiyong_list) if xiyong_list else False
                        xi_ji = "喜用神" if is_xiyong else "忌神"
                        print(f"  ⚠️ 大运伏吟：大运与{pillar}（{gan_zhi}{gan_shi}{zhi_shi}）伏吟，重叠{gan_shi}{zhi_shi}（{xi_ji}）")
            
            # 未来五年流年（十神）
            if liunian_gan and liunian_zhi:
                print(f"未来五年流年：", end='')
                future_liunian = []
                from ganzhi import Gan, Zhi
                if Gan and Zhi:
                    gan_idx = Gan.index(liunian_gan) if liunian_gan in Gan else 0
                    zhi_idx = Zhi.index(liunian_zhi) if liunian_zhi in Zhi else 0
                    for i in range(5):
                        future_gan = Gan[(gan_idx + i) % 10]
                        future_zhi = Zhi[(zhi_idx + i) % 12]
                        gan_shi = ten_deities.get(self.day_gan, {}).get(future_gan, '')
                        zhi_shi = get_zhi_shishen(self.day_gan, future_zhi)
                        future_year = self.liunian_year + i
                        future_liunian.append(f"{future_year}年{future_gan}{future_zhi}（{gan_shi}{zhi_shi}）")
                print(f"{'、'.join(future_liunian)}")
        
        # 打印总大运（10个）
        if hasattr(self, 'dayun_liunian') and self.dayun_liunian:
            print(f"\n大运：", end='')
            dayun_list = []
            for dayun in self.dayun_liunian.dayuns[:10]:  # 取前10个大运
                gan_zhi = dayun.get('gan_zhi', '')
                start_date = dayun.get('start_date', '')
                
                # 从start_date计算起始年份
                start_year = ''
                if start_date:
                    try:
                        start_year = datetime.strptime(start_date, "%Y-%m-%d").year
                    except:
                        pass
                
                # 计算大运十神 - 地支取藏干主气
                if len(gan_zhi) >= 2:
                    dayun_gan = gan_zhi[0]
                    dayun_zhi = gan_zhi[1]
                    if self.day_gan in ten_deities:
                        gan_shi = ten_deities[self.day_gan].get(dayun_gan, '')
                        zhi_canggan = zhi5_list.get(dayun_zhi, [])
                        if zhi_canggan:
                            zhi_shi = ten_deities[self.day_gan].get(zhi_canggan[0], '')
                        else:
                            zhi_shi = ''
                        dayun_list.append(f"{start_year}年{gan_zhi}({gan_shi}{zhi_shi})")
                    else:
                        dayun_list.append(f"{start_year}年{gan_zhi}")
                else:
                    dayun_list.append(f"{start_year}年{gan_zhi}")
            
            if dayun_list:
                print(f"{'、'.join(dayun_list)}")
                basic_info_analysis["大运"] = dayun_list
            else:
                print("无")
        
        # 保存所有获取的数据到basic_info_analysis
        basic_info_analysis["四柱"] = sizhu_info
        basic_info_analysis["十二长生"] = changsheng_data
        basic_info_analysis["纳音"] = nayin_data
        basic_info_analysis["日元"] = self.day_gan if self.day_gan else ""
        basic_info_analysis["日支"] = self.zhis[2] if len(self.zhis) > 2 else ""
        basic_info_analysis["月令"] = yueling
        basic_info_analysis["五行旺相"] = wuxing_qiangruo
        basic_info_analysis["身强身弱判定"] = rizhu_wangshuai
        basic_info_analysis["格局类型"] = geju_list
        basic_info_analysis["旺衰类型"] = wangshuai_type
        basic_info_analysis["最旺五行"] = strongest_wuxing
        basic_info_analysis["调候用神"] = tiaohou_yongshen
        
        # 保存原局关系数据
        basic_info_analysis["原局天干关系"] = third_level.get('天干五合', []) + third_level.get('天干相克', [])
        basic_info_analysis["原局地支关系"] = [f"{k}：{v}" for k, v in second_level.items() if v and v != '无' and k != '刑冲克害说明']
        basic_info_analysis["原局干支关系"] = [f"{k}：{v}" for k, v in fourth_level.items() if v and v != '无']
        
        # 将基础信息综合分析存储到analysis_result
        self.analysis_result['基础信息综合分析'] = basic_info_analysis
    
    def _print_mingpan_zonghe_analysis(self):
        """
        打印命盘综合信息分析，并将数据存储到analysis_result
        遍历原局命盘中的日主、日柱、十神组合、十天干强弱、格局及特殊格局、神煞、天干地支关系
        调用zonghe_database.py获取对应的所有信息
        """
        print("\n" + "=" * 80)
        print("【命盘综合信息分析】")
        print("=" * 80)
        
        # 初始化命盘综合信息数据结构
        mingpan_zonghe = {
            "日主信息": {},
            "日柱信息": {},
            "格局信息": {},
            "神煞信息": {},
            "天干地支作用关系": {}
        }
        
        try:
            from zonghe_database import RiZhuDatabase, GanShenDatabase, GeJuDatabase, ShenShaDatabase
            zonghe_db = RiZhuDatabase()
            gan_shen_db = GanShenDatabase()
            geju_db = GeJuDatabase()
            shensha_db = ShenShaDatabase()
        except ImportError as e:
            print(f"  无法导入zonghe_database模块，跳过命盘综合信息分析: {e}")
            self.analysis_result['命盘综合信息分析'] = mingpan_zonghe
            return
        
        # 1. 日主信息
        if self.day_gan:
            print(f"\n【日主信息 - {self.day_gan}】")
            # 获取十天干身强身弱信息
            # 从第一论级获取身强身弱判定
            first_level = self.analysis_result.get('第一论级_月令与格局', {})
            shenqiang_panduan = first_level.get('身强身弱', '')
            if shenqiang_panduan:
                # 映射为身强/身弱
                # 均衡格统一按照身弱来分析
                if shenqiang_panduan in ['偏强', '强', '从强']:
                    strength_type = '身强'
                elif shenqiang_panduan in ['偏弱', '弱', '从弱', '均衡']:
                    strength_type = '身弱'
                else:
                    strength_type = '身弱'  # 默认按身弱
                shenqiang_info = gan_shen_db.get_gan_shen_dict(self.day_gan, strength_type)
                if shenqiang_info:
                    print(f"  描述概念: {shenqiang_info.get('描述概念', '')}")
                    print(f"  心理特质: {shenqiang_info.get('心理特质', '')}")
                    print(f"  性格优点: {shenqiang_info.get('性格优点', '')}")
                    print(f"  性格缺点: {shenqiang_info.get('性格缺点', '')}")
                    print(f"  行为模式: {shenqiang_info.get('行为模式', '')}")
                    print(f"  成长建议: {shenqiang_info.get('成长建议', '')}")
                    # 存储到数据结构
                    mingpan_zonghe["日主信息"] = {
                        "日主": self.day_gan,
                        "身强身弱": shenqiang_panduan,
                        "类型": strength_type,
                        **shenqiang_info
                    }
                else:
                    print(f"  未找到日主 {self.day_gan} {strength_type}的详细信息")
            else:
                print(f"  未找到身强身弱判定信息")
        
        # 2. 日柱信息
        rizhu = self.day_gan + self.zhis[2] if hasattr(self, 'day_gan') and hasattr(self, 'zhis') and len(self.zhis) > 2 else ''
        if rizhu:
            print(f"\n【日柱信息 - {rizhu}】")
            # 使用get_rizhu_dict获取字典格式数据
            rizhu_info = zonghe_db.get_rizhu_dict(rizhu)
            if rizhu_info:
                print(f"  描述概念: {rizhu_info.get('描述概念', '')}")
                print(f"  十二长生: {rizhu_info.get('十二长生', '')}")
                print(f"  纳音: {rizhu_info.get('纳音', '')}")
                print(f"  性格优点: {rizhu_info.get('性格优点', '')}")
                print(f"  性格缺点: {rizhu_info.get('性格缺点', '')}")
                print(f"  心理特质: {rizhu_info.get('心理特质', '')}")
                print(f"  行为模式: {rizhu_info.get('行为模式', '')}")
                print(f"  匹配程度: {rizhu_info.get('匹配程度', '')}")
                print(f"  成长建议: {rizhu_info.get('成长建议', '')}")
            else:
                print(f"  未找到日柱 {rizhu} 的详细信息")
        
        # 3. 格局信息
        final_geju = self.analysis_result.get('格局综合判定', {})
        zhugeju = final_geju.get('主格局', '')
        cigeju = final_geju.get('次要格局', [])
        
        if zhugeju:
            print(f"\n【格局信息 - {zhugeju}】")
            # 格局名称映射（解决名称不一致问题）
            geju_name_mapping = {
                '七杀格': '七杀格（偏官格）',
                '偏官格': '七杀格（偏官格）',
                '正官格': '正官格',
                '正财格': '正财格',
                '偏财格': '偏财格',
                '正印格': '正印格（印绶格）',
                '印绶格': '正印格（印绶格）',
                '偏印格': '偏印格（枭神格）',
                '枭神格': '偏印格（枭神格）',
                '食神格': '食神格',
                '伤官格': '伤官格',
                '从儿格': '从儿格（食伤生财格）',
            }
            # 尝试直接获取，如果失败则尝试映射后的名称
            geju_info = geju_db.get_geju_dict(zhugeju)
            if not geju_info and zhugeju in geju_name_mapping:
                mapped_name = geju_name_mapping[zhugeju]
                geju_info = geju_db.get_geju_dict(mapped_name)
            if geju_info:
                print(f"  格局名称: {geju_info.get('格局名称', '')}")
                print(f"  概念描述: {geju_info.get('概念描述', '')}")
                print(f"  判断标准: {geju_info.get('判断标准', '')}")
                print(f"  成格条件: {geju_info.get('成格条件', '')}")
                print(f"  不成格例子: {geju_info.get('不成格例子', '')}")
                print(f"  心理特质: {geju_info.get('心理特质', '')}")
                print(f"  行为模式: {geju_info.get('行为模式', '')}")
                print(f"  成长建议: {geju_info.get('成长建议', '')}")
            else:
                print(f"  未找到格局 {zhugeju} 的详细信息")
        
        # 4. 特殊格局信息
        first_level = self.analysis_result.get('第一论级_月令与格局', {})
        special_geju = first_level.get('特殊格局', [])
        if special_geju:
            print(f"\n【特殊格局信息】")
            for s_geju in special_geju:
                print(f"  - {s_geju}")
        
        # 5. 神煞信息
        aux_info = self.analysis_result.get('第五论级_辅助信息', {})
        shensha_data = aux_info.get('神煞', {})
        if shensha_data:
            print(f"\n【神煞信息】")
            all_shensha = []
            shensha_by_pillar = {}  # 按柱位分组
            for pillar, shensha_list in shensha_data.items():
                if shensha_list:
                    for shensha in shensha_list:
                        all_shensha.append(shensha)
                        if shensha not in shensha_by_pillar:
                            shensha_by_pillar[shensha] = []
                        shensha_by_pillar[shensha].append(pillar)
            # 去重保持顺序
            unique_shensha = list(dict.fromkeys(all_shensha))
            print(f"  原局共发现 {len(unique_shensha)} 个神煞:")
            
            # 神煞名称映射（解决名称不一致问题）
            shensha_name_mapping = {
                '阴阳差错': '阴差阳错',
                '阴阳差错日': '阴差阳错',
                '桃花': '咸池（桃花）',
                '咸池': '咸池（桃花）',
                '元辰': '元辰（大耗）',
                '大耗': '元辰（大耗）',
            }
            
            for shensha in unique_shensha:
                pillars = shensha_by_pillar.get(shensha, [])
                pillar_str = f"（{'、'.join(pillars)}）" if pillars else ""
                
                # 尝试直接获取，如果失败则尝试映射后的名称
                shensha_info = shensha_db.get_shensha_dict(shensha)
                if not shensha_info and shensha in shensha_name_mapping:
                    mapped_name = shensha_name_mapping[shensha]
                    shensha_info = shensha_db.get_shensha_dict(mapped_name)
                    
                if shensha_info:
                    print(f"  \n  {shensha}{pillar_str}:")
                    print(f"    概念描述: {shensha_info.get('概念描述', '')}")
                    print(f"    优点: {shensha_info.get('优点', '')}")
                    print(f"    缺点: {shensha_info.get('缺点', '')}")
                    print(f"    心理特质: {shensha_info.get('心理特质', '')}")
                    
                    # 根据神煞所在柱位打印对应的影响分析
                    print(f"    柱位影响分析:")
                    for pillar in pillars:
                        if pillar == '年柱':
                            effect = shensha_info.get('年柱影响', '')
                            if effect:
                                print(f"      【年柱】{effect}")
                        elif pillar == '月柱':
                            effect = shensha_info.get('月柱影响', '')
                            if effect:
                                print(f"      【月柱】{effect}")
                        elif pillar == '日柱':
                            effect = shensha_info.get('日柱影响', '')
                            if effect:
                                print(f"      【日柱】{effect}")
                        elif pillar == '时柱':
                            effect = shensha_info.get('时柱影响', '')
                            if effect:
                                print(f"      【时柱】{effect}")
                    
                    # 根据命主性别打印对应的成长建议
                    gender = getattr(self, 'is_male', True)
                    if gender:
                        advice = shensha_info.get('男命成长建议', '')
                        if advice:
                            print(f"    【男命成长建议】{advice}")
                    else:
                        advice = shensha_info.get('女命成长建议', '')
                        if advice:
                            print(f"    【女命成长建议】{advice}")
                else:
                    print(f"  {shensha}{pillar_str}: 暂无详细信息")
        
        # 6. 天干地支作用关系
        print(f"\n【天干地支作用关系】")
        
        # 获取第二论级地支关系
        second_level = self.analysis_result.get('第二论级_地支关系', {})
        # 获取第三论级天干关系
        third_level = self.analysis_result.get('第三论级_天干关系', {})
        # 获取第四论级干支关系
        fourth_level = self.analysis_result.get('第四论级_天干与地支的关系', {})
        
        relation_found = False
        
        # 显示地支关系（第二论级）
        zhi_relation_types = ['三会', '拱会', '三合', '半合', '六合', '六冲', '三刑', '六破', '六害', '自刑', '地支暗合']
        for rel_type in zhi_relation_types:
            relations = second_level.get(rel_type, [])
            if relations and relations != '无':
                if isinstance(relations, list):
                    for relation in relations:
                        if relation and relation != '无':
                            # 使用zonghe_db的get_ganzhi_relation_info_with_fallback方法
                            relation_info = zonghe_db.get_ganzhi_relation_info_with_fallback(relation, rel_type)
                            
                            # 打印结果
                            print(f"  【{rel_type}】{relation}:")
                            if relation_info:
                                print(f"    命理组合: {relation_info.get('命理组合', '')}")
                                print(f"    核心概念: {relation_info.get('核心概念', '')}")
                                print(f"    心理特质: {relation_info.get('心理特质', '')}")
                                print(f"    积极作用: {relation_info.get('积极作用', '')}")
                                print(f"    消极作用: {relation_info.get('消极作用', '')}")
                                print(f"    行为模式: {relation_info.get('行为模式', '')}")
                                print(f"    成长建议: {relation_info.get('成长建议', '')}")
                            else:
                                print(f"    该关系暂无详细数据库信息")
                            relation_found = True
                else:
                    print(f"  【{rel_type}】{relations}")
                    relation_found = True
        
        # 显示天干关系（第三论级）
        gan_relation_types = ['天干五合', '天干相克', '天干相生', '天干相冲']
        for rel_type in gan_relation_types:
            relations = third_level.get(rel_type, [])
            if relations and relations != '无':
                if isinstance(relations, list):
                    for relation in relations:
                        if relation and relation != '无':
                            # 使用zonghe_db的get_ganzhi_relation_info_with_fallback方法
                            relation_info = zonghe_db.get_ganzhi_relation_info_with_fallback(relation, rel_type)
                            
                            # 打印结果
                            print(f"  【{rel_type}】{relation}:")
                            if relation_info:
                                print(f"    命理组合: {relation_info.get('命理组合', '')}")
                                print(f"    核心概念: {relation_info.get('核心概念', '')}")
                                print(f"    心理特质: {relation_info.get('心理特质', '')}")
                                print(f"    积极作用: {relation_info.get('积极作用', '')}")
                                print(f"    消极作用: {relation_info.get('消极作用', '')}")
                                print(f"    行为模式: {relation_info.get('行为模式', '')}")
                                print(f"    成长建议: {relation_info.get('成长建议', '')}")
                            else:
                                print(f"    该关系暂无详细数据库信息")
                            relation_found = True
                else:
                    print(f"  【{rel_type}】{relations}")
                    relation_found = True
        
        # 显示第四论级干支关系
        fourth_relation_types = ['伏吟', '反吟', '盖头', '截脚', '天地德合', '天地合']
        for rel_type in fourth_relation_types:
            relations = fourth_level.get(rel_type, [])
            if relations and relations != '无':
                if isinstance(relations, list):
                    for relation in relations:
                        if relation and relation != '无':
                            # 使用zonghe_db的get_ganzhi_relation_info_with_fallback方法
                            relation_info = zonghe_db.get_ganzhi_relation_info_with_fallback(relation, rel_type)
                            
                            # 打印结果（第四论级关系总是打印）
                            print(f"  【{rel_type}】{relation}:")
                            if relation_info:
                                print(f"    命理组合: {relation_info.get('命理组合', '')}")
                                print(f"    核心概念: {relation_info.get('核心概念', '')}")
                                print(f"    心理特质: {relation_info.get('心理特质', '')}")
                                print(f"    积极作用: {relation_info.get('积极作用', '')}")
                                print(f"    消极作用: {relation_info.get('消极作用', '')}")
                                print(f"    行为模式: {relation_info.get('行为模式', '')}")
                                print(f"    成长建议: {relation_info.get('成长建议', '')}")
                            else:
                                print(f"    该关系暂无详细数据库信息")
                            relation_found = True
                else:
                    # 使用zonghe_db的get_ganzhi_relation_info_with_fallback方法
                    relation_info = zonghe_db.get_ganzhi_relation_info_with_fallback(relations, rel_type)
                    
                    # 打印结果（第四论级关系总是打印）
                    print(f"  【{rel_type}】{relations}:")
                    if relation_info:
                        print(f"    命理组合: {relation_info.get('命理组合', '')}")
                        print(f"    核心概念: {relation_info.get('核心概念', '')}")
                        print(f"    心理特质: {relation_info.get('心理特质', '')}")
                        print(f"    积极作用: {relation_info.get('积极作用', '')}")
                        print(f"    消极作用: {relation_info.get('消极作用', '')}")
                        print(f"    行为模式: {relation_info.get('行为模式', '')}")
                        print(f"    成长建议: {relation_info.get('成长建议', '')}")
                    else:
                        print(f"    该关系暂无详细数据库信息")
                    relation_found = True
        
        if not relation_found:
            print("  原局未发现特殊的天干地支作用关系")
        
        # 将命盘综合信息分析数据存储到analysis_result
        self.analysis_result['命盘综合信息分析'] = mingpan_zonghe
        
        # 7. 岁运干支分析（天克地冲、岁运并临、伏吟）- 如果存在第六论级数据
        if self.liunian_year:
            sixth_level = self.analysis_result.get('第六论级', {})
            if sixth_level:
                special_liunian = sixth_level.get('特殊流年分析', {})
                has_special = (
                    special_liunian.get('流年天克地冲', []) or
                    special_liunian.get('岁运并临', {}).get('发生', False) or
                    special_liunian.get('流年伏吟', []) or
                    special_liunian.get('大运伏吟', [])
                )
                
                if has_special:
                    print(f"\n【岁运干支分析 - {self.liunian_year}年】")
                    
                    # 获取喜用神信息
                    xiji_info = self.analysis_result.get('第五论级_定喜忌', {})
                    xiyong_list = []
                    for key in ['调候用神', '格局用神', '日主强弱用神']:
                        if key in xiji_info:
                            yongshen = xiji_info[key]
                            if isinstance(yongshen, list):
                                xiyong_list.extend(yongshen)
                            elif isinstance(yongshen, str) and yongshen:
                                xiyong_list.extend(yongshen.split('、'))
                    xiyong_list = list(set(xiyong_list))
                    
                    # 辅助函数：判断某柱对日主来说是喜用还是忌神
                    def get_pillar_xi_ji(pillar_gan, pillar_zhi):
                        """判断柱位对日主来说是喜用还是忌神"""
                        gan_shishen = ten_deities.get(self.day_gan, {}).get(pillar_gan, '')
                        zhi_canggan = zhi5_list.get(pillar_zhi, []) if zhi5_list and pillar_zhi else []
                        zhi_shishen = ten_deities.get(self.day_gan, {}).get(zhi_canggan[0], '') if zhi_canggan else ''
                        
                        gan_is_xiyong = any(xy in gan_shishen for xy in xiyong_list) if gan_shishen and xiyong_list else False
                        zhi_is_xiyong = any(xy in zhi_shishen for xy in xiyong_list) if zhi_shishen and xiyong_list else False
                        
                        return {
                            'gan_shishen': gan_shishen,
                            'zhi_shishen': zhi_shishen,
                            'gan_is_xiyong': gan_is_xiyong,
                            'zhi_is_xiyong': zhi_is_xiyong,
                            'is_xiyong': gan_is_xiyong or zhi_is_xiyong
                        }
                    
                    # 辅助函数：获取柱位十神描述
                    def get_pillar_shishen_desc(pillar_gan, pillar_zhi):
                        """获取柱位十神描述，如戊午财杀"""
                        info = get_pillar_xi_ji(pillar_gan, pillar_zhi)
                        gan_shi = info['gan_shishen']
                        zhi_shi = info['zhi_shishen']
                        return f"{pillar_gan}{pillar_zhi}{gan_shi}{zhi_shi}"
                    
                    # 天克地冲
                    tiankedichong_list = special_liunian.get('流年天克地冲', [])
                    if tiankedichong_list:
                        print(f"\n  ⚠️ 天克地冲（反吟）:")
                        for item in tiankedichong_list:
                            pillar = item['柱位']
                            yuanju_gan = item['原局干支'][0]
                            yuanju_zhi = item['原局干支'][1]
                            
                            # 获取原局柱位十神描述
                            yuanju_desc = get_pillar_shishen_desc(yuanju_gan, yuanju_zhi)
                            # 判断是喜用还是忌神
                            yuanju_info = get_pillar_xi_ji(yuanju_gan, yuanju_zhi)
                            xi_ji_type = "喜用神" if yuanju_info['is_xiyong'] else "忌神"
                            
                            print(f"    - 天克地冲：流年与{pillar}（{yuanju_desc}）天克地冲，冲克{yuanju_info['gan_shishen']}{yuanju_info['zhi_shishen']}（{xi_ji_type}）")
                            
                            # 从数据库获取详细信息和应对措施
                            try:
                                from zonghe_database import get_liunian_database
                                liunian_db = get_liunian_database()
                                
                                # 作用于喜用神/忌神的整体定义
                                if yuanju_info['is_xiyong']:
                                    tkdc_xiyong_info = liunian_db.get_dict('天克地冲（反吟）', '作用于喜用神')
                                    if tkdc_xiyong_info:
                                        print(f"\n      【作用于喜用神】")
                                        print(f"        {tkdc_xiyong_info.get('核心内容', '')}")
                                else:
                                    tkdc_xiyong_info = liunian_db.get_dict('天克地冲（反吟）', '作用于忌神')
                                    if tkdc_xiyong_info:
                                        print(f"\n      【作用于忌神】")
                                        print(f"        {tkdc_xiyong_info.get('核心内容', '')}")
                                
                                # 分柱影响
                                tkdc_pillar_info = liunian_db.get_dict('天克地冲（反吟）', f'作用于{pillar}')
                                if tkdc_pillar_info:
                                    print(f"\n      【作用于{pillar}】")
                                    print(f"        {tkdc_pillar_info.get('核心内容', '')}")
                                
                                # 喜忌对应策略
                                if yuanju_info['is_xiyong']:
                                    tkdc_strategy = liunian_db.get_dict('天克地冲（反吟）', '喜忌对应策略-冲喜用神')
                                    if tkdc_strategy:
                                        print(f"\n      【冲喜用神应对策略】")
                                        print(f"        {tkdc_strategy.get('核心内容', '')}")
                                else:
                                    tkdc_strategy = liunian_db.get_dict('天克地冲（反吟）', '喜忌对应策略-冲忌神')
                                    if tkdc_strategy:
                                        print(f"\n      【冲忌神应对策略】")
                                        print(f"        {tkdc_strategy.get('核心内容', '')}")
                                
                                # 分柱对应策略
                                tkdc_pillar_strategy = liunian_db.get_dict('天克地冲（反吟）', f'分柱对应策略-{pillar}')
                                if tkdc_pillar_strategy:
                                    print(f"\n      【{pillar}对应策略】")
                                    print(f"        {tkdc_pillar_strategy.get('核心内容', '')}")
                            except Exception:
                                pass
                    
                    # 岁运并临
                    suiyun_binglin = special_liunian.get('岁运并临', {})
                    if suiyun_binglin.get('发生'):
                        print(f"\n  ⚠️ 岁运并临:")
                        gan_zhi = suiyun_binglin['干支']
                        # 判断岁运并临干支是喜用还是忌
                        liunian_info = get_pillar_xi_ji(gan_zhi[0], gan_zhi[1])
                        xi_ji_type = "喜用神" if liunian_info['is_xiyong'] else "忌神"
                        print(f"    - 岁运并临：流年大运干支{gan_zhi}（{liunian_info['gan_shishen']}{liunian_info['zhi_shishen']}，{xi_ji_type}）")
                        
                        # 从数据库获取详细信息和应对措施
                        try:
                            from zonghe_database import get_liunian_database
                            liunian_db = get_liunian_database()
                            
                            # 作用于喜用神/忌神的整体定义
                            if liunian_info['is_xiyong']:
                                sybl_xiyong_info = liunian_db.get_dict('岁运并临', '作用于喜用神')
                                if sybl_xiyong_info:
                                    print(f"\n      【作用于喜用神】")
                                    print(f"        {sybl_xiyong_info.get('核心内容', '')}")
                            else:
                                sybl_xiyong_info = liunian_db.get_dict('岁运并临', '作用于忌神')
                                if sybl_xiyong_info:
                                    print(f"\n      【作用于忌神】")
                                    print(f"        {sybl_xiyong_info.get('核心内容', '')}")
                            
                            # 喜忌对应策略
                            if liunian_info['is_xiyong']:
                                sybl_strategy = liunian_db.get_dict('岁运并临', '喜忌对应策略-作用于喜用神')
                                if sybl_strategy:
                                    print(f"\n      【作用于喜用神策略】")
                                    print(f"        {sybl_strategy.get('核心内容', '')}")
                            else:
                                sybl_strategy = liunian_db.get_dict('岁运并临', '喜忌对应策略-作用于忌神')
                                if sybl_strategy:
                                    print(f"\n      【作用于忌神策略】")
                                    print(f"        {sybl_strategy.get('核心内容', '')}")
                        except Exception:
                            pass
                    
                    # 流年伏吟
                    liunian_fuyin = special_liunian.get('流年伏吟', [])
                    if liunian_fuyin:
                        print(f"\n  ⚠️ 流年伏吟:")
                        for item in liunian_fuyin:
                            pillar = item['柱位']
                            fuyin_gan = item['干支'][0]
                            fuyin_zhi = item['干支'][1]
                            # 获取原局柱位十神描述
                            yuanju_desc = get_pillar_shishen_desc(fuyin_gan, fuyin_zhi)
                            # 判断是喜用还是忌神
                            yuanju_info = get_pillar_xi_ji(fuyin_gan, fuyin_zhi)
                            xi_ji_type = "喜用神" if yuanju_info['is_xiyong'] else "忌神"
                            print(f"    - 流年伏吟：流年与{pillar}（{yuanju_desc}）伏吟，重叠{yuanju_info['gan_shishen']}{yuanju_info['zhi_shishen']}（{xi_ji_type}）")
                            
                            # 从数据库获取详细信息和应对措施
                            try:
                                from zonghe_database import get_liunian_database
                                liunian_db = get_liunian_database()
                                
                                # 作用于喜用神/忌神的整体定义
                                if yuanju_info['is_xiyong']:
                                    fuyin_xiyong_info = liunian_db.get_dict('伏吟', '作用于喜用神')
                                    if fuyin_xiyong_info:
                                        print(f"\n      【作用于喜用神】")
                                        print(f"        {fuyin_xiyong_info.get('核心内容', '')}")
                                else:
                                    fuyin_xiyong_info = liunian_db.get_dict('伏吟', '作用于忌神')
                                    if fuyin_xiyong_info:
                                        print(f"\n      【作用于忌神】")
                                        print(f"        {fuyin_xiyong_info.get('核心内容', '')}")
                                
                                # 分柱影响
                                fuyin_pillar_info = liunian_db.get_dict('伏吟', f'作用于{pillar}')
                                if fuyin_pillar_info:
                                    print(f"\n      【作用于{pillar}】")
                                    print(f"        {fuyin_pillar_info.get('核心内容', '')}")
                                
                                # 喜忌对应策略
                                if yuanju_info['is_xiyong']:
                                    fuyin_strategy = liunian_db.get_dict('伏吟', '喜忌对应策略-作用于喜用神')
                                    if fuyin_strategy:
                                        print(f"\n      【伏吟喜用神应对策略】")
                                        print(f"        {fuyin_strategy.get('核心内容', '')}")
                                else:
                                    fuyin_strategy = liunian_db.get_dict('伏吟', '喜忌对应策略-作用于忌神')
                                    if fuyin_strategy:
                                        print(f"\n      【伏吟忌神应对策略】")
                                        print(f"        {fuyin_strategy.get('核心内容', '')}")
                                
                                # 分柱对应策略
                                fuyin_pillar_strategy = liunian_db.get_dict('伏吟', f'分柱对应策略-{pillar}')
                                if fuyin_pillar_strategy:
                                    print(f"\n      【{pillar}对应策略】")
                                    print(f"        {fuyin_pillar_strategy.get('核心内容', '')}")
                            except Exception:
                                pass
                    
                    # 大运伏吟
                    dayun_fuyin = special_liunian.get('大运伏吟', [])
                    if dayun_fuyin:
                        print(f"\n  ⚠️ 大运伏吟:")
                        for item in dayun_fuyin:
                            pillar = item['柱位']
                            fuyin_gan = item['干支'][0]
                            fuyin_zhi = item['干支'][1]
                            # 获取原局柱位十神描述
                            yuanju_desc = get_pillar_shishen_desc(fuyin_gan, fuyin_zhi)
                            # 判断是喜用还是忌神
                            yuanju_info = get_pillar_xi_ji(fuyin_gan, fuyin_zhi)
                            xi_ji_type = "喜用神" if yuanju_info['is_xiyong'] else "忌神"
                            print(f"    - 大运伏吟：大运与{pillar}（{yuanju_desc}）伏吟，重叠{yuanju_info['gan_shishen']}{yuanju_info['zhi_shishen']}（{xi_ji_type}）")
                            
                            # 从数据库获取详细信息和应对措施
                            try:
                                from zonghe_database import get_liunian_database
                                liunian_db = get_liunian_database()
                                
                                # 作用于喜用神/忌神的整体定义
                                if yuanju_info['is_xiyong']:
                                    fuyin_xiyong_info = liunian_db.get_dict('伏吟', '作用于喜用神')
                                    if fuyin_xiyong_info:
                                        print(f"\n      【作用于喜用神】")
                                        print(f"        {fuyin_xiyong_info.get('核心内容', '')}")
                                else:
                                    fuyin_xiyong_info = liunian_db.get_dict('伏吟', '作用于忌神')
                                    if fuyin_xiyong_info:
                                        print(f"\n      【作用于忌神】")
                                        print(f"        {fuyin_xiyong_info.get('核心内容', '')}")
                                
                                # 分柱影响
                                fuyin_pillar_info = liunian_db.get_dict('伏吟', f'作用于{pillar}')
                                if fuyin_pillar_info:
                                    print(f"\n      【作用于{pillar}】")
                                    print(f"        {fuyin_pillar_info.get('核心内容', '')}")
                                
                                # 喜忌对应策略
                                if yuanju_info['is_xiyong']:
                                    fuyin_strategy = liunian_db.get_dict('伏吟', '喜忌对应策略-作用于喜用神')
                                    if fuyin_strategy:
                                        print(f"\n      【伏吟喜用神应对策略】")
                                        print(f"        {fuyin_strategy.get('核心内容', '')}")
                                else:
                                    fuyin_strategy = liunian_db.get_dict('伏吟', '喜忌对应策略-作用于忌神')
                                    if fuyin_strategy:
                                        print(f"\n      【伏吟忌神应对策略】")
                                        print(f"        {fuyin_strategy.get('核心内容', '')}")
                                
                                # 分柱对应策略
                                fuyin_pillar_strategy = liunian_db.get_dict('伏吟', f'分柱对应策略-{pillar}')
                                if fuyin_pillar_strategy:
                                    print(f"\n      【{pillar}对应策略】")
                                    print(f"        {fuyin_pillar_strategy.get('核心内容', '')}")
                            except Exception:
                                pass
        
        print("\n" + "-" * 80)
    
    def print_fifth_level(self):
        """只打印第五论级的信息（支持三柱或四柱）"""
        from datetime import datetime
        
        # 辅助信息表格
        print(f"\n基础排盘信息：")
        print("-" * 80)
        
        aux_info = self.analysis_result.get('第五论级_辅助信息', {})
        # 根据是否有时间柱决定打印几列
        if self.has_time_pillar:
            pillars = ['年柱', '月柱', '日柱', '时柱']
        else:
            pillars = ['年柱', '月柱', '日柱']
        
        # 准备表格数据
        # 日期行
        print(f"{'日期':<8}", end='')
        for pillar in pillars:
            print(f"{pillar:<10}", end='')
        print()
        
        # 主星行（天干对应的十神）
        print(f"{'主星':<8}", end='')
        for i in range(len(pillars)):
            gan = self.gans[i] if i < len(self.gans) else ''
            if gan and self.day_gan in ten_deities:
                zhusing = ten_deities[self.day_gan].get(gan, '')
            else:
                zhusing = ''
            print(f"{zhusing:<10}", end='')
        print()

        # 天干行
        print(f"{'天干':<8}", end='')
        for i in range(len(pillars)):
            gan = self.gans[i] if i < len(self.gans) else ''
            print(f"{gan:<10}", end='')
        print()

        # 地支行
        print(f"{'地支':<8}", end='')
        for i in range(len(pillars)):
            zhi = self.zhis[i] if i < len(self.zhis) else ''
            print(f"{zhi:<10}", end='')
        print()

        # 藏干行
        print(f"{'藏干':<8}", end='')
        for i in range(len(pillars)):
            zhi = self.zhis[i] if i < len(self.zhis) else ''
            canggan = zhi5_list.get(zhi, []) if zhi5_list and zhi else []
            canggan_str = ' '.join(canggan) if canggan else ''
            print(f"{canggan_str:<10}", end='')
        print()

        # 副星行（藏干对应的十神）
        print(f"{'副星':<8}", end='')
        for i in range(len(pillars)):
            zhi = self.zhis[i] if i < len(self.zhis) else ''
            canggan_list = zhi5_list.get(zhi, []) if zhi5_list and zhi else []
            if canggan_list and self.day_gan in ten_deities:
                fuxing_list = [ten_deities[self.day_gan].get(cg, '') for cg in canggan_list]
                fuxing_str = ' '.join(fuxing_list)
            else:
                fuxing_str = ''
            print(f"{fuxing_str:<10}", end='')
        print()

        # 添加空行填充
        for _ in range(2):
            print(f"{'':<8}", end='')
            for _ in pillars:
                print(f"{'':<10}", end='')
            print()
        
        # 星运行
        changsheng_data = aux_info.get('十二长生', {})
        print(f"{'星运':<8}", end='')
        for pillar in pillars:
            xingyun = changsheng_data.get(pillar, {}).get('星运', '')
            print(f"{xingyun:<10}", end='')
        print()
        
        # 自坐行
        print(f"{'自坐':<8}", end='')
        for pillar in pillars:
            zizuo = changsheng_data.get(pillar, {}).get('自坐', '')
            print(f"{zizuo:<10}", end='')
        print()
        
        # 空亡行
        kongwang_data = aux_info.get('空亡', {})
        print(f"{'空亡':<8}", end='')
        for pillar in pillars:
            kong_info = kongwang_data.get(pillar, {})
            if isinstance(kong_info, dict):
                is_kong = kong_info.get('空亡', False)
            else:
                is_kong = kong_info  # 兼容旧格式
            kong_str = ''
            if is_kong:
                if isinstance(kong_info, dict):
                    zhi = kong_info.get('地支', '')
                    kong_str = zhi
                else:
                    # 旧格式兼容
                    day_gan_zhi = self.day_gan + self.zhis[2]
                    if (self.day_gan, self.zhis[2]) in empties:
                        kongwang_zhis = empties[(self.day_gan, self.zhis[2])]
                        kong_str = ''.join(kongwang_zhis)
            print(f"{kong_str:<10}", end='')
        print()
        
        # 纳音行
        nayin_data = aux_info.get('纳音', {})
        print(f"{'纳音':<8}", end='')
        for pillar in pillars:
            nayin = nayin_data.get(pillar, '')
            print(f"{nayin:<10}", end='')
        print()
        
        # 神煞行（多行）
        shensha_data = aux_info.get('神煞', {})
        max_shensha = max(len(shensha_data.get(pillar, [])) for pillar in pillars) if shensha_data else 0

        for i in range(max_shensha):
            print(f"{'神煞':<8}", end='')
            for pillar in pillars:
                shensha_list = shensha_data.get(pillar, [])
                if i < len(shensha_list):
                    print(f"{shensha_list[i]:<10}", end='')
                else:
                    print(f"{'':<10}", end='')
            print()

        # 调候用神行
        xiji_info = self.analysis_result.get('第五论级_定喜忌', {})
        tiaohou_yongshen = xiji_info.get('调候用神', [])
        print(f"{'调候用神':<8}", end='')
        if tiaohou_yongshen:
            # 将调候用神列表合并显示在第一列
            yongshen_str = ' '.join(tiaohou_yongshen)
            print(f"{yongshen_str}")
        else:
            print()
        
        # 打印大运列表（10个）
        if hasattr(self, 'dayun_liunian') and self.dayun_liunian:
            dayun_list = []
            for dayun in self.dayun_liunian.dayuns[:10]:  # 取前10个大运
                gan_zhi = dayun.get('gan_zhi', '')
                start_date = dayun.get('start_date', '')
                
                # 从start_date计算起始年份
                start_year = ''
                if start_date:
                    try:
                        start_year = datetime.strptime(start_date, "%Y-%m-%d").year
                    except:
                        pass
                
                # 计算大运十神 - 地支取藏干主气
                if len(gan_zhi) >= 2:
                    dayun_gan = gan_zhi[0]
                    dayun_zhi = gan_zhi[1]
                    if self.day_gan in ten_deities:
                        gan_shi = ten_deities[self.day_gan].get(dayun_gan, '')
                        zhi_canggan = zhi5_list.get(dayun_zhi, [])
                        if zhi_canggan:
                            zhi_shi = ten_deities[self.day_gan].get(zhi_canggan[0], '')
                        else:
                            zhi_shi = ''
                        dayun_list.append(f"{start_year}年{gan_zhi}({gan_shi}{zhi_shi})")
                    else:
                        dayun_list.append(f"{start_year}年{gan_zhi}")
                else:
                    dayun_list.append(f"{start_year}年{gan_zhi}")
            
            if dayun_list:
                print(f"大运：{'、'.join(dayun_list)}")

        # ==================== 新增：原局与岁运干支关系打印 ====================
        # 1. 原局天干（数据来自第三论级）
        third_level = self.analysis_result.get('第三论级_天干关系', {})
        yuanju_tian_gan = []
        # 天干五合
        wuhe_list = third_level.get('天干五合', [])
        for item in wuhe_list:
            if item and item != '无':
                yuanju_tian_gan.append(item)
        # 天干相克
        xiangke_list = third_level.get('天干相克', [])
        for item in xiangke_list:
            if item and item != '无':
                yuanju_tian_gan.append(item)
        if yuanju_tian_gan:
            print(f"原局天干：{'，'.join(yuanju_tian_gan)}")
        
        # 2. 原局地支（数据来自第二论级）
        second_level = self.analysis_result.get('第二论级_地支关系', {})
        yuanju_di_zhi = []
        zhi_relations = ['三会', '拱会', '三合', '半合', '拱合', '六合', '六破', '六害', '三刑', '六冲', '自刑', '地支暗合']
        for rel in zhi_relations:
            value = second_level.get(rel)
            if value and value != '无':
                if isinstance(value, list):
                    for item in value:
                        if item and item != '无':
                            yuanju_di_zhi.append(f"{rel}：{item}" if '：' not in str(item) else item)
                else:
                    yuanju_di_zhi.append(f"{rel}：{value}")
        if yuanju_di_zhi:
            print(f"原局地支：{'，'.join(yuanju_di_zhi)}")
        else:
            print(f"原局地支：无")
        
        # 3. 原局干支（数据来自第四论级_天干与地支的关系）
        fourth_level_ganzhi = self.analysis_result.get('第四论级_天干与地支的关系', {})
        yuanju_ganzhi = []
        # 盖头
        gaitou_list = fourth_level_ganzhi.get('盖头', [])
        for item in gaitou_list:
            if item and item != '无':
                yuanju_ganzhi.append(f"盖头：{item}")
        # 截脚
        jiejiao_list = fourth_level_ganzhi.get('截脚', [])
        for item in jiejiao_list:
            if item and item != '无':
                yuanju_ganzhi.append(f"截脚：{item}")
        if yuanju_ganzhi:
            print(f"原局干支：{'，'.join(yuanju_ganzhi)}")
        
        # 4-6. 岁运相关分析（需要第六论级数据）
        if self.liunian_year:
            sixth_level = self.analysis_result.get('第六论级', {})
            
            # 获取喜用神信息用于判断
            xiji_info = self.analysis_result.get('第五论级_定喜忌', {})
            xiyong_list = []
            for key in ['调候用神', '格局用神', '日主强弱用神']:
                if key in xiji_info:
                    yongshen = xiji_info[key]
                    if isinstance(yongshen, list):
                        xiyong_list.extend(yongshen)
                    elif isinstance(yongshen, str) and yongshen:
                        xiyong_list.extend(yongshen.split('、'))
            xiyong_list = list(set(xiyong_list))
            
            # 辅助函数：判断某柱对日主来说是喜用还是忌神
            def get_pillar_xi_ji(pillar_gan, pillar_zhi):
                """判断柱位对日主来说是喜用还是忌神"""
                gan_shishen = ten_deities.get(self.day_gan, {}).get(pillar_gan, '')
                zhi_canggan = zhi5_list.get(pillar_zhi, []) if pillar_zhi else []
                zhi_shishen = ten_deities.get(self.day_gan, {}).get(zhi_canggan[0], '') if zhi_canggan else ''
                
                gan_is_xiyong = any(xy in gan_shishen for xy in xiyong_list) if gan_shishen and xiyong_list else False
                zhi_is_xiyong = any(xy in zhi_shishen for xy in xiyong_list) if zhi_shishen and xiyong_list else False
                
                return {
                    'gan_shishen': gan_shishen,
                    'zhi_shishen': zhi_shishen,
                    'gan_is_xiyong': gan_is_xiyong,
                    'zhi_is_xiyong': zhi_is_xiyong,
                    'is_xiyong': gan_is_xiyong or zhi_is_xiyong
                }
            
            # 辅助函数：格式化喜忌神显示
            def format_xi_ji(gan_shishen, zhi_shishen, gan_is_xiyong, zhi_is_xiyong):
                """格式化喜忌神显示"""
                if gan_is_xiyong and zhi_is_xiyong:
                    return f"{gan_shishen}{zhi_shishen}为喜用神"
                elif not gan_is_xiyong and not zhi_is_xiyong:
                    return f"{gan_shishen}{zhi_shishen}为忌神"
                else:
                    gan_xi_ji = "喜用神" if gan_is_xiyong else "忌神"
                    zhi_xi_ji = "喜用神" if zhi_is_xiyong else "忌神"
                    return f"{gan_shishen}为{gan_xi_ji}，{zhi_shishen}为{zhi_xi_ji}"
            
            # 4. 岁运天干（数据来自第六论级的岁运天干分析）
            suiyun_gan_analysis = sixth_level.get('岁运天干分析', {})
            suiyun_tian_gan = []
            # 大运天干影响
            for pillar, impacts in suiyun_gan_analysis.get('大运天干影响', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        suiyun_tian_gan.append(impact['描述'])
            # 流年天干影响
            for pillar, impacts in suiyun_gan_analysis.get('流年天干影响', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        suiyun_tian_gan.append(impact['描述'])
            # 大运流年天干关系
            for relation, impacts in suiyun_gan_analysis.get('大运流年天干关系', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        suiyun_tian_gan.append(impact['描述'])
            if suiyun_tian_gan:
                print(f"岁运天干：{'，'.join(suiyun_tian_gan)}")
            
            # 5. 岁运地支（数据来自第六论级的岁运地支分析）
            suiyun_zhi_analysis = sixth_level.get('岁运地支分析', {})
            suiyun_di_zhi = []
            # 大运地支影响
            for pillar, impacts in suiyun_zhi_analysis.get('大运地支影响', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        suiyun_di_zhi.append(impact['描述'])
            # 流年地支影响
            for pillar, impacts in suiyun_zhi_analysis.get('流年地支影响', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        suiyun_di_zhi.append(impact['描述'])
            # 大运流年地支关系
            for relation, impacts in suiyun_zhi_analysis.get('大运流年地支关系', {}).items():
                for impact in impacts:
                    if impact.get('类型') and impact.get('描述'):
                        suiyun_di_zhi.append(impact['描述'])
            if suiyun_di_zhi:
                print(f"岁运地支：{'，'.join(suiyun_di_zhi)}")
            
            # 6. 岁运干支（数据来自第六论级的岁运干支分析和特殊流年分析）
            suiyun_ganzhi_analysis = sixth_level.get('岁运干支分析', {})
            special_liunian = sixth_level.get('特殊流年分析', {})
            suiyun_ganzhi = []
            
            # 添加岁运并临信息
            if special_liunian.get('岁运并临', {}).get('发生', False):
                gan_zhi = special_liunian['岁运并临']['干支']
                liunian_info = get_pillar_xi_ji(gan_zhi[0], gan_zhi[1])
                xi_ji_desc = format_xi_ji(liunian_info['gan_shishen'], liunian_info['zhi_shishen'], 
                                          liunian_info['gan_is_xiyong'], liunian_info['zhi_is_xiyong'])
                suiyun_ganzhi.append(f"岁运并临：{gan_zhi}（{liunian_info['gan_shishen']}{liunian_info['zhi_shishen']}，{xi_ji_desc}）")
            
            # 添加天克地冲信息
            for item in special_liunian.get('流年天克地冲', []):
                pillar = item['柱位']
                gan = item['原局干支'][0]
                zhi = item['原局干支'][1]
                liunian_info = get_pillar_xi_ji(gan, zhi)
                xi_ji_desc = format_xi_ji(liunian_info['gan_shishen'], liunian_info['zhi_shishen'], 
                                          liunian_info['gan_is_xiyong'], liunian_info['zhi_is_xiyong'])
                suiyun_ganzhi.append(f"天克地冲：流年与{pillar}（{gan}{zhi}{liunian_info['gan_shishen']}{liunian_info['zhi_shishen']}）相冲（{xi_ji_desc}）")
            
            # 添加伏吟信息
            for item in special_liunian.get('流年伏吟', []):
                pillar = item['柱位']
                gan = item['干支'][0]
                zhi = item['干支'][1]
                liunian_info = get_pillar_xi_ji(gan, zhi)
                xi_ji_desc = format_xi_ji(liunian_info['gan_shishen'], liunian_info['zhi_shishen'], 
                                          liunian_info['gan_is_xiyong'], liunian_info['zhi_is_xiyong'])
                suiyun_ganzhi.append(f"流年伏吟：流年与{pillar}（{gan}{zhi}{liunian_info['gan_shishen']}{liunian_info['zhi_shishen']}）伏吟（{xi_ji_desc}）")
            
            for item in special_liunian.get('大运伏吟', []):
                pillar = item['柱位']
                gan = item['干支'][0]
                zhi = item['干支'][1]
                liunian_info = get_pillar_xi_ji(gan, zhi)
                xi_ji_desc = format_xi_ji(liunian_info['gan_shishen'], liunian_info['zhi_shishen'], 
                                          liunian_info['gan_is_xiyong'], liunian_info['zhi_is_xiyong'])
                suiyun_ganzhi.append(f"大运伏吟：大运与{pillar}（{gan}{zhi}{liunian_info['gan_shishen']}{liunian_info['zhi_shishen']}）伏吟（{xi_ji_desc}）")
            
            # 大运干支关系
            dayun_ganzhi = suiyun_ganzhi_analysis.get('大运干支关系', {})
            for rel_type, items in dayun_ganzhi.items():
                if items and items != '无':
                    if isinstance(items, list):
                        for item in items:
                            if item and item != '无' and isinstance(item, str):
                                suiyun_ganzhi.append(f"大运{rel_type}：{item}")
                    elif isinstance(items, str):
                        suiyun_ganzhi.append(f"大运{rel_type}：{items}")
            # 流年干支关系
            liunian_ganzhi = suiyun_ganzhi_analysis.get('流年干支关系', {})
            for rel_type, items in liunian_ganzhi.items():
                if items and items != '无':
                    if isinstance(items, list):
                        for item in items:
                            if item and item != '无' and isinstance(item, str):
                                suiyun_ganzhi.append(f"流年{rel_type}：{item}")
                    elif isinstance(items, str):
                        suiyun_ganzhi.append(f"流年{rel_type}：{items}")
            # 岁运原局干支关系
            for relation, items in suiyun_ganzhi_analysis.get('岁运原局干支关系', {}).items():
                if items and items != '无':
                    if isinstance(items, list):
                        for item in items:
                            if item and item != '无' and isinstance(item, str):
                                suiyun_ganzhi.append(f"{relation}：{item}")
                    elif isinstance(items, str):
                        suiyun_ganzhi.append(f"{relation}：{items}")
            if suiyun_ganzhi:
                print(f"岁运干支：{'，'.join(suiyun_ganzhi)}")
            else:
                print(f"岁运干支：无")



    def get_basic_paipan_data(self) -> Dict:
        """
        获取基本排盘界面的结构化数据
        
        返回格式：
        {
            "基本信息": {
                "农历": "...",
                "阳历": "...",
                "性别": "乾造/坤造",
            },
            "四柱": {
                "年柱": {"主星": "...", "天干": "...", "地支": "...", "藏干": [...], "副星": [...], ...},
                "月柱": {...},
                "日柱": {...},
                "时柱": {...}
            },
            "大运列表": [...]
        }
        """
        from ganzhi import ten_deities, zhi5_list, gan5
        from datetime import datetime
        
        aux_info = self.analysis_result.get('第五论级_辅助信息', {})
        xiji_info = self.analysis_result.get('第五论级_定喜忌', {})
        changsheng_data = aux_info.get('十二长生', {})
        kongwang_data = aux_info.get('空亡', {})
        nayin_data = aux_info.get('纳音', {})
        shensha_data = aux_info.get('神煞', {})
        tiaohou_yongshen = xiji_info.get('调候用神', [])
        
        # 四柱名称
        pillars = ['年柱', '月柱', '日柱', '时柱']
        pillar_keys = ['year', 'month', 'day', 'time']
        
        # 基本信息
        basic_info = {
            "农历": getattr(self, 'lunar_date', ''),
            "阳历": getattr(self, 'solar_date', ''),
            "性别": "乾造" if getattr(self, 'is_male', True) else "坤造",
        }
        
        # 构建四柱数据
        sizhu = {}
        for i, pillar_name in enumerate(pillars):
            if i >= len(self.gans) or i >= len(self.zhis):
                continue
                
            gan = self.gans[i]
            zhi = self.zhis[i]
            
            # 获取藏干列表
            canggan_list = zhi5_list.get(zhi, []) if zhi5_list and zhi else []
            
            # 获取主星（天干对应的十神）
            if i == 2:  # 日柱
                zhuxing = "元男" if getattr(self, 'is_male', True) else "元女"
            elif gan and self.day_gan in ten_deities:
                zhuxing = ten_deities[self.day_gan].get(gan, '')
            else:
                zhuxing = ''
            
            # 获取副星（藏干对应的十神）
            fuxing_list = []
            if canggan_list and self.day_gan in ten_deities:
                fuxing_list = [ten_deities[self.day_gan].get(cg, '') for cg in canggan_list]
            
            # 获取空亡信息
            kongwang_info = kongwang_data.get(pillar_name, {})
            kongwang_str = ''
            if isinstance(kongwang_info, dict) and kongwang_info.get('空亡', False):
                kongwang_str = kongwang_info.get('地支', '')
            elif kongwang_info:
                kongwang_str = str(kongwang_info)
            
            sizhu[pillar_name] = {
                "主星": zhuxing,
                "天干": gan,
                "地支": zhi,
                "藏干": canggan_list,
                "副星": fuxing_list,
                "星运": changsheng_data.get(pillar_name, {}).get('星运', ''),
                "自坐": changsheng_data.get(pillar_name, {}).get('自坐', ''),
                "空亡": kongwang_str,
                "纳音": nayin_data.get(pillar_name, ''),
                "神煞": shensha_data.get(pillar_name, [])
            }
        
        # 调候用神
        tiaohou_str = ' '.join(tiaohou_yongshen) if tiaohou_yongshen else ''
        
        # 构建大运列表
        dayun_list = []
        if hasattr(self, 'dayun_liunian') and self.dayun_liunian:
            for dayun in self.dayun_liunian.dayuns[:10]:  # 取前10个大运
                gan_zhi = dayun.get('gan_zhi', '')
                start_age = dayun.get('age', '')  # 如 "3岁0个月"
                start_date = dayun.get('start_date', '')
                
                # 从start_date计算起始年份
                start_year = ''
                if start_date:
                    try:
                        start_year = str(datetime.strptime(start_date, "%Y-%m-%d").year)
                    except:
                        pass
                
                dayun_list.append({
                    "干支": gan_zhi,
                    "起始年份": start_year,
                    "起始年龄": start_age
                })
        
        # 将数据存储到analysis_result
        mingpan_zonghe = self.analysis_result.get('命盘综合信息分析', {})
        mingpan_zonghe['四柱'] = sizhu
        mingpan_zonghe['调候用神'] = tiaohou_str
        mingpan_zonghe['大运列表'] = dayun_list
        self.analysis_result['命盘综合信息分析'] = mingpan_zonghe
        
        return {
            "基本信息": basic_info,
            "四柱": sizhu,
            "调候用神": tiaohou_str,
            "大运列表": dayun_list
        }

    def get_complete_print_data(self) -> Dict:
        """
        获取完整的打印数据结构
        
        返回格式包含：
        - 基本信息（阴历、阳历、性别、姓名、胎命身）
        - 大运（当前大运详细信息）
        - 流年（当前流年详细信息）
        - 四柱（年柱、月柱、日柱、时柱详细信息）
        - 起运信息
        - 大运表
        - 流年表
        - 五行旺相
        - 干支图示（各类关系分析）
        """
        from ganzhi import ten_deities, zhi5_list, gan5
        
        aux_info = self.analysis_result.get('第五论级_辅助信息', {})
        xiji_info = self.analysis_result.get('第五论级_定喜忌', {})
        changsheng_data = aux_info.get('十二长生', {})
        kongwang_data = aux_info.get('空亡', {})
        nayin_data = aux_info.get('纳音', {})
        shensha_data = aux_info.get('神煞', {})
        
        # 获取大运流年信息
        suiyun_info = self.analysis_result.get('第五论级_大运流年', {})
        sixth_level = self.analysis_result.get('第六论级', {})
        
        # 基本信息
        basic_info = {
            "阴历": getattr(self, 'lunar_date', ''),
            "阳历": getattr(self, 'solar_date', ''),
            "性别": "乾造" if getattr(self, 'is_male', True) else "坤造",
            "姓名": getattr(self, 'user_name', ''),
            "胎命身": "未提供"
        }
        
        # 辅助函数：获取单个柱的详细信息
        def get_pillar_detail(pillar_name: str, gan: str, zhi: str, is_rizhu: bool = False) -> Dict:
            """获取单个柱的详细信息"""
            # 获取主星（天干对应的十神）
            if is_rizhu:
                zhuxing = "元男" if getattr(self, 'is_male', True) else "元女"
            elif gan and self.day_gan in ten_deities:
                zhuxing = ten_deities[self.day_gan].get(gan, '')
            else:
                zhuxing = ''
            
            # 获取藏干及对应十神
            canggan_dict = {}
            canggan_list = zhi5_list.get(zhi, []) if zhi5_list and zhi else []
            if canggan_list and self.day_gan in ten_deities:
                for cg in canggan_list:
                    cg_shishen = ten_deities[self.day_gan].get(cg, '')
                    if cg_shishen:
                        canggan_dict[cg] = cg_shishen
            
            # 获取空亡信息
            kongwang_info = kongwang_data.get(pillar_name, {})
            kongwang_str = ''
            if isinstance(kongwang_info, dict) and kongwang_info.get('空亡', False):
                kongwang_str = kongwang_info.get('地支', '')
            elif kongwang_info:
                kongwang_str = str(kongwang_info)
            
            return {
                "主星": zhuxing,
                "天干": gan,
                "地支": zhi,
                "藏干": canggan_dict,
                "星运": changsheng_data.get(pillar_name, {}).get('星运', ''),
                "自坐": changsheng_data.get(pillar_name, {}).get('自坐', '') if not is_rizhu else '',
                "空亡": kongwang_str,
                "纳音": nayin_data.get(pillar_name, ''),
                "神煞": shensha_data.get(pillar_name, [])
            }
        
        # 构建四柱数据
        pillars = ['年柱', '月柱', '日柱', '时柱']
        sizhu = {}
        for i, pillar_name in enumerate(pillars):
            if i >= len(self.gans) or i >= len(self.zhis):
                continue
            gan = self.gans[i]
            zhi = self.zhis[i]
            is_rizhu = (i == 2)  # 日柱
            sizhu[pillar_name] = get_pillar_detail(pillar_name, gan, zhi, is_rizhu)
        
        # 当前大运信息
        dayun_gan = suiyun_info.get('大运干支', '')[0] if suiyun_info.get('大运干支') else ''
        dayun_zhi = suiyun_info.get('大运干支', '')[1] if suiyun_info.get('大运干支') else ''
        dayun_detail = get_pillar_detail('大运', dayun_gan, dayun_zhi) if dayun_gan and dayun_zhi else {}
        dayun_detail.pop('自坐', None)  # 大运不需要自坐
        
        # 当前流年信息
        liunian_gan = suiyun_info.get('流年干支', '')[0] if suiyun_info.get('流年干支') else ''
        liunian_zhi = suiyun_info.get('流年干支', '')[1] if suiyun_info.get('流年干支') else ''
        liunian_detail = get_pillar_detail('流年', liunian_gan, liunian_zhi) if liunian_gan and liunian_zhi else {}
        liunian_detail.pop('自坐', None)  # 流年不需要自坐
        
        # 起运信息
        qiyun_info = {
            "起运时间": f"出生后{suiyun_info.get('起运年龄', '')}起运" if suiyun_info.get('起运年龄') else "未计算"
        }
        
        # 导入常量
        from dayun_liunian import GAN_KE, ZHI_CHONG
        from shensha_database import ShenShaCalculator
        
        # 初始化神煞计算器
        shensha_calc = ShenShaCalculator()
        
        # 准备原局八字字典用于神煞计算
        original_bazi = {
            'year_gan': self.gans[0] if len(self.gans) > 0 else '',
            'year_zhi': self.zhis[0] if len(self.zhis) > 0 else '',
            'month_gan': self.gans[1] if len(self.gans) > 1 else '',
            'month_zhi': self.zhis[1] if len(self.zhis) > 1 else '',
            'day_gan': self.day_gan,
            'day_zhi': self.zhis[2] if len(self.zhis) > 2 else '',
            'time_gan': self.gans[3] if self.has_time_pillar and len(self.gans) > 3 else '',
            'time_zhi': self.zhis[3] if self.has_time_pillar and len(self.zhis) > 3 else ''
        }
        
        # 大运表（详细格式，与dayun_liunian.py格式一致）
        dayun_table = []
        dayun_table_detailed = []  # 新增：详细格式大运流年表
        seq = 0
        
        if self.dayun_liunian and hasattr(self.dayun_liunian, 'dayuns'):
            for dayun in self.dayun_liunian.dayuns:
                dayun_g = dayun.get('gan', '')
                dayun_z = dayun.get('zhi', '')
                dayun_shishen = ten_deities.get(self.day_gan, {}).get(dayun_g, '') if dayun_g else ''
                age_range = dayun.get('age_range', '')
                
                # 计算起始年份和日期
                start_year = ''
                start_date = dayun.get('start_date', '')
                if start_date:
                    try:
                        from datetime import datetime
                        start_year = datetime.strptime(start_date, "%Y-%m-%d").year
                    except:
                        pass
                
                dayun_table.append({
                    "年龄区间": age_range,
                    "天干": dayun_g,
                    "地支": dayun_z,
                    "十神": dayun_shishen,
                    "开始年份": start_year
                })
                
                # 获取大运的十二长生、纳音、神煞
                dayun_changsheng = get_changsheng(self.day_gan, dayun_z) if dayun_z else ''
                dayun_nayin = nayins.get((dayun_g, dayun_z), '') if dayun_g and dayun_z else ''
                
                # 获取大运藏干十神
                dayun_canggan = []
                if dayun_z and dayun_z in zhi5_list:
                    for cg in zhi5_list[dayun_z]:
                        cg_shi = ten_deities.get(self.day_gan, {}).get(cg, '')
                        dayun_canggan.append(f"{cg}{cg_shi}")
                
                # 获取大运神煞（使用ShenShaCalculator计算）
                dayun_shensha = []
                try:
                    dayun_shensha = shensha_calc.calculate_dayun_liunian(
                        dayun_g, dayun_z, 'dayun', original_bazi, getattr(self, 'is_male', True)
                    )
                except Exception as e:
                    print(f"[DEBUG] 大运神煞计算失败: {e}")
                
                # 如果计算失败，尝试从shensha_data获取
                if not dayun_shensha and shensha_data and '大运' in shensha_data:
                    dayun_shensha = shensha_data['大运']
                
                # 检查天克地冲（大运与原局）
                tkdc_pillars = []
                if dayun_g and dayun_z:
                    for i, (gan, zhi) in enumerate(zip(self.gans, self.zhis)):
                        if not gan or not zhi:
                            continue
                        # 天干相克
                        gan_ke = False
                        if GAN_KE.get(dayun_g) == gan or GAN_KE.get(gan) == dayun_g:
                            gan_ke = True
                        # 地支相冲
                        zhi_chong = ZHI_CHONG.get(dayun_z) == zhi
                        if gan_ke and zhi_chong:
                            pillar_name = ['年柱', '月柱', '日柱', '时柱'][i]
                            tkdc_pillars.append(pillar_name)
                
                # 添加大运行
                seq += 1
                dayun_table_detailed.append({
                    "序号": f"大运{seq}",
                    "年份": age_range,
                    "起运日期": start_date,
                    "干支": f"{dayun_g}{dayun_z}",
                    "十二长生": dayun_changsheng,
                    "纳音": dayun_nayin,
                    "十神": dayun_shishen,
                    "天干": dayun_g,
                    "地支": dayun_z,
                    "藏干十神": dayun_canggan,
                    "神煞": dayun_shensha,
                    "特殊备注": ' '.join([f"天克地冲({p})" for p in tkdc_pillars]) if tkdc_pillars else ''
                })
                
                # 添加该大运下的流年
                if start_year:
                    try:
                        start_y = int(start_year)
                        # 计算大运结束年份（假设每个大运10年）
                        end_y = start_y + 9
                        for year in range(start_y, end_y + 1):
                            seq += 1
                            from lunar_python import Lunar
                            liunian_g = Lunar.fromYmd(year, 1, 1).getYearGan()
                            liunian_z = Lunar.fromYmd(year, 1, 1).getYearZhi()
                            liunian_shishen = ten_deities.get(self.day_gan, {}).get(liunian_g, '')
                            liunian_nayin = nayins.get((liunian_g, liunian_z), '')
                            liunian_changsheng = get_changsheng(self.day_gan, liunian_z)
                            
                            # 流年藏干十神
                            liunian_canggan = []
                            if liunian_z in zhi5_list:
                                for cg in zhi5_list[liunian_z]:
                                    cg_shi = ten_deities.get(self.day_gan, {}).get(cg, '')
                                    liunian_canggan.append(f"{cg}{cg_shi}")
                            
                            # 流年神煞（使用ShenShaCalculator计算）
                            liunian_shensha = []
                            try:
                                liunian_shensha = shensha_calc.calculate_dayun_liunian(
                                    liunian_g, liunian_z, 'liunian', original_bazi, getattr(self, 'is_male', True)
                                )
                            except Exception as e:
                                print(f"[DEBUG] 流年神煞计算失败: {e}")
                            
                            # 检查天克地冲（流年与原局）
                            liunian_tkdc = []
                            for i, (gan, zhi) in enumerate(zip(self.gans, self.zhis)):
                                if not gan or not zhi:
                                    continue
                                gan_ke = False
                                if GAN_KE.get(liunian_g) == gan or GAN_KE.get(gan) == liunian_g:
                                    gan_ke = True
                                zhi_chong = ZHI_CHONG.get(liunian_z) == zhi
                                if gan_ke and zhi_chong:
                                    pillar_name = ['年柱', '月柱', '日柱', '时柱'][i]
                                    liunian_tkdc.append(pillar_name)
                            
                            # 检查岁运并临
                            suiyun_binglin = (liunian_g == dayun_g and liunian_z == dayun_z)
                            
                            remarks = []
                            if liunian_tkdc:
                                remarks.append(f"天克地冲({','.join(liunian_tkdc)})")
                            if suiyun_binglin:
                                remarks.append("岁运并临")
                            
                            dayun_table_detailed.append({
                                "序号": str(year),
                                "年份": "",
                                "起运日期": "",
                                "干支": f"{liunian_g}{liunian_z}",
                                "十二长生": liunian_changsheng,
                                "纳音": liunian_nayin,
                                "十神": liunian_shishen,
                                "天干": liunian_g,
                                "地支": liunian_z,
                                "藏干十神": liunian_canggan,
                                "神煞": liunian_shensha,
                                "特殊备注": ' '.join(remarks)
                            })
                    except:
                        pass
        
        # 流年表（未来10年）
        liunian_table = []
        if self.liunian_year:
            for year_offset in range(10):
                year = self.liunian_year + year_offset
                # 计算流年干支
                from lunar_python import Lunar
                liunian_g = Lunar.fromYmd(year, 1, 1).getYearGan()
                liunian_z = Lunar.fromYmd(year, 1, 1).getYearZhi()
                liunian_shishen = ten_deities.get(self.day_gan, {}).get(liunian_g, '') if liunian_g else ''
                
                # 获取纳音
                liunian_nayin = nayins.get((liunian_g, liunian_z), '')
                
                # 简化备注：显示与大运的关系
                remark = ""
                if dayun_gan and dayun_zhi:
                    if liunian_g == dayun_gan:
                        remark = "岁运并临"
                    elif liunian_z == dayun_zhi:
                        remark = "岁运同支"
                
                liunian_table.append({
                    "年份": year,
                    "天干": liunian_g,
                    "地支": liunian_z,
                    "十神": liunian_shishen,
                    "纳音": liunian_nayin,
                    "备注": remark
                })
        
        # 五行旺相（从格局综合判定中获取）
        wuxing_qiangruo = {}
        geju_info = self.analysis_result.get('格局综合判定', {})
        wuxing_scores = geju_info.get('五行能量分析', {})
        if wuxing_scores:
            # 按分数排序，确定旺衰
            sorted_wuxing = sorted(wuxing_scores.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_wuxing) >= 5:
                wuxing_qiangruo = {
                    sorted_wuxing[0][0]: "旺",
                    sorted_wuxing[1][0]: "相",
                    sorted_wuxing[2][0]: "休",
                    sorted_wuxing[3][0]: "囚",
                    sorted_wuxing[4][0]: "死"
                }
        
        # 干支图示（从第六论级获取）
        ganzhi_tushi = {
            "岁运天干": [],
            "岁运地支": [],
            "岁运干支": [],
            "原局天干": [],
            "原局地支": [],
            "原局干支": []
        }
        
        # 从第六论级获取分析结果
        sixth_gan_analysis = sixth_level.get('岁运天干分析', {})
        sixth_zhi_analysis = sixth_level.get('岁运地支分析', {})
        sixth_ganzhi_analysis = sixth_level.get('岁运干支分析', {})
        
        # 转换分析结果为图示格式
        if isinstance(sixth_gan_analysis, dict):
            for relation, details in sixth_gan_analysis.items():
                if details:
                    ganzhi_tushi["岁运天干"].append(f"{relation}")
        
        if isinstance(sixth_zhi_analysis, dict):
            for relation, details in sixth_zhi_analysis.items():
                if details and details != '无':
                    ganzhi_tushi["岁运地支"].append(f"{relation}")
        
        # 原局天干关系
        third_level = self.analysis_result.get('第三论级_天干关系', {})
        if third_level.get('天干五合'):
            ganzhi_tushi["原局天干"].append("天干五合")
        if third_level.get('天干相克'):
            ganzhi_tushi["原局天干"].append("天干相克")
        
        # 原局地支关系
        second_level = self.analysis_result.get('第二论级_地支关系', {})
        zhi_relations = ['三会', '拱会', '三合', '半合', '拱合', '六合', '六破', '六害', '三刑', '六冲', '自刑', '地支暗合']
        for rel in zhi_relations:
            if second_level.get(rel) and second_level.get(rel) != '无':
                ganzhi_tushi["原局地支"].append(rel)
        
        # 原局干支关系
        fourth_level = self.analysis_result.get('第四论级_天干与地支的关系', {})
        if fourth_level.get('盖头'):
            ganzhi_tushi["原局干支"].append("盖头")
        if fourth_level.get('截脚'):
            ganzhi_tushi["原局干支"].append("截脚")
        
        # 填充空值为"无"
        for key in ganzhi_tushi:
            if not ganzhi_tushi[key]:
                ganzhi_tushi[key] = ["无"]
        
        # 获取基础信息综合分析和命盘综合信息分析
        basic_info_analysis = self.analysis_result.get('基础信息综合分析', {})
        mingpan_zonghe_analysis = self.analysis_result.get('命盘综合信息分析', {})
        
        return {
            "基本信息": basic_info,
            "大运": dayun_detail,
            "流年": liunian_detail,
            "四柱": sizhu,
            "起运": qiyun_info,
            "大运表": dayun_table,
            "流年表": liunian_table,
            "大运流年详细表": dayun_table_detailed,
            "五行旺相": wuxing_qiangruo,
            "干支图示": ganzhi_tushi,
            "基础信息综合分析": basic_info_analysis,
            "命盘综合信息分析": mingpan_zonghe_analysis
        }
    
    def get_database_analysis(self) -> Dict:
        """
        从zonghe_database.py获取详细解析数据
        用于APK详细信息界面的展示
        
        返回:
            包含数据库详细解析的字典
        """
        try:
            from zonghe_database import RiZhuDatabase, GanShenDatabase, GeJuDatabase, ShenShaDatabase
            zonghe_db = RiZhuDatabase()
            gan_shen_db = GanShenDatabase()
            geju_db = GeJuDatabase()
            shensha_db = ShenShaDatabase()
            print(f"[DEBUG] get_database_analysis: All databases imported successfully")
        except ImportError as e:
            print(f"[DEBUG] get_database_analysis: Import error: {e}")
            import traceback
            traceback.print_exc()
            return {"错误": f"无法导入zonghe_database模块: {e}"}
        
        result = {
            "日主信息": {},
            "日柱信息": {},
            "格局信息": {},
            "神煞信息": {},
            "天干地支作用关系": {}
        }
        
        # 1. 日主信息
        if self.day_gan:
            first_level = self.analysis_result.get('第一论级_月令与格局', {})
            shenqiang_panduan = first_level.get('身强身弱', '')
            if shenqiang_panduan:
                # 映射为身强/身弱
                if shenqiang_panduan in ['偏强', '强', '从强']:
                    strength_type = '身强'
                elif shenqiang_panduan in ['偏弱', '弱', '从弱', '均衡']:
                    strength_type = '身弱'
                else:
                    strength_type = '身弱'
                
                shenqiang_info = gan_shen_db.get_gan_shen_dict(self.day_gan, strength_type)
                if shenqiang_info:
                    result["日主信息"] = {
                        "日主": self.day_gan,
                        "身强身弱": shenqiang_panduan,
                        "类型": strength_type,
                        "描述概念": shenqiang_info.get('描述概念', ''),
                        "心理特质": shenqiang_info.get('心理特质', ''),
                        "性格优点": shenqiang_info.get('性格优点', ''),
                        "性格缺点": shenqiang_info.get('性格缺点', ''),
                        "行为模式": shenqiang_info.get('行为模式', ''),
                        "成长建议": shenqiang_info.get('成长建议', '')
                    }
        
        # 2. 日柱信息
        rizhu = self.day_gan + self.zhis[2] if len(self.zhis) > 2 else ''
        if rizhu:
            rizhu_info = zonghe_db.get_rizhu_dict(rizhu)
            if rizhu_info:
                result["日柱信息"] = {
                    "日柱": rizhu,
                    "描述概念": rizhu_info.get('描述概念', ''),
                    "十二长生": rizhu_info.get('十二长生', ''),
                    "纳音": rizhu_info.get('纳音', ''),
                    "性格优点": rizhu_info.get('性格优点', ''),
                    "性格缺点": rizhu_info.get('性格缺点', ''),
                    "心理特质": rizhu_info.get('心理特质', ''),
                    "行为模式": rizhu_info.get('行为模式', ''),
                    "匹配程度": rizhu_info.get('匹配程度', ''),
                    "成长建议": rizhu_info.get('成长建议', '')
                }
        
        # 3. 格局信息
        final_geju = self.analysis_result.get('格局综合判定', {})
        zhugeju = final_geju.get('主格局', '')
        if zhugeju:
            # 格局名称映射
            geju_name_mapping = {
                '七杀格': '七杀格（偏官格）',
                '偏官格': '七杀格（偏官格）',
                '正官格': '正官格',
                '正财格': '正财格',
                '偏财格': '偏财格',
                '正印格': '正印格（印绶格）',
                '印绶格': '正印格（印绶格）',
                '偏印格': '偏印格（枭神格）',
                '枭神格': '偏印格（枭神格）',
                '食神格': '食神格',
                '伤官格': '伤官格',
                '从儿格': '从儿格（食伤生财格）',
            }
            geju_info = geju_db.get_geju_dict(zhugeju)
            if not geju_info and zhugeju in geju_name_mapping:
                mapped_name = geju_name_mapping[zhugeju]
                geju_info = geju_db.get_geju_dict(mapped_name)
            
            if geju_info:
                result["格局信息"] = {
                    "主格局": zhugeju,
                    "格局名称": geju_info.get('格局名称', ''),
                    "概念描述": geju_info.get('概念描述', ''),
                    "判断标准": geju_info.get('判断标准', ''),
                    "成格条件": geju_info.get('成格条件', ''),
                    "不成格例子": geju_info.get('不成格例子', ''),
                    "心理特质": geju_info.get('心理特质', ''),
                    "行为模式": geju_info.get('行为模式', ''),
                    "成长建议": geju_info.get('成长建议', '')
                }
        
        # 4. 神煞信息（按神煞详细解析）
        aux_info = self.analysis_result.get('第五论级_辅助信息', {})
        shensha_data = aux_info.get('神煞', {})
        if shensha_data:
            shensha_details = []
            all_shensha = set()
            shensha_by_pillar = {}
            
            for pillar, shensha_list in shensha_data.items():
                if shensha_list:
                    for shensha in shensha_list:
                        all_shensha.add(shensha)
                        if shensha not in shensha_by_pillar:
                            shensha_by_pillar[shensha] = []
                        shensha_by_pillar[shensha].append(pillar)
            
            # 神煞名称映射
            shensha_name_mapping = {
                '阴阳差错': '阴差阳错',
                '阴阳差错日': '阴差阳错',
                '桃花': '咸池（桃花）',
                '咸池': '咸池（桃花）',
                '元辰': '元辰（大耗）',
                '大耗': '元辰（大耗）',
            }
            
            for shensha in all_shensha:
                pillars = shensha_by_pillar.get(shensha, [])
                
                shensha_info = shensha_db.get_shensha_dict(shensha)
                if not shensha_info and shensha in shensha_name_mapping:
                    mapped_name = shensha_name_mapping[shensha]
                    shensha_info = shensha_db.get_shensha_dict(mapped_name)
                
                if shensha_info:
                    # 根据性别获取成长建议
                    is_male = getattr(self, 'is_male', True)
                    if is_male:
                        advice = shensha_info.get('男命成长建议', '')
                    else:
                        advice = shensha_info.get('女命成长建议', '')
                    
                    shensha_details.append({
                        "神煞名称": shensha,
                        "所在柱位": pillars,
                        "概念描述": shensha_info.get('概念描述', ''),
                        "优点": shensha_info.get('优点', ''),
                        "缺点": shensha_info.get('缺点', ''),
                        "心理特质": shensha_info.get('心理特质', ''),
                        "年柱影响": shensha_info.get('年柱影响', ''),
                        "月柱影响": shensha_info.get('月柱影响', ''),
                        "日柱影响": shensha_info.get('日柱影响', ''),
                        "时柱影响": shensha_info.get('时柱影响', ''),
                        "成长建议": advice
                    })
            
            result["神煞信息"] = {
                "神煞总数": len(all_shensha),
                "神煞列表": shensha_details
            }
        
        # 5. 天干地支作用关系详细解析
        ganzhi_relations = []
        
        # 地支关系（第二论级）
        second_level = self.analysis_result.get('第二论级_地支关系', {})
        zhi_relation_types = ['三会', '拱会', '三合', '半合', '六合', '六冲', '三刑', '六破', '六害', '自刑', '地支暗合']
        for rel_type in zhi_relation_types:
            relations = second_level.get(rel_type, [])
            if relations and relations != '无':
                if isinstance(relations, list):
                    for relation in relations:
                        if relation and relation != '无':
                            # 使用zonghe_db的get_ganzhi_relation_info_with_fallback方法
                            relation_info = zonghe_db.get_ganzhi_relation_info_with_fallback(relation, rel_type)
                            
                            ganzhi_relations.append({
                                "关系类型": rel_type,
                                "关系描述": relation,
                                "命理组合": relation_info.get('命理组合', '') if relation_info else '',
                                "核心概念": relation_info.get('核心概念', '') if relation_info else '',
                                "心理特质": relation_info.get('心理特质', '') if relation_info else '',
                                "积极作用": relation_info.get('积极作用', '') if relation_info else '',
                                "消极作用": relation_info.get('消极作用', '') if relation_info else '',
                                "行为模式": relation_info.get('行为模式', '') if relation_info else '',
                                "成长建议": relation_info.get('成长建议', '') if relation_info else ''
                            })
        
        # 天干关系（第三论级）
        third_level = self.analysis_result.get('第三论级_天干关系', {})
        gan_relation_types = ['天干五合', '天干相克', '天干相生', '天干相冲']
        for rel_type in gan_relation_types:
            relations = third_level.get(rel_type, [])
            if relations and relations != '无':
                if isinstance(relations, list):
                    for relation in relations:
                        if relation and relation != '无':
                            # 使用zonghe_db的get_ganzhi_relation_info_with_fallback方法
                            relation_info = zonghe_db.get_ganzhi_relation_info_with_fallback(relation, rel_type)
                            
                            ganzhi_relations.append({
                                "关系类型": rel_type,
                                "关系描述": relation,
                                "命理组合": relation_info.get('命理组合', '') if relation_info else '',
                                "核心概念": relation_info.get('核心概念', '') if relation_info else '',
                                "心理特质": relation_info.get('心理特质', '') if relation_info else '',
                                "积极作用": relation_info.get('积极作用', '') if relation_info else '',
                                "消极作用": relation_info.get('消极作用', '') if relation_info else '',
                                "行为模式": relation_info.get('行为模式', '') if relation_info else '',
                                "成长建议": relation_info.get('成长建议', '') if relation_info else ''
                            })
        
        # 第四论级干支关系
        fourth_level = self.analysis_result.get('第四论级_天干与地支的关系', {})
        fourth_relation_types = ['伏吟', '反吟', '盖头', '截脚', '天地德合', '天地合']
        for rel_type in fourth_relation_types:
            relations = fourth_level.get(rel_type, [])
            if relations and relations != '无':
                if isinstance(relations, list):
                    for relation in relations:
                        if relation and relation != '无':
                            # 使用zonghe_db的get_ganzhi_relation_info_with_fallback方法
                            relation_info = zonghe_db.get_ganzhi_relation_info_with_fallback(relation, rel_type)
                            
                            ganzhi_relations.append({
                                "关系类型": rel_type,
                                "关系描述": relation,
                                "命理组合": relation_info.get('命理组合', '') if relation_info else '',
                                "核心概念": relation_info.get('核心概念', '') if relation_info else '',
                                "心理特质": relation_info.get('心理特质', '') if relation_info else '',
                                "积极作用": relation_info.get('积极作用', '') if relation_info else '',
                                "消极作用": relation_info.get('消极作用', '') if relation_info else '',
                                "行为模式": relation_info.get('行为模式', '') if relation_info else '',
                                "成长建议": relation_info.get('成长建议', '') if relation_info else ''
                            })
        
        result["天干地支作用关系"] = ganzhi_relations
        
        # 6. 特殊流年分析（天克地冲、岁运并临、伏吟）
        print(f"[DEBUG] analysis_result has 第六论级: {'第六论级' in self.analysis_result}")
        sixth_level = self.analysis_result.get('第六论级', {})
        print(f"[DEBUG] sixth_level type: {type(sixth_level)}, empty: {len(sixth_level) == 0}")
        special_liunian = sixth_level.get('特殊流年分析', {})
        print(f"[DEBUG] special_liunian type: {type(special_liunian)}, empty: {len(special_liunian) == 0}")
        print(f"[DEBUG] special_liunian keys: {special_liunian.keys() if special_liunian else 'None'}")
        if special_liunian and len(special_liunian) > 0:
            # 从LiuNianYunShiDatabase获取详细解析
            try:
                from zonghe_database import LiuNianYunShiDatabase
                liunian_db = LiuNianYunShiDatabase()
                print(f"[DEBUG] LiuNianYunShiDatabase initialized successfully")
                
                # 获取喜用神信息用于判断
                xiji_info = self.analysis_result.get('第五论级_定喜忌', {})
                xiyong_list = []
                for key in ['调候用神', '格局用神', '日主强弱用神']:
                    if key in xiji_info:
                        yongshen = xiji_info[key]
                        if isinstance(yongshen, list):
                            xiyong_list.extend(yongshen)
                        elif isinstance(yongshen, str) and yongshen:
                            xiyong_list.append(yongshen)
                xiyong_list = list(set(xiyong_list))
                
                # 处理流年伏吟 - 添加数据库解析
                liunian_fuyin = special_liunian.get('流年伏吟', [])
                if liunian_fuyin:
                    for item in liunian_fuyin:
                        pillar = item.get('柱位', '')
                        gan_zhi = item.get('干支', '')
                        if gan_zhi and pillar:
                            # 判断是喜用神还是忌神
                            from ganzhi import ten_deities, zhi5_list
                            gan = gan_zhi[0] if len(gan_zhi) > 0 else ''
                            zhi = gan_zhi[1] if len(gan_zhi) > 1 else ''
                            gan_shishen = ten_deities.get(self.day_gan, {}).get(gan, '')
                            zhi_canggan = zhi5_list.get(zhi, []) if zhi else []
                            zhi_shishen = ten_deities.get(self.day_gan, {}).get(zhi_canggan[0], '') if zhi_canggan else ''
                            is_xiyong = any(xy in gan_shishen or xy in zhi_shishen for xy in xiyong_list) if xiyong_list else False
                            xi_ji = "喜用神" if is_xiyong else "忌神"
                            
                            # 从数据库获取伏吟解析
                            fuyin_info = liunian_db.get_dict('伏吟', '整体定义')
                            fuyin_pillar = liunian_db.get_dict('伏吟', f'作用于{pillar}')
                            fuyin_xiji = liunian_db.get_dict('伏吟', f'作用于{xi_ji}')
                            fuyin_strategy = liunian_db.get_dict('伏吟', f'分柱对应策略-{pillar}')
                            
                            item['数据库解析'] = {
                                '整体定义': fuyin_info.get('核心内容', '') if fuyin_info else '',
                                '作用于柱位': fuyin_pillar.get('核心内容', '') if fuyin_pillar else '',
                                '作用于喜忌': fuyin_xiji.get('核心内容', '') if fuyin_xiji else '',
                                '对应策略': fuyin_strategy.get('核心内容', '') if fuyin_strategy else ''
                            }
                
                # 处理大运伏吟 - 添加数据库解析
                dayun_fuyin = special_liunian.get('大运伏吟', [])
                if dayun_fuyin:
                    for item in dayun_fuyin:
                        pillar = item.get('柱位', '')
                        gan_zhi = item.get('干支', '')
                        if gan_zhi and pillar:
                            # 判断是喜用神还是忌神
                            from ganzhi import ten_deities, zhi5_list
                            gan = gan_zhi[0] if len(gan_zhi) > 0 else ''
                            zhi = gan_zhi[1] if len(gan_zhi) > 1 else ''
                            gan_shishen = ten_deities.get(self.day_gan, {}).get(gan, '')
                            zhi_canggan = zhi5_list.get(zhi, []) if zhi else []
                            zhi_shishen = ten_deities.get(self.day_gan, {}).get(zhi_canggan[0], '') if zhi_canggan else ''
                            is_xiyong = any(xy in gan_shishen or xy in zhi_shishen for xy in xiyong_list) if xiyong_list else False
                            xi_ji = "喜用神" if is_xiyong else "忌神"
                            
                            # 从数据库获取伏吟解析
                            fuyin_info = liunian_db.get_dict('伏吟', '整体定义')
                            fuyin_pillar = liunian_db.get_dict('伏吟', f'作用于{pillar}')
                            fuyin_xiji = liunian_db.get_dict('伏吟', f'作用于{xi_ji}')
                            fuyin_strategy = liunian_db.get_dict('伏吟', f'分柱对应策略-{pillar}')
                            
                            item['数据库解析'] = {
                                '整体定义': fuyin_info.get('核心内容', '') if fuyin_info else '',
                                '作用于柱位': fuyin_pillar.get('核心内容', '') if fuyin_pillar else '',
                                '作用于喜忌': fuyin_xiji.get('核心内容', '') if fuyin_xiji else '',
                                '对应策略': fuyin_strategy.get('核心内容', '') if fuyin_strategy else ''
                            }
                
                # 处理天克地冲 - 添加数据库解析
                tiankedichong = special_liunian.get('流年天克地冲', [])
                if tiankedichong:
                    for item in tiankedichong:
                        pillar = item.get('柱位', '')
                        if pillar:
                            # 从数据库获取天克地冲解析
                            tkdc_info = liunian_db.get_dict('天克地冲（反吟）', '整体定义')
                            tkdc_pillar = liunian_db.get_dict('天克地冲（反吟）', f'作用于{pillar}')
                            tkdc_strategy = liunian_db.get_dict('天克地冲（反吟）', f'分柱对应策略-{pillar}')
                            
                            item['数据库解析'] = {
                                '整体定义': tkdc_info.get('核心内容', '') if tkdc_info else '',
                                '作用于柱位': tkdc_pillar.get('核心内容', '') if tkdc_pillar else '',
                                '对应策略': tkdc_strategy.get('核心内容', '') if tkdc_strategy else ''
                            }
                
                # 处理岁运并临 - 添加数据库解析（使用伏吟的定义，因为是伏吟的一种）
                suiyun_binglin = special_liunian.get('岁运并临', {})
                if suiyun_binglin and suiyun_binglin.get('发生'):
                    fuyin_info = liunian_db.get_dict('伏吟', '整体定义')
                    fuyin_xiyong = liunian_db.get_dict('伏吟', '作用于喜用神')
                    fuyin_jishen = liunian_db.get_dict('伏吟', '作用于忌神')
                    
                    suiyun_binglin['数据库解析'] = {
                        '整体定义': fuyin_info.get('核心内容', '') if fuyin_info else '',
                        '作用于喜用神': fuyin_xiyong.get('核心内容', '') if fuyin_xiyong else '',
                        '作用于忌神': fuyin_jishen.get('核心内容', '') if fuyin_jishen else ''
                    }
                
            except Exception as e:
                # 如果数据库查询失败，不影响原有数据
                print(f"[DEBUG] 特殊流年数据库解析获取失败: {e}")
                import traceback
                traceback.print_exc()
                pass
            
            result["特殊流年分析"] = special_liunian
            print(f"[DEBUG] Added 特殊流年分析 to result, keys: {result.keys()}")
            print(f"[DEBUG] 流年伏吟: {special_liunian.get('流年伏吟', [])}")
        else:
            print(f"[DEBUG] special_liunian is empty or None, skipping")
        
        return result


def get_bazi_from_user_input() -> Tuple[Dict[str, str], str, Optional[Dict]]:
    """
    从用户输入获取八字信息

    支持两种输入方式：
    1. 出生日期（推荐）：年月日时（时若有）
    2. 八字干支：年月日时四柱

    返回：八字字典、出生日期、真太阳时信息（可选）
    """
    print("=" * 80)
    print("八字格局分析系统 - 五级论级 + 第六论级（大运流年）")
    print("=" * 80)

    # 选择输入方式
    print("\n请选择输入方式：")
    print("  1. 出生日期（推荐，可精确计算起运）")
    print("  2. 八字干支（年月日时四柱）")

    while True:
        choice = input("\n请输入选择 (1/2, 默认1): ").strip()
        if choice == '':
            choice = '1'

        if choice in ['1', '2']:
            break
        print("输入错误，请重新输入")

    if choice == '1':
        # 使用出生日期
        return get_bazi_from_date_input()
    else:
        # 使用八字干支
        return get_bazi_from_ganzhi_input()


def get_bazi_from_date_input() -> Tuple[Dict[str, str], str, Optional[Dict]]:
    """从出生日期获取八字（支持无时柱），可选真太阳时"""
    print("\n" + "=" * 80)
    print("【出生日期输入】")
    print("=" * 80)
    print("输入格式：年月日时（时可选），例如：")
    print("  199801011600  (带时辰)  或  19980614  (无时辰)")
    print("  200010011000  (带时辰)  或  20001001  (无时辰)")

    while True:
        try:
            date_str = input("\n请输入出生日期: ").strip()

            if len(date_str) < 8:
                print("输入格式错误，最少需要8位数字（年月日），如：19980614")
                continue

            # 解析年月日
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])

            # 验证范围
            if not (1900 <= year <= 2100):
                print("年份范围应在1900-2100之间")
                continue
            if not (1 <= month <= 12):
                print("月份应在01-12之间")
                continue
            if not (1 <= day <= 31):
                print("日期应在01-31之间")
                continue

            # 解析时辰（可选）
            has_hour = len(date_str) >= 12
            if has_hour:
                hour = int(date_str[8:10])
                if not (0 <= hour <= 23):
                    print("时辰应在00-23之间")
                    continue
            else:
                hour = None  # 没有提供时辰

            # 使用 lunar_python 计算八字
            from lunar_python import Solar
            
            # 获取年月日三柱
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

            # 只有提供了时辰才计算时柱
            if has_hour:
                solar_with_time = Solar.fromYmdHms(year, month, day, hour, 0, 0)
                lunar_with_time = solar_with_time.getLunar()
                ba_with_time = lunar_with_time.getEightChar()
                bazi_dict['time_gan'] = ba_with_time.getTimeGan()
                bazi_dict['time_zhi'] = ba_with_time.getTimeZhi()
                birth_date = f"{year}-{month:02d}-{day:02d} {hour:02d}:00"
            else:
                birth_date = f"{year}-{month:02d}-{day:02d}"
            
            # 询问是否使用真太阳时
            true_solar_info = None
            if has_hour:
                print("\n" + "-" * 80)
                print("【真太阳时选项】")
                print("-" * 80)
                print("真太阳时是根据出生地经度精确计算的时间，比北京时间更准确")
                print("东部城市（如哈尔滨）真太阳时比北京时间快")
                print("西部城市（如乌鲁木齐）真太阳时比北京时间慢")
                
                use_true_solar = input("\n是否使用真太阳时？(y/N, 默认N): ").strip().upper() == 'Y'
                
                if use_true_solar:
                    try:
                        from city_database import get_city_list
                        from true_solar_time import calculate_true_solar_time, format_true_solar_time_result
                        
                        # 显示城市列表（简化显示）
                        print("\n请选择出生地（输入城市名称，如：北京、上海、广州）：")
                        city_input = input("请输入城市名称: ").strip()
                        
                        # 查找城市
                        from city_database import search_city
                        matched_cities = search_city(city_input)
                        
                        if matched_cities:
                            if len(matched_cities) == 1:
                                # 只有一个匹配，直接使用
                                prov, city, lon, lat = matched_cities[0]
                                print(f"\n已选择: {prov} {city}")
                                print(f"经纬度: 东经{lon:.4f}°, 北纬{lat:.4f}°")
                            else:
                                # 多个匹配，让用户选择
                                print(f"\n找到{len(matched_cities)}个匹配城市：")
                                for i, (prov, city, lon, lat) in enumerate(matched_cities[:10], 1):
                                    print(f"  {i}. {prov} {city}")
                                
                                choice = input(f"\n请选择 (1-{min(len(matched_cities), 10)}): ").strip()
                                try:
                                    idx = int(choice) - 1
                                    if 0 <= idx < len(matched_cities):
                                        prov, city, lon, lat = matched_cities[idx]
                                        print(f"\n已选择: {prov} {city}")
                                    else:
                                        print("选择无效，不使用真太阳时")
                                        use_true_solar = False
                                except ValueError:
                                    print("输入无效，不使用真太阳时")
                                    use_true_solar = False
                            
                            if use_true_solar:
                                # 计算真太阳时
                                result = calculate_true_solar_time(year, month, day, hour, 0, lon, lat)
                                true_solar_info = {
                                    'original_time': result['original_time'],
                                    'true_solar_time': result['true_solar_time'],
                                    'longitude_diff': result['longitude_diff'],
                                    'equation_of_time': result['equation_of_time'],
                                    'total_diff': result['total_diff'],
                                    'longitude': lon,
                                    'latitude': lat,
                                    'city': f"{prov} {city}"
                                }
                                
                                # 显示计算结果
                                print("\n" + format_true_solar_time_result(result))
                                
                                # 询问是否使用真太阳时进行八字计算
                                confirm = input("\n是否使用真太阳时进行八字计算？(Y/n, 默认Y): ").strip()
                                if confirm.upper() != 'N':
                                    # 使用真太阳时的时间重新计算八字
                                    new_year = result['year']
                                    new_month = result['month']
                                    new_day = result['day']
                                    new_hour = result['hour']
                                    
                                    # 重新计算八字
                                    solar_new = Solar.fromYmdHms(new_year, new_month, new_day, new_hour, 0, 0)
                                    lunar_new = solar_new.getLunar()
                                    ba_new = lunar_new.getEightChar()
                                    
                                    bazi_dict = {
                                        'year_gan': ba_new.getYearGan(),
                                        'year_zhi': ba_new.getYearZhi(),
                                        'month_gan': ba_new.getMonthGan(),
                                        'month_zhi': ba_new.getMonthZhi(),
                                        'day_gan': ba_new.getDayGan(),
                                        'day_zhi': ba_new.getDayZhi(),
                                        'time_gan': ba_new.getTimeGan(),
                                        'time_zhi': ba_new.getTimeZhi()
                                    }
                                    birth_date = f"{new_year}-{new_month:02d}-{new_day:02d} {new_hour:02d}:00"
                                    
                                    print("\n" + "=" * 80)
                                    print("【真太阳时八字】")
                                    print("=" * 80)
                                    print(f"  年柱: {bazi_dict['year_gan']}{bazi_dict['year_zhi']}")
                                    print(f"  月柱: {bazi_dict['month_gan']}{bazi_dict['month_zhi']}")
                                    print(f"  日柱: {bazi_dict['day_gan']}{bazi_dict['day_zhi']}")
                                    print(f"  时柱: {bazi_dict['time_gan']}{bazi_dict['time_zhi']}")
                                    print(f"  出生日期: {birth_date}")
                                    print("=" * 80)
                                else:
                                    print("使用原时间进行八字计算")
                        else:
                            print(f"未找到城市'{city_input}'，不使用真太阳时")
                    except Exception as e:
                        print(f"真太阳时计算出错: {e}")
                        print("使用原时间进行八字计算")
            
            return bazi_dict, birth_date, true_solar_info
            
        except ValueError as e:
            print(f"输入错误: {e}")
            continue
        except Exception as e:
            print(f"发生错误: {e}")
            continue


def get_bazi_from_ganzhi_input() -> Tuple[Dict[str, str], str, None]:
    """从八字干支获取八字"""
    print("\n" + "=" * 80)
    print("【八字干支输入】")
    print("=" * 80)
    print("请依次输入八字的四柱干支")
    print("格式：年月日时四柱，例如：")
    print("  戊寅戊午壬辰戊申")

    # 天干列表
    GANS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    # 地支列表
    ZHIS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    while True:
        try:
            ganzhi_str = input("\n请输入八字（年月日时四柱，如戊寅戊午壬辰戊申）: ").strip()

            # 验证长度
            if len(ganzhi_str) != 8:
                print("输入格式错误，请输入8位干支（年月日时四柱），如：戊寅戊午壬辰戊申")
                continue

            # 分解为四柱
            year_pillar = ganzhi_str[0:2]
            month_pillar = ganzhi_str[2:4]
            day_pillar = ganzhi_str[4:6]
            time_pillar = ganzhi_str[6:8]

            # 验证每个柱
            pillars = {
                '年柱': year_pillar,
                '月柱': month_pillar,
                '日柱': day_pillar,
                '时柱': time_pillar
            }

            valid = True
            for pillar_name, pillar in pillars.items():
                if len(pillar) != 2 or pillar[0] not in GANS or pillar[1] not in ZHIS:
                    print(f"{pillar_name}格式错误，请输入正确的干支，如：{year_pillar} {month_pillar}")
                    valid = False
                    break

            if not valid:
                continue

            bazi_dict = {
                'year_gan': year_pillar[0],
                'year_zhi': year_pillar[1],
                'month_gan': month_pillar[0],
                'month_zhi': month_pillar[1],
                'day_gan': day_pillar[0],
                'day_zhi': day_pillar[1],
                'time_gan': time_pillar[0],
                'time_zhi': time_pillar[1]
            }

            birth_date = None  # 干支输入方式没有具体出生日期

            print("\n" + "-" * 80)
            print("输入的八字：")
            print(f"  年柱: {bazi_dict['year_gan']}{bazi_dict['year_zhi']}")
            print(f"  月柱: {bazi_dict['month_gan']}{bazi_dict['month_zhi']}")
            print(f"  日柱: {bazi_dict['day_gan']}{bazi_dict['day_zhi']}")
            print(f"  时柱: {bazi_dict['time_gan']}{bazi_dict['time_zhi']}")
            print("-" * 80)

            confirm = input("\n八字输入正确吗？(Y/n, 默认Y): ").strip()
            if confirm.upper() != 'N':
                break

        except Exception as e:
            print(f"输入错误: {e}")
            print("请重新输入")

    return bazi_dict, birth_date, None


def get_gender() -> bool:
    """获取性别"""
    print("\n" + "=" * 80)
    print("【性别输入】")
    print("=" * 80)
    print("  1：男命")
    print("  0：女命")

    while True:
        gender = input("\n请输入性别 (1/0, 默认1): ").strip()
        if gender == '':
            return True
        if gender == '1':
            return True
        elif gender == '0':
            return False
        print("输入错误，请输入 1（男）或 0（女）")


def get_liunian_year() -> Optional[int]:
    """获取流年年份（可选）"""
    print("\n" + "=" * 80)
    print("【流年分析】")
    print("=" * 80)
    print("提示：第六论级（大运流年综合分析）需要指定流年年份")
    print("如果不指定，将只进行第一至五论级的分析")

    while True:
        year_input = input("\n请输入要分析的流年年份 (如: 2026, 留空则默认使用今年): ").strip()

        if year_input == '':
            # 默认使用今年
            from datetime import datetime
            current_year = datetime.now().year
            print(f"默认使用当前年份: {current_year}")
            return current_year

        try:
            year = int(year_input)
            if 1900 <= year <= 2100:
                return year
            else:
                print("年份范围应在1900-2100之间")
        except ValueError:
            print("输入错误，请输入有效的年份")


def interactive_main():
    """交互式主函数"""
    # 获取八字信息（支持真太阳时）
    bazi_dict, birth_date, true_solar_info = get_bazi_from_user_input()

    # 获取性别
    is_male = get_gender()

    # 获取流年年份（可选）
    liunian_year = get_liunian_year()

    # 创建分析器
    print("\n" + "=" * 80)
    print("开始分析...")
    
    # 显示真太阳时信息（如果使用了）
    if true_solar_info:
        print("\n【使用真太阳时计算】")
        print(f"  出生地: {true_solar_info['city']}")
        print(f"  原时间: {true_solar_info['original_time']}")
        print(f"  真太阳时: {true_solar_info['true_solar_time']}")
        print(f"  总时差: {true_solar_info['total_diff']:+.2f}分钟")
    print("=" * 80)

    analyzer = GeJuAnalyzerV5(
        bazi_dict,
        liunian_year=liunian_year,
        is_male=is_male,
        birth_date=birth_date
    )

    # 执行分析
    result = analyzer.analyze()

    # 打印结果
    print("\n")
    analyzer.print_analysis()

    # 如果有大运流年分析，打印第五论级
    if liunian_year and analyzer.dayun_liunian:
        print("\n")
        analyzer.print_fifth_level()

    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)


def main():
    """主函数: 交互式界面"""
    interactive_main()


if __name__ == '__main__':
    main()
