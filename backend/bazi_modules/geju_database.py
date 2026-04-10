#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格局数据库系统
用于八字格局类型识别和身强身弱分析

作者: Claude AI
创建日期: 2025-01-30
版本: 1.0
"""

from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, namedtuple
import json


class ShiShenCalculator:
    """
    十神计算器
    用于计算天干相对于日主的十神关系
    """
    
    # 十神名称
    SHI_SHEN_NAMES = {
        '正官': '正官',
        '七杀': '七杀', 
        '正印': '正印',
        '偏印': '偏印',
        '食神': '食神',
        '伤官': '伤官',
        '正财': '正财',
        '偏财': '偏财',
        '比肩': '比肩',
        '劫财': '劫财'
    }
    
    def __init__(self):
        """初始化十神计算器"""
        pass
    
    def get_shishen(self, day_gan: str, target_gan: str) -> str:
        """
        计算某天干相对于日主的十神
        
        参数:
            day_gan: 日主天干
            target_gan: 目标天干
            
        返回:
            十神名称
        """
        if not day_gan or not target_gan:
            return ''
        if day_gan == target_gan:
            return '比肩'
        
        # 五行
        gan_wuxing = {
            '甲': '木', '乙': '木',
            '丙': '火', '丁': '火',
            '戊': '土', '己': '土',
            '庚': '金', '辛': '金',
            '壬': '水', '癸': '水'
        }
        
        # 阴阳属性
        gan_yinyang = {
            '甲': '阳', '乙': '阴',
            '丙': '阳', '丁': '阴',
            '戊': '阳', '己': '阴',
            '庚': '阳', '辛': '阴',
            '壬': '阳', '癸': '阴'
        }
        
        # 五行生克关系
        wuxing_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        wuxing_ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        
        day_wx = gan_wuxing[day_gan]
        day_yy = gan_yinyang[day_gan]
        target_wx = gan_wuxing[target_gan]
        target_yy = gan_yinyang[target_gan]
        
        # 同五行
        if day_wx == target_wx:
            return '比肩' if day_yy == target_yy else '劫财'
        
        # 目标生我（印星）
        if wuxing_sheng[target_wx] == day_wx:
            return '正印' if day_yy != target_yy else '偏印'
        
        # 我生目标（食伤）
        if wuxing_sheng[day_wx] == target_wx:
            return '食神' if day_yy != target_yy else '伤官'
        
        # 目标克我（官杀）
        if wuxing_ke[target_wx] == day_wx:
            return '正官' if day_yy != target_yy else '七杀'
        
        # 我克目标（财星）
        if wuxing_ke[day_wx] == target_wx:
            return '正财' if day_yy != target_yy else '偏财'
        
        return ''
    
    def get_zhishishen(self, day_gan: str, zhi: str) -> List[Tuple[str, str, float]]:
        """
        获取地支藏干对应的十神
        
        参数:
            day_gan: 日主天干
            zhi: 地支
            
        返回:
            [(藏干, 十神, 力量系数), ...]
        """
        if not zhi:
            return []
        
        # 地支藏干
        zhi_cangan = {
            '子': [('癸', 1.0)],
            '丑': [('己', 1.0), ('癸', 0.6), ('辛', 0.3)],
            '寅': [('甲', 1.0), ('丙', 0.6), ('戊', 0.3)],
            '卯': [('乙', 1.0)],
            '辰': [('戊', 1.0), ('乙', 0.6), ('癸', 0.3)],
            '巳': [('丙', 1.0), ('戊', 0.6), ('庚', 0.3)],
            '午': [('丁', 1.0), ('己', 0.6)],
            '未': [('己', 1.0), ('丁', 0.6), ('乙', 0.3)],
            '申': [('庚', 1.0), ('壬', 0.6), ('戊', 0.3)],
            '酉': [('辛', 1.0)],
            '戌': [('戊', 1.0), ('辛', 0.6), ('丁', 0.3)],
            '亥': [('壬', 1.0), ('甲', 0.6)]
        }
        
        result = []
        for cangan, power in zhi_cangan.get(zhi, []):
            shishen = self.get_shishen(day_gan, cangan)
            result.append((cangan, shishen, power))
        return result
    
    def analyze_bazi_shishen(self, bazi: Dict[str, str]) -> Dict:
        """
        分析八字的十神分布
        
        参数:
            bazi: 八字字典
            
        返回:
            十神分析结果
        """
        day_gan = bazi.get('day_gan', '')
        if not day_gan:
            return {}
        
        # 天干十神
        tian_gan_shishen = {}
        gan_positions = {
            'year_gan': '年干',
            'month_gan': '月干',
            'time_gan': '时干'
        }
        
        for key, name in gan_positions.items():
            gan = bazi.get(key, '')
            if gan:
                tian_gan_shishen[name] = self.get_shishen(day_gan, gan)
        
        # 地支十神（以本气为主）
        zhi_shishen = {}
        zhi_positions = {
            'year_zhi': '年支',
            'month_zhi': '月支',
            'day_zhi': '日支',
            'time_zhi': '时支'
        }
        
        for key, name in zhi_positions.items():
            zhi = bazi.get(key, '')
            if zhi:
                cangan_list = self.get_zhishishen(day_gan, zhi)
                if cangan_list:
                    # 本气十神
                    zhi_shishen[name] = {
                        '本气': cangan_list[0][1],
                        '藏干': [(cg, ss) for cg, ss, _ in cangan_list]
                    }
        
        # 统计十神数量
        shishen_count = defaultdict(float)
        
        # 天干十神计数（权重1.0）
        for pos, ss in tian_gan_shishen.items():
            shishen_count[ss] += 1.0
        
        # 地支十神计数（本气权重1.0，中气0.6，余气0.3）
        for pos, info in zhi_shishen.items():
            zhi = bazi.get('year_zhi' if pos == '年支' else 'month_zhi' if pos == '月支' 
                          else 'day_zhi' if pos == '日支' else 'time_zhi', '')
            cangan_list = self.get_zhishishen(day_gan, zhi)
            for cg, ss, power in cangan_list:
                shishen_count[ss] += power
        
        return {
            '天干十神': tian_gan_shishen,
            '地支十神': zhi_shishen,
            '十神统计': dict(shishen_count)
        }


class ShiShenGeJuAnalyzer:
    """
    十神组合格局分析器
    用于分析八字中的十神组合格局
    """
    
    def __init__(self):
        """初始化分析器"""
        self.shishen_calc = ShiShenCalculator()
        self.geju_rules = self._init_geju_rules()
    
    def _init_geju_rules(self) -> Dict:
        """初始化格局规则"""
        return {
            '贪财坏印': {
                'condition': '1. 财星当令或旺相；2. 印星衰弱无根；3. 财星与印星直接作用；4. 日主衰弱（非必须）',
                'description': '财星旺而克破印星，主学业受阻、与长辈缘薄、因财失义',
                'buchengge': '印星有强根，或财星与印星中间有通关之物'
            },
            '伤官克官': {
                'condition': '1. 伤官当令或旺相；2. 正官透出且无救应；3. 伤官与正官直接作用',
                'description': '伤官旺而克正官，主是非口舌、官非、与上司不和',
                'buchengge': '有强旺印星制伤官（伤官配印），或有财星通关'
            },
            '劫财败财': {
                'condition': '1. 劫财当令或旺相；2. 财星衰弱无护；3. 劫财与财星直接作用；4. 日主身强',
                'description': '劫财旺而克破财星，主破财、被朋友拖累、财运不稳',
                'buchengge': '有官杀制劫，或财星未直接被克'
            },
            '枭神夺食': {
                'condition': '1. 枭神当令或旺相；2. 食神弱而无护；3. 枭神与食神直接作用',
                'description': '偏印旺而克食神，主才华不展、健康问题、子女缘薄',
                'buchengge': '有财星制枭，或枭神与食神中间有比劫通关'
            },
            '杀印相生': {
                'condition': '1. 七杀当令或旺相；2. 正印透出有力；3. 印星无破损；4. 日主有根',
                'description': '七杀生印星，印星生日主，主贵气、权威、化险为夷',
                'buchengge': '印星弱而受制，或七杀与印星不相邻'
            },
            '官杀制财': {
                'condition': '1. 官杀当令或旺相；2. 财星弱而无护；3. 官杀与财星直接作用',
                'description': '官杀克制财星，需辩证看待：财为忌则吉，财为喜则凶',
                'buchengge': '有食伤通关，或财星有比劫帮扶'
            },
            '食神生财': {
                'condition': '1. 食神当令或旺相；2. 财星透出有根；3. 食神与财星相生；4. 日主有根',
                'description': '食神生财星，主技术变现、财源稳定、衣食无忧',
                'buchengge': '财星虚浮无根，或有枭神夺食'
            },
            '食神制杀': {
                'condition': '1. 七杀当令或旺相；2. 食神有力；3. 食神与七杀力量相当；4. 无印财破格',
                'description': '食神克制七杀，主以技艺化解危机、武职显贵',
                'buchengge': '有印星克制食神，或杀重食轻制不住'
            },
            '财官双美': {
                'condition': '1. 财星与官星配合有情；2. 财官皆为喜用；3. 财官清纯不杂；4. 财官有根透干',
                'description': '财星生官星，主富贵双全、事业有成、社会地位高',
                'buchengge': '身弱不胜财官，或财官被冲克'
            },
            '羊刃制杀': {
                'condition': '1. 羊刃当令或旺相；2. 七杀透出有力；3. 羊刃与七杀力量相当；4. 无印食通关',
                'description': '羊刃克制七杀，主武职显贵、刚毅果断、能成大事',
                'buchengge': '有印星化杀，或羊刃无制'
            },
            '官印相生': {
                'condition': '1. 正官当令或旺相；2. 正印透出有根；3. 官印相生无破；4. 日主有根',
                'description': '正官生正印，主文职贵气、学业有成、清贵高雅',
                'buchengge': '有财星坏印，或伤官克官'
            },
            '伤官见官': {
                'condition': '1. 伤官当令或旺相；2. 正官透出有力；3. 无财星通关；4. 无印星制伤',
                'description': '伤官克制正官，主叛逆不羁、官非口舌、事业起伏',
                'buchengge': '有印星制伤官，或有财星通关'
            },
            '比劫林立': {
                'condition': '1. 比劫多现；2. 日主强旺；3. 财星弱而无护',
                'description': '比劫过多克制财星，主破财、竞争激烈、易与人争斗',
                'buchengge': '有官杀制劫，或有食伤泄秀'
            }
        }
    
    def analyze_shishen_geju(self, bazi: Dict[str, str], shenqiang_result: Dict = None) -> Dict:
        """
        分析十神组合格局
        
        参数:
            bazi: 八字字典
            shenqiang_result: 身强身弱分析结果（可选）
            
        返回:
            十神组合格局分析结果
        """
        day_gan = bazi.get('day_gan', '')
        if not day_gan:
            return {'格局列表': [], '格局详情': {}}
        
        # 获取十神分布
        shishen_dist = self.shishen_calc.analyze_bazi_shishen(bazi)
        
        # 判断各格局
        identified_gejus = []
        geju_details = {}
        
        # 1. 贪财坏印
        if self._check_tancaihuaiyin(bazi, shishen_dist):
            identified_gejus.append('贪财坏印')
            geju_details['贪财坏印'] = self._get_geju_detail('贪财坏印', shishen_dist)
        
        # 2. 伤官克官
        if self._check_shangguankeguan(bazi, shishen_dist):
            identified_gejus.append('伤官克官')
            geju_details['伤官克官'] = self._get_geju_detail('伤官克官', shishen_dist)
        
        # 3. 劫财败财
        if self._check_jiecaibaicai(bazi, shishen_dist, shenqiang_result):
            identified_gejus.append('劫财败财')
            geju_details['劫财败财'] = self._get_geju_detail('劫财败财', shishen_dist)
        
        # 4. 枭神夺食
        if self._check_xiaoshenduoshi(bazi, shishen_dist):
            identified_gejus.append('枭神夺食')
            geju_details['枭神夺食'] = self._get_geju_detail('枭神夺食', shishen_dist)
        
        # 5. 杀印相生
        if self._check_shayinxiangxing(bazi, shishen_dist):
            identified_gejus.append('杀印相生')
            geju_details['杀印相生'] = self._get_geju_detail('杀印相生', shishen_dist)
        
        # 6. 官杀制财
        if self._check_guanshazhicai(bazi, shishen_dist):
            identified_gejus.append('官杀制财')
            geju_details['官杀制财'] = self._get_geju_detail('官杀制财', shishen_dist)
        
        # 7. 食神生财
        if self._check_shishengshengcai(bazi, shishen_dist):
            identified_gejus.append('食神生财')
            geju_details['食神生财'] = self._get_geju_detail('食神生财', shishen_dist)
        
        # 8. 食神制杀
        if self._check_shishenzhisha(bazi, shishen_dist):
            identified_gejus.append('食神制杀')
            geju_details['食神制杀'] = self._get_geju_detail('食神制杀', shishen_dist)
        
        # 9. 财官双美
        if self._check_caiguanshuangmei(bazi, shishen_dist):
            identified_gejus.append('财官双美')
            geju_details['财官双美'] = self._get_geju_detail('财官双美', shishen_dist)
        
        # 10. 羊刃制杀
        if self._check_yangrenzhisha(bazi, shishen_dist):
            identified_gejus.append('羊刃制杀')
            geju_details['羊刃制杀'] = self._get_geju_detail('羊刃制杀', shishen_dist)
        
        # 11. 官印相生
        if self._check_guanyinxiangxing(bazi, shishen_dist):
            identified_gejus.append('官印相生')
            geju_details['官印相生'] = self._get_geju_detail('官印相生', shishen_dist)
        
        # 12. 伤官见官
        if self._check_shangguanjianguan(bazi, shishen_dist):
            identified_gejus.append('伤官见官')
            geju_details['伤官见官'] = self._get_geju_detail('伤官见官', shishen_dist)
        
        # 13. 比劫林立
        if self._check_bijielinli(bazi, shishen_dist, shenqiang_result):
            identified_gejus.append('比劫林立')
            geju_details['比劫林立'] = self._get_geju_detail('比劫林立', shishen_dist)
        
        return {
            '格局列表': identified_gejus,
            '格局详情': geju_details,
            '十神分布': shishen_dist
        }
    
    def _get_geju_detail(self, geju_name: str, shishen_dist: Dict) -> Dict:
        """获取格局详细信息"""
        rule = self.geju_rules.get(geju_name, {})
        return {
            '名称': geju_name,
            '成格条件': rule.get('condition', ''),
            '格局描述': rule.get('description', ''),
            '不成格情况': rule.get('buchengge', '')
        }
    
    def _get_shishen_count(self, shishen_dist: Dict, shishen_name: str) -> float:
        """获取某十神的数量"""
        return shishen_dist.get('十神统计', {}).get(shishen_name, 0)
    
    def _has_shishen_in_month(self, bazi: Dict, shishen_name: str) -> bool:
        """检查某十神是否当令（月令）"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        if not day_gan or not month_zhi:
            return False
        
        zhi_cangan = {
            '子': [('癸', 1.0)],
            '丑': [('己', 1.0), ('癸', 0.6), ('辛', 0.3)],
            '寅': [('甲', 1.0), ('丙', 0.6), ('戊', 0.3)],
            '卯': [('乙', 1.0)],
            '辰': [('戊', 1.0), ('乙', 0.6), ('癸', 0.3)],
            '巳': [('丙', 1.0), ('戊', 0.6), ('庚', 0.3)],
            '午': [('丁', 1.0), ('己', 0.6)],
            '未': [('己', 1.0), ('丁', 0.6), ('乙', 0.3)],
            '申': [('庚', 1.0), ('壬', 0.6), ('戊', 0.3)],
            '酉': [('辛', 1.0)],
            '戌': [('戊', 1.0), ('辛', 0.6), ('丁', 0.3)],
            '亥': [('壬', 1.0), ('甲', 0.6)]
        }
        
        cangan_list = zhi_cangan.get(month_zhi, [])
        for cangan, _ in cangan_list:
            ss = self.shishen_calc.get_shishen(day_gan, cangan)
            if ss == shishen_name:
                return True
        return False
    
    def _get_gan_shishen_positions(self, bazi: Dict, shishen_name: str) -> List[str]:
        """获取某十神在天干的位置列表"""
        day_gan = bazi.get('day_gan', '')
        positions = []
        gan_map = {
            'year_gan': '年干',
            'month_gan': '月干', 
            'time_gan': '时干'
        }
        
        for key, pos_name in gan_map.items():
            gan = bazi.get(key, '')
            if gan:
                ss = self.shishen_calc.get_shishen(day_gan, gan)
                if ss == shishen_name:
                    positions.append(pos_name)
        return positions
    
    def _check_tancaihuaiyin(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查贪财坏印"""
        day_gan = bazi.get('day_gan', '')
        
        # 财星旺相
        cai_count = self._get_shishen_count(shishen_dist, '正财') + self._get_shishen_count(shishen_dist, '偏财')
        if cai_count < 1.5:
            return False
        
        # 印星衰弱
        yin_count = self._get_shishen_count(shishen_dist, '正印') + self._get_shishen_count(shishen_dist, '偏印')
        if yin_count > 1.0:
            return False
        
        # 财星当令或透干
        cai_in_month = self._has_shishen_in_month(bazi, '正财') or self._has_shishen_in_month(bazi, '偏财')
        cai_tougan = len(self._get_gan_shishen_positions(bazi, '正财')) + len(self._get_gan_shishen_positions(bazi, '偏财'))
        
        if cai_in_month or cai_tougan >= 1:
            return True
        
        return False
    
    def _check_shangguankeguan(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查伤官克官"""
        # 伤官旺相
        shangguan_count = self._get_shishen_count(shishen_dist, '伤官')
        if shangguan_count < 1.0:
            return False
        
        # 正官透出
        zhengguan_positions = self._get_gan_shishen_positions(bazi, '正官')
        if len(zhengguan_positions) < 1:
            return False
        
        # 伤官当令或透干
        shangguan_in_month = self._has_shishen_in_month(bazi, '伤官')
        shangguan_tougan = len(self._get_gan_shishen_positions(bazi, '伤官'))
        
        if shangguan_in_month or shangguan_tougan >= 1:
            # 检查无印星制伤
            yin_count = self._get_shishen_count(shishen_dist, '正印')
            if yin_count < 1.0:
                return True
        
        return False
    
    def _check_jiecaibaicai(self, bazi: Dict, shishen_dist: Dict, shenqiang_result: Dict = None) -> bool:
        """检查劫财败财"""
        # 劫财旺相
        jiecai_count = self._get_shishen_count(shishen_dist, '劫财')
        if jiecai_count < 1.5:
            return False
        
        # 财星衰弱
        cai_count = self._get_shishen_count(shishen_dist, '正财') + self._get_shishen_count(shishen_dist, '偏财')
        if cai_count > 1.5:
            return False
        
        # 日主身强
        if shenqiang_result:
            qiangruo = shenqiang_result.get('强弱判定', '')
            if '弱' in qiangruo and '从' not in qiangruo:
                return False
        
        # 劫财当令或透干
        jiecai_in_month = self._has_shishen_in_month(bazi, '劫财')
        jiecai_tougan = len(self._get_gan_shishen_positions(bazi, '劫财'))
        
        if jiecai_in_month or jiecai_tougan >= 1:
            return True
        
        return False
    
    def _check_xiaoshenduoshi(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查枭神夺食"""
        # 偏印旺相
        pianyin_count = self._get_shishen_count(shishen_dist, '偏印')
        if pianyin_count < 1.0:
            return False
        
        # 食神弱
        shishen_count = self._get_shishen_count(shishen_dist, '食神')
        if shishen_count > 1.0:
            return False
        
        # 偏印当令或透干
        pianyin_in_month = self._has_shishen_in_month(bazi, '偏印')
        pianyin_tougan = len(self._get_gan_shishen_positions(bazi, '偏印'))
        
        if pianyin_in_month or pianyin_tougan >= 1:
            # 检查无财星制枭
            cai_count = self._get_shishen_count(shishen_dist, '正财') + self._get_shishen_count(shishen_dist, '偏财')
            if cai_count < 1.0:
                return True
        
        return False
    
    def _check_shayinxiangxing(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查杀印相生"""
        # 七杀旺相
        qisha_count = self._get_shishen_count(shishen_dist, '七杀')
        if qisha_count < 1.0:
            return False
        
        # 正印有力
        zhengyin_count = self._get_shishen_count(shishen_dist, '正印')
        if zhengyin_count < 0.5:
            return False
        
        # 七杀当令或透干
        qisha_in_month = self._has_shishen_in_month(bazi, '七杀')
        qisha_tougan = len(self._get_gan_shishen_positions(bazi, '七杀'))
        
        if qisha_in_month or qisha_tougan >= 1:
            # 正印透干
            zhengyin_tougan = len(self._get_gan_shishen_positions(bazi, '正印'))
            if zhengyin_tougan >= 1:
                return True
        
        return False
    
    def _check_guanshazhicai(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查官杀制财"""
        # 官杀旺相
        guan_count = self._get_shishen_count(shishen_dist, '正官') + self._get_shishen_count(shishen_dist, '七杀')
        if guan_count < 1.0:
            return False
        
        # 财星弱
        cai_count = self._get_shishen_count(shishen_dist, '正财') + self._get_shishen_count(shishen_dist, '偏财')
        if cai_count > 1.5:
            return False
        
        # 官杀当令或透干
        guan_in_month = self._has_shishen_in_month(bazi, '正官') or self._has_shishen_in_month(bazi, '七杀')
        guan_tougan = len(self._get_gan_shishen_positions(bazi, '正官')) + len(self._get_gan_shishen_positions(bazi, '七杀'))
        
        if guan_in_month or guan_tougan >= 1:
            return True
        
        return False
    
    def _check_shishengshengcai(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查食神生财"""
        # 食神旺相
        shishen_count = self._get_shishen_count(shishen_dist, '食神')
        if shishen_count < 1.0:
            return False
        
        # 财星有根
        cai_count = self._get_shishen_count(shishen_dist, '正财') + self._get_shishen_count(shishen_dist, '偏财')
        if cai_count < 0.5:
            return False
        
        # 食神当令或透干
        shishen_in_month = self._has_shishen_in_month(bazi, '食神')
        shishen_tougan = len(self._get_gan_shishen_positions(bazi, '食神'))
        
        if shishen_in_month or shishen_tougan >= 1:
            # 无枭神夺食
            pianyin_count = self._get_shishen_count(shishen_dist, '偏印')
            if pianyin_count < 1.0:
                return True
        
        return False
    
    def _check_shishenzhisha(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查食神制杀"""
        # 七杀旺相
        qisha_count = self._get_shishen_count(shishen_dist, '七杀')
        if qisha_count < 1.0:
            return False
        
        # 食神有力
        shishen_count = self._get_shishen_count(shishen_dist, '食神')
        if shishen_count < 0.5:
            return False
        
        # 七杀当令或透干
        qisha_in_month = self._has_shishen_in_month(bazi, '七杀')
        qisha_tougan = len(self._get_gan_shishen_positions(bazi, '七杀'))
        
        if qisha_in_month or qisha_tougan >= 1:
            # 食神透干
            shishen_tougan = len(self._get_gan_shishen_positions(bazi, '食神'))
            if shishen_tougan >= 1:
                # 无印星克制食神
                zhengyin_count = self._get_shishen_count(shishen_dist, '正印')
                if zhengyin_count < 1.0:
                    return True
        
        return False
    
    def _check_caiguanshuangmei(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查财官双美"""
        # 财星旺相
        cai_count = self._get_shishen_count(shishen_dist, '正财') + self._get_shishen_count(shishen_dist, '偏财')
        if cai_count < 1.0:
            return False
        
        # 官星旺相
        guan_count = self._get_shishen_count(shishen_dist, '正官')
        if guan_count < 1.0:
            return False
        
        # 财官均透干
        cai_tougan = len(self._get_gan_shishen_positions(bazi, '正财')) + len(self._get_gan_shishen_positions(bazi, '偏财'))
        guan_tougan = len(self._get_gan_shishen_positions(bazi, '正官'))
        
        if cai_tougan >= 1 and guan_tougan >= 1:
            return True
        
        return False
    
    def _check_yangrenzhisha(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查羊刃制杀"""
        day_gan = bazi.get('day_gan', '')
        
        # 羊刃地支
        yangren_zhi = {'甲': '卯', '丙': '午', '戊': '午', '庚': '酉', '壬': '子'}
        
        if day_gan not in yangren_zhi:
            return False
        
        # 羊刃当令
        month_zhi = bazi.get('month_zhi', '')
        yangren_zhi_value = yangren_zhi.get(day_gan, '')
        
        if month_zhi != yangren_zhi_value:
            # 检查地支是否有羊刃
            zhis = [bazi.get('year_zhi', ''), bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
            if yangren_zhi_value not in zhis:
                return False
        
        # 七杀有力
        qisha_count = self._get_shishen_count(shishen_dist, '七杀')
        if qisha_count < 1.0:
            return False
        
        # 七杀透干
        qisha_tougan = len(self._get_gan_shishen_positions(bazi, '七杀'))
        if qisha_tougan >= 1:
            return True
        
        return False
    
    def _check_guanyinxiangxing(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查官印相生"""
        # 正官旺相
        zhengguan_count = self._get_shishen_count(shishen_dist, '正官')
        if zhengguan_count < 1.0:
            return False
        
        # 正印有力
        zhengyin_count = self._get_shishen_count(shishen_dist, '正印')
        if zhengyin_count < 0.5:
            return False
        
        # 正官当令或透干
        guan_in_month = self._has_shishen_in_month(bazi, '正官')
        guan_tougan = len(self._get_gan_shishen_positions(bazi, '正官'))
        
        if guan_in_month or guan_tougan >= 1:
            # 正印透干
            zhengyin_tougan = len(self._get_gan_shishen_positions(bazi, '正印'))
            if zhengyin_tougan >= 1:
                # 无财星坏印
                cai_count = self._get_shishen_count(shishen_dist, '正财') + self._get_shishen_count(shishen_dist, '偏财')
                if cai_count < 1.0:
                    return True
        
        return False
    
    def _check_shangguanjianguan(self, bazi: Dict, shishen_dist: Dict) -> bool:
        """检查伤官见官"""
        # 伤官旺相
        shangguan_count = self._get_shishen_count(shishen_dist, '伤官')
        if shangguan_count < 1.0:
            return False
        
        # 正官有力
        zhengguan_count = self._get_shishen_count(shishen_dist, '正官')
        if zhengguan_count < 1.0:
            return False
        
        # 伤官当令或透干
        shangguan_in_month = self._has_shishen_in_month(bazi, '伤官')
        shangguan_tougan = len(self._get_gan_shishen_positions(bazi, '伤官'))
        
        if shangguan_in_month or shangguan_tougan >= 1:
            # 正官透干
            zhengguan_tougan = len(self._get_gan_shishen_positions(bazi, '正官'))
            if zhengguan_tougan >= 1:
                # 无财星通关
                cai_count = self._get_shishen_count(shishen_dist, '正财') + self._get_shishen_count(shishen_dist, '偏财')
                if cai_count < 0.5:
                    return True
        
        return False
    
    def _check_bijielinli(self, bazi: Dict, shishen_dist: Dict, shenqiang_result: Dict = None) -> bool:
        """检查比劫林立"""
        # 比劫多现（超过3个）
        biji_count = self._get_shishen_count(shishen_dist, '比肩') + self._get_shishen_count(shishen_dist, '劫财')
        if biji_count < 3.0:
            return False
        
        # 财星弱
        cai_count = self._get_shishen_count(shishen_dist, '正财') + self._get_shishen_count(shishen_dist, '偏财')
        if cai_count > 1.5:
            return False
        
        # 日主强旺
        if shenqiang_result:
            qiangruo = shenqiang_result.get('强弱判定', '')
            if '弱' in qiangruo and '从' not in qiangruo:
                return False
        
        return True
    
    def print_shishen_geju(self, result: Dict, bazi: Dict = None):
        """
        打印十神组合格局分析结果
        
        参数:
            result: analyze_shishen_geju的返回结果
            bazi: 八字字典（可选，用于显示天干地支）
        """
        print("\n" + "=" * 80)
        print("十神组合格局分析")
        print("=" * 80)
        
        # 打印八字信息
        if bazi:
            year_gan = bazi.get('year_gan', '')
            year_zhi = bazi.get('year_zhi', '')
            month_gan = bazi.get('month_gan', '')
            month_zhi = bazi.get('month_zhi', '')
            day_gan = bazi.get('day_gan', '')
            day_zhi = bazi.get('day_zhi', '')
            time_gan = bazi.get('time_gan', '')
            time_zhi = bazi.get('time_zhi', '')
            
            print(f"\n【八字】 {year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {time_gan}{time_zhi}")
            print(f"【日主】 {day_gan}")
        
        # 打印十神分布
        shishen_dist = result.get('十神分布', {})
        print("\n【十神分布】")
        print("  天干十神:")
        for pos, ss in shishen_dist.get('天干十神', {}).items():
            print(f"    {pos}: {ss}")
        
        print("  地支十神（本气）:")
        for pos, info in shishen_dist.get('地支十神', {}).items():
            benqi = info.get('本气', '')
            canggan = info.get('藏干', [])
            cg_str = ', '.join([f"{cg}({ss})" for cg, ss in canggan])
            print(f"    {pos}: {benqi}（藏干: {cg_str}）")
        
        print("  十神统计:")
        for ss, count in shishen_dist.get('十神统计', {}).items():
            print(f"    {ss}: {count:.2f}")
        
        # 打印识别的格局
        geju_list = result.get('格局列表', [])
        geju_details = result.get('格局详情', {})
        
        print(f"\n【十神组合格局】共识别 {len(geju_list)} 个格局")
        print("-" * 80)
        
        if not geju_list:
            print("  未识别出明显的十神组合格局")
        else:
            for i, geju_name in enumerate(geju_list, 1):
                detail = geju_details.get(geju_name, {})
                print(f"\n  【{i}】{geju_name}")
                print(f"      成格条件: {detail.get('成格条件', '')}")
                print(f"      格局描述: {detail.get('格局描述', '')}")
                print(f"      不成格情况: {detail.get('不成格情况', '')}")
        
        print("\n" + "=" * 80)


class GeJuInfo:
    """格局信息类,存储单个格局的完整属性"""
    
    def __init__(self, name: str, category: str, definition: str, 
                 preference: str, condition: str, explanation: str, source: str):
        """
        初始化格局信息
        
        参数:
            name: 格局名称
            category: 类别(正格)
            definition: 定义说明
            preference: 喜忌
            condition: 形成条件
            explanation: 说明描述及古籍依据
            source: 古籍依据
        """
        self.name = name
        self.category = category
        self.definition = definition
        self.preference = preference
        self.condition = condition
        self.explanation = explanation
        self.source = source
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'name': self.name,
            'category': self.category,
            'definition': self.definition,
            'preference': self.preference,
            'condition': self.condition,
            'explanation': self.explanation,
            'source': self.source
        }


class GeJuDatabase:
    """格局数据库类,存储所有格局的定义和计算规则"""
    
    # 天干五行
    GAN_WUXING = {
        '甲': '木', '乙': '木',
        '丙': '火', '丁': '火',
        '戊': '土', '己': '土',
        '庚': '金', '辛': '金',
        '壬': '水', '癸': '水'
    }
    
    # 地支五行
    ZHI_WUXING = {
        '子': '水', '丑': '土',
        '寅': '木', '卯': '木',
        '辰': '土', '巳': '火',
        '午': '火', '未': '土',
        '申': '金', '酉': '金',
        '戌': '土', '亥': '水'
    }
    
    # 地支藏干(本气、中气、余气及力量系数)
    ZHI_CANGAN = {
        '子': [('癸', 1.0)],  # 癸水本气
        '丑': [('己', 1.0), ('癸', 0.6), ('辛', 0.3)],  # 己土本气,癸水中气,辛金余气
        '寅': [('甲', 1.0), ('丙', 0.6), ('戊', 0.3)],  # 甲木本气,丙火中气,戊土余气
        '卯': [('乙', 1.0)],  # 乙木本气
        '辰': [('戊', 1.0), ('乙', 0.6), ('癸', 0.3)],  # 戊土本气,乙木中气,癸水余气
        '巳': [('丙', 1.0), ('戊', 0.6), ('庚', 0.3)],  # 丙火本气,戊土中气,庚金余气
        '午': [('丁', 1.0), ('己', 0.6)],  # 丁火本气,己土中气
        '未': [('己', 1.0), ('丁', 0.6), ('乙', 0.3)],  # 己土本气,丁火中气,乙木余气
        '申': [('庚', 1.0), ('壬', 0.6), ('戊', 0.3)],  # 庚金本气,壬水中气,戊土余气
        '酉': [('辛', 1.0)],  # 辛金本气
        '戌': [('戊', 1.0), ('辛', 0.6), ('丁', 0.3)],  # 戊土本气,辛金中气,丁火余气
        '亥': [('壬', 1.0), ('甲', 0.6)],  # 壬水本气,甲木中气
    }
    
    # 日干禄位
    RI_LU = {
        '甲': '寅', '乙': '卯',
        '丙': '巳', '丁': '午',
        '戊': '巳', '己': '午',
        '庚': '申', '辛': '酉',
        '壬': '亥', '癸': '子'
    }
    
    # 阳干帝旺位(羊刃)
    YANGREN = {
        '甲': '卯', '丙': '午', '戊': '午', '庚': '酉', '壬': '子'
    }
    
    # 五行相生关系
    WUXING_SHENG = {
        '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
    }
    
    # 五行相克关系
    WUXING_KE = {
        '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
    }
    
    # 五行对立关系(死位)
    WUXING_SI = {
        '木': '金', '金': '火', '火': '水', '水': '土', '土': '木'
    }
    
    # 天干阴阳属性
    GAN_YINYANG = {
        '甲': '阳', '乙': '阴',
        '丙': '阳', '丁': '阴',
        '戊': '阳', '己': '阴',
        '庚': '阳', '辛': '阴',
        '壬': '阳', '癸': '阴'
    }
    
    # 地支阴阳属性
    ZHI_YINYANG = {
        '子': '阳', '丑': '阴',
        '寅': '阳', '卯': '阴',
        '辰': '阳', '巳': '阴',
        '午': '阳', '未': '阴',
        '申': '阳', '酉': '阴',
        '戌': '阳', '亥': '阴'
    }

    def _init_tougan_tonggen_data(self):
        """
        初始化透干通根相关数据
        
        依据：
        一、通根定义：天干在地支获得同五行支持
        二、透干定义：地支藏干中的五行在天干透出且与原五行相同
        三、分类：
            1. 按阴阳属性分：通根（阴阳同）、借根（阴阳异）
            2. 按藏干位置分：本气根、中气根、余气根
            3. 按力量大小分：本气通根（力量大）、生扶通根（力量中）、余气通根（力量弱）
        四、强弱等级：
            地支位置：月令 > 日支 > 年支 > 时支
            藏干位置：本气 > 中气 > 余气
            本气通根 vs 余气通根：本气通根力大
            通根 vs 借根：通根（阴阳同）力量强
        """
        # 生扶通根：地支有印星生扶天干
        # 印星五行（生助日主五行）
        self.SHENGFU_GEN = {
            '甲': '水', '乙': '水',
            '丙': '木', '丁': '木',
            '戊': '火', '己': '火',
            '庚': '土', '辛': '土',
            '壬': '金', '癸': '金'
        }

    def __init__(self):
        """初始化格局数据库"""
        self._geju_dict: Dict[str, GeJuInfo] = {}
        self._init_geju_data()

        # 初始化透干通根相关数据
        self._init_tougan_tonggen_data()

        # 初始化喜用神数据
        self._init_xiyongshen_data()

    def _init_xiyongshen_data(self):
        """
        初始化喜用神（衰旺论）数据
        根据日主天干和身强身弱来判断喜用神和忌神
        """
        self.XIYONGSHEN_DATA = {
            '壬': {
                '身强': {
                    '喜神': '木（食伤）、火（财）、土（官杀）',
                    '用神': '木（食伤）、火（财）、土（官杀）',
                    '忌神': '金（印）、水（比劫）',
                    '成长建议': '**喜用神：木（食伤）、火（财）、土（官杀）** \n**忌神：金（印）、水（比劫）** \n**原理**：水势泛滥需疏导。宜加强自律（土），将精力投入创作或技术钻研（木泄秀），或以明确财富目标（火）引导行动。忌再增金水，否则易漂泊无定。'
                },
                '身弱': {
                    '喜神': '金（印）、水（比劫）',
                    '用神': '金（印）、水（比劫）',
                    '忌神': '火（财）、土（官杀）',
                    '成长建议': '**喜用神：金（印）、水（比劫）** \n**忌神：火（财）、土（官杀）** \n**原理**：水弱需扶。宜多读书学习（金印），或加入团队依靠伙伴（水比劫）。避免承担过重压力（土）或追求超出能力的财富目标（火），以防心力交瘁。'
                }
            },
            '癸': {
                '身强': {
                    '喜神': '木（食伤）、火（财）',
                    '用神': '木（食伤）、火（财）',
                    '忌神': '金（印）、水（比劫）',
                    '成长建议': '**喜用神：木（食伤）、火（财）** \n**忌神：金（印）、水（比劫）** \n**原理**：阴水过旺则易凝滞。需以木（食伤）疏导其智谋，转化为才华输出；或以火（财）为目标，让阴柔之力有具体价值去向。忌再增金水，否则易陷入固执与阴郁。'
                },
                '身弱': {
                    '喜神': '金（印）、水（比劫）',
                    '用神': '金（印）、水（比劫）',
                    '忌神': '火（财）、土（官杀）',
                    '成长建议': '**喜用神：金（印）、水（比劫）** \n**忌神：火（财）、土（官杀）** \n**原理**：弱水最需源头活水。需靠学习经典、长辈扶持（金印）增强底气；多与朋友交流（水比劫）分担压力。避免财星（火）耗神或官杀（土）克身带来的过度劳累与压力。'
                }
            },
            '甲': {
                '身强': {
                    '喜神': '火（食伤）、金（官杀）',
                    '用神': '火（食伤）、金（官杀）',
                    '忌神': '水（印）、木（比劫）',
                    '成长建议': '**喜用神：火（食伤）、金（官杀）** \n**忌神：水（印）、木（比劫）** \n**原理**：木旺需疏。宜以火（食伤）发挥才华，将能量导向创造与表达；或以金（官杀）自律，接受规则与磨练以成器。忌再添水木，否则易成"藤萝系甲"，徒增固执而无进展。'
                },
                '身弱': {
                    '喜神': '水（印）、木（比劫）',
                    '用神': '水（印）、木（比劫）',
                    '忌神': '金（官杀）、土（财）',
                    '成长建议': '**喜用神：水（印）、木（比劫）** \n**忌神：金（官杀）、土（财）** \n**原理**：木弱需扶。需靠学习、长辈（水印）增强底蕴，或结伴同行（木比劫）互相扶持。避免过度追求财富（土财）或承担超出能力的压力（金官杀），以免根基动摇。'
                }
            },
            '乙': {
                '身强': {
                    '喜神': '火（食伤）、金（官杀）',
                    '用神': '火（食伤）、金（官杀）',
                    '忌神': '水（印）、木（比劫）',
                    '成长建议': '**喜用神：火（食伤）、金（官杀）** \n**忌神：水（印）、木（比劫）** \n**原理**：藤蔓过盛需引导。宜以火（食伤）展现才华，确立独特风格；或以金（官杀）自律，修剪枝蔓，明确界限。忌再增水木，否则易纠缠不清、缺乏方向。'
                },
                '身弱': {
                    '喜神': '水（印）、木（比劫）',
                    '用神': '水（印）、木（比劫）',
                    '忌神': '金（官杀）、土（财）',
                    '成长建议': '**喜用神：水（印）、木（比劫）** \n**忌神：金（官杀）、土（财）** \n**原理**：弱草最需滋养。需以学习、精神修养（水印）稳固内心；多与同辈、朋友（木比劫）互动增强能量。避免承担过重责任（金）或为物质（土）过度奔波，以防身心俱疲。'
                }
            },
            '丙': {
                '身强': {
                    '喜神': '土（食伤）、金（财）',
                    '用神': '土（食伤）、金（财）',
                    '忌神': '木（印）、火（比劫）',
                    '成长建议': '**喜用神：土（食伤）、金（财）** \n**忌神：木（印）、火（比劫）** \n**原理**：火旺需泄。宜以土（食伤）将能量转化为实际成果，或以金（财）为目标导向，让精力有具体价值去向。忌再添木火，否则易虚火上升，徒耗精力。'
                },
                '身弱': {
                    '喜神': '木（印）、火（比劫）',
                    '用神': '木（印）、火（比劫）',
                    '忌神': '土（食伤）、金（财）、水（官杀）',
                    '成长建议': '**喜用神：木（印）、火（比劫）** \n**忌神：土（食伤）、金（财）、水（官杀）** \n**原理**：火弱需扶。需靠学习、精神修养（木印）增强内在能量，或多与同辈交流（火比劫）互相取暖。避免过度输出（土）或追逐超出能力的目标（金），远离高压环境（水）。'
                }
            },
            '丁': {
                '身强': {
                    '喜神': '土（食伤）、金（财）',
                    '用神': '土（食伤）、金（财）',
                    '忌神': '木（印）、火（比劫）',
                    '成长建议': '**喜用神：土（食伤）、金（财）** \n**忌神：木（印）、火（比劫）** \n**原理**：丁火过旺则易灼烧。宜以土（食伤）疏导细腻心思，转化为创作或技术输出；或以金（财）为目标，将精神追求落地为实际价值。忌再添木火，否则易思虑过度。'
                },
                '身弱': {
                    '喜神': '木（印）、火（比劫）',
                    '用神': '木（印）、火（比劫）',
                    '忌神': '土（食伤）、金（财）、水（官杀）',
                    '成长建议': '**喜用神：木（印）、火（比劫）** \n**忌神：土（食伤）、金（财）、水（官杀）** \n**原理**：弱火最需添油。需靠学习经典、提升内在（木印）稳固心力，或依靠团队伙伴（火比劫）获得支持。避免过度消耗（土）或追求物质压力（金），远离苛刻环境（水）。'
                }
            },
            '戊': {
                '身强': {
                    '喜神': '木（官杀）、金（食伤）',
                    '用神': '木（官杀）、金（食伤）',
                    '忌神': '火（印）、土（比劫）',
                    '成长建议': '**喜用神：木（官杀）、金（食伤）** \n**忌神：火（印）、土（比劫）** \n**原理**：土旺需疏。宜以木（官杀）加强目标感与自律，接受规则与挑战；或以金（食伤）发挥才华，将稳重转化为创造力。忌再添火土，否则易顽固不化、停滞不前。'
                },
                '身弱': {
                    '喜神': '火（印）、土（比劫）',
                    '用神': '火（印）、土（比劫）',
                    '忌神': '木（官杀）、水（财）、金（食伤）',
                    '成长建议': '**喜用神：火（印）、土（比劫）** \n**忌神：木（官杀）、水（财）、金（食伤）** \n**原理**：土弱需扶。需靠学习、长辈（火印）增强底蕴，或依靠团队伙伴（土比劫）稳固根基。避免承担过重压力（木）或追逐过多物质（水），避免过度消耗（金）。'
                }
            },
            '己': {
                '身强': {
                    '喜神': '木（官杀）、金（食伤）',
                    '用神': '木（官杀）、金（食伤）',
                    '忌神': '火（印）、土（比劫）',
                    '成长建议': '**喜用神：木（官杀）、金（食伤）** \n**忌神：火（印）、土（比劫）** \n**原理**：己土过旺则易板结。宜以木（官杀）确立原则与目标，激发进取心；或以金（食伤）引导才华输出，将细腻转化为价值。忌再添火土，否则易满足于现状、缺乏成长。'
                },
                '身弱': {
                    '喜神': '火（印）、土（比劫）',
                    '用神': '火（印）、土（比劫）',
                    '忌神': '木（官杀）、水（财）、金（食伤）',
                    '成长建议': '**喜用神：火（印）、土（比劫）** \n**忌神：木（官杀）、水（财）、金（食伤）** \n**原理**：弱土最需生扶。需靠学习、精神修养（火印）增强内在力量，或多与同辈交流（土比劫）获得支持。避免承担过重责任（木）或为物质奔波（水），避免过度消耗心力（金）。'
                }
            },
            '庚': {
                '身强': {
                    '喜神': '火（官杀）、水（食伤）',
                    '用神': '火（官杀）、水（食伤）',
                    '忌神': '土（印）、金（比劫）',
                    '成长建议': '**喜用神：火（官杀）、水（食伤）** \n**忌神：土（印）、金（比劫）** \n**原理**：金旺需炼。宜以火（官杀）锻炼心性，接受规则与挑战，将刚锐化为担当；或以水（食伤）泄其锋芒，转化为才华与智慧。忌再添土金，否则易刚折、顽固不化。'
                },
                '身弱': {
                    '喜神': '土（印）、金（比劫）',
                    '用神': '土（印）、金（比劫）',
                    '忌神': '火（官杀）、木（财）、水（食伤）',
                    '成长建议': '**喜用神：土（印）、金（比劫）** \n**忌神：火（官杀）、木（财）、水（食伤）** \n**原理**：金弱需扶。需靠学习、长辈（土印）增强底蕴，或依靠团队伙伴（金比劫）互相支撑。避免承担过重压力（火）或为物质奔波（木），避免过度消耗（水）。'
                }
            },
            '辛': {
                '身强': {
                    '喜神': '水（食伤）、火（官杀）',
                    '用神': '水（食伤）、火（官杀）',
                    '忌神': '土（印）、金（比劫）',
                    '成长建议': '**喜用神：水（食伤）、火（官杀）** \n**忌神：土（印）、金（比劫）** \n**原理**：辛金过旺则易滞涩。宜以水（食伤）淘洗，将细腻转化为才华输出，开阔心胸；或以火（官杀）锻炼，接受规则与挑战，提升格局。忌再添土金，否则易固步自封、计较琐碎。'
                },
                '身弱': {
                    '喜神': '土（印）、金（比劫）',
                    '用神': '土（印）、金（比劫）',
                    '忌神': '火（官杀）、木（财）、水（食伤）',
                    '成长建议': '**喜用神：土（印）、金（比劫）** \n**忌神：火（官杀）、木（财）、水（食伤）** \n**原理**：弱金最需生扶。需靠学习、精神修养（土印）稳固内心，或依靠团队伙伴（金比劫）获得支持。避免高压环境（火）或过度追求物质（木），避免过度输出才华（水）导致透支。'
                }
            }
        }

    def get_xiyongshen(self, day_gan: str, qiangruo: str) -> Dict:
        """
        获取喜用神（衰旺论）信息

        参数:
            day_gan: 日主天干
            qiangruo: 强弱判定结果（偏强、强、从强、偏弱、弱、从弱、均衡）

        返回:
            喜用神信息字典
        """
        if not day_gan or day_gan not in self.XIYONGSHEN_DATA:
            return {'error': '无效日主天干'}

        # 将强弱判定映射为身强/身弱
        # 身强对应：偏强、强、从强
        # 身弱对应：偏弱、弱、从弱
        # 均衡格统一按照身弱来分析
        if qiangruo in ['偏强', '强', '从强']:
            strength_type = '身强'
        elif qiangruo in ['偏弱', '弱', '从弱', '均衡']:
            # 均衡格统一按照身弱来分析
            strength_type = '身弱'
        else:
            # 对于其他情况，默认按照身弱处理
            strength_type = '身弱'

        xys_data = self.XIYONGSHEN_DATA[day_gan][strength_type]

        return {
            '日主': day_gan,
            '强弱判定': qiangruo,
            '身强身弱分类': strength_type,
            '喜神': xys_data['喜神'],
            '用神': xys_data['用神'],
            '忌神': xys_data['忌神'],
            '成长建议': xys_data['成长建议']
        }
    
    def _init_geju_data(self):
        """初始化所有格局数据"""
        
        # ============ 正格（八格） ============
        
        # 正官格
        self._add_geju(
            name='正官格',
            category='正格',
            definition='以月令本气或透干的正官（克日主且阴阳异）为用神的格局',
            preference='喜：身强（任官）、财生官（官有源）、印护官（制伤官）；忌：身弱（官克身）、伤官见官（伤克官）、七杀混官（官杀杂）、刑冲（官星损）',
            condition='1.月令本气为正官（如日主甲木，月令酉金<辛金正官>）；2.月令藏干透出正官（如日主甲木，月令丑土<藏辛金正官>透辛金）',
            explanation='主文职贵气、仕途顺遂。《渊海子平·论正官》："正官者，六格之尊……喜身旺、财旺、印旺，忌身弱、伤官、七杀、刑冲。"',
            source='《渊海子平·论正官》'
        )
        
        # 七杀格（偏官格）
        self._add_geju(
            name='七杀格',
            category='正格',
            definition='以月令本气或透干的七杀（克日主且阴阳同）为用神的格局',
            preference='喜：身强（任杀）、食制杀（食神克杀）、印化杀（印星泄杀生身）；忌：身弱（杀攻身）、财党杀（财生杀）、官杀混（官杀杂）',
            condition='1.月令本气为七杀（如日主甲木，月令申金<庚金七杀>）；2.月令藏干透出七杀（如日主甲木，月令戌土<藏戊土七杀>透戊土）',
            explanation='主武职、权威，需制化方贵。《渊海子平·论偏官》："偏官者，杀也……喜身旺、食制、印化，忌身弱、财党、官混。"',
            source='《渊海子平·论偏官》'
        )
        
        # 正财格
        self._add_geju(
            name='正财格',
            category='正格',
            definition='以月令本气或透干的正财（日主克且阴阳异）为用神的格局',
            preference='喜：身强（任财）、食生财（食神生财）、官护财（官星制比劫）；忌：身弱（财耗身）、比劫夺财（比劫克财）、七杀泄财（七杀耗财）',
            condition='1.月令本气为正财（如日主甲木，月令未土<己土正财>）；2.月令藏干透出正财（如日主甲木，月令未土<藏己土正财>透己土）',
            explanation='主稳定财富、实业兴家。《渊海子平·论正财》："正财者，养命之源……喜身旺、食神、官星，忌身弱、比劫、七杀。"',
            source='《渊海子平·论正财》'
        )
        
        # 偏财格
        self._add_geju(
            name='偏财格',
            category='正格',
            definition='以月令本气或透干的偏财（日主克且阴阳同）为用神的格局',
            preference='喜：身强（任财）、食/伤生财（食伤生财）；忌：身弱（财耗身）、比劫夺财（比劫克财）、正官制财（正官克偏财）',
            condition='1.月令本气为偏财（如日主甲木，月令戌土<戊土偏财>）；2.月令藏干透出偏财（如日主甲木，月令辰土<藏戊土偏财>透戊土）',
            explanation='主横财、商业成功。《渊海子平·论偏财》："偏财者，众人之财……喜身旺、食伤生财，忌身弱、比劫夺财。"',
            source='《渊海子平·论偏财》'
        )
        
        # 正印格（印绶格）
        self._add_geju(
            name='正印格',
            category='正格',
            definition='以月令本气或透干的正印（生日主且阴阳异）为用神的格局',
            preference='喜：身弱（印生身）、官杀生印（官杀生印）；忌：身强（印泄身）、财坏印（财克印）、食伤克印（食伤克印）',
            condition='1.月令本气为正印（如日主甲木，月令子水<癸水正印>）；2.月令藏干透出正印（如日主乙木，月令亥水<藏壬水正印>透壬水）',
            explanation='主学业、贵人扶持、福寿。《渊海子平·论印绶》："印绶者，生身之母……喜官杀生印、身弱用印，忌财星坏印、身强印旺。"',
            source='《渊海子平·论印绶》'
        )
        
        # 偏印格（枭神格）
        self._add_geju(
            name='偏印格',
            category='正格',
            definition='以月令本气或透干的偏印（生日主且阴阳同）为用神的格局',
            preference='喜：身弱（枭生身）、食制枭（食神克枭）；忌：身强（枭泄身）、财坏枭（财克枭）、七杀混枭（七杀杂枭）',
            condition='1.月令本气为偏印（如日主甲木，月令亥水<壬水偏印>）；2.月令藏干透出偏印（如日主丙火，月令寅木<藏甲木偏印>透甲木）',
            explanation='主特殊技艺（如玄学、艺术），易孤独。《渊海子平·论偏印》："偏印者，枭神也……喜身弱、食神制，忌身强、财星坏。"',
            source='《渊海子平·论偏印》'
        )
        
        # 食神格
        self._add_geju(
            name='食神格',
            category='正格',
            definition='以月令本气或透干的食神（日主生且阴阳异）为用神的格局',
            preference='喜：身强（食泄秀）、财引化（食生财）；忌：身弱（食泄身）、枭夺食（偏印克食）、七杀混食（七杀杂食）',
            condition='1.月令本气为食神（如日主甲木，月令巳火<丙火食神>）；2.月令藏干透出食神（如日主甲木，月令巳火<藏丙火食神>透丙火）',
            explanation='主文才、福气、享乐。《渊海子平·论食神》："食神者，寿星也……喜身旺、财星，忌身弱、枭神。"',
            source='《渊海子平·论食神》'
        )
        
        # 伤官格
        self._add_geju(
            name='伤官格',
            category='正格',
            definition='以月令本气或透干的伤官（日主生且阴阳同）为用神的格局',
            preference='喜：身强（伤泄秀）、财引化（伤生财）、印制化（印星克伤）；忌：身弱（伤泄身）、官见伤（正官克伤）、比劫助伤（比劫生伤）',
            condition='1.月令本气为伤官（如日主甲木，月令午火<丁火伤官>）；2.月令藏干透出伤官（如日主甲木，月令未土<藏丁火伤官>透丁火）',
            explanation='主才华横溢、创新，需财印引化方贵。《渊海子平·论伤官》："伤官者，盗气也……喜身旺、财印，忌身弱、官星。"',
            source='《渊海子平·论伤官》'
        )
        
        # ============ 专旺格 ============

        # 曲直格（木专旺格）
        self._add_geju(
            name='曲直格',
            category='专旺格',
            definition='日主为甲/乙木，全局木气独旺，成木势专旺之象',
            preference='喜：水（生木）、木（帮身）；忌：金（克木）、土（耗木）、火（泄木过重）',
            condition='1.日主甲/乙木透干；2.地支寅卯辰会木局或亥卯未合木局；3.无庚辛申酉金冲克破局（或有少量金被木转化）；4.水木相生助旺（可带少量火通关）',
            explanation='木主仁，性格仁慈宽厚，若成格纯粹，富贵长寿；忌金破局则凶。',
            source='《渊海子平·论曲直格》'
        )

        # 炎上格（火专旺格）
        self._add_geju(
            name='炎上格',
            category='专旺格',
            definition='日主为丙/丁火，全局火势独旺，成火德光明之象',
            preference='喜：木（生火）、火（帮身）；忌：水（克火）、金（耗火）、土（晦火过重）',
            condition='1.日主丙/丁火透干；2.地支巳午未会火局或寅午戌合火局；3.无壬癸亥子水冲克破局（或有少量水被火转化）；4.木火相生助旺（可带少量土泄秀）',
            explanation='火主礼，性格热情积极，成格者易有显贵，忌水破局则多灾。',
            source='《渊海子平·论炎上格》'
        )

        # 稼穑格（土专旺格）
        self._add_geju(
            name='稼穑格',
            category='专旺格',
            definition='日主为戊/己土，全局土气独旺，成土德厚重之象',
            preference='喜：火（生土）、土（帮身）；忌：木（克土）、水（耗土）、金（泄土过重）',
            condition='1.日主戊/己土透干；2.地支辰戌丑未四库全（或三会土局）；3.无甲乙寅卯木冲克破局（或有少量木被土转化）；4.火土相生助旺（可带少量金泄秀）',
            explanation='土主信，性格稳重务实，成格者多富，忌木破局则破败。',
            source='《渊海子平·论稼穑格》'
        )

        # 从革格（金专旺格）
        self._add_geju(
            name='从革格',
            category='专旺格',
            definition='日主为庚/辛金，全局金气独旺，成金性刚健之象',
            preference='喜：土（生金）、金（帮身）；忌：火（克金）、木（耗金）、水（泄金过重）',
            condition='1.日主庚/辛金透干；2.地支申酉戌会金局或巳酉丑合金局；3.无丙丁巳午火冲克破局（或有少量火被金转化）；4.土金相生助旺（可带少量水泄秀）',
            explanation='金主义，性格刚毅果断，成格者多武贵，忌火破局则多争斗。',
            source='《渊海子平·论从革格》'
        )

        # 润下格（水专旺格）
        self._add_geju(
            name='润下格',
            category='专旺格',
            definition='日主为壬/癸水，全局水气独旺，成水德流动之象',
            preference='喜：金（生水）、水（帮身）；忌：土（克水）、火（耗水）、木（泄水过重）',
            condition='1.日主壬/癸水透干；2.地支亥子丑会水局或申子辰合水局；3.无戊己辰戌土冲克破局（或有少量土被水转化）；4.金水相生助旺（可带少量木泄秀）',
            explanation='水主智，性格灵活善变，成格者多智谋，忌土破局则多困顿。',
            source='《渊海子平·论润下格》'
        )

        # ============ 从格 ============

        # 从儿格（食伤生财格）
        self._add_geju(
            name='从儿格',
            category='从格',
            definition='日主极弱，食神/伤官（儿）旺而透干，食伤生财星',
            preference='喜：食伤（儿）、财星（儿所生）、官杀（财生官）；忌：印星（克食伤）、比劫（生扶日主）',
            condition='1.日主弱（无根或根微）；2.食神/伤官透干且旺；3.食伤生财星，财星有根；4.无印星克制食伤，无比劫生扶日主',
            explanation='从儿格以"儿"为中心，重才华与财运；若食伤过旺无财，反成"伤官见官"之患。',
            source='《渊海子平·论从儿格》'
        )

        # 从财格
        self._add_geju(
            name='从财格',
            category='从格',
            definition='日主极弱，财星（正财/偏财）旺而透干，日主从财星之势',
            preference='喜：财星、食伤（生财）、官杀（护财）；忌：印星（生身抗财）、比劫（夺财）',
            condition='1.日主弱（无根或根微）；2.财星透干且旺（地支有根或会局）；3.无印星生扶日主，无比劫克财（或比劫被化）；4.可带食伤生财（增强财势）',
            explanation='从财格以"财"为核心，重财富积累；若财星无源（无食伤生），或官杀克身，则难成。',
            source='《渊海子平·论从财格》'
        )

        # 从杀格
        self._add_geju(
            name='从杀格',
            category='从格',
            definition='日主极弱，七杀（偏官）旺而透干，日主从七杀之势',
            preference='喜：七杀、财星（生杀）、食伤（制杀）；忌：印星（生身抗杀）、比劫（助身抗杀）',
            condition='1.日主弱（无根或根微）；2.七杀透干且旺（地支有根或会局）；3.无印星生扶日主，无比劫抗杀（或比劫被化）；4.可带食伤制杀（需制伏得宜）或财星生杀（增强杀势）',
            explanation='从杀格以"杀"为用，重权威与地位；若杀星无制（无食伤/财星），或印比出现，则易招灾。',
            source='《渊海子平·论从杀格》'
        )

        # 从强格
        self._add_geju(
            name='从强格',
            category='从格',
            definition='日主极旺（得令、得地、得势），无克泄耗之力，日主从自身强旺之势',
            preference='喜：印星（生身）、比劫（帮身）；忌：官杀（克）、财星（耗）、食伤（泄）',
            condition='1.日主强（如甲木生于春，地支寅卯辰，天干透甲乙）；2.无官杀（克）、财星（耗）、食伤（泄）克制日主；3.印星旺而生扶日主（或比劫帮身）',
            explanation='从强格强调日主绝对强势，性格固执坚韧；忌逆势五行破坏平衡（如见官杀易冲突）。',
            source='《渊海子平·论从强格》'
        )

        # 从弱格
        self._add_geju(
            name='从弱格',
            category='从格',
            definition='日主极弱（失令、失地、失势），无生扶之力，只能顺从克泄耗之势',
            preference='喜：官杀（克）、财星（耗）、食伤（泄）；忌：印星（生身）、比劫（帮身）',
            condition='1.日主弱（如无根或根被冲克）；2.全局官杀、财星、食伤旺而主导；3.无印星生扶日主，无比劫帮身；4.细分可为从财、从杀、从儿等子类',
            explanation='从弱格是"弱者从势"，需完全顺从旺势；成格者需结合自身从属五行判断运势（如从财重财运，从杀重权力）；若日主稍有根气（假从），则格局层次降低。',
            source='《渊海子平·论从弱格》'
        )

    def get_zhuangwangge(self) -> Dict[str, GeJuInfo]:
        """获取所有专旺格"""
        return {k: v for k, v in self._geju_dict.items() if v.category == '专旺格'}

    def get_congge(self) -> Dict[str, GeJuInfo]:
        """获取所有从格"""
        return {k: v for k, v in self._geju_dict.items() if v.category == '从格'}

    
    def _add_geju(self, name: str, category: str, definition: str, 
                  preference: str, condition: str, explanation: str, source: str):
        """添加格局到数据库"""
        info = GeJuInfo(name, category, definition, preference, condition, explanation, source)
        self._geju_dict[name] = info
    
    def get_geju_info(self, name: str) -> Optional[GeJuInfo]:
        """获取指定格局的详细信息"""
        return self._geju_dict.get(name)
    
    def get_geju_dict(self, name: str) -> Optional[Dict]:
        """
        获取指定格局的字典格式信息
        与 bazi_geju_refactored_v5.py 中的字段命名保持一致
        """
        info = self._geju_dict.get(name)
        if not info:
            return None
        
        # 映射字段名以与 bazi_geju_refactored_v5.py 保持一致
        return {
            '格局名称': info.name,
            '概念描述': info.definition,
            '判断标准': info.condition,
            '成格条件': info.condition,
            '不成格例子': '',  # 原数据库无此字段，留空
            '心理特质': '',  # 原数据库无此字段，留空
            '行为模式': '',  # 原数据库无此字段，留空
            '成长建议': info.preference,
            # 原始字段也保留
            'name': info.name,
            'category': info.category,
            'definition': info.definition,
            'preference': info.preference,
            'condition': info.condition,
            'explanation': info.explanation,
            'source': info.source
        }
    
    def get_all_geju(self) -> Dict[str, GeJuInfo]:
        """获取所有格局信息"""
        return self._geju_dict.copy()
    
    def get_zhengge(self) -> Dict[str, GeJuInfo]:
        """获取所有正格"""
        return {k: v for k, v in self._geju_dict.items() if v.category == '正格'}


class TouGanTongGenAnalyzer:
    """
    透干通根分析器
    
    功能：
    1. 分析四柱天干的通根情况
    2. 分析四地支藏干的透干情况
    3. 按照力量大小和阴阳属性分类
    4. 计算强弱等级（地支位置、藏干位置、通根/借根）
    """
    
    def __init__(self, db: GeJuDatabase = None):
        """初始化分析器"""
        self.db = db if db is not None else GeJuDatabase()
    
    def analyze_tougan_tonggen(self, bazi: Dict[str, str]) -> Dict:
        """
        分析透干与通根情况
        
        参数:
            bazi: 八字字典 {'year_gan': '甲', 'year_zhi': '子', ...}
        
        返回:
            包含透干通根分析结果的字典
        """
        result = {
            '天干通根分析': {},
            '地支透干分析': {},
            '综合评述': ''
        }
        
        # 提取八字信息
        gans = [
            bazi.get('year_gan', ''),
            bazi.get('month_gan', ''),
            bazi.get('day_gan', ''),
            bazi.get('time_gan', '')
        ]
        zhis = [
            bazi.get('year_zhi', ''),
            bazi.get('month_zhi', ''),
            bazi.get('day_zhi', ''),
            bazi.get('time_zhi', '')
        ]
        pillar_names = ['年柱', '月柱', '日柱', '时柱']
        
        # 一、分析天干通根情况
        result['天干通根分析'] = self._analyze_gans_tonggen(gans, zhis, pillar_names)
        
        # 二、分析地支透干情况
        result['地支透干分析'] = self._analyze_zhis_tougan(gans, zhis, pillar_names)
        
        # 三、生成综合评述
        result['综合评述'] = self._generate_summary(result['天干通根分析'], result['地支透干分析'])

        return result

    def analyze_tougan_tonggen_with_dayun_liunian(self, bazi: Dict[str, str],
                                                  dayun_gan: str, dayun_zhi: str,
                                                  liunian_gan: str, liunian_zhi: str) -> Dict:
        """
        分析透干与通根情况（含大运流年）

        说明：
        - 将大运、流年视为额外的柱，参与透干通根分析
        - 大运视为月柱2（仅次于月令）
        - 流年视为年柱2（仅次于年柱）
        - 分析逻辑与原局完全一致

        参数:
            bazi: 八字字典 {'year_gan': '甲', 'year_zhi': '子', ...}
            dayun_gan: 大运天干
            dayun_zhi: 大运地支
            liunian_gan: 流年天干
            liunian_zhi: 流年地支

        返回:
            包含透干通根分析结果的字典
        """
        result = {
            '天干通根分析': {},
            '地支透干分析': {},
            '综合评述': ''
        }

        # 提取八字信息
        gans = [
            bazi.get('year_gan', ''),
            bazi.get('month_gan', ''),
            bazi.get('day_gan', ''),
            bazi.get('time_gan', ''),
            dayun_gan,   # 大运天干（视为月柱2）
            liunian_gan  # 流年天干（视为年柱2）
        ]
        zhis = [
            bazi.get('year_zhi', ''),
            bazi.get('month_zhi', ''),
            bazi.get('day_zhi', ''),
            bazi.get('time_zhi', ''),
            dayun_zhi,   # 大运地支
            liunian_zhi  # 流年地支
        ]
        pillar_names = ['年柱', '月柱', '日柱', '时柱', '月柱2(大运)', '年柱2(流年)']

        # 一、分析天干通根情况
        result['天干通根分析'] = self._analyze_gans_tonggen_with_dayun_liunian(gans, zhis, pillar_names)

        # 二、分析地支透干情况
        result['地支透干分析'] = self._analyze_zhis_tougan_with_dayun_liunian(gans, zhis, pillar_names)

        # 三、生成综合评述
        result['综合评述'] = self._generate_summary(result['天干通根分析'], result['地支透干分析'])

        return result

    def _analyze_gans_tonggen_with_dayun_liunian(self, gans: List[str], zhis: List[str],
                                                   pillar_names: List[str]) -> Dict:
        """
        分析天干通根情况（含大运流年）

        逻辑：
        - 大运（月柱2）权重仅次于月令
        - 流年（年柱2）权重仅次于年柱
        - 其他逻辑与原局一致
        """
        result = {}

        # 地支位置权重：月令(5) > 月柱2(4) > 日支(3) > 年支(2) > 年柱2(1) > 时支(0)
        position_weights = {
            '月柱': 5, '月柱2(大运)': 4, '日柱': 3,
            '年柱': 2, '年柱2(流年)': 1, '时柱': 0
        }

        for i, gan in enumerate(gans):
            if not gan:
                continue

            pillar_name = pillar_names[i]
            gan_wuxing = self.db.GAN_WUXING.get(gan, '')
            gan_yinyang = self.db.GAN_YINYANG.get(gan, '')

            result[pillar_name] = {
                '天干': gan,
                '天干五行': gan_wuxing,
                '阴阳': gan_yinyang,
                '通根情况': [],
                '详细分析': []
            }

            # 检查所有地支中的通根
            for j, (check_zhi, check_pillar) in enumerate(zip(zhis, pillar_names)):
                if not check_zhi:
                    continue

                tonggen_info = self._check_single_tonggen(
                    gan, gan_wuxing, gan_yinyang,
                    check_zhi, check_pillar
                )

                if tonggen_info:
                    result[pillar_name]['通根情况'].append(tonggen_info)
                    result[pillar_name]['详细分析'].append(tonggen_info['详细说明'])

        return result

    def _analyze_zhis_tougan_with_dayun_liunian(self, gans: List[str], zhis: List[str],
                                                   pillar_names: List[str]) -> Dict:
        """
        分析地支透干情况（含大运流年）

        遍历逻辑：
        1. 遍历年月日时及大运流年的六个地支
        2. 对每个地支，取出其所有藏干（本气、中气、余气）
        3. 将这些藏干与所有天干（包括大运流年）进行比较
        4. 如果某藏干在天干中找到完全相同的字，即为透干
        """
        result = {}

        # 获取所有天干的集合（用于检查透出，包括大运流年）
        all_gans_with_pillar = [(g, p) for g, p in zip(gans, pillar_names) if g]

        # 遍历每个地支
        for i, zhi in enumerate(zhis):
            if not zhi:
                continue

            pillar_name = pillar_names[i]
            gan = gans[i]  # 对应的天干（用于判断通根透）

            result[pillar_name] = {
                '地支': zhi,
                '地支五行': self.db.ZHI_WUXING.get(zhi, ''),
                '天干': gan if gan else '',
                '天干五行': self.db.GAN_WUXING.get(gan, '') if gan else '',
                '藏干透出': [],
                '通根透': []
            }

            # 获取地支藏干
            cangan_list = self.db.ZHI_CANGAN.get(zhi, [])

            # 检查每个藏干是否在天干中透出（必须同字，可以不同柱）
            for cangan, cangan_weight in cangan_list:
                cangan_wuxing = self.db.GAN_WUXING.get(cangan, '')
                cangan_yinyang = self.db.GAN_YINYANG.get(cangan, '')

                # 检查是否在任何一个天干中透出（必须完全同字，包括大运流年）
                toupillars = []
                for check_gan, check_pillar in all_gans_with_pillar:
                    if check_gan == cangan:  # 必须同字
                        toupillars.append(check_pillar)

                # 去重透出柱名
                toupillars = list(set(toupillars))

                if toupillars:
                    # 判断是否为通根透（干支一柱内，且同字）
                    is_tougentou = (gan == cangan)

                    # 获取藏干位置类型
                    position_idx = cangan_list.index((cangan, cangan_weight))
                    position_type = ['本气', '中气', '余气'][min(position_idx, 2)]

                    tou_info = {
                        '藏干': cangan,
                        '藏干五行': cangan_wuxing,
                        '阴阳': cangan_yinyang,
                        '藏干位置': position_type,
                        '透出柱名': sorted(toupillars),
                        '透出方式': '通根透' if is_tougentou else '透干',
                        '是否同字透出': True
                    }
                    result[pillar_name]['藏干透出'].append(tou_info)

                    # 分类：通根透 或 其他透出
                    if is_tougentou:
                        result[pillar_name]['通根透'].append(cangan)

        return result

    def _analyze_gans_tonggen(self, gans: List[str], zhis: List[str],
                             pillar_names: List[str]) -> Dict:
        """
        分析天干通根情况
        
        分析每个天干在地支中的通根情况：
        1. 按阴阳属性分：通根（阴阳同）、借根（阴阳异）
        2. 按藏干位置分：本气根、中气根、余气根
        3. 按力量大小分：本气通根（力量大）、生扶通根（力量中）、余气通根（力量弱）
        """
        result = {}
        
        # 地支位置权重：月令(4) > 日支(3) > 年支(2) > 时支(1)
        position_weights = {'月柱': 4, '日柱': 3, '年柱': 2, '时柱': 1}
        
        for i, gan in enumerate(gans):
            if not gan:
                continue
                
            pillar_name = pillar_names[i]
            gan_wuxing = self.db.GAN_WUXING.get(gan, '')
            gan_yinyang = self.db.GAN_YINYANG.get(gan, '')
            
            result[pillar_name] = {
                '天干': gan,
                '天干五行': gan_wuxing,
                '阴阳': gan_yinyang,
                '通根情况': [],
                '详细分析': []
            }
            
            # 检查所有地支中的通根
            for j, (check_zhi, check_pillar) in enumerate(zip(zhis, pillar_names)):
                if not check_zhi:
                    continue
                
                tonggen_info = self._check_single_tonggen(
                    gan, gan_wuxing, gan_yinyang,
                    check_zhi, check_pillar
                )

                if tonggen_info:
                    result[pillar_name]['通根情况'].append(tonggen_info)
                    result[pillar_name]['详细分析'].append(tonggen_info['详细说明'])
        
        return result
    
    def _check_single_tonggen(self, gan: str, gan_wuxing: str, gan_yinyang: str,
                            zhi: str, zhi_name: str) -> Optional[Dict]:
        """
        检查单个天干在单个地支中的通根情况
        
        参数:
            gan: 天干
            gan_wuxing: 天干五行
            gan_yinyang: 天干阴阳
            zhi: 地支
            zhi_name: 地支所属柱名（如'月柱'）

        返回:
            通根信息字典或None
        """
        zhi_wuxing = self.db.ZHI_WUXING.get(zhi, '')
        zhi_yinyang = self.db.ZHI_YINYANG.get(zhi, '')
        
        # 检查地支藏干
        cangan_list = self.db.ZHI_CANGAN.get(zhi, [])
        
        for idx, (cangan, cangan_weight) in enumerate(cangan_list):
            cangan_wuxing = self.db.GAN_WUXING.get(cangan, '')
            
            # 一、检查是否通根（五行相同）
            if cangan_wuxing == gan_wuxing:
                cangan_yinyang = self.db.GAN_YINYANG.get(cangan, '')
                
                # 判断通根类型
                is_same_yinyang = (cangan_yinyang == gan_yinyang)
                root_type = '通根' if is_same_yinyang else '借根'
                
                # 判断藏干位置类型
                position_types = ['本气', '中气', '余气']
                position_type = position_types[idx] if idx < 3 else '余气'

                # 阴阳属性描述
                yinyang_desc = f'({cangan_yinyang}{position_type}根)'

                # 生成详细说明
                detail_desc = (
                    f'{zhi_name}({zhi}){yinyang_desc}：'
                    f'{gan}{gan_wuxing}见{zhi}({cangan_wuxing})，{root_type}'
                )

                return {
                    '地支': zhi,
                    '地支五行': zhi_wuxing,
                    '藏干': cangan,
                    '藏干五行': cangan_wuxing,
                    '藏干位置': position_type,
                    '通根类型': root_type,
                    '阴阳是否相同': is_same_yinyang,
                    '详细说明': detail_desc
                }
        
        return None
    
    def _analyze_zhis_tougan(self, gans: List[str], zhis: List[str],
                             pillar_names: List[str]) -> Dict:
        """
        分析地支透干情况（遍历地支）

        遍历逻辑：
        1. 遍历年月日时四个地支
        2. 对每个地支，取出其所有藏干（本气、中气、余气）
        3. 将这些藏干与所有天干（年月日时）进行比较
        4. 如果某藏干在天干中找到完全相同的字，即为透干

        举例：
        - 地支申金藏庚壬戊，天干也见庚金、壬水、戊土即透干（必须同字）
        - 若地支申金，见天干辛金、癸水、戊土不算透干（辛不是庚，癸不是壬）
        - 干支一柱内的透出称为"通根透"
        """
        result = {}

        # 获取所有天干的集合（用于检查透出）
        all_gans_with_pillar = [(g, p) for g, p in zip(gans, pillar_names) if g]

        # 遍历每个地支
        for i, zhi in enumerate(zhis):
            if not zhi:
                continue

            pillar_name = pillar_names[i]
            gan = gans[i]  # 对应的天干（用于判断通根透）

            result[pillar_name] = {
                '地支': zhi,
                '地支五行': self.db.ZHI_WUXING.get(zhi, ''),
                '天干': gan if gan else '',
                '天干五行': self.db.GAN_WUXING.get(gan, '') if gan else '',
                '藏干透出': [],
                '通根透': []
            }

            # 获取地支藏干
            cangan_list = self.db.ZHI_CANGAN.get(zhi, [])
            
            # 检查每个藏干是否在天干中透出（必须同字，可以不同柱）
            for cangan, cangan_weight in cangan_list:
                cangan_wuxing = self.db.GAN_WUXING.get(cangan, '')
                cangan_yinyang = self.db.GAN_YINYANG.get(cangan, '')
                
                # 检查是否在任何一个天干中透出（必须完全同字）
                toupillars = []
                for check_gan, check_pillar in all_gans_with_pillar:
                    if check_gan == cangan:  # 必须同字
                        toupillars.append(check_pillar)
                
                # 去重透出柱名
                toupillars = list(set(toupillars))
                
                if toupillars:
                    # 判断是否为通根透（干支一柱内，且同字）
                    is_tougentou = (gan == cangan)
                    
                    # 获取藏干位置类型
                    position_idx = cangan_list.index((cangan, cangan_weight))
                    position_type = ['本气', '中气', '余气'][min(position_idx, 2)]
                    
                    tou_info = {
                        '藏干': cangan,
                        '藏干五行': cangan_wuxing,
                        '阴阳': cangan_yinyang,
                        '藏干位置': position_type,
                        '透出柱名': sorted(toupillars),
                        '透出方式': '通根透' if is_tougentou else '透干',
                        '是否同字透出': True
                    }
                    result[pillar_name]['藏干透出'].append(tou_info)
                    
                    # 分类：通根透 或 其他透出
                    if is_tougentou:
                        result[pillar_name]['通根透'].append(cangan)
        
        return result
    
    def _generate_summary(self, tonggen_result: Dict, tougan_result: Dict) -> str:
        """
        生成综合评述
        
        参数:
            tonggen_result: 天干通根分析结果
            tougan_result: 地支透干分析结果
        
        返回:
            综合评述字符串
        """
        summary_parts = []

        # 统计通根情况
        tonggen_count = 0
        jiegen_count = 0

        for pillar, info in tonggen_result.items():
            if info.get('通根情况'):
                for root in info.get('通根情况', []):
                    if root.get('通根类型') == '通根':
                        tonggen_count += 1
                    else:
                        jiegen_count += 1

        # 统计透出情况
        total_tougan = 0  # 同字透出
        total_tougentou = 0  # 通根透（干支一柱内）

        for info in tougan_result.values():
            for tou in info.get('藏干透出', []):
                if tou.get('是否同字透出'):
                    total_tougan += 1

        total_tougentou = sum(len(info.get('通根透', [])) for info in tougan_result.values())

        # 生成评述
        summary_parts.append(f"【通根情况】共发现{tonggen_count + jiegen_count}处通根，其中通根{tonggen_count}处，借根{jiegen_count}处")
        summary_parts.append(f"【透出情况】共发现{total_tougan}处同字透出，其中通根透{total_tougentou}处")

        if total_tougan >= 4:
            summary_parts.append("【透出分析】藏干同字透出较多，格局较为清透")
        elif total_tougan >= 2:
            summary_parts.append("【透出分析】藏干同字透出适中，格局较为平和")
        else:
            summary_parts.append("【透出分析】藏干同字透出较少，格局较为潜藏")
        
        return '。'.join(summary_parts)
    
    def print_analysis(self, result: Dict):
        """
        打印透干通根分析结果（简化版）
        """
        print("\n" + "=" * 80)
        print("【透干通根分析】")
        print("=" * 80)

        # 打印天干通根分析
        print("\n【一、天干通根分析】")

        for pillar, info in result['天干通根分析'].items():
            print(f"【{pillar}】{info['天干']}({info['天干五行']}) - 阴阳: {info['阴阳']}")

            if info['通根情况']:
                root_list = ', '.join([root['详细说明'] for root in info['通根情况']])
                print(f"  通根情况: {root_list}")
            else:
                print(f"  通根情况: 无通根")
            print()

        # 打印地支透干分析
        print("\n【二、地支透干分析】")

        for pillar, info in result['地支透干分析'].items():
            print(f"【{pillar}】{info['天干']}{info['地支']}")

            if info['藏干透出']:
                tou_list = []
                for tou in info['藏干透出']:
                    pillars_str = ', '.join(tou['透出柱名'])
                    tou_list.append(f"{tou['藏干']}({tou['藏干五行']})→{pillars_str}")
                print(f"  藏干透出: {', '.join(tou_list)}")
            else:
                print(f"  藏干情况: 无藏干透出")
            print()

        # 打印综合评述
        print("\n【三、综合评述】")
        print(result['综合评述'])
        print("=" * 80)

    def print_analysis_with_dayun_liunian(self, result: Dict,
                                         dayun_gan: str, dayun_zhi: str,
                                         liunian_gan: str, liunian_zhi: str):
        """
        打印透干通根分析结果（含大运流年）

        参数:
            result: 分析结果字典
            dayun_gan: 大运天干
            dayun_zhi: 大运地支
            liunian_gan: 流年天干
            liunian_zhi: 流年地支
        """
        print("\n" + "=" * 80)
        print(f"【透干通根分析（含大运：{dayun_gan}{dayun_zhi} / 流年：{liunian_gan}{liunian_zhi}）】")
        print("=" * 80)
        print("\n说明：")
        print("  - 大运被视为月柱2（仅次于月令）")
        print("  - 流年被视为年柱2（仅次于年支）")
        print("  - 透干、通根判定逻辑与原局完全一致")
        print()

        # 打印天干通根分析
        print("\n【一、天干通根分析】")

        for pillar, info in result['天干通根分析'].items():
            print(f"【{pillar}】{info['天干']}({info['天干五行']}) - 阴阳: {info['阴阳']}")

            if info['通根情况']:
                root_list = ', '.join([root['详细说明'] for root in info['通根情况']])
                print(f"  通根情况: {root_list}")
            else:
                print(f"  通根情况: 无通根")
            print()

        # 打印地支透干分析
        print("\n【二、地支透干分析】")

        for pillar, info in result['地支透干分析'].items():
            print(f"【{pillar}】{info['天干']}{info['地支']}")

            if info['藏干透出']:
                tou_list = []
                for tou in info['藏干透出']:
                    pillars_str = ', '.join(tou['透出柱名'])
                    tou_list.append(f"{tou['藏干']}({tou['藏干五行']})→{pillars_str}")
                print(f"  藏干透出: {', '.join(tou_list)}")
            else:
                print(f"  藏干情况: 无藏干透出")
            print()

        # 打印综合评述
        print("\n【三、综合评述】")
        print(result['综合评述'])
        print("=" * 80)


class ShenQiangCalculator:
    """
    身强身弱计算器
    基于新算法计算日主强弱
    """
    
    def __init__(self, db: GeJuDatabase = None):
        """初始化计算器"""
        self.db = db if db is not None else GeJuDatabase()
    
    def calculate(self, bazi: Dict[str, str]) -> Dict:
        """
        计算日主强弱
        支持无时柱的情况（仅提供年月日三柱）

        参数:
            bazi: 八字字典

        返回:
            包含强弱分析结果的字典
        """
        # 提取八字信息
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        year_gan = bazi.get('year_gan', '')
        month_gan = bazi.get('month_gan', '')
        time_gan = bazi.get('time_gan', '')
        day_zhi = bazi.get('day_zhi', '')
        year_zhi = bazi.get('year_zhi', '')
        time_zhi = bazi.get('time_zhi', '')
        
        # 检查时柱是否有效（支持无时柱分析）
        has_time_pillar = time_gan and time_zhi and time_gan.strip() and time_zhi.strip()

        # 获取日主五行
        ri_wuxing = self.db.GAN_WUXING.get(day_gan, '')
        if not ri_wuxing:
            return {'error': '日主无效'}

        result = {
            '日主': day_gan,
            '日主五行': ri_wuxing,
            '得令': False,
            '得令详情': '',
            '得地': False,
            '得地详情': '',
            '得势': False,
            '得势详情': '',
            '强弱判定': '',
            '格局类型': '',
            '特殊格局': None,
            '详细说明': []
        }

        # 第一步：判断得令（月令强弱）
        deling_info = self._judge_deling(ri_wuxing, month_zhi)
        result['得令'] = deling_info['得令']
        result['得令详情'] = deling_info['详情']
        result['详细说明'].append(f"【第一步】得令判断：{deling_info['详情']}")

        # 第二步：判断得地（地支有根）- 传入时柱（可能为空）
        dedi_info = self._judge_dedi(ri_wuxing, day_zhi, year_zhi, month_zhi, time_zhi if has_time_pillar else '')
        result['得地'] = dedi_info['得地']
        result['得地详情'] = dedi_info['详情']
        result['详细说明'].append(f"【第二步】得地判断：{dedi_info['详情']}")

        # 第三步：判断得势（天干生扶）- 传入时干（可能为空）
        deshi_info = self._judge_deshi(ri_wuxing, year_gan, month_gan, time_gan if has_time_pillar else '')
        result['得势'] = deshi_info['得势']
        result['得势详情'] = deshi_info['详情']
        result['详细说明'].append(f"【第三步】得势判断：{deshi_info['详情']}")

        # 第四步：综合判定强弱（细致分类）
        result['强弱判定'] = self._judge_shenqiang_detailed(
            result['得令'], result['得地'], result['得势']
        )

        # 判断是否为从格
        from_congrong, geju_type = self._judge_from_congrong(
            bazi, result['得令'], result['得地'], result['得势']
        )
        if from_congrong:
            result['强弱判定'] = geju_type
            result['特殊格局'] = geju_type
            result['格局类型'] = geju_type
            qiang_count = sum([result['得令'], result['得地'], result['得势']])
            if geju_type == '从强格':
                result['详细说明'].append(f"【第四步】综合判定：得令={result['得令']}，得地={result['得地']}，得势={result['得势']}，除日主外的其余七个十神都是生助日主，判定：从强格")
            else:  # 从弱格
                result['详细说明'].append(f"【第四步】综合判定：得令={result['得令']}，得地={result['得地']}，得势={result['得势']}，除日主外的其余七个十神都是克泄耗日主，判定：从弱格")
        else:
            qiang_count = sum([result['得令'], result['得地'], result['得势']])
            result['详细说明'].append(f"【第四步】综合判定：得令={result['得令']}，得地={result['得地']}，得势={result['得势']}，占{qiang_count}项，判定：{result['强弱判定']}")

        return result
    
    def _judge_deling(self, ri_wuxing: str, month_zhi: str) -> Dict:
        """
        判断得令（月令强弱）
        依据：日干五行属性与月支（月令）的五行属性一致或相生

        日干五行 得令的月份（地支）
        甲、乙（木）  寅（正月）、卯（二月）
        丙、丁（火）  巳（四月）、午（五月）
        戊、己（土）  辰（三月）、未（六月）、戌（九月）、丑（十二月）
        庚、辛（金）  申（七月）、酉（八月）
        壬、癸（水）  亥（十月）、子（十一月）

        返回:
            {'得令': bool, '详情': str}
        """
        month_wuxing = self.db.ZHI_WUXING.get(month_zhi, '')

        # 判断日干五行与月支五行是否一致（同类）
        if ri_wuxing == month_wuxing:
            return {
                '得令': True,
                '详情': f'日主{ri_wuxing}生于{month_zhi}月，五行相同，得令'
            }

        # 判断月支是否生日主（相生关系）
        if self.db.WUXING_SHENG[month_wuxing] == ri_wuxing:
            return {
                '得令': True,
                '详情': f'日主{ri_wuxing}生于{month_zhi}月，月令生日主，得令'
            }

        # 不得令
        reason = ''
        if self.db.WUXING_KE[month_wuxing] == ri_wuxing:
            reason = f'月令克日主（月令{month_wuxing}克日主{ri_wuxing}）'
        elif self.db.WUXING_SHENG[ri_wuxing] == month_wuxing:
            reason = f'日主生月令（日主{ri_wuxing}生月令{month_wuxing}）'
        else:
            reason = f'五行相克（日主{ri_wuxing}与月令{month_wuxing}相克）'

        return {
            '得令': False,
            '详情': f'日主{ri_wuxing}生于{month_zhi}月，{reason}，不得令'
        }

    def _judge_dedi(self, ri_wuxing: str, day_zhi: str,
                    year_zhi: str, month_zhi: str, time_zhi: str = '') -> Dict:
        """
        判断得地（地支有根）
        依据：地支藏干中含有与日干相同的五行（本气根、中气根、余气根）
        支持无时柱的情况（time_zhi为空）

        日干   本气根（最强）  中气根（次强）    余气根（弱）
        甲、乙   寅、卯         辰（乙）、未（乙）  亥（甲）
        丙、丁   巳、午         未（丁）、戌（丁）  寅（丙）
        戊、己   辰、戌、丑、未  巳（戊）、午（己）  -
        庚、辛   申、酉         戌（辛）、丑（辛）  巳（庚）
        壬、癸   亥、子         丑（癸）、辰（癸）  申（壬）

        返回:
            {'得地': bool, '详情': str}
        """
        # 定义各类根气
        benqi_gen = {
            '甲': ['寅', '卯'], '乙': ['寅', '卯'],
            '丙': ['巳', '午'], '丁': ['巳', '午'],
            '戊': ['辰', '戌', '丑', '未'], '己': ['辰', '戌', '丑', '未'],
            '庚': ['申', '酉'], '辛': ['申', '酉'],
            '壬': ['亥', '子'], '癸': ['亥', '子']
        }

        zhongqi_gen = {
            '甲': ['辰', '未'], '乙': ['辰', '未'],
            '丙': ['未', '戌'], '丁': ['未', '戌'],
            '戊': ['巳'], '己': ['午'],
            '庚': ['戌', '丑'], '辛': ['戌', '丑'],
            '壬': ['丑', '辰'], '癸': ['丑', '辰']
        }

        yuqi_gen = {
            '甲': ['亥'], '乙': [],
            '丙': ['寅'], '丁': [],
            '戊': [], '己': [],
            '庚': ['巳'], '辛': [],
            '壬': ['申'], '癸': []
        }

        # 获取日干
        ri_gan = ''
        for gan, wx in self.db.GAN_WUXING.items():
            if wx == ri_wuxing:
                ri_gan = gan
                break

        # 检查地支根气（支持无时柱）
        if time_zhi:
            zhis = [year_zhi, month_zhi, day_zhi, time_zhi]
            zhi_names = ['年支', '月支', '日支', '时支']
        else:
            zhis = [year_zhi, month_zhi, day_zhi]
            zhi_names = ['年支', '月支', '日支']

        found_roots = []

        for zhi, name in zip(zhis, zhi_names):
            if not zhi:
                continue

            # 检查本气根
            if zhi in benqi_gen.get(ri_gan, []):
                found_roots.append(f'{name}({zhi})有本气根')

            # 检查中气根
            if zhi in zhongqi_gen.get(ri_gan, []):
                found_roots.append(f'{name}({zhi})有中气根')

            # 检查余气根
            if zhi in yuqi_gen.get(ri_gan, []):
                found_roots.append(f'{name}({zhi})有余气根')

        if found_roots:
            return {
                '得地': True,
                '详情': f'地支有根：{"; ".join(found_roots)}，得地'
            }

        return {
            '得地': False,
            '详情': f'地支无根，不得地'
        }

    def _judge_deshi(self, ri_wuxing: str,
                     year_gan: str, month_gan: str, time_gan: str = '') -> Dict:
        """
        判断得势（天干生扶）
        依据：天干中有比肩、劫财或印星生助日主
        支持无时柱的情况（time_gan为空）

        日干   比劫（直接帮扶）  印星（间接生扶）
        甲、乙   甲、乙           壬、癸（水）
        丙、丁   丙、丁           甲、乙（木）
        戊、己   戊、己           丙、丁（火）
        庚、辛   庚、辛           戊、己（土）
        壬、癸   壬、癸           庚、辛（金）

        返回:
            {'得势': bool, '详情': str}
        """
        # 获取日干
        ri_gan = ''
        for gan, wx in self.db.GAN_WUXING.items():
            if wx == ri_wuxing:
                ri_gan = gan
                break

        # 定义比劫和印星
        bijie_gans = []
        yin_gans = []

        for gan, wx in self.db.GAN_WUXING.items():
            # 比劫：同五行
            if wx == ri_wuxing:
                bijie_gans.append(gan)
            # 印星：生助五行
            elif self.db.WUXING_SHENG[wx] == ri_wuxing:
                yin_gans.append(gan)

        # 检查天干（支持无时柱）
        if time_gan:
            gans = [year_gan, month_gan, time_gan]
            gan_names = ['年干', '月干', '时干']
        else:
            gans = [year_gan, month_gan]
            gan_names = ['年干', '月干']

        found_help = []

        for gan, name in zip(gans, gan_names):
            if not gan:
                continue

            # 检查比劫
            if gan in bijie_gans:
                bijie_type = '比肩' if (gan in '甲丙戊庚壬') == (ri_gan in '甲丙戊庚壬') else '劫财'
                found_help.append(f'{name}({gan})是{bijie_type}')

            # 检查印星
            if gan in yin_gans:
                yin_type = '正印' if (gan in '甲丙戊庚壬') != (ri_gan in '甲丙戊庚壬') else '偏印'
                found_help.append(f'{name}({gan})是{yin_type}')

        if found_help:
            return {
                '得势': True,
                '详情': f'天干有生扶：{"; ".join(found_help)}，得势'
            }

        return {
            '得势': False,
            '详情': f'天干无生扶，不得势'
        }
    
    def _check_special_geju(self, deling: bool, dedi: bool, deshi: bool,
                            bazi: Dict[str, str]) -> Optional[str]:
        """
        特殊格局校验
        优先于普通判定

        注意：从格判断已移至 _judge_from_congrong 方法处理

        参数:
            deling: 是否得令
            dedi: 是否得地
            deshi: 是否得势
            bazi: 八字字典
        """
        # 从强格：得令、得地、得势
        if deling and dedi and deshi:
            return '从强格'

        return None

    def _judge_shenqiang_detailed(self, deling: bool, dedi: bool, deshi: bool) -> str:
        """
        详细判定日主身强身弱

        判定依据：
        从强格   除日元外的其余七个十神都是生助日元
        强       得令+得地+得势
        偏强     得令+得地+不得势 或 得令+不得地+得势
        均衡     不得令+得地+得势 或 得令+不得地+不得势
        偏弱     不得令+得地+不得势 或 不得令+不得地+得势
        弱       不得令+不得地+不得势
        从弱格   除日元外的其余七个十神都是克泄耗日元

        参数:
            deling: 是否得令
            dedi: 是否得地
            deshi: 是否得势

        返回:
            身强身弱状态
        """
        # 强：得令+得地+得势
        if deling and dedi and deshi:
            return '强'

        # 偏强：得令+得地+不得势 或 得令+不得地+得势
        if deling and dedi and not deshi:
            return '偏强'
        if deling and not dedi and deshi:
            return '偏强'

        # 均衡：不得令+得地+得势 或 得令+不得地+不得势
        if not deling and dedi and deshi:
            return '均衡'
        if deling and not dedi and not deshi:
            return '均衡'

        # 偏弱：不得令+得地+不得势 或 不得令+不得地+得势
        if not deling and dedi and not deshi:
            return '偏弱'
        if not deling and not dedi and deshi:
            return '偏弱'

        # 弱：不得令+不得地+不得势
        if not deling and not dedi and not deshi:
            return '弱'

        return '均衡'

    def _judge_from_congrong(self, bazi: Dict[str, str],
                              deling: bool, dedi: bool, deshi: bool,
                              dayun_gan: str = '', dayun_zhi: str = '',
                              liunian_gan: str = '', liunian_zhi: str = '') -> Tuple[bool, str]:
        """
        判断是否为从强格或从弱格

        原局：
        从强格：除日元外的其余七个十神都是生助日元
        从弱格：除日元外的其余七个十神都是克泄耗日元

        大运流年：
        专旺格：除日元外的其余十一个十神都是生助日元
        从弱格：除日元外的其余十一个十神都是克泄耗日元

        重要规则：
        - 地支（包括大运流年）仅分析本气，中气余气不考虑
        - 例如：日主壬水，地支辰土，辰藏戊土（七杀）、乙木（伤官）、癸水（劫财），则以七杀论

        参数:
            bazi: 八字字典
            deling: 是否得令
            dedi: 是否得地
            deshi: 是否得势
            dayun_gan: 大运天干（可选，用于区分是否为大运流年分析）
            dayun_zhi: 大运地支（可选）
            liunian_gan: 流年天干（可选）
            liunian_zhi: 流年地支（可选）

        返回:
            (是否为特殊格, 格局类型)
        """
        day_gan = bazi.get('day_gan', '')
        ri_wuxing = self.db.GAN_WUXING.get(day_gan, '')

        # 判断是否为大运流年分析
        is_dayun_liunian = bool(dayun_gan or liunian_gan)

        if is_dayun_liunian:
            # 大运流年分析：十一个十神（原局7个 + 大运天干1个 + 流年天干1个 + 地支藏干）
            gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                    bazi.get('time_gan', ''), dayun_gan, liunian_gan]
            zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                    bazi.get('day_zhi', ''), bazi.get('time_zhi', ''),
                    dayun_zhi, liunian_zhi]
        else:
            # 原局分析：七个十神（原局3个天干 + 地支藏干）
            gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                    bazi.get('time_gan', '')]
            zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                    bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]

        shishens = []  # 十神列表

        # 收集天干的十神
        for gan in gans:
            if not gan:
                continue
            gan_wuxing = self.db.GAN_WUXING.get(gan, '')
            shishens.append(self._get_shishen_type(gan_wuxing, ri_wuxing, gan, day_gan))

        # 收集地支藏干的十神（仅取本气，不考虑中气和余气）
        for zhi in zhis:
            if zhi not in self.db.ZHI_CANGAN:
                continue
            # 只取地支藏干中的本气（第一个元素）
            cang_gan_list = self.db.ZHI_CANGAN[zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING.get(cang_gan, '')
                shishens.append(self._get_shishen_type(cang_wuxing, ri_wuxing, cang_gan, day_gan))

        # 过滤掉空值
        shishens = [ss for ss in shishens if ss != '其他']

        if not shishens:
            return (False, '')

        # 判断所有十神类型
        shengfu_count = sum(1 for ss in shishens if ss in ['比劫', '印星'])
        kexie_count = sum(1 for ss in shishens if ss in ['官杀', '财星', '食伤'])

        if is_dayun_liunian:
            # 大运流年分析：十一个十神判断
            if shengfu_count == len(shishens) and len(shishens) > 0:
                return (True, '从强格')  # 除日主外的其余十一个十神都是生助
            if kexie_count == len(shishens) and len(shishens) > 0:
                return (True, '从弱格')  # 除日主外的其余十一个十神都是克泄耗
        else:
            # 原局分析：七个十神判断
            if shengfu_count == len(shishens) and len(shishens) > 0:
                return (True, '从强格')  # 除日主外的其余七个十神都是生助
            if kexie_count == len(shishens) and len(shishens) > 0:
                return (True, '从弱格')  # 除日主外的其余七个十神都是克泄耗

        return (False, '')

    def _get_shishen_type(self, gan_wuxing: str, ri_wuxing: str,
                           gan: str, day_gan: str) -> str:
        """
        获取十神类型

        参数:
            gan_wuxing: 天干五行
            ri_wuxing: 日主五行
            gan: 天干
            day_gan: 日干

        返回:
            十神类型：'比劫', '印星', '官杀', '财星', '食伤'
        """
        # 比劫：同五行
        if gan_wuxing == ri_wuxing:
            return '比劫'

        # 印星：生助日主
        if self.db.WUXING_SHENG[gan_wuxing] == ri_wuxing:
            return '印星'

        # 官杀：克日主
        if self.db.WUXING_KE[gan_wuxing] == ri_wuxing:
            return '官杀'

        # 食伤：泄日主
        if self.db.WUXING_SHENG[ri_wuxing] == gan_wuxing:
            return '食伤'

        # 财星：耗日主
        if self.db.WUXING_KE[ri_wuxing] == gan_wuxing:
            return '财星'

        return '其他'

    def calculate_with_dayun_liunian(self, bazi: Dict[str, str],
                                      dayun_gan: str, dayun_zhi: str,
                                      liunian_gan: str, liunian_zhi: str) -> Dict:
        """
        计算结合大运流年的日主强弱

        判断逻辑（或的关系）：
        - 得令：原局月支 或 大运地支得令 → 得令
        - 得地：原局地支 或 流年地支有根 → 得地
        - 得势：原局天干 或 大运天干 或 流年天干有生扶 → 得势

        参数:
            bazi: 原局八字字典
            dayun_gan: 大运天干
            dayun_zhi: 大运地支
            liunian_gan: 流年天干
            liunian_zhi: 流年地支

        返回:
            包含原局、大运流年、综合分析的字典
        """
        # 提取原局八字信息
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        year_gan = bazi.get('year_gan', '')
        month_gan = bazi.get('month_gan', '')
        time_gan = bazi.get('time_gan', '')
        day_zhi = bazi.get('day_zhi', '')
        year_zhi = bazi.get('year_zhi', '')
        time_zhi = bazi.get('time_zhi', '')

        # 获取日主五行
        ri_wuxing = self.db.GAN_WUXING.get(day_gan, '')
        if not ri_wuxing:
            return {'error': '日主无效'}

        result = {
            '日主': day_gan,
            '日主五行': ri_wuxing,
            '大运': f'{dayun_gan}{dayun_zhi}',
            '流年': f'{liunian_gan}{liunian_zhi}',
            '原局分析': {},
            '综合分析': {},
            '详细说明': []
        }

        # ============ 原局分析 ============
        result['详细说明'].append("========== 原局分析 ==========")

        # 原局得令
        deling_yuanju = self._judge_deling(ri_wuxing, month_zhi)
        result['原局分析']['得令'] = deling_yuanju['得令']
        result['原局分析']['得令详情'] = deling_yuanju['详情']
        result['详细说明'].append(f"原局得令：{deling_yuanju['详情']}")

        # 原局得地
        dedi_yuanju = self._judge_dedi(ri_wuxing, day_zhi, year_zhi, month_zhi, time_zhi)
        result['原局分析']['得地'] = dedi_yuanju['得地']
        result['原局分析']['得地详情'] = dedi_yuanju['详情']
        result['详细说明'].append(f"原局得地：{dedi_yuanju['详情']}")

        # 原局得势
        deshi_yuanju = self._judge_deshi(ri_wuxing, year_gan, month_gan, time_gan)
        result['原局分析']['得势'] = deshi_yuanju['得势']
        result['原局分析']['得势详情'] = deshi_yuanju['详情']
        result['详细说明'].append(f"原局得势：{deshi_yuanju['详情']}")

        # 原局强弱判定（细致分类）
        yuanju_qiangruo = self._judge_shenqiang_detailed(
            deling_yuanju['得令'], dedi_yuanju['得地'], deshi_yuanju['得势']
        )
        result['原局分析']['强弱判定'] = yuanju_qiangruo
        result['详细说明'].append(f"原局强弱判定：{yuanju_qiangruo}")

        # ============ 大运流年分析 ============
        result['详细说明'].append("")
        result['详细说明'].append("========== 大运流年分析 ==========")

        # 大运地支得令
        deling_dayun = self._judge_deling(ri_wuxing, dayun_zhi)
        result['大运地支得令'] = deling_dayun['得令']
        result['大运地支得令详情'] = deling_dayun['详情']
        result['详细说明'].append(f"大运地支({dayun_zhi})得令判断：{deling_dayun['详情']}")

        # 流年地支得地
        dedi_liunian = self._judge_dedi_single_zhi(ri_wuxing, liunian_zhi, '流年地支')
        result['流年地支得地'] = dedi_liunian['得地']
        result['流年地支得地详情'] = dedi_liunian['详情']
        result['详细说明'].append(f"流年地支({liunian_zhi})得地判断：{dedi_liunian['详情']}")

        # 大运天干得势
        deshi_dayun = self._judge_deshi_single_gan(ri_wuxing, dayun_gan, '大运天干')
        result['大运天干得势'] = deshi_dayun['得势']
        result['大运天干得势详情'] = deshi_dayun['详情']
        result['详细说明'].append(f"大运天干({dayun_gan})得势判断：{deshi_dayun['详情']}")

        # 流年天干得势
        deshi_liunian = self._judge_deshi_single_gan(ri_wuxing, liunian_gan, '流年天干')
        result['流年天干得势'] = deshi_liunian['得势']
        result['流年天干得势详情'] = deshi_liunian['详情']
        result['详细说明'].append(f"流年天干({liunian_gan})得势判断：{deshi_liunian['详情']}")

        # ============ 综合判定 ============
        result['详细说明'].append("")
        result['详细说明'].append("========== 综合判定 ==========")

        # 综合得令：原局 或 大运地支
        zonghe_deling = result['原局分析']['得令'] or result['大运地支得令']
        deling_sources = []
        if result['原局分析']['得令']:
            deling_sources.append('原局月支')
        if result['大运地支得令']:
            deling_sources.append('大运地支')
        result['综合分析']['得令'] = zonghe_deling
        result['综合分析']['得令详情'] = f"{' + '.join(deling_sources)}得令" if deling_sources else "原局与大运地支均不得令"
        result['详细说明'].append(f"综合得令（原局或大运地支）：{result['综合分析']['得令详情']}")

        # 综合得地：原局 或 流年地支
        zonghe_dedi = result['原局分析']['得地'] or result['流年地支得地']
        dedi_sources = []
        if result['原局分析']['得地']:
            dedi_sources.append('原局地支')
        if result['流年地支得地']:
            dedi_sources.append('流年地支')
        result['综合分析']['得地'] = zonghe_dedi
        result['综合分析']['得地详情'] = f"{' + '.join(dedi_sources)}有根" if dedi_sources else "原局与流年地支均无根"
        result['详细说明'].append(f"综合得地（原局或流年地支）：{result['综合分析']['得地详情']}")

        # 综合得势：原局 或 大运天干 或 流年天干
        zonghe_deshi = result['原局分析']['得势'] or result['大运天干得势'] or result['流年天干得势']
        deshi_sources = []
        if result['原局分析']['得势']:
            deshi_sources.append('原局天干')
        if result['大运天干得势']:
            deshi_sources.append('大运天干')
        if result['流年天干得势']:
            deshi_sources.append('流年天干')
        result['综合分析']['得势'] = zonghe_deshi
        result['综合分析']['得势详情'] = f"{' + '.join(deshi_sources)}有生扶" if deshi_sources else "原局、大运天干、流年天干均无生扶"
        result['详细说明'].append(f"综合得势（原局或大运天干或流年天干）：{result['综合分析']['得势详情']}")

        # 综合强弱判定（细致分类）
        original_panding = self._judge_shenqiang_detailed(
            zonghe_deling, zonghe_dedi, zonghe_deshi
        )
        result['综合分析']['强弱判定'] = original_panding

        # 判断是否为从格（大运流年分析：十一个十神）
        from_congrong, geju_type = self._judge_from_congrong(
            bazi, zonghe_deling, zonghe_dedi, zonghe_deshi,
            dayun_gan, dayun_zhi, liunian_gan, liunian_zhi
        )
        if from_congrong:
            result['综合分析']['强弱判定'] = geju_type
            if geju_type == '从强格':
                result['综合分析']['特殊格局'] = geju_type
                result['综合分析']['格局类型'] = geju_type
                result['详细说明'].append(f"【综合判定】除日主外的其余十一个十神都是生助日主，判定：从强格")
            else:  # 从弱格
                result['综合分析']['特殊格局'] = geju_type
                result['综合分析']['格局类型'] = geju_type
                result['详细说明'].append(f"【综合判定】除日主外的其余十一个十神都是克泄耗日主，判定：从弱格")
        else:
            # 均衡格判定调整：统一按照身弱（偏弱）来分析
            if original_panding == '均衡':
                result['综合分析']['强弱判定'] = '偏弱'
                result['详细说明'].append(f"【均衡格调整】均衡格统一按照身弱（偏弱）来分析")
            else:
                qiang_count = sum([zonghe_deling, zonghe_dedi, zonghe_deshi])
                result['详细说明'].append(f"【综合判定】得令={zonghe_deling}，得地={zonghe_dedi}，得势={zonghe_deshi}，占{qiang_count}项，判定：{result['综合分析']['强弱判定']}")

        return result

    def _judge_dedi_single_zhi(self, ri_wuxing: str, zhi: str, zhi_name: str) -> Dict:
        """
        判断单个地支是否有根
        用于大运流年的得地判断

        参数:
            ri_wuxing: 日主五行
            zhi: 地支
            zhi_name: 地支名称（如'流年地支'）

        返回:
            {'得地': bool, '详情': str}
        """
        # 获取日干
        ri_gan = ''
        for gan, wx in self.db.GAN_WUXING.items():
            if wx == ri_wuxing:
                ri_gan = gan
                break

        # 定义各类根气
        benqi_gen = {
            '甲': ['寅', '卯'], '乙': ['寅', '卯'],
            '丙': ['巳', '午'], '丁': ['巳', '午'],
            '戊': ['辰', '戌', '丑', '未'], '己': ['辰', '戌', '丑', '未'],
            '庚': ['申', '酉'], '辛': ['申', '酉'],
            '壬': ['亥', '子'], '癸': ['亥', '子']
        }

        zhongqi_gen = {
            '甲': ['辰', '未'], '乙': ['辰', '未'],
            '丙': ['未', '戌'], '丁': ['未', '戌'],
            '戊': ['巳'], '己': ['午'],
            '庚': ['戌', '丑'], '辛': ['戌', '丑'],
            '壬': ['丑', '辰'], '癸': ['丑', '辰']
        }

        yuqi_gen = {
            '甲': ['亥'], '乙': [],
            '丙': ['寅'], '丁': [],
            '戊': [], '己': [],
            '庚': ['巳'], '辛': [],
            '壬': ['申'], '癸': []
        }

        # 检查根气
        if zhi in benqi_gen.get(ri_gan, []):
            return {
                '得地': True,
                '详情': f'{zhi_name}({zhi})有本气根，得地'
            }
        elif zhi in zhongqi_gen.get(ri_gan, []):
            return {
                '得地': True,
                '详情': f'{zhi_name}({zhi})有中气根，得地'
            }
        elif zhi in yuqi_gen.get(ri_gan, []):
            return {
                '得地': True,
                '详情': f'{zhi_name}({zhi})有余气根，得地'
            }

        return {
            '得地': False,
            '详情': f'{zhi_name}({zhi})无根，不得地'
        }

    def _judge_deshi_single_gan(self, ri_wuxing: str, gan: str, gan_name: str) -> Dict:
        """
        判断单个天干是否有生扶
        用于大运流年的得势判断

        参数:
            ri_wuxing: 日主五行
            gan: 天干
            gan_name: 天干名称（如'大运天干'）

        返回:
            {'得势': bool, '详情': str}
        """
        # 获取日干
        ri_gan = ''
        for g, wx in self.db.GAN_WUXING.items():
            if wx == ri_wuxing:
                ri_gan = g
                break

        gan_wuxing = self.db.GAN_WUXING.get(gan, '')

        # 检查比劫（同五行）
        if gan_wuxing == ri_wuxing:
            bijie_type = '比肩' if (gan in '甲丙戊庚壬') == (ri_gan in '甲丙戊庚壬') else '劫财'
            return {
                '得势': True,
                '详情': f'{gan_name}({gan})是{bijie_type}，得势'
            }

        # 检查印星（生助五行）
        if self.db.WUXING_SHENG[gan_wuxing] == ri_wuxing:
            yin_type = '正印' if (gan in '甲丙戊庚壬') != (ri_gan in '甲丙戊庚壬') else '偏印'
            return {
                '得势': True,
                '详情': f'{gan_name}({gan})是{yin_type}，得势'
            }

        return {
            '得势': False,
            '详情': f'{gan_name}({gan})无生扶，不得势'
        }

    def _is_shengzhu_ri(self, ri_wuxing: str, gan: str, zhi: str) -> Dict:
        """
        判断大运是否生助日主
        用于均衡格的判定调整

        参数:
            ri_wuxing: 日主五行
            gan: 大运天干
            zhi: 大运地支

        返回:
            {
                '天干生助': bool,
                '地支生助': bool,
                '生助数量': int,
                '详情': str
            }
        """
        # 获取日干
        ri_gan = ''
        for g, wx in self.db.GAN_WUXING.items():
            if wx == ri_wuxing:
                ri_gan = g
                break

        gan_shengzhu = False
        zhi_shengzhu = False
        details = []

        # 判断天干是否生助日主
        if gan:
            gan_wuxing = self.db.GAN_WUXING.get(gan, '')
            # 比劫（同五行）生助
            if gan_wuxing == ri_wuxing:
                gan_shengzhu = True
                bijie_type = '比肩' if (gan in '甲丙戊庚壬') == (ri_gan in '甲丙戊庚壬') else '劫财'
                details.append(f'天干{gan}是{bijie_type}，生助日主')
            # 印星生助
            elif self.db.WUXING_SHENG[gan_wuxing] == ri_wuxing:
                gan_shengzhu = True
                yin_type = '正印' if (gan in '甲丙戊庚壬') != (ri_gan in '甲丙戊庚壬') else '偏印'
                details.append(f'天干{gan}是{yin_type}，生助日主')
            else:
                details.append(f'天干{gan}是克泄耗日主')

        # 判断地支本气是否生助日主
        if zhi and zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING.get(cang_gan, '')
                # 比劫（同五行）生助
                if cang_wuxing == ri_wuxing:
                    zhi_shengzhu = True
                    bijie_type = '比肩' if (cang_gan in '甲丙戊庚壬') == (ri_gan in '甲丙戊庚壬') else '劫财'
                    details.append(f'地支{zhi}本气{cang_gan}是{bijie_type}，生助日主')
                # 印星生助
                elif self.db.WUXING_SHENG[cang_wuxing] == ri_wuxing:
                    zhi_shengzhu = True
                    yin_type = '正印' if (cang_gan in '甲丙戊庚壬') != (ri_gan in '甲丙戊庚壬') else '偏印'
                    details.append(f'地支{zhi}本气{cang_gan}是{yin_type}，生助日主')
                else:
                    details.append(f'地支{zhi}本气{cang_gan}是克泄耗日主')

        shengzhu_count = sum([gan_shengzhu, zhi_shengzhu])

        return {
            '天干生助': gan_shengzhu,
            '地支生助': zhi_shengzhu,
            '生助数量': shengzhu_count,
            '详情': '；'.join(details)
        }

    def print_result_with_dayun_liunian(self, result: Dict):
        """打印结合大运流年的格局分析结果（简化版）"""
        print("=" * 80)
        print(f"八字格局分析结果（含大运流年：{result.get('大运', '')} / {result.get('流年', '')}）")
        print("=" * 80)

        print(f"\n【基本信息】")
        shenqiang = result.get('身强身弱', {})
        day_gan = shenqiang.get('日主', '')
        print(f"日主: {day_gan} ({shenqiang.get('日主五行', '')})")
        print(f"大运: {result.get('大运', '')}")
        print(f"流年: {result.get('流年', '')}")

        # 原局格局
        print(f"\n【原局格局识别】")
        print(f"主要格局: {result.get('原局主要格局', '无')}")
        print(f"格局列表: {', '.join(result.get('原局格局列表', []))}")

        # 综合格局
        print(f"\n【综合格局识别（含大运流年）】")
        print(f"主要格局: {result.get('综合主要格局', '无')}")
        print(f"格局列表: {', '.join(result.get('综合格局列表', []))}")

        # 原局身强身弱分析
        print(f"\n【原局身强身弱分析】")
        yuanju = shenqiang.get('原局分析', {})
        print(f"得令: {yuanju.get('得令', False)} - {yuanju.get('得令详情', '')}")
        print(f"得地: {yuanju.get('得地', False)} - {yuanju.get('得地详情', '')}")
        print(f"得势: {yuanju.get('得势', False)} - {yuanju.get('得势详情', '')}")

        # 综合身强身弱分析
        print(f"\n【综合身强身弱分析】")
        zonghe = shenqiang.get('综合分析', {})
        print(f"得令: {zonghe.get('得令', False)} - {zonghe.get('得令详情', '')}")
        print(f"得地: {zonghe.get('得地', False)} - {zonghe.get('得地详情', '')}")
        print(f"得势: {zonghe.get('得势', False)} - {zonghe.get('得势详情', '')}")
        print(f"强弱判定: {zonghe.get('强弱判定', '')}")

        if zonghe.get('特殊格局'):
            print(f"特殊格局: {zonghe['特殊格局']}")

        # 喜用神（衰旺论）打印 - 基于原局分析（均衡格则结合大运转化）
        print(f"\n【喜用神（衰旺论）】")
        # 获取原局和综合强弱判定
        yuanju_qiangruo = yuanju.get('强弱判定', '')
        zonghe_qiangruo = zonghe.get('强弱判定', '')

        # 判断是否为均衡格
        if yuanju_qiangruo == '均衡':
            # 均衡格统一按照身弱来分析
            final_qiangruo = '偏弱'
            print(f"  原局判定: 均衡格（按身弱分析）")
        else:
            # 非均衡格直接使用原局判定
            final_qiangruo = yuanju_qiangruo

        xiyongshen = self.db.get_xiyongshen(day_gan, final_qiangruo)

        if 'error' in xiyongshen:
            print(f"  获取喜用神失败: {xiyongshen['error']}")
        else:
            print(f"  日主: {xiyongshen['日主']}")
            print(f"  喜用神: {xiyongshen['喜神']}")
            print(f"  忌神: {xiyongshen['忌神']}")
            print(f"\n  【成长建议】")
            for line in xiyongshen['成长建议'].split('\n'):
                print(f"  {line}")

        print("=" * 80)


class GeJuCalculator:
    """
    格局计算器
    用于计算八字包含的格局类型
    """
    
    def __init__(self, db: GeJuDatabase = None):
        """初始化格局计算器"""
        self.db = db if db is not None else GeJuDatabase()
        self.shenqiang_calc = ShenQiangCalculator(db)
        self.shishen_geju_analyzer = ShiShenGeJuAnalyzer()
    
    def calculate(self, bazi: Dict[str, str]) -> Dict:
        """
        计算八字格局

        参数:
            bazi: 八字字典

        返回:
            包含格局分析结果的字典
        """
        # 计算身强身弱
        shenqiang_result = self.shenqiang_calc.calculate(bazi)

        # 识别格局
        gejus = self._identify_geju(bazi, shenqiang_result)

        # 确定主要格局：从格 > 正格
        main_geju = '无'
        # 优先级1: 从格（从强格、从弱格）
        congge_patterns = ['从强格', '从弱格']
        for pattern in congge_patterns:
            if pattern in gejus:
                main_geju = pattern
                break
        # 优先级2: 正格
        if main_geju == '无':
            zhengge_patterns = ['正官格', '七杀格', '正财格', '偏财格', '正印格', '偏印格', '食神格', '伤官格']
            for pattern in zhengge_patterns:
                if pattern in gejus:
                    main_geju = pattern
                    break
        if main_geju == '无' and gejus:
            main_geju = gejus[0]

        # 分析十神组合格局
        shishen_geju_result = self.shishen_geju_analyzer.analyze_shishen_geju(bazi, shenqiang_result)

        return {
            '身强身弱': shenqiang_result,
            '格局列表': gejus,
            '主要格局': main_geju,
            '十神组合格局': shishen_geju_result
        }

    def calculate_with_dayun_liunian(self, bazi: Dict[str, str],
                                     dayun_gan: str, dayun_zhi: str,
                                     liunian_gan: str, liunian_zhi: str) -> Dict:
        """
        计算结合大运流年的八字格局

        判断逻辑：
        - 将大运天干、流年天干加入到八字中，重新计算格局
        - 月令仍以原局月令为准（格局基于月令判断）

        参数:
            bazi: 原局八字字典
            dayun_gan: 大运天干
            dayun_zhi: 大运地支
            liunian_gan: 流年天干
            liunian_zhi: 流年地支

        返回:
            包含原局、大运流年、综合分析的字典
        """
        # 计算身强身弱（含大运流年）
        shenqiang_result = self.shenqiang_calc.calculate_with_dayun_liunian(
            bazi, dayun_gan, dayun_zhi, liunian_gan, liunian_zhi
        )

        # 识别原局格局
        gejus_yuanju = self._identify_geju(bazi, shenqiang_result['原局分析'])

        # 构建包含大运流年的八字用于格局分析
        bazi_with_dayun_liunian = bazi.copy()

        # 注意：格局判断基于月令，月令不变
        # 但大运流年的干支会影响透干等判断

        # 识别包含大运流年的格局
        gejus_zonghe = self._identify_geju_with_dayun_liunian(
            bazi, dayun_gan, liunian_gan, shenqiang_result
        )

        # 确定原局主要格局：从格 > 正格
        main_geju_yuanju = '无'
        # 从格优先级最高
        congge_patterns = ['从强格', '从弱格']
        for pattern in congge_patterns:
            if pattern in gejus_yuanju:
                main_geju_yuanju = pattern
                break
        # 其次为正格
        if main_geju_yuanju == '无':
            zhengge_patterns = ['正官格', '七杀格', '正财格', '偏财格', '正印格', '偏印格', '食神格', '伤官格']
            for pattern in zhengge_patterns:
                if pattern in gejus_yuanju:
                    main_geju_yuanju = pattern
                    break
        if main_geju_yuanju == '无' and gejus_yuanju:
            main_geju_yuanju = gejus_yuanju[0]

        # 确定综合主要格局：从格 > 正格
        main_geju_zonghe = '无'
        # 从格优先级最高
        for pattern in congge_patterns:
            if pattern in gejus_zonghe:
                main_geju_zonghe = pattern
                break
        # 其次为正格
        if main_geju_zonghe == '无':
            for pattern in zhengge_patterns:
                if pattern in gejus_zonghe:
                    main_geju_zonghe = pattern
                    break
        if main_geju_zonghe == '无' and gejus_zonghe:
            main_geju_zonghe = gejus_zonghe[0]

        return {
            '大运': f'{dayun_gan}{dayun_zhi}',
            '流年': f'{liunian_gan}{liunian_zhi}',
            '身强身弱': shenqiang_result,
            '原局格局列表': gejus_yuanju,
            '原局主要格局': main_geju_yuanju,
            '综合格局列表': gejus_zonghe,
            '综合主要格局': main_geju_zonghe
        }
    
    def _identify_geju(self, bazi: Dict[str, str],
                     shenqiang_result: Dict) -> List[str]:
        """
        识别八字格局
        仅保留：正格 + 从格（从强格、从弱格）
        """
        gejus = []

        # 检查从格（从强格、从弱格）
        special_geju = shenqiang_result.get('特殊格局')
        if special_geju and special_geju in ['从强格', '从弱格']:
            gejus.append(special_geju)

        # 检查正格
        zhengge = self._check_zhengge(bazi)
        gejus.extend(zhengge)

        return gejus

    def _identify_geju_with_dayun_liunian(self, bazi: Dict[str, str],
                                          dayun_gan: str, liunian_gan: str,
                                          shenqiang_result: Dict) -> List[str]:
        """
        识别包含大运流年的八字格局
        仅保留：正格 + 从格（从强格、从弱格）
        格局判断仍以月令为准，但大运流年干支参与透干等地支组合判断
        """
        gejus = []

        # 检查从格（从强格、从弱格）- 基于综合分析
        zonghe = shenqiang_result.get('综合分析', {})
        special_geju = zonghe.get('特殊格局')
        if special_geju and special_geju in ['从强格', '从弱格']:
            gejus.append(special_geju)

        # 检查正格（透干会考虑大运流年）
        zhengge = self._check_zhengge_with_dayun_liunian(bazi, dayun_gan, liunian_gan)
        gejus.extend(zhengge)

        return gejus

    def _check_zhengge_with_dayun_liunian(self, bazi: Dict[str, str],
                                          dayun_gan: str, liunian_gan: str) -> List[str]:
        """检查正格（含大运流年透干判断）"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')

        gejus = []

        # 构建扩展的天干列表（含大运流年）
        all_gans = [
            bazi.get('year_gan', ''),
            bazi.get('month_gan', ''),
            bazi.get('day_gan', ''),
            bazi.get('time_gan', ''),
            dayun_gan,
            liunian_gan
        ]

        # 正官格、七杀格
        if self._is_guan_with_dayun_liunian(bazi, day_gan, month_zhi, all_gans, is_pian=False):
            gejus.append('正官格')
        if self._is_guan_with_dayun_liunian(bazi, day_gan, month_zhi, all_gans, is_pian=True):
            gejus.append('七杀格')

        # 正财格、偏财格
        if self._is_cai_with_dayun_liunian(bazi, day_gan, month_zhi, all_gans, is_pian=False):
            gejus.append('正财格')
        if self._is_cai_with_dayun_liunian(bazi, day_gan, month_zhi, all_gans, is_pian=True):
            gejus.append('偏财格')

        # 正印格、偏印格
        if self._is_yin_with_dayun_liunian(bazi, day_gan, month_zhi, all_gans, is_pian=False):
            gejus.append('正印格')
        if self._is_yin_with_dayun_liunian(bazi, day_gan, month_zhi, all_gans, is_pian=True):
            gejus.append('偏印格')

        # 食神格、伤官格
        if self._is_shishen_with_dayun_liunian(bazi, day_gan, month_zhi, all_gans, is_pian=False):
            gejus.append('食神格')
        if self._is_shishen_with_dayun_liunian(bazi, day_gan, month_zhi, all_gans, is_pian=True):
            gejus.append('伤官格')

        return gejus

    def _is_guan_with_dayun_liunian(self, bazi: Dict[str, str], day_gan: str,
                                   month_zhi: str, all_gans: List[str], is_pian: bool) -> bool:
        """检查是否为官杀格（含大运流年透干判断）"""
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')
        month_zhi_wuxing = self.db.ZHI_WUXING[month_zhi]

        # 判断月令是否为官杀（看月令地支五行是否克日主）
        if self.db.WUXING_KE[month_zhi_wuxing] == day_gan_wuxing:
            # 月令地支五行克日主，需要看藏干本气的阴阳来确定是正官还是七杀
            if month_zhi in self.db.ZHI_CANGAN:
                cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
                if cang_gan_list:
                    cang_gan = cang_gan_list[0][0]  # 取本气
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:  # 七杀:阴阳相同
                        if cang_gan_is_yang == day_gan_is_yang:
                            return True
                    else:  # 正官:阴阳不同
                        if cang_gan_is_yang != day_gan_is_yang:
                            return True

        # 检查月令藏干是否透出官杀（含大运流年，仅取本气）
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                if self.db.WUXING_KE[cang_wuxing] == day_gan_wuxing:
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:
                        if cang_gan_is_yang == day_gan_is_yang and cang_gan in all_gans:
                            return True
                    else:
                        if cang_gan_is_yang != day_gan_is_yang and cang_gan in all_gans:
                            return True

        return False

    def _is_cai_with_dayun_liunian(self, bazi: Dict[str, str], day_gan: str,
                                  month_zhi: str, all_gans: List[str], is_pian: bool) -> bool:
        """检查是否为财格（含大运流年透干判断）"""
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')

        # 判断月令藏干本气是否为财
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                if self.db.WUXING_KE[day_gan_wuxing] == cang_wuxing:
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:
                        if cang_gan_is_yang == day_gan_is_yang:
                            return True
                    else:
                        if cang_gan_is_yang != day_gan_is_yang:
                            return True

        # 检查月令藏干是否透出财（含大运流年，仅取本气）
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                if self.db.WUXING_KE[day_gan_wuxing] == cang_wuxing:
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:
                        if cang_gan_is_yang == day_gan_is_yang and cang_gan in all_gans:
                            return True
                    else:
                        if cang_gan_is_yang != day_gan_is_yang and cang_gan in all_gans:
                            return True

        return False

    def _is_yin_with_dayun_liunian(self, bazi: Dict[str, str], day_gan: str,
                                  month_zhi: str, all_gans: List[str], is_pian: bool) -> bool:
        """检查是否为印格（含大运流年透干判断）"""
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')

        # 判断月令藏干本气是否为印
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                if self.db.WUXING_SHENG[cang_wuxing] == day_gan_wuxing:
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:
                        if cang_gan_is_yang == day_gan_is_yang:
                            return True
                    else:
                        if cang_gan_is_yang != day_gan_is_yang:
                            return True

        # 检查月令藏干是否透出印（含大运流年，仅取本气）
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                if self.db.WUXING_SHENG[cang_wuxing] == day_gan_wuxing:
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:
                        if cang_gan_is_yang == day_gan_is_yang and cang_gan in all_gans:
                            return True
                    else:
                        if cang_gan_is_yang != day_gan_is_yang and cang_gan in all_gans:
                            return True

        return False

    def _is_shishen_with_dayun_liunian(self, bazi: Dict[str, str], day_gan: str,
                                      month_zhi: str, all_gans: List[str], is_pian: bool) -> bool:
        """检查是否为食伤格（含大运流年透干判断）
        is_pian=False表示食神(阴阳相同), is_pian=True表示伤官(阴阳不同)
        """
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')

        # 判断月令藏干本气是否为食伤
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                if self.db.WUXING_SHENG[day_gan_wuxing] == cang_wuxing:
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    # 食神:阴阳相同,伤官:阴阳不同
                    if is_pian:  # 伤官:阴阳不同
                        if cang_gan_is_yang != day_gan_is_yang:
                            return True
                    else:  # 食神:阴阳相同
                        if cang_gan_is_yang == day_gan_is_yang:
                            return True

        # 检查月令藏干是否透出食伤（含大运流年，仅取本气）
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                if self.db.WUXING_SHENG[day_gan_wuxing] == cang_wuxing:
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    # 食神:阴阳相同,伤官:阴阳不同
                    if is_pian:  # 伤官:阴阳不同
                        if cang_gan_is_yang != day_gan_is_yang and cang_gan in all_gans:
                            return True
                    else:  # 食神:阴阳相同
                        if cang_gan_is_yang == day_gan_is_yang and cang_gan in all_gans:
                            return True

        return False

    def _check_zaqi_geju_with_dayun_liunian(self, bazi: Dict[str, str],
                                           dayun_gan: str, liunian_gan: str) -> bool:
        """检查杂气财官格（含大运流年透干）"""
        month_zhi = bazi.get('month_zhi', '')
        if month_zhi not in ['辰', '戌', '丑', '未']:
            return False

        # 构建扩展天干列表
        all_gans = [
            bazi.get('year_gan', ''),
            bazi.get('month_gan', ''),
            bazi.get('day_gan', ''),
            bazi.get('time_gan', ''),
            dayun_gan,
            liunian_gan
        ]

        day_gan = bazi.get('day_gan', '')
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]

        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                if cang_gan in all_gans:
                    cang_wuxing = self.db.GAN_WUXING[cang_gan]
                    if (self.db.WUXING_KE[day_gan_wuxing] == cang_wuxing or
                        self.db.WUXING_KE[cang_wuxing] == day_gan_wuxing or
                        self.db.WUXING_SHENG[cang_wuxing] == day_gan_wuxing):
                        return True

        return False

    def _check_zhengge(self, bazi: Dict[str, str]) -> List[str]:
        """检查正格"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')

        gejus = []
        day_gan_yinyang = (day_gan in '甲丙戊庚壬')  # True=阳干, False=阴干

        # 正官格 (阴克阳或阳克阴,阴阳不同)
        if self._is_guan(bazi, day_gan, month_zhi, is_pian=False):
            gejus.append('正官格')

        # 七杀格 (阳克阳或阴克阴,阴阳相同)
        if self._is_guan(bazi, day_gan, month_zhi, is_pian=True):
            gejus.append('七杀格')

        # 正财格 (阴克阳或阳克阴,阴阳不同)
        if self._is_cai(bazi, day_gan, month_zhi, is_pian=False):
            gejus.append('正财格')

        # 偏财格 (阳克阳或阴克阴,阴阳相同)
        if self._is_cai(bazi, day_gan, month_zhi, is_pian=True):
            gejus.append('偏财格')

        # 正印格 (阳生日主或阴生日主,阴阳不同)
        if self._is_yin(bazi, day_gan, month_zhi, is_pian=False):
            gejus.append('正印格')

        # 偏印格 (阳生日主或阴生日主,阴阳相同)
        if self._is_yin(bazi, day_gan, month_zhi, is_pian=True):
            gejus.append('偏印格')

        # 食神格 (日主生出的阴阳不同)
        if self._is_shishen(bazi, day_gan, month_zhi, is_pian=False):
            gejus.append('食神格')

        # 伤官格 (日主生出的阴阳相同)
        if self._is_shishen(bazi, day_gan, month_zhi, is_pian=True):
            gejus.append('伤官格')

        return gejus




    
    def _is_guan(self, bazi: Dict[str, str], day_gan: str,
                 month_zhi: str, is_pian: bool) -> bool:
        """
        检查是否为官杀格
        is_pian=False表示正官(阴阳不同), is_pian=True表示七杀(阴阳相同)
        """
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')
        month_zhi_wuxing = self.db.ZHI_WUXING[month_zhi]

        # 判断月令是否为官杀（看月令地支五行是否克日主）
        if self.db.WUXING_KE[month_zhi_wuxing] == day_gan_wuxing:
            # 月令地支五行克日主，需要看藏干本气的阴阳来确定是正官还是七杀
            if month_zhi in self.db.ZHI_CANGAN:
                cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
                if cang_gan_list:
                    cang_gan = cang_gan_list[0][0]  # 取本气
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    # 正官:阴阳不同,七杀:阴阳相同
                    if is_pian:  # 七杀:阴阳相同
                        if cang_gan_is_yang == day_gan_is_yang:
                            return True
                    else:  # 正官:阴阳不同
                        if cang_gan_is_yang != day_gan_is_yang:
                            return True

        # 检查月令藏干是否透出官杀（仅取本气，不考虑中气和余气）
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                # 检查是否为官杀
                if self.db.WUXING_KE[cang_wuxing] == day_gan_wuxing:
                    # 检查阴阳
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:  # 七杀:阴阳相同
                        if cang_gan_is_yang == day_gan_is_yang:
                            # 检查是否透出
                            if self._is_tougan(cang_gan, bazi):
                                return True
                    else:  # 正官:阴阳不同
                        if cang_gan_is_yang != day_gan_is_yang:
                            # 检查是否透出
                            if self._is_tougan(cang_gan, bazi):
                                return True

        return False

    def _is_cai(self, bazi: Dict[str, str], day_gan: str,
                month_zhi: str, is_pian: bool) -> bool:
        """
        检查是否为财格
        is_pian=False表示正财(阴阳不同), is_pian=True表示偏财(阴阳相同)
        """
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')
        month_zhi_wuxing = self.db.ZHI_WUXING[month_zhi]

        # 判断月令是否为财
        if self.db.WUXING_KE[day_gan_wuxing] == month_zhi_wuxing:
            # 检查阴阳是否符合
            month_zhi_is_yang = (month_zhi_wuxing in '甲丙戊庚壬')
            # 正财:阴阳不同,偏财:阴阳相同
            if is_pian:  # 偏财:阴阳相同
                if month_zhi_is_yang == day_gan_is_yang:
                    return True
            else:  # 正财:阴阳不同
                if month_zhi_is_yang != day_gan_is_yang:
                    return True

        # 检查月令藏干是否透出财（仅取本气，不考虑中气和余气）
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                # 检查是否为财
                if self.db.WUXING_KE[day_gan_wuxing] == cang_wuxing:
                    # 检查阴阳
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:  # 偏财:阴阳相同
                        if cang_gan_is_yang == day_gan_is_yang:
                            # 检查是否透出
                            if self._is_tougan(cang_gan, bazi):
                                return True
                    else:  # 正财:阴阳不同
                        if cang_gan_is_yang != day_gan_is_yang:
                            # 检查是否透出
                            if self._is_tougan(cang_gan, bazi):
                                return True

        return False

    def _is_yin(self, bazi: Dict[str, str], day_gan: str,
               month_zhi: str, is_pian: bool) -> bool:
        """
        检查是否为印格
        is_pian=False表示正印(阴阳不同), is_pian=True表示偏印(阴阳相同)
        """
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')
        month_zhi_wuxing = self.db.ZHI_WUXING[month_zhi]

        # 判断月令是否为印
        if self.db.WUXING_SHENG[month_zhi_wuxing] == day_gan_wuxing:
            # 检查阴阳是否符合
            month_zhi_is_yang = (month_zhi_wuxing in '甲丙戊庚壬')
            # 正印:阴阳不同,偏印:阴阳相同
            if is_pian:  # 偏印:阴阳相同
                if month_zhi_is_yang == day_gan_is_yang:
                    return True
            else:  # 正印:阴阳不同
                if month_zhi_is_yang != day_gan_is_yang:
                    return True

        # 检查月令藏干是否透出印（仅取本气，不考虑中气和余气）
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                # 检查是否为印
                if self.db.WUXING_SHENG[cang_wuxing] == day_gan_wuxing:
                    # 检查阴阳
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:  # 偏印:阴阳相同
                        if cang_gan_is_yang == day_gan_is_yang:
                            # 检查是否透出
                            if self._is_tougan(cang_gan, bazi):
                                return True
                    else:  # 正印:阴阳不同
                        if cang_gan_is_yang != day_gan_is_yang:
                            # 检查是否透出
                            if self._is_tougan(cang_gan, bazi):
                                return True

        return False

    def _is_shishen(self, bazi: Dict[str, str], day_gan: str,
                    month_zhi: str, is_pian: bool) -> bool:
        """
        检查是否为食伤格
        is_pian=False表示食神(阴阳相同), is_pian=True表示伤官(阴阳不同)
        """
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')
        month_zhi_wuxing = self.db.ZHI_WUXING[month_zhi]

        # 判断月令是否为食伤（看月令藏干本气是否为食伤）
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                # 检查月令藏干本气是否为食伤（火生土）
                if self.db.WUXING_SHENG[day_gan_wuxing] == cang_wuxing:
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    # 食神:阴阳相同,伤官:阴阳不同
                    if is_pian:  # 伤官:阴阳不同
                        if cang_gan_is_yang != day_gan_is_yang:
                            return True
                    else:  # 食神:阴阳相同
                        if cang_gan_is_yang == day_gan_is_yang:
                            return True

        # 检查月令藏干是否透出食伤（仅取本气，不考虑中气和余气）
        if month_zhi in self.db.ZHI_CANGAN:
            cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
            if cang_gan_list:
                cang_gan = cang_gan_list[0][0]  # 取本气
                cang_wuxing = self.db.GAN_WUXING[cang_gan]
                # 检查是否为食伤
                if self.db.WUXING_SHENG[day_gan_wuxing] == cang_wuxing:
                    # 检查阴阳
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    if is_pian:  # 伤官:阴阳不同
                        if cang_gan_is_yang != day_gan_is_yang:
                            # 检查是否透出
                            if self._is_tougan(cang_gan, bazi):
                                return True
                    else:  # 食神:阴阳相同
                        if cang_gan_is_yang == day_gan_is_yang:
                            # 检查是否透出
                            if self._is_tougan(cang_gan, bazi):
                                return True

        return False
    
    def _is_tougan(self, target_gan: str, bazi: Dict[str, str]) -> bool:
        """检查天干是否透出"""
        gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                bazi.get('day_gan', ''), bazi.get('time_gan', '')]
        return target_gan in gans
    
    def _check_zaqi_geju(self, bazi: Dict[str, str]) -> bool:
        """检查杂气财官格"""
        month_zhi = bazi.get('month_zhi', '')
        if month_zhi not in ['辰', '戌', '丑', '未']:
            return False
        
        # 检查是否有财/官/印透出
        day_gan = bazi.get('day_gan', '')
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        
        if month_zhi in self.db.ZHI_CANGAN:
            for cang_gan, _ in self.db.ZHI_CANGAN[month_zhi]:
                if self._is_tougan(cang_gan, bazi):
                    cang_wuxing = self.db.GAN_WUXING[cang_gan]
                    # 财
                    if self.db.WUXING_KE[day_gan_wuxing] == cang_wuxing:
                        return True
                    # 官杀
                    if self.db.WUXING_KE[cang_wuxing] == day_gan_wuxing:
                        return True
                    # 印
                    if self.db.WUXING_SHENG[cang_wuxing] == day_gan_wuxing:
                        return True
        
        return False
    
    def _check_jianlu(self, bazi: Dict[str, str]) -> bool:
        """检查建禄格（月令为比肩，阴阳相同）"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        month_zhi_wuxing = self.db.ZHI_WUXING[month_zhi]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')
        
        # 月令本气为比肩（建禄）：五行相同且阴阳相同
        if day_gan_wuxing == month_zhi_wuxing:
            if month_zhi in self.db.ZHI_CANGAN:
                cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
                if cang_gan_list:
                    cang_gan = cang_gan_list[0][0]  # 取本气
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    # 比肩：阴阳相同
                    if cang_gan_is_yang == day_gan_is_yang:
                        # 需有财官透出
                        if self._has_caiguan_tou(bazi):
                            return True
        
        return False
    
    def _check_yuejie(self, bazi: Dict[str, str]) -> bool:
        """检查月劫格（月令为劫财，阴阳不同）"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        month_zhi_wuxing = self.db.ZHI_WUXING[month_zhi]
        day_gan_is_yang = (day_gan in '甲丙戊庚壬')
        
        # 月令本气为劫财（月劫）：五行相同且阴阳不同
        if day_gan_wuxing == month_zhi_wuxing:
            if month_zhi in self.db.ZHI_CANGAN:
                cang_gan_list = self.db.ZHI_CANGAN[month_zhi]
                if cang_gan_list:
                    cang_gan = cang_gan_list[0][0]  # 取本气
                    cang_gan_is_yang = (cang_gan in '甲丙戊庚壬')
                    # 劫财：阴阳不同
                    if cang_gan_is_yang != day_gan_is_yang:
                        # 需有财官透出
                        if self._has_caiguan_tou(bazi):
                            return True
        
        return False
    
    def _has_caiguan_tou(self, bazi: Dict[str, str]) -> bool:
        """检查是否有财官透出"""
        day_gan = bazi.get('day_gan', '')
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        
        gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                bazi.get('time_gan', '')]
        
        for gan in gans:
            if not gan:
                continue
            gan_wuxing = self.db.GAN_WUXING[gan]
            # 检查是否为财（日主克的五行）
            if self.db.WUXING_KE[day_gan_wuxing] == gan_wuxing:
                return True
            # 检查是否为官杀（克日主的五行）
            if self.db.WUXING_KE[gan_wuxing] == day_gan_wuxing:
                return True
        
        return False
    
    def _check_yangren(self, bazi: Dict[str, str]) -> bool:
        """检查羊刃格"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        
        # 阳干帝旺位
        if day_gan in self.db.YANGREN:
            if self.db.YANGREN[day_gan] == month_zhi:
                return True
        
        return False
    
    def _check_rilu_gui_shi(self, bazi: Dict[str, str]) -> bool:
        """检查日禄归时格"""
        day_gan = bazi.get('day_gan', '')
        time_zhi = bazi.get('time_zhi', '')
        
        # 时支为日主禄
        if day_gan in self.db.RI_LU:
            if self.db.RI_LU[day_gan] == time_zhi:
                # 需无官杀克禄
                return not self._has_guansha_ke_lu(bazi)
        
        return False
    
    def _check_ren_qi_longbei(self, bazi: Dict[str, str]) -> bool:
        """检查壬骑龙背格"""
        day_gan = bazi.get('day_gan', '')
        
        if day_gan != '壬':
            return False
        
        # 检查是否有辰土
        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        
        # 日坐辰或地支有辰
        if bazi.get('day_zhi', '') == '辰' or zhis.count('辰') >= 2:
            return True
        
        return False
    
    def _check_feitian_luma(self, bazi: Dict[str, str]) -> bool:
        """检查飞天禄马格"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        
        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        
        # 日主庚金，生于亥月，地支多亥（冲巳）
        if day_gan == '庚' and month_zhi == '亥' and zhis.count('亥') >= 2:
            return True
        
        # 日主壬水，生于子月，地支多子（冲午）
        if day_gan == '壬' and month_zhi == '子' and zhis.count('子') >= 2:
            return True
        
        return False
    
    def _check_daochong_lu(self, bazi: Dict[str, str]) -> bool:
        """检查倒冲禄格"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        
        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        
        # 日主丙火/丁火，生于午月，地支多午
        if day_gan in ['丙', '丁'] and month_zhi == '午' and zhis.count('午') >= 2:
            return True
        
        return False
    
    def _check_liuyin_zhaoyang(self, bazi: Dict[str, str]) -> bool:
        """检查六阴朝阳格"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        
        if day_gan != '己' or month_zhi != '亥':
            return False
        
        # 检查地支是否全阴
        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        
        # 亥子丑全阴
        if all(zhi in ['亥', '子', '丑'] for zhi in zhis):
            return True
        
        return False
    
    def _check_jinglan_cha(self, bazi: Dict[str, str]) -> bool:
        """检查井栏叉格"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        
        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        
        # 日主庚金，生于申/酉月，地支多申/酉
        if day_gan == '庚' and month_zhi in ['申', '酉'] and zhis.count('申') + zhis.count('酉') >= 2:
            return True
        
        return False
    
    def _check_zi_yao_si(self, bazi: Dict[str, str]) -> bool:
        """检查子遥巳格"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        
        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        
        # 日主甲木，生于子月，地支多子（遥合巳）
        if day_gan == '甲' and month_zhi == '子' and zhis.count('子') >= 2:
            return True
        
        return False
    
    def _check_chou_yao_si(self, bazi: Dict[str, str]) -> bool:
        """检查丑遥巳格"""
        day_gan = bazi.get('day_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        
        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        
        # 日主辛金，生于丑月，地支多丑（遥合巳）
        if day_gan == '辛' and month_zhi == '丑' and zhis.count('丑') >= 2:
            return True
        
        return False
    
    def _check_xinghe(self, bazi: Dict[str, str]) -> bool:
        """检查刑合格"""
        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        
        # 检查是否有三刑
        # 寅巳申三刑
        if all(zhi in zhis for zhi in ['寅', '巳', '申']):
            return True
        # 丑戌未三刑
        if all(zhi in zhis for zhi in ['丑', '戌', '未']):
            return True
        
        return False
    
    def _check_yaohe(self, bazi: Dict[str, str]) -> bool:
        """检查遥合格"""
        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        
        # 检查是否有遥合（子丑合、寅亥合等）
        # 子丑合
        if all(zhi in zhis for zhi in ['子', '丑']):
            return True
        # 寅亥合
        if all(zhi in zhis for zhi in ['寅', '亥']):
            return True
        
        return False
    
    def _has_caiguan_tou(self, bazi: Dict[str, str]) -> bool:
        """检查是否有财官透出"""
        day_gan = bazi.get('day_gan', '')
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        
        gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                bazi.get('day_gan', ''), bazi.get('time_gan', '')]
        
        for gan in gans:
            if not gan:
                continue
            gan_wuxing = self.db.GAN_WUXING[gan]
            # 财
            if self.db.WUXING_KE[day_gan_wuxing] == gan_wuxing:
                return True
            # 官杀
            if self.db.WUXING_KE[gan_wuxing] == day_gan_wuxing:
                return True
        
        return False
    
    def _has_guansha_ke_lu(self, bazi: Dict[str, str]) -> bool:
        """检查是否有官杀克禄"""
        day_gan = bazi.get('day_gan', '')
        
        if day_gan not in self.db.RI_LU:
            return False
        
        lu = self.db.RI_LU[day_gan]
        gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                bazi.get('time_gan', '')]
        
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        lu_wuxing = self.db.ZHI_WUXING[lu]
        
        for gan in gans:
            if not gan:
                continue
            gan_wuxing = self.db.GAN_WUXING[gan]
            # 检查是否为官杀且克禄
            if self.db.WUXING_KE[gan_wuxing] == lu_wuxing:
                return True
        
        return False

    # ============ 专旺格检查方法 ============

    def _check_quzhi(self, bazi: Dict[str, str]) -> bool:
        """
        检查曲直格（木专旺格）
        1.日主甲/乙木透干；2.地支寅卯辰会木局或亥卯未合木局；3.天干地支无庚辛申酉金。
        """
        day_gan = bazi.get('day_gan', '')
        if day_gan not in ['甲', '乙']:
            return False

        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                bazi.get('day_gan', ''), bazi.get('time_gan', '')]

        # 条件1：日主甲/乙木透干（日主即透干）
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        if day_gan_wuxing != '木':
            return False

        # 条件2：地支寅卯辰会木局或亥卯未合木局
        has_yin = '寅' in zhis
        has_mao = '卯' in zhis
        has_chen = '辰' in zhis
        has_hai = '亥' in zhis
        has_wei = '未' in zhis

        # 寅卯辰三会木局
        if has_yin and has_mao and has_chen:
            pass  # 继续检查条件3
        # 亥卯未三合木局
        elif has_hai and has_mao and has_wei:
            pass  # 继续检查条件3
        else:
            # 至少有两个木相关地支
            wood_zhis = zhis.count('寅') + zhis.count('卯') + zhis.count('辰') + zhis.count('亥') + zhis.count('未')
            if wood_zhis < 2:
                return False

        # 条件3：天干地支无庚辛申酉金
        # 检查天干是否有庚辛金
        has_geng = '庚' in gans
        has_xin = '辛' in gans
        # 检查地支是否有申酉金
        has_shen = '申' in zhis
        has_you = '酉' in zhis

        # 无庚辛申酉金
        if has_geng or has_xin or has_shen or has_you:
            return False

        return True

    def _check_yanshang(self, bazi: Dict[str, str]) -> bool:
        """
        检查炎上格（火专旺格）
        1.日主丙/丁火透干；2.地支巳午未会火局或寅午戌合火局；3.天干地支无壬癸亥子。
        """
        day_gan = bazi.get('day_gan', '')
        if day_gan not in ['丙', '丁']:
            return False

        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                bazi.get('day_gan', ''), bazi.get('time_gan', '')]

        # 条件1：日主丙/丁火透干（日主即透干）
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        if day_gan_wuxing != '火':
            return False

        # 条件2：地支巳午未会火局或寅午戌合火局
        has_si = '巳' in zhis
        has_wu = '午' in zhis
        has_wei = '未' in zhis
        has_yin = '寅' in zhis
        has_xu = '戌' in zhis

        # 巳午未三会火局
        if has_si and has_wu and has_wei:
            pass  # 继续检查条件3
        # 寅午戌三合火局
        elif has_yin and has_wu and has_xu:
            pass  # 继续检查条件3
        else:
            # 至少有两个火相关地支
            fire_zhis = zhis.count('巳') + zhis.count('午') + zhis.count('未') + zhis.count('寅') + zhis.count('戌')
            if fire_zhis < 2:
                return False

        # 条件3：天干地支无壬癸亥子水
        # 检查天干是否有壬癸水
        has_ren = '壬' in gans
        has_gui = '癸' in gans
        # 检查地支是否有亥子水
        has_hai = '亥' in zhis
        has_zi = '子' in zhis

        # 无壬癸亥子水
        if has_ren or has_gui or has_hai or has_zi:
            return False

        return True

    def _check_jiashe(self, bazi: Dict[str, str]) -> bool:
        """
        检查稼穑格（土专旺格）
        1.日主戊/己土透干；2.地支辰戌丑未四库全（或三会土局：申酉戌/亥子丑不属土，需辰戌丑未组合）；3.天干地支无甲乙寅卯木。
        """
        day_gan = bazi.get('day_gan', '')
        if day_gan not in ['戊', '己']:
            return False

        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                bazi.get('day_gan', ''), bazi.get('time_gan', '')]

        # 条件1：日主戊/己土透干（日主即透干）
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        if day_gan_wuxing != '土':
            return False

        # 条件2：地支辰戌丑未四库全（或至少有三个土库）
        earth_zhis = zhis.count('辰') + zhis.count('戌') + zhis.count('丑') + zhis.count('未')

        # 四库全或至少有三个土库
        if earth_zhis < 3:
            return False

        # 条件3：天干地支无甲乙寅卯木
        # 检查天干是否有甲乙木
        has_jia = '甲' in gans
        has_yi = '乙' in gans
        # 检查地支是否有寅卯木
        has_yin = '寅' in zhis
        has_mao = '卯' in zhis

        # 无甲乙寅卯木
        if has_jia or has_yi or has_yin or has_mao:
            return False

        return True

    def _check_congge_jin(self, bazi: Dict[str, str]) -> bool:
        """
        检查从革格（金专旺格）
        1.日主庚/辛金透干；2.地支申酉戌会金局或巳酉丑合金局；3.天干地支无丙丁巳午火。
        """
        day_gan = bazi.get('day_gan', '')
        if day_gan not in ['庚', '辛']:
            return False

        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                bazi.get('day_gan', ''), bazi.get('time_gan', '')]

        # 条件1：日主庚/辛金透干（日主即透干）
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        if day_gan_wuxing != '金':
            return False

        # 条件2：地支申酉戌会金局或巳酉丑合金局
        has_shen = '申' in zhis
        has_you = '酉' in zhis
        has_xu = '戌' in zhis
        has_si = '巳' in zhis
        has_chou = '丑' in zhis

        # 申酉戌三会金局
        if has_shen and has_you and has_xu:
            pass  # 继续检查条件3
        # 巳酉丑三合金局
        elif has_si and has_you and has_chou:
            pass  # 继续检查条件3
        else:
            # 至少有两个金相关地支
            gold_zhis = zhis.count('申') + zhis.count('酉') + zhis.count('戌') + zhis.count('巳') + zhis.count('丑')
            if gold_zhis < 2:
                return False

        # 条件3：天干地支无丙丁巳午火
        # 检查天干是否有丙丁火
        has_bing = '丙' in gans
        has_ding = '丁' in gans
        # 检查地支是否有巳午火
        has_si = '巳' in zhis
        has_wu = '午' in zhis

        # 无丙丁巳午火
        if has_bing or has_ding or has_si or has_wu:
            return False

        return True

        return False

    def _check_runxia(self, bazi: Dict[str, str]) -> bool:
        """
        检查润下格（水专旺格）
        1.日主壬/癸水透干；2.地支亥子丑会水局或申子辰合水局；3.天干地支无戊己辰戌土。
        """
        day_gan = bazi.get('day_gan', '')
        if day_gan not in ['壬', '癸']:
            return False

        zhis = [bazi.get('year_zhi', ''), bazi.get('month_zhi', ''),
                bazi.get('day_zhi', ''), bazi.get('time_zhi', '')]
        gans = [bazi.get('year_gan', ''), bazi.get('month_gan', ''),
                bazi.get('day_gan', ''), bazi.get('time_gan', '')]

        # 条件1：日主壬/癸水透干（日主即透干）
        day_gan_wuxing = self.db.GAN_WUXING[day_gan]
        if day_gan_wuxing != '水':
            return False

        # 条件2：地支亥子丑会水局或申子辰合水局
        has_hai = '亥' in zhis
        has_zi = '子' in zhis
        has_chou = '丑' in zhis
        has_shen = '申' in zhis
        has_chen = '辰' in zhis

        # 亥子丑三会水局
        if has_hai and has_zi and has_chou:
            pass  # 继续检查条件3
        # 申子辰三合水局
        elif has_shen and has_zi and has_chen:
            pass  # 继续检查条件3
        else:
            # 至少有两个水相关地支
            water_zhis = zhis.count('亥') + zhis.count('子') + zhis.count('丑') + zhis.count('申') + zhis.count('辰')
            if water_zhis < 2:
                return False

        # 条件3：天干地支无戊己辰戌土
        # 检查天干是否有戊己土
        has_wu = '戊' in gans
        has_ji = '己' in gans
        # 检查地支是否有辰戌土（丑未虽然属土，但不是纯土库，辰戌为土之墓库）
        has_chen = '辰' in zhis
        has_xu = '戌' in zhis

        # 无戊己辰戌土
        if has_wu or has_ji or has_chen or has_xu:
            return False

        return True

    def print_result(self, result: Dict, bazi: Dict = None):
        """打印格局分析结果（简化版）"""
        print("=" * 60)
        print("八字格局分析结果")
        print("=" * 60)

        # 身强身弱
        shenqiang = result['身强身弱']
        print(f"\n【身强身弱分析】")
        print(f"日主: {shenqiang['日主']} ({shenqiang['日主五行']})")
        print(f"得令: {shenqiang['得令']} - {shenqiang['得令详情']}")
        print(f"得地: {shenqiang['得地']} - {shenqiang['得地详情']}")
        print(f"得势: {shenqiang['得势']} - {shenqiang['得势详情']}")
        print(f"强弱判定: {shenqiang['强弱判定']}")

        # 格局类型
        print(f"\n【格局识别】")
        print(f"主要格局: {result['主要格局']}")
        print(f"格局列表: {', '.join(result['格局列表'])}")

        # 十神组合格局
        shishen_geju = result.get('十神组合格局', {})
        if shishen_geju:
            self.shishen_geju_analyzer.print_shishen_geju(shishen_geju, bazi)

        print("=" * 60)

    def print_result_with_dayun_liunian(self, result: Dict):
        """打印结合大运流年的格局分析结果（简化版）"""
        print("=" * 80)
        print(f"八字格局分析结果（含大运流年：{result.get('大运', '')} / {result.get('流年', '')}）")
        print("=" * 80)

        print(f"\n【基本信息】")
        shenqiang = result.get('身强身弱', {})
        day_gan = shenqiang.get('日主', '')
        print(f"日主: {day_gan} ({shenqiang.get('日主五行', '')})")
        print(f"大运: {result.get('大运', '')}")
        print(f"流年: {result.get('流年', '')}")

        # 原局格局
        print(f"\n【原局格局识别】")
        print(f"主要格局: {result.get('原局主要格局', '无')}")
        print(f"格局列表: {', '.join(result.get('原局格局列表', []))}")

        # 综合格局
        print(f"\n【综合格局识别（含大运流年）】")
        print(f"主要格局: {result.get('综合主要格局', '无')}")
        print(f"格局列表: {', '.join(result.get('综合格局列表', []))}")

        # 原局身强身弱分析
        print(f"\n【原局身强身弱分析】")
        yuanju = shenqiang.get('原局分析', {})
        print(f"得令: {yuanju.get('得令', False)} - {yuanju.get('得令详情', '')}")
        print(f"得地: {yuanju.get('得地', False)} - {yuanju.get('得地详情', '')}")
        print(f"得势: {yuanju.get('得势', False)} - {yuanju.get('得势详情', '')}")

        # 综合身强身弱分析
        print(f"\n【综合身强身弱分析】")
        zonghe = shenqiang.get('综合分析', {})
        print(f"得令: {zonghe.get('得令', False)} - {zonghe.get('得令详情', '')}")
        print(f"得地: {zonghe.get('得地', False)} - {zonghe.get('得地详情', '')}")
        print(f"得势: {zonghe.get('得势', False)} - {zonghe.get('得势详情', '')}")
        print(f"强弱判定: {zonghe.get('强弱判定', '')}")

        if zonghe.get('特殊格局'):
            print(f"特殊格局: {zonghe['特殊格局']}")

        # 喜用神（衰旺论）打印 - 基于原局分析（均衡格则结合大运转化）
        print(f"\n【喜用神（衰旺论）】")
        # 获取原局和综合强弱判定
        yuanju_qiangruo = yuanju.get('强弱判定', '')
        zonghe_qiangruo = zonghe.get('强弱判定', '')

        # 判断是否为均衡格
        if yuanju_qiangruo == '均衡':
            # 均衡格统一按照身弱来分析
            final_qiangruo = '偏弱'
            print(f"  原局判定: 均衡格（按身弱分析）")
        else:
            # 非均衡格直接使用原局判定
            final_qiangruo = yuanju_qiangruo

        xiyongshen = self.db.get_xiyongshen(day_gan, final_qiangruo)

        if 'error' in xiyongshen:
            print(f"  获取喜用神失败: {xiyongshen['error']}")
        else:
            print(f"  日主: {xiyongshen['日主']}")
            print(f"  喜用神: {xiyongshen['喜神']}")
            print(f"  忌神: {xiyongshen['忌神']}")
            print(f"\n  【成长建议】")
            for line in xiyongshen['成长建议'].split('\n'):
                print(f"  {line}")

        print("=" * 80)


