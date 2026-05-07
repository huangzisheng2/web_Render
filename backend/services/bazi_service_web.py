"""
八字分析服务 - Web端专用
整合命理模块提供完整分析功能，用于Web前端和APP端调用
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

# 命理模块路径已在 main.py 中添加
from lunar_python import Solar
from city_database import CITY_DATABASE
from true_solar_time import calculate_true_solar_time
from bazi_bridge import analyze_bazi_unified


class BaziAnalysisServiceWeb:
    """
    八字分析服务 - Web端专用
    
    该类封装了前端/APP端需要的所有八字分析功能，
    与核心计算程序隔离，便于多端统一维护。
    """
    
    def __init__(self):
        self.city_data = CITY_DATABASE
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
    
    # ==================== 1. 城市位置服务 ====================
    
    def get_cities(self) -> Dict[str, list]:
        """
        获取城市列表
        
        Returns:
            {"省份": ["城市1", "城市2", ...], ...}
        """
        cities = {}
        for province, city, _, _ in self.city_data:
            if province not in cities:
                cities[province] = []
            cities[province].append(city)
        return cities
    
    def get_location(self, province: str, city: str) -> Tuple[Optional[float], Optional[float]]:
        """
        根据省份城市获取经纬度
        
        Args:
            province: 省份名称
            city: 城市名称
            
        Returns:
            (longitude, latitude) 或 (None, None)
        """
        try:
            # 清理输入
            province = province.strip() if province else ""
            city = city.strip() if city else ""
            
            print(f"[DEBUG] 查找城市: province='{province}', city='{city}'")
            
            if not province or not city:
                print("[DEBUG] 省份或城市为空，跳过真太阳时计算")
                return (None, None)
            
            # 遍历城市数据库查找
            for prov, c, lon, lat in self.city_data:
                if prov == province and c == city:
                    print(f"[DEBUG] 找到城市: {prov} {c}, 经度: {lon}, 纬度: {lat}")
                    return (lon, lat)
            
            # 尝试仅按城市名查找
            for prov, c, lon, lat in self.city_data:
                if c == city:
                    print(f"[DEBUG] 按城市名找到: {prov} {c}, 经度: {lon}, 纬度: {lat}")
                    return (lon, lat)
            
            print(f"[DEBUG] 未找到城市: {province} {city}")
            return (None, None)
        except Exception as e:
            print(f"获取城市位置失败: {e}")
            import traceback
            traceback.print_exc()
            return (None, None)
    
    # ==================== 2. 时间转换服务 ====================
    
    def apply_true_solar_time(
        self, 
        year: int, month: int, day: int, 
        hour: int, minute: int,
        longitude: Optional[float]
    ) -> Tuple[int, int, int, int, int]:
        """
        应用真太阳时转换
        
        Args:
            year, month, day: 日期
            hour, minute: 时间
            longitude: 经度
            
        Returns:
            (adjusted_year, adjusted_month, adjusted_day, adjusted_hour, adjusted_minute)
        """
        if longitude is None:
            return (year, month, day, hour, minute)
        
        try:
            result = calculate_true_solar_time(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                longitude=longitude
            )
            return (
                result.get("year", year),
                result.get("month", month),
                result.get("day", day),
                result.get("hour", hour),
                result.get("minute", minute)
            )
        except Exception as e:
            print(f"真太阳时计算失败，使用原时间: {e}")
            return (year, month, day, hour, minute)
    
    def convert_to_bazi(
        self, 
        year: int, month: int, day: int, 
        hour: Optional[int] = None, minute: int = 0
    ) -> Dict[str, str]:
        """
        公历转八字
        
        Args:
            hour: None 表示不计算时柱
            
        Returns:
            {
                'year_gan': '甲', 'year_zhi': '子',
                'month_gan': '乙', 'month_zhi': '丑',
                'day_gan': '丙', 'day_zhi': '寅',
                'time_gan': '丁', 'time_zhi': '卯'
            }
        """
        solar = Solar.fromYmd(year, month, day)
        lunar = solar.getLunar()
        ba = lunar.getEightChar()
        
        bazi = {
            'year_gan': ba.getYearGan(),
            'year_zhi': ba.getYearZhi(),
            'month_gan': ba.getMonthGan(),
            'month_zhi': ba.getMonthZhi(),
            'day_gan': ba.getDayGan(),
            'day_zhi': ba.getDayZhi(),
            'time_gan': '',
            'time_zhi': '',
        }
        
        if hour is not None:
            solar_with_time = Solar.fromYmdHms(year, month, day, hour, minute, 0)
            lunar_with_time = solar_with_time.getLunar()
            ba_with_time = lunar_with_time.getEightChar()
            bazi['time_gan'] = ba_with_time.getTimeGan()
            bazi['time_zhi'] = ba_with_time.getTimeZhi()
        
        return bazi
    
    # ==================== 3. 核心分析服务 ====================
    
    def analyze_basic(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行基础八字分析（不含AI分析）
        
        Args:
            birth_data: {
                "name": str,
                "year": int, "month": int, "day": int,
                "hour": Optional[int], "minute": int,
                "gender": "male" | "female",
                "province": str, "city": str
            }
        
        Returns:
            基础分析结果字典
        """
        # 1. 获取地理位置
        province = birth_data.get("province", "")
        city = birth_data.get("city", "")
        longitude, latitude = self.get_location(province, city)
        
        # 2. 真太阳时转换
        hour = birth_data.get("hour")
        if hour is not None:
            adj_year, adj_month, adj_day, adj_hour, adj_minute = self.apply_true_solar_time(
                birth_data["year"],
                birth_data["month"],
                birth_data["day"],
                hour,
                birth_data.get("minute", 0),
                longitude
            )
        else:
            adj_year = birth_data["year"]
            adj_month = birth_data["month"]
            adj_day = birth_data["day"]
            adj_hour = None
            adj_minute = 0
        
        # 3. 转换为八字
        bazi_dict = self.convert_to_bazi(adj_year, adj_month, adj_day, adj_hour, adj_minute)
        
        # 4. 命理分析
        is_male = birth_data.get("gender") == "male"
        analysis_result = analyze_bazi_unified(
            adj_year,
            adj_month,
            adj_day,
            adj_hour,
            adj_minute,
            is_male=is_male,
            liunian_year=datetime.now().year,
            name=birth_data.get("name", ""),
            province_city=f"{birth_data.get('province', '')} {birth_data.get('city', '')}".strip()
        )

        # 5. 组装结果
        lunji_data = analysis_result.get('analysis', {})
        complete_data = analysis_result.get('complete_data', {})
        
        merged_data = {
            **complete_data,
            **lunji_data,
            '第一论级_月令与格局': lunji_data.get('第一论级_月令与格局', {}),
            '第二论级_地支关系': lunji_data.get('第二论级_地支关系', {}),
            '第三论级_天干关系': lunji_data.get('第三论级_天干关系', {}),
            '第四论级_天干与地支的关系': lunji_data.get('第四论级_天干与地支的关系', {}),
            '第五论级_定喜忌': lunji_data.get('第五论级_定喜忌', {}),
            '第五论级_辅助信息': lunji_data.get('第五论级_辅助信息', {}),
            '第六论级_大运流年': lunji_data.get('第六论级_大运流年', {}),
            '格局综合判定': lunji_data.get('格局综合判定', {}),
            '基础信息综合分析': complete_data.get('基础信息综合分析', {}),
            '命盘综合信息分析': complete_data.get('命盘综合信息分析', {}),
        }
        
        geju_summary = lunji_data.get('格局综合判定', {})
        first_level = lunji_data.get('第一论级_月令与格局', {})
        
        # 构建AI提示词
        user_info = {
            "name": birth_data.get("name", "匿名"),
            "gender": "male" if is_male else "female",
        }
        ai_prompt = self._build_ai_prompt(bazi_dict, merged_data, user_info)
        
        result = {
            "report_id": f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(birth_data['name']) % 10000:04d}",
            "user_info": {
                "name": birth_data.get("name"),
                "gender": "男" if is_male else "女",
                "birth_time": {
                    "original": {
                        "year": birth_data["year"],
                        "month": birth_data["month"],
                        "day": birth_data["day"],
                        "hour": birth_data.get("hour"),
                        "minute": birth_data.get("minute", 0),
                    },
                    "adjusted": {
                        "year": adj_year,
                        "month": adj_month,
                        "day": adj_day,
                        "hour": adj_hour,
                        "minute": adj_minute,
                    } if hour is not None else None,
                    "location": {
                        "province": birth_data.get("province"),
                        "city": birth_data.get("city"),
                        "longitude": longitude,
                        "latitude": latitude,
                    }
                }
            },
            "bazi": {
                "year_gan": bazi_dict['year_gan'],
                "year_zhi": bazi_dict['year_zhi'],
                "month_gan": bazi_dict['month_gan'],
                "month_zhi": bazi_dict['month_zhi'],
                "day_gan": bazi_dict['day_gan'],
                "day_zhi": bazi_dict['day_zhi'],
                "time_gan": bazi_dict['time_gan'],
                "time_zhi": bazi_dict['time_zhi'],
                "year_pillar": f"{bazi_dict['year_gan']}{bazi_dict['year_zhi']}",
                "month_pillar": f"{bazi_dict['month_gan']}{bazi_dict['month_zhi']}",
                "day_pillar": f"{bazi_dict['day_gan']}{bazi_dict['day_zhi']}",
                "time_pillar": f"{bazi_dict['time_gan']}{bazi_dict['time_zhi']}" if bazi_dict['time_gan'] else "未提供",
                "day_master": bazi_dict['day_gan'],
                "month_command": first_level.get('月令', ''),
            },
            "analysis": {
                "strength": first_level.get('身强身弱', '未知'),
                "main_pattern": first_level.get('主要格局', geju_summary.get('主格局', '未知')),
                "wuxing_energy": geju_summary.get('五行能量分析', {}),
                "shishen_energy": geju_summary.get('十神能量分析', {}),
                "yongshen": {
                    "yong": lunji_data.get('第五论级_定喜忌', {}).get('用神', '无'),
                    "xi": lunji_data.get('第五论级_定喜忌', {}).get('喜神', '无'),
                    "ji": lunji_data.get('第五论级_定喜忌', {}).get('忌神', '无'),
                }
            },
            "raw_data": merged_data,
            "ai_prompt": ai_prompt,
            "ai_report": None
        }
        
        return result
    
    def analyze_ai(self, report_id: str, basic_result: Dict[str, Any], mode: str = "detail") -> str:
        """
        执行AI天赋分析
        
        Args:
            report_id: 报告ID
            basic_result: 基础分析结果
            mode: 分析模式 - "simple"(简易版) 或 "detail"(详细版)
            
        Returns:
            AI分析报告文本
        """
        bazi_data = basic_result.get("bazi", {})
        analysis_data = basic_result.get("raw_data", {})
        user_info = {
            "name": basic_result.get("user_info", {}).get("name", "匿名"),
            "gender": "male" if basic_result.get("user_info", {}).get("gender") == "男" else "female",
        }
        
        if mode == "simple":
            ai_report = self._call_deepseek_api(bazi_data, analysis_data, user_info, mode="simple")
        elif mode == "deep_explore":
            ai_report = self._call_deepseek_api(bazi_data, analysis_data, user_info, mode="deep_explore")
        else:
            # 兼容旧版 detail 模式
            ai_report = self._call_deepseek_api(bazi_data, analysis_data, user_info, mode="detail")
        return ai_report
    
    def analyze_full(self, birth_data: Dict[str, Any], skip_ai: bool = False) -> Dict[str, Any]:
        """
        执行完整分析流程
        
        Args:
            birth_data: 出生信息
            skip_ai: 是否跳过AI分析
        
        Returns:
            完整的分析结果字典
        """
        result = self.analyze_basic(birth_data)
        
        if not skip_ai:
            ai_report = self.analyze_ai(result["report_id"], result)
            result["ai_report"] = ai_report
        
        return result
    
    # ==================== 4. AI服务 ====================
    
    def _call_deepseek_api(self, bazi_data: Dict, analysis_data: Dict, user_info: Dict, mode: str = "detail") -> str:
        """
        调用 DeepSeek API 生成分析报告
        """
        import urllib.request
        import json
        
        if mode == "simple":
            prompt = self._build_simple_prompt(bazi_data, analysis_data, user_info)
            max_tokens = 4000
            system_content = "你是一位专攻青年潜能开发的导师，擅长把复杂的个人特质解读翻译成让年轻人一看就懂的成长指南。请严格按提示词要求的三个模块输出，语言像朋友间推心置腹的对话，绝对禁止使用任何命理学原有术语。"
        elif mode == "deep_explore":
            prompt = self._build_deep_explore_prompt(bazi_data, analysis_data, user_info)
            max_tokens = 8000
            system_content = "你是一位天赋解读导师。你曾研究传统智慧，但更精通现代心理学与优势教育。你相信每个人都不是带着'命运'出生的，而是携带着一套独特的'出厂设置'——即天赋潜能。你的任务是帮助年轻探索者看见自己身上那些尚未被完全激活的光亮。你的分析不带任何宿命色彩，而是聚焦于'可能性'、'倾向性'与'发展区'。"
        else:
            prompt = self._build_ai_prompt(bazi_data, analysis_data, user_info)
            max_tokens = 4000
            system_content = "你是一位精通中国传统命理学的专家分析师，擅长通过八字分析一个人的天赋和性格特征。请用专业、客观、建设性的语调进行阐述。"
        
        try:
            req_data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": system_content
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": max_tokens
            }
            
            req = urllib.request.Request(
                "https://api.deepseek.com/v1/chat/completions",
                data=json.dumps(req_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.deepseek_api_key}'
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
                
        except Exception as e:
            print(f"DeepSeek API 调用失败: {e}")
            return f"AI 分析暂时不可用，请稍后重试。错误: {str(e)}"
    
    def _build_ai_prompt(self, bazi_data: Dict, analysis_data: Dict, user_info: Dict) -> str:
        """
        构建 AI 分析提示词
        """
        # 提取数据
        geju_summary = analysis_data.get('格局综合判定', {})
        first_level = analysis_data.get('第一论级_月令与格局', {})
        sixth_level = analysis_data.get('第六论级_大运流年', {})
        fifth_level_aux = analysis_data.get('第五论级_辅助信息', {})
        basic_info = analysis_data.get('基础信息综合分析', {})
        
        # 格式化能量
        def format_energy(data_dict, name_map=None):
            if not data_dict:
                return "暂无数据"
            total = sum(max(v, 0) for v in data_dict.values())
            sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
            lines = []
            for k, v in sorted_items:
                name = name_map.get(k, k) if name_map else k
                pct = (v / total * 100) if total > 0 else 0
                lines.append(f"{name}({k}): {v:.1f}分 (占比{pct:.1f}%)")
            return "、".join(lines)
        
        shishen_names = {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官',
                        '财': '正财', '才': '偏财', '官': '正官', '杀': '七杀',
                        '印': '正印', '枭': '偏印'}
        
        # 神煞
        shensha_data = fifth_level_aux.get('神煞', {})
        all_shensha = []
        for pillar in ['年柱', '月柱', '日柱', '时柱']:
            all_shensha.extend(shensha_data.get(pillar, []))
        shensha_str = "、".join(all_shensha) if all_shensha else "无"
        
        # 从基础信息提取
        ri_gan = basic_info.get('日元', bazi_data.get('day_gan', '未知'))
        ri_zhi = basic_info.get('日支', bazi_data.get('day_zhi', '未知'))
        yue_ling = basic_info.get('月令', first_level.get('月令', '未知'))
        wuxing_wangxiang = basic_info.get('五行旺相', '未知')
        zhu_geju = geju_summary.get('主格局', first_level.get('主要格局', '未知'))
        tiaohou = "、".join(basic_info.get('调候用神', [])) if basic_info.get('调候用神') else "无"
        
        # 关系
        yuanju_tiangan = "、".join(basic_info.get('原局天干关系', [])) or "无"
        yuanju_dizhi = "、".join(basic_info.get('原局地支关系', [])) or "无"
        yuanju_ganzhi = "、".join(basic_info.get('原局干支关系', [])) or "无"
        suiyun_tiangan = "、".join(basic_info.get('岁运天干关系', [])) or "无"
        suiyun_dizhi = "、".join(basic_info.get('岁运地支关系', [])) or "无"
        
        # 岁运干支关系
        def format_relations(data, keys):
            items = []
            for key in keys:
                val = data.get(key)
                if val and val != '无':
                    items.extend(val) if isinstance(val, list) else items.append(val)
            return "、".join(items) if items else "无"
        
        suiyun_ganzhi = format_relations(sixth_level.get('岁运干支分析', {}), ['伏吟', '天克地冲', '截脚', '盖头'])
        
        # 大运流年
        dangqian_liunian = basic_info.get('当前流年', '未知')
        dangqian_dayun = basic_info.get('当前大运', '未知')
        future_liunian = basic_info.get('未来五年流年', [])
        future_liunian_str = "、".join(future_liunian) if future_liunian else "暂无数据"
        
        prompt = f"""# 角色
你是一位兼具传统命理逻辑与现代心理学视角的天赋分析师。你的分析不宣扬宿命论，而是基于八字中的十神、五行、神煞、格局等信息，推导一个人可能具有的潜在心理倾向、能力特质与兴趣爱好。请使用"可能倾向于"、"大概率擅长"等概率性语言，避免绝对化断言。

# 输入数据
- 日干：{ri_gan}
- 日支：{ri_zhi}
- 月令：{yue_ling}
- 五行旺相：{wuxing_wangxiang}
- 十神能量占比（由高到低，大运流年影响后）：{format_energy(geju_summary.get('大运流年十神能量分析', {}), shishen_names)}
- 五行能量占比（由高到低，大运流年影响后）：{format_energy(geju_summary.get('大运流年五行能量分析', {}))}
- 主格局：{zhu_geju}
- 四柱神煞：{shensha_str}
- 调候用神：{tiaohou}
- 原局天干关系（冲克合等）：{yuanju_tiangan}
- 原局地支关系（刑冲合害等）：{yuanju_dizhi}
- 原局干支关系（伏吟、天克地冲、截脚、盖头）：{yuanju_ganzhi}
- 岁运天干关系（冲克合等）：{suiyun_tiangan}
- 岁运地支关系（刑冲合害等）：{suiyun_dizhi}
- 岁运干支关系（伏吟、天克地冲、截脚、盖头）：{suiyun_ganzhi}
- 当前流年：{dangqian_liunian}
- 当前大运：{dangqian_dayun}
- 未来五年流年信息：{future_liunian_str}

# 分析步骤（请严格遵守）
1. **格局定性**：先看主格局。这决定了一个人最核心的生存策略与能量发挥方向。
2. **十神能量主导**：依据十神能量占比排序，识别出最强的一到两个十神。解释这些十神所代表的天赋领域。如有特殊格局（如杀印相生、食伤生财、伤官配印等），请重点阐述其带来的独特优势。
3. **五行平衡倾向**：结合五行能量占比与五行旺相，指出五行偏颇或平衡带来的行为偏好
4. **神煞点缀**：选取与天赋直接相关的神煞，说明它们对兴趣的具体修饰，并且点出此人的兴趣点在哪些地方。（例如：华盖→哲学/艺术/孤独创作，桃花→审美/社交/表演）。
5. **动态影响**：参考当前大运、流年及未来五年流年，指出近期可能被激发的天赋方向或兴趣变化。
6. **综合结论**：综合以上，总结该人最可能具备的**3个核心天赋**、**2-3个强烈兴趣爱好**，以及**1个需要警惕的过度倾向**（例如：伤官过旺容易眼高手低，印重容易行动迟缓）。

# 天赋落地应用终极建议
1. 核心天赋适配的职业赛道、细分领域、岗位类型
2. 匹配天赋特质的学习成长路径、高效学习方法
3. 天赋发挥的成长意见（请基于调候用神，并指出调候满足后，第6点综合结论将如何更顺畅释放（例如：食神从空想转向创作，七杀从冲动转向策略）。避免玄学表述，用现代心理与行为语言。）
4. 短板补全的核心方向，平衡能力结构的实操建议（请基于格局成格条件分析）

# 注意事项
请仅基于「地支刑冲破害」给出注意事项：
1. **需要注意的问题**：刑冲破害可能带来的挑战
2. **化解建议**：如何应对和化解这些不利影响

# 输出格式要求
- 使用中文，分段清晰，每段前加小标题（如【格局定性】、【十神天赋】等）。
- 结尾加上一句"命理仅供参考，天赋需要后天努力与机遇触发"。

### 绝对禁止的内容红线（违反任意一条均视为无效输出）
1. 禁止任何宿命论、绝对化表述，包括但不限于"必定成功""天生富贵""命里带灾"等话术
2. 禁止脱离给定的八字参数，进行无依据的凭空分析、编造信息
3. 禁止涉及封建迷信内容，禁止推广算命、改运等违规内容
4. 禁止跑偏到与天赋无关的内容，包括婚姻、子女、健康、纯财运/官运等非天赋分析范畴
5. 禁止使用晦涩难懂的纯命理黑话，所有专业术语必须配套对应的现代语境解释，确保内容通俗易懂

请你严格遵守以上所有规则，基于我提供的完整八字参数，完成精准、科学、落地的天赋分析。
"""
        return prompt

    def _build_simple_prompt(self, bazi_data: Dict, analysis_data: Dict, user_info: Dict) -> str:
        """
        构建简易版AI分析提示词（青年天赋网站内容生成器，3个板块）
        """
        # 复用详细版的数据提取逻辑
        geju_summary = analysis_data.get('格局综合判定', {})
        first_level = analysis_data.get('第一论级_月令与格局', {})
        sixth_level = analysis_data.get('第六论级_大运流年', {})
        fifth_level_aux = analysis_data.get('第五论级_辅助信息', {})
        basic_info = analysis_data.get('基础信息综合分析', {})
        
        def format_energy(data_dict, name_map=None):
            if not data_dict:
                return "暂无数据"
            total = sum(max(v, 0) for v in data_dict.values())
            sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
            lines = []
            for k, v in sorted_items:
                name = name_map.get(k, k) if name_map else k
                pct = (v / total * 100) if total > 0 else 0
                lines.append(f"{name}({k}): {v:.1f}分 (占比{pct:.1f}%)")
            return "、".join(lines)
        
        shishen_names = {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官',
                        '财': '正财', '才': '偏财', '官': '正官', '杀': '七杀',
                        '印': '正印', '枭': '偏印'}
        
        # 神煞
        shensha_data = fifth_level_aux.get('神煞', {})
        all_shensha = []
        for pillar in ['年柱', '月柱', '日柱', '时柱']:
            all_shensha.extend(shensha_data.get(pillar, []))
        shensha_str = "、".join(all_shensha) if all_shensha else "无"
        
        # 基础信息
        ri_gan = basic_info.get('日元', bazi_data.get('day_gan', '未知'))
        ri_zhi = basic_info.get('日支', bazi_data.get('day_zhi', '未知'))
        yue_ling = basic_info.get('月令', first_level.get('月令', '未知'))
        wuxing_wangxiang = basic_info.get('五行旺相', '未知')
        zhu_geju = geju_summary.get('主格局', first_level.get('主要格局', '未知'))
        tiaohou = "、".join(basic_info.get('调候用神', [])) if basic_info.get('调候用神') else "无"
        
        # 关系
        yuanju_tiangan = "、".join(basic_info.get('原局天干关系', [])) or "无"
        yuanju_dizhi = "、".join(basic_info.get('原局地支关系', [])) or "无"
        yuanju_ganzhi = "、".join(basic_info.get('原局干支关系', [])) or "无"
        suiyun_tiangan = "、".join(basic_info.get('岁运天干关系', [])) or "无"
        suiyun_dizhi = "、".join(basic_info.get('岁运地支关系', [])) or "无"
        
        def format_relations(data, keys):
            items = []
            for key in keys:
                val = data.get(key)
                if val and val != '无':
                    items.extend(val) if isinstance(val, list) else items.append(val)
            return "、".join(items) if items else "无"
        
        suiyun_ganzhi = format_relations(sixth_level.get('岁运干支分析', {}), ['伏吟', '天克地冲', '截脚', '盖头'])
        
        dangqian_liunian = basic_info.get('当前流年', '未知')
        dangqian_dayun = basic_info.get('当前大运', '未知')
        future_liunian = basic_info.get('未来五年流年', [])
        future_liunian_str = "、".join(future_liunian) if future_liunian else "暂无数据"
        
        prompt = f"""# 系统指令：青年天赋网站内容生成器

# 用户输入信息
请使用以下用户八字数据进行分析（若某项为空，请基于已有信息合理推断或忽略）：
- 日柱：日干 {ri_gan}；日支 {ri_zhi}；月令 {yue_ling}；五行旺相 {wuxing_wangxiang}
- 十神能量占比（大运流年影响后，由高到低）：{format_energy(geju_summary.get('大运流年十神能量分析', {}), shishen_names)}
- 五行能量占比（大运流年影响后，由高到低）：{format_energy(geju_summary.get('大运流年五行能量分析', {}))}
- 格局：{zhu_geju}
- 四柱神煞：{shensha_str}
- 调候用神：{tiaohou}
- 原局天干（冲克合等）：{yuanju_tiangan}
- 原局地支（刑冲合害等）：{yuanju_dizhi}
- 原局干支（伏吟、天克地冲、岁运并临、截脚盖头）：{yuanju_ganzhi}
- 岁运天干（冲克合等）：{suiyun_tiangan}
- 岁运地支（刑冲合害等）：{suiyun_dizhi}
- 岁运干支（伏吟、天克地冲、岁运并临、截脚盖头）：{suiyun_ganzhi}
- 当前流年：{dangqian_liunian}
- 当前大运：{dangqian_dayun}
- 未来五年流年信息：{future_liunian_str}

你的身份是一位专攻青年潜能开发的导师，擅长把复杂的个人特质解读，翻译成让15-25岁年轻人一看就懂、读完会感到被理解的成长指南。你需要基于给出的「个人先天特质参数」（一套用类比方式描述的能量结构数据），生成一个用于展示在网站上的《核心天赋与成长方向》内容。输出必须严格遵循三个模块的结构，语言要像朋友间推心置腹的对话，充满认同感和鼓励，绝对禁止说教。

## 你必须完成的分析逻辑（内部消化，不体现在最终文字中）
1. **格局定性**：先看主格局。这决定了一个人最核心的生存策略与能量发挥方向。
2. **十神能量主导**：依据十神能量占比排序，识别出最强的一到两个十神。解释这些十神所代表的天赋领域。如有特殊格局（如杀印相生、食伤生财、伤官配印等），请重点阐述其带来的独特优势。
3. **五行平衡倾向**：结合五行能量占比与五行旺相，指出五行偏颇或平衡带来的行为偏好
4. **神煞点缀**：选取与天赋直接相关的神煞，说明它们对兴趣的具体修饰，并且点出此人的兴趣点在哪些地方。（例如：华盖→哲学/艺术/孤独创作，桃花→审美/社交/表演）。
5. **动态影响**：参考当前大运、流年及未来五年流年，指出近期可能被激发的天赋方向或兴趣变化。
6. **综合结论**：综合以上，总结该人最可能具备的**3个核心天赋**、**2-3个强烈兴趣爱好**，以及**1个需要警惕的过度倾向**（例如：伤官过旺容易眼高手低，印重容易行动迟缓）。

## 绝对禁止红线（违反任一条则输出无效）
1. 禁止任何宿命论或绝对化表述，如"注定成功"、"天生富贵命"等。
2. 禁止脱离给出的参数凭空编造分析。
3. 禁止涉及封建迷信内容或推广算命改运。
4. 禁止跑题到婚姻、子女、健康、财运官运等非天赋领域。
5. **最高禁令：最终输出的所有文字，绝对不能出现任何一个命理学原有术语。** 必须全部转化为现代心理学、行为科学、管理学或日常成长语境下的词汇。例如用"深度聚焦动能"代替"印"，用"破局执行力"代替"七杀"，用"社交和审美催化剂"代替"桃花"。整个文本读起来就是一份现代个人成长报告，毫无玄学痕迹。

## 输出格式（必须严格按此结构输出，三个模块缺一不可）

### 核心天赋
这一部分需要结合内在的能量运作模式、主导动能、驱动倾向和兴趣催化剂，总结提炼出该用户**最突出的5个天赋（需要综合以下天赋的组合，一起说明：格局定性1个天赋，TOP3强的十神能量3个天赋，TOP2强的五行能量2个天赋，神煞点缀5个）**。每个天赋都必须包含：
- **一个独特且有共鸣感的标签**（方便年轻人自我认同和在社交中分享，例如「深度破局者」「概念架构师」「情感共振体」）
- **一段1-2句的简要说明**，解释这个天赋会让他自然而然在哪些方面表现突出，带给他什么独特优势。
*此部分内容要浓缩分析逻辑1-4的结论。*

### 天赋场景
针对每一个核心天赋（数量要对的上），用几个小故事或场景让用户代入：
- **天赋领域**不写"你擅长逻辑分析"，而是：
  > "当别人还在讨论表面现象时，你已经在脑中画出了这件事的运行齿轮。就像小时候拆掉闹钟再装回去一样——你不是在破坏，你是在解码世界的规律。"
- **成长建议**不用"你需要加强时间管理"，而是：
  > "你的能量像那种需要预热的光剑，前五分钟可能还在走神，但一旦启动，就能切开整个下午的任务。给自己一个启动仪式感，比如泡一杯特定的茶。"。语气要充满鼓励、欣赏和激励，让读者产生"原来我这些特征是这样宝贵的啊"的顿悟。每个天赋写一个场景段落，共3段，不用再设小标题。

### 成长意见
这一部分提供3条具体、可立刻行动的建议，帮助年轻人把天赋发挥出来，同时避免掉入天赋过度使用的坑。必须涵盖：
- **天赋培养路径**：根据该用户最适配的成长方式（例如"在压力下反而思路清晰"的人适合项目制学习，"发散联想强"的人适合先建知识树再填充细节），给出1条具体的高效学习方法或训练习惯。
- **近期兴趣激活指引**：结合当前及未来数年的能量趋势（分析逻辑5），指出哪个沉睡的兴趣领域可能会被唤醒，可以如何低成本地试探和实践（例如"未来一年你可能会突然迷上用影像记录故事，试着拿手机先拍一个月的每日1分钟vlog"）。
- **平衡与保护机制**：指出那个最需要警惕的"天赋过度使用倾向"（例如思考过度而不行动、创新过多而不专注等），并给出1条实实在在的调节行动建议。这条建议需要基于持续激发天赋所必需的心理平衡点（调候用神），用现代行为语言表述，比如"当内心燥动时，通过游泳让身体先获得释放，你的创意会从乱流变成有序表达"。

## 语言与字数要求
- 全篇轻快易读，不堆砌辞藻。
- 标签、场景和成长意见都要保持风格统一，避免跳脱到专业理论。
- 不要出现"你的天赋是""你的格局是"这种报告式开头，直接进入内容。
- 最终让读者感觉："这说的不就是我吗！原来我不是奇怪，我只是还没用对地方。"
"""
        return prompt

    def _build_deep_explore_prompt(self, bazi_data: Dict, analysis_data: Dict, user_info: Dict) -> str:
        """构建深度探索版 AI 提示词"""
        # 调试：确认 raw_data 是否传入
        has_data = bool(analysis_data)
        print(f"[DEEP] analysis_data keys: {list(analysis_data.keys())[:10] if has_data else 'EMPTY'}")
        
        geju_summary = analysis_data.get('格局综合判定', {})
        first_level = analysis_data.get('第一论级_月令与格局', {})
        sixth_level = analysis_data.get('第六论级_大运流年', {})
        fifth_level_aux = analysis_data.get('第五论级_辅助信息', {})
        basic_info = analysis_data.get('基础信息综合分析', {})
        
        print(f"[DEEP] basic_info keys: {list(basic_info.keys())[:10] if basic_info else 'EMPTY'}")
        print(f"[DEEP] geju_summary keys: {list(geju_summary.keys())[:10] if geju_summary else 'EMPTY'}")

        def format_energy(data_dict, name_map=None):
            if not data_dict:
                return "暂无数据"
            total = sum(max(v, 0) for v in data_dict.values())
            sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
            lines = []
            for k, v in sorted_items:
                name = name_map.get(k, k) if name_map else k
                pct = (v / total * 100) if total > 0 else 0
                lines.append(f"{name}({k}): {v:.1f}分 (占比{pct:.1f}%)")
            return "、".join(lines)

        shishen_names = {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官',
                        '财': '正财', '才': '偏财', '官': '正官', '杀': '七杀',
                        '印': '正印', '枭': '偏印'}

        shensha_data = fifth_level_aux.get('神煞', {})
        all_shensha = []
        for pillar in ['年柱', '月柱', '日柱', '时柱']:
            all_shensha.extend(shensha_data.get(pillar, []))
        shensha_str = "、".join(all_shensha) if all_shensha else "无"

        ri_gan = basic_info.get('日元', bazi_data.get('day_gan', '未知'))
        ri_zhi = basic_info.get('日支', bazi_data.get('day_zhi', '未知'))
        yue_ling = basic_info.get('月令', first_level.get('月令', '未知'))
        wuxing_wangxiang = basic_info.get('五行旺相', '未知')
        zhu_geju = geju_summary.get('主格局', first_level.get('主要格局', '未知'))
        tiaohou = "、".join(basic_info.get('调候用神', [])) if basic_info.get('调候用神') else "无"

        yuanju_tiangan = "、".join(basic_info.get('原局天干关系', [])) or "无"
        yuanju_dizhi = "、".join(basic_info.get('原局地支关系', [])) or "无"
        yuanju_ganzhi = "、".join(basic_info.get('原局干支关系', [])) or "无"
        suiyun_tiangan = "、".join(basic_info.get('岁运天干关系', [])) or "无"
        suiyun_dizhi = "、".join(basic_info.get('岁运地支关系', [])) or "无"

        def format_relations(data, keys):
            items = []
            for key in keys:
                val = data.get(key)
                if val and val != '无':
                    items.extend(val) if isinstance(val, list) else items.append(val)
            return "、".join(items) if items else "无"

        suiyun_ganzhi = format_relations(sixth_level.get('岁运干支分析', {}), ['伏吟', '天克地冲', '截脚', '盖头'])
        dangqian_liunian = basic_info.get('当前流年', '未知')
        dangqian_dayun = basic_info.get('当前大运', '未知')
        future_liunian = basic_info.get('未来五年流年', [])
        future_liunian_str = "、".join(future_liunian) if future_liunian else "暂无数据"

        # 十神列表（格式化）
        shishen_list = format_energy(geju_summary.get('大运流年十神能量分析', {}), shishen_names)
        wuxing_list = format_energy(geju_summary.get('大运流年五行能量分析', {}))

        prompt = f"""# 系统指令：为年轻探索者定制的天赋分析报告

## 【角色设定】
你是一位天赋解读导师。你曾研究传统智慧，但更精通现代心理学与优势教育。你坚信每个人都不是带着"命运"出生的，而是携带着一套独特的"出厂设置"——即天赋潜能。你的任务是与15-25岁的年轻探索者对话，用温暖、平视、充满洞察力的语言，帮助他们看见自己身上那些尚未被完全激活的光亮。你的分析不带任何宿命色彩，而是聚焦于"可能性"、"倾向性"与"发展区"。

## 【输入数据】
# 用户输入信息
请使用以下用户八字数据进行分析（若某项为空，请基于已有信息合理推断或忽略）：
- 日柱：日干 {ri_gan}；日支 {ri_zhi}；月令 {yue_ling}；五行旺相 {wuxing_wangxiang}
- 十神能量占比（大运流年影响后，由高到低）：{shishen_list}
- 五行能量占比（大运流年影响后，由高到低）：{wuxing_list}
- 格局：{zhu_geju}
- 四柱神煞：{shensha_str}
- 调候用神：{tiaohou}
- 原局天干（冲克合等）：{yuanju_tiangan}
- 原局地支（刑冲合害等）：{yuanju_dizhi}
- 原局干支（伏吟、天克地冲、岁运并临、截脚盖头）：{yuanju_ganzhi}
- 岁运天干（冲克合等）：{suiyun_tiangan}
- 岁运地支（刑冲合害等）：{suiyun_dizhi}
- 岁运干支（伏吟、天克地冲、岁运并临、截脚盖头）：{suiyun_ganzhi}
- 当前流年：{dangqian_liunian}
- 当前大运：{dangqian_dayun}
- 未来五年流年信息：{future_liunian_str}

## 【分析步骤与输出格式】
请严格遵循以下模块与语言风格，生成报告。全文使用"你"作为人称，营造对话感。

---

#### **模块一：你的核心天赋图谱**

**(此部分旨在清晰、有共鸣地呈现5个核心天赋)**

1. **【天赋操作系统】**：从你的{zhu_geju}出发，用比喻的方式描绘你最底层的生存策略和能量运作模式。需解释这个格局为何是你的核心优势引擎。

2. **【你的两大心智超能力】**：基于十神列表中最强的两股能量，定义并解读你的心智天赋。为每个天赋赋予一个独特的、便于社交认同的标签。
   - **格式**：`标签名称` + `天赋描述`

3. **【你的行为风格密钥】**：结合五行能量占比和五行旺相，将五行能量转化为现代行为心理学描述。指出能量偏颇带来的行为偏好，而非优缺点。

4. **【你的隐藏兴趣启动器】**：从{shensha_str}中挑选2-3个与兴趣、才华直接相关的神煞，进行场景化解读，点出它们如何修饰你的兴趣点。

5. **【近期能量焦点】**：结合{dangqian_dayun}和{dangqian_liunian}，用鼓励的语调说明当前阶段你哪些天赋最容易被激发，或者对哪些新领域会产生兴趣。

---

#### **模块二：你的专属天赋落地指南**

**(此部分为实操性建议，给出具体路径)**

1. **赛道选择建议**：基于以上5个核心天赋，推荐3-4个适配的职业或专业赛道、细分领域和岗位类型。避免通用的"适合创业"，而是给出如"游戏化教育产品设计"、"文化类短视频内容策划"等具体方向。

2. **属于你的成长加速器**：针对你的心智模式，推荐高效学习方法。例如，对"比肩"能量强的人，可建议"组建学习小组，在竞争与合作中快速成长"；对"印星"能量强的人，则建议"通过建立知识树体系、深度学习经典来建构认知框架"。

3. **成长路上的关键拼图**：基于{tiaohou}，用现代心理语言给出建议。清晰说明调候满足后，如何疏通天赋释放的卡点。

4. **平衡你的天赋飞轮**：基于格局成格条件，洞察可能的能力短板，给出补全建议。

---

#### **模块三：天赋使用说明书——场景化演绎**

**(此部分将天赋用年轻人熟悉的场景进行翻译，注入鼓励和认同感)**

请从以下3-5个年轻人高频场景中选择，用第一/二人称混合视角描绘你的天赋如何发挥：

1. **学习与考试场景**："别人熬夜死记硬背，你可能随便翻翻书，脑海里就能自动生成一张关联知识图谱，甚至能举一反三地把知识编成故事。这是你的'关联思考'天赋在学习中的降维打击。"

2. **社交与团队合作场景**："在小组讨论里，你大概率不是那个最先开口的人，但你一开口就能一针见血地指出逻辑漏洞，或是提出一个整合所有人观点的巧妙方案。你是团队里那个不可或缺的'架构师'。"

3. **独处与自我提升场景**："当你独处时，整个世界都是你的素材库。一部电影、一首歌、甚至路边观察到的小事，都能在你心里引发深刻的体悟，并沉淀为你的独特气质和创作源泉。"

4. **面临选择与迷茫场景**："当别人还在为选择A或B纠结时，你的直觉和收集到的信息，可能已经本能地将你推向那个更具长期价值风险比的选项。要相信你的'内在雷达'，它不是凭空而来，是你思维模式高速计算的产物。"

---

#### **模块四：与天赋共舞的成长提醒**

**(此部分包含综合结论中1个需要警惕的过度倾向，以及基于地支关系的注意事项)**

1. **警惕你的"天赋阴影"**：基于能量最强的十神，点出一个可能过度发展的倾向，并用鼓励的语气化解。

2. **关系中的能量密码**：仅基于{yuanju_dizhi}与{suiyun_dizhi}中的刑冲破害关系，给出对人际互动和个人状态的提醒。严禁使用命理黑话，必须转化为现代场景语言。最后给出化解建议。

---

## 【结语】
最后，请加上一句温暖的总结，如："以上所有，只是你天赋拼图的一角。它描绘的不是一个既定的你，而是一个充满可能性的你。分析仅供参考，天赋的种子需要后天的汗水、机遇的阳光和勇气的土壤，才能真正长成参天大树。你才是自己人生的总设计师。"

## 【绝对禁止红线】
1. 禁止任何宿命论或绝对化表述，如"注定成功"、"天生富贵命"等。
2. 禁止涉及封建迷信内容或推广算命改运。
3. 禁止跑题到婚姻、子女、健康、财运官运等非天赋领域。
4. **最高禁令：最终输出的所有文字，绝对不能出现任何一个命理学原有术语。** 必须全部转化为现代心理学、行为科学、管理学或日常成长语境下的词汇。
"""
        return prompt


# 兼容旧版导入
BaziAnalysisService = BaziAnalysisServiceWeb