def parse_bazi_input(bazi_str: str) -> Dict[str, str]:
    """
    解析八字输入字符串
    
    参数:
        bazi_str: 八字字符串,格式为 "甲子 乙丑 丙寅 丁卯"
        
    返回:
        八字字典
    """
    parts = bazi_str.split()
    
    if len(parts) < 4:
        raise ValueError("八字输入格式错误,需要四柱,格式为: 甲子 乙丑 丙寅 丁卯")
    
    result = {}
    
    # 年柱
    result['year_gan'] = parts[0][0] if len(parts[0]) > 0 else ''
    result['year_zhi'] = parts[0][1] if len(parts[0]) > 1 else ''
    
    # 月柱
    result['month_gan'] = parts[1][0] if len(parts[1]) > 0 else ''
    result['month_zhi'] = parts[1][1] if len(parts[1]) > 1 else ''
    
    # 日柱
    result['day_gan'] = parts[2][0] if len(parts[2]) > 0 else ''
    result['day_zhi'] = parts[2][1] if len(parts[2]) > 1 else ''
    
    # 时柱
    result['time_gan'] = parts[3][0] if len(parts[3]) > 0 else ''
    result['time_zhi'] = parts[3][1] if len(parts[3]) > 1 else ''
    
    return result


def main():
    """主函数: 示例用法"""
    # 创建数据库和计算器
    db = GeJuDatabase()
    calculator = GeJuCalculator(db)

    # 示例八字
    bazi_str = "戊寅 戊午 壬辰 戊申"

    print(f"输入八字: {bazi_str}")
    print()

    # 解析八字
    bazi_dict = parse_bazi_input(bazi_str)

    # 计算格局（原局）
    result = calculator.calculate(bazi_dict)

    # 打印结果
    calculator.print_result(result)


if __name__ == '__main__':
    # 创建数据库和计算器
    db = GeJuDatabase()
    calculator = GeJuCalculator(db)
    tougan_tonggen_analyzer = TouGanTongGenAnalyzer(db)

    # 示例八字
    bazi_str = "戊寅 戊午 壬辰 戊申"

    print(f"输入八字: {bazi_str}")
    print()

    # 解析八字
    bazi_dict = parse_bazi_input(bazi_str)

    # 计算格局（原局）
    result = calculator.calculate(bazi_dict)

    # 打印结果
    calculator.print_result(result)

    # 透干通根分析（原局）
    print("\n\n" + "=" * 80)
    print("透干通根分析示例")
    print("=" * 80)

    tougan_tonggen_result = tougan_tonggen_analyzer.analyze_tougan_tonggen(bazi_dict)
    tougan_tonggen_analyzer.print_analysis(tougan_tonggen_result)

    # 大运流年格局分析示例（新功能）
    print("\n\n" + "=" * 80)
    print("大运流年格局分析示例（包含格局识别）")
    print("=" * 80)

    # 示例：原局 + 大运 + 流年
    result_with_dayun_geju = calculator.calculate_with_dayun_liunian(
        bazi_dict,
        dayun_gan='辛',   # 大运天干
        dayun_zhi='酉',    # 大运地支
        liunian_gan='丙',  # 流年天干
        liunian_zhi='午'   # 流年地支
    )

    # 打印大运流年格局分析结果
    calculator.print_result_with_dayun_liunian(result_with_dayun_geju)

    # 透干通根分析（含大运流年）
    print("\n\n" + "=" * 80)
    print("透干通根分析示例（含大运流年）")
    print("=" * 80)

    tougan_tonggen_result_with_dayun = tougan_tonggen_analyzer.analyze_tougan_tonggen_with_dayun_liunian(
        bazi_dict,
        dayun_gan='辛',
        dayun_zhi='酉',
        liunian_gan='丙',
        liunian_zhi='午'
    )
    tougan_tonggen_analyzer.print_analysis_with_dayun_liunian(
        tougan_tonggen_result_with_dayun,
        dayun_gan='辛',
        dayun_zhi='酉',
        liunian_gan='丙',
        liunian_zhi='午'
    )
