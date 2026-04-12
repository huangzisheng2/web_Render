"""
八字分析服务
整合命理模块提供完整分析功能
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 命理模块路径已在 main.py 中添加
from lunar_python import Solar
from city_database import CITY_DATABASE
from true_solar_time import calculate_true_solar_time
from bazi_bridge import analyze_bazi_unified


class BaziAnalysisService:
    """八字分析服务"""
    
    def __init__(self):
        self.city_data = CITY_DATABASE
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "sk-99f76dba24a242d9b6b358365b356d79")
    
    def get_cities(self) -> Dict[str, list]:
        """获取城市列表"""
        cities = {}
        for province, city, _, _ in self.city_data:
            if province not in cities:
                cities[province] = []
            cities[province].append(city)
        return cities
    
    def _get_location(self, province: str, city: str) -> tuple:
        """
        根据省份城市获取经纬度
        
        Returns:
            (longitude, latitude) 或 (None, None)
        """
        try:
            # 遍历城市数据库查找
            for prov, c, lon, lat in self.city_data:
                if prov == province and c == city:
                    return (lon, lat)
            
            # 尝试仅按城市名查找
            for prov, c, lon, lat in self.city_data:
                if c == city:
                    return (lon, lat)
            
            return (None, None)
        except Exception as e:
            print(f"获取城市位置失败: {e}")
            return (None, None)
    
    def _apply_true_solar_time(
        self, 
        year: int, month: int, day: int, 
        hour: int, minute: int,
        longitude: Optional[float]
    ) -> tuple:
        """
        应用真太阳时转换
        
        Returns:
            (adjusted_year, adjusted_month, adjusted_day, adjusted_hour, adjusted_minute)
        """
        if longitude is None:
            # 无经纬度，使用原时间
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
    
    def _convert_to_bazi(
        self, 
        year: int, month: int, day: int, 
        hour: Optional[int] = None, minute: int = 0
    ) -> Dict[str, str]:
        """
        公历转八字
        
        Args:
            hour: None 表示不计算时柱
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
        
        # 计算时柱
        if hour is not None:
            solar_with_time = Solar.fromYmdHms(year, month, day, hour, minute, 0)
            lunar_with_time = solar_with_time.getLunar()
            ba_with_time = lunar_with_time.getEightChar()
            bazi['time_gan'] = ba_with_time.getTimeGan()
            bazi['time_zhi'] = ba_with_time.getTimeZhi()
        
        return bazi
    
    def _call_deepseek(self, bazi_data: Dict, analysis_data: Dict, user_info: Dict) -> str:
        """
        调用 DeepSeek API 生成分析报告
        
        Args:
            bazi_data: 八字数据
            analysis_data: 命理分析数据
            user_info: 用户信息（姓名、性别等）
        
        Returns:
            AI 生成的报告文本
        """
        import urllib.request
        import json
        
        # 构建提示词
        prompt = self._build_deepseek_prompt(bazi_data, analysis_data, user_info)
        
        try:
            req_data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": "你是一位精通中国传统命理学的专家分析师，擅长通过八字分析一个人的天赋和性格特征。请用专业、客观、建设性的语调进行阐述。"
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
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
    
    def _build_deepseek_prompt(
        self, 
        bazi_data: Dict, 
        analysis_data: Dict, 
        user_info: Dict
    ) -> str:
        """构建 DeepSeek 提示词 - 天赋与性格分析专用模板"""
        
        # 提取各级论级数据
        geju_summary = analysis_data.get('格局综合判定', {})
        first_level = analysis_data.get('第一论级_月令与格局', {})
        second_level = analysis_data.get('第二论级_地支关系', {})
        third_level = analysis_data.get('第三论级_天干关系', {})
        fourth_level = analysis_data.get('第四论级_天干与地支的关系', {})
        fifth_level_xiji = analysis_data.get('第五论级_定喜忌', {})
        fifth_level_aux = analysis_data.get('第五论级_辅助信息', {})
        sixth_level = analysis_data.get('第六论级_大运流年', {})
        basic_info = analysis_data.get('基础信息综合分析', {})
        
        gender_str = "男" if user_info.get('gender') == 'male' else "女"
        
        # 格式化五行能量（按占比排序）
        def format_wuxing_energy(wuxing_dict):
            if not wuxing_dict:
                return "  暂无数据"
            total = sum(max(v, 0) for v in wuxing_dict.values())
            sorted_items = sorted(wuxing_dict.items(), key=lambda x: x[1], reverse=True)
            lines = []
            for k, v in sorted_items:
                pct = (v / total * 100) if total > 0 else 0
                lines.append(f"  {k}: {v:.1f}分 (占比{pct:.1f}%)")
            return "\n".join(lines)
        
        # 格式化十神能量（按占比排序）
        def format_shishen_energy(shishen_dict):
            if not shishen_dict:
                return "  暂无数据"
            shishen_names = {
                '比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官',
                '财': '正财', '才': '偏财', '官': '正官', '杀': '七杀',
                '印': '正印', '枭': '偏印'
            }
            total = sum(max(v, 0) for v in shishen_dict.values())
            sorted_items = sorted(shishen_dict.items(), key=lambda x: x[1], reverse=True)
            lines = []
            for k, v in sorted_items:
                full_name = shishen_names.get(k, k)
                pct = (v / total * 100) if total > 0 else 0
                lines.append(f"  {full_name}({k}): {v:.1f}分 (占比{pct:.1f}%)")
            return "\n".join(lines)
        
        # 格式化关系列表
        def format_relations(relations_dict, keys):
            items = []
            for key in keys:
                val = relations_dict.get(key)
                if val and val != '无':
                    if isinstance(val, list):
                        items.extend(val)
                    elif isinstance(val, str):
                        items.append(val)
            return "、".join(items) if items else "无"
        
        # 获取四柱信息
        sizhu = f"年柱{bazi_data.get('year_gan', '')}{bazi_data.get('year_zhi', '')}、"
        sizhu += f"月柱{bazi_data.get('month_gan', '')}{bazi_data.get('month_zhi', '')}、"
        sizhu += f"日柱{bazi_data.get('day_gan', '')}{bazi_data.get('day_zhi', '')}、"
        sizhu += f"时柱{bazi_data.get('time_gan', '')}{bazi_data.get('time_zhi', '')}" if bazi_data.get('time_gan') else "时柱未提供"
        
        # 获取神煞
        shensha_data = fifth_level_aux.get('神煞', {})
        shensha_nian = "、".join(shensha_data.get('年柱', [])) if shensha_data.get('年柱') else "无"
        shensha_yue = "、".join(shensha_data.get('月柱', [])) if shensha_data.get('月柱') else "无"
        shensha_ri = "、".join(shensha_data.get('日柱', [])) if shensha_data.get('日柱') else "无"
        shensha_shi = "、".join(shensha_data.get('时柱', [])) if shensha_data.get('时柱') else "无"
        
        # 获取大运流年
        dayun_info = sixth_level.get('当前大运', {}) if sixth_level else {}
        liunian_info = sixth_level.get('当前流年', {}) if sixth_level else {}
        dayun_ganzhi = dayun_info.get('干支', '未知')
        dayun_age = dayun_info.get('年龄范围', '未知')
        liunian_ganzhi = liunian_info.get('干支', '未知')
        
        # 未来五年流年
        future_liunian = []
        from datetime import datetime
        current_year = datetime.now().year
        for i in range(5):
            year = current_year + i
            future_liunian.append(f"{year}年")
        future_liunian_str = "、".join(future_liunian)
        
        prompt = f"""# 角色
你是一位兼具传统命理逻辑与现代心理学视角的天赋分析师。你的分析不宣扬宿命论，而是基于八字中的十神、五行、神煞、格局等信息，推导一个人可能具有的潜在心理倾向、能力特质与兴趣爱好。请使用"可能倾向于"、"大概率擅长"等概率性语言，避免绝对化断言。

# 输入数据

## 一、命盘基础信息
- 日干（日主）：{bazi_data.get('day_gan', '未知')}
- 日支：{bazi_data.get('day_zhi', '未知')}
- 月令：{first_level.get('月令', bazi_data.get('month_zhi', '未知'))}
- 四柱：{sizhu}

## 二、五行与十神能量分析
### 原局五行能量占比（由高到低）
{format_wuxing_energy(geju_summary.get('五行能量分析', {}))}

### 原局十神能量占比（由高到低）
{format_shishen_energy(geju_summary.get('十神能量分析', {}))}

### 大运流年作用后五行能量占比（由高到低）
{format_wuxing_energy(geju_summary.get('大运流年五行能量分析', {}))}

### 大运流年作用后十神能量占比（由高到低）
{format_shishen_energy(geju_summary.get('大运流年十神能量分析', {}))}

## 三、格局与旺衰
- 主格局：{geju_summary.get('主格局', first_level.get('主要格局', '未知'))}
- 次要格局：{"、".join(geju_summary.get('次要格局', [])) if geju_summary.get('次要格局') else "无"}
- 身强身弱判定：{first_level.get('身强身弱', '未知')}
- 五行旺相状态：{first_level.get('五行旺相', '未知')}

## 四、调候与喜忌
- 调候用神：{"、".join(basic_info.get('调候用神', [])) if basic_info.get('调候用神') else "无"}
- 用神：{"、".join(fifth_level_xiji.get('用神', [])) if fifth_level_xiji.get('用神') else "无"}
- 喜神：{"、".join(fifth_level_xiji.get('喜神', [])) if fifth_level_xiji.get('喜神') else "无"}
- 忌神：{"、".join(fifth_level_xiji.get('忌神', [])) if fifth_level_xiji.get('忌神') else "无"}

## 五、四柱神煞信息
- 年柱神煞：{shensha_nian}
- 月柱神煞：{shensha_yue}
- 日柱神煞：{shensha_ri}
- 时柱神煞：{shensha_shi}

## 六、天干地支作用关系

### 原局天干关系（冲克合等）
{format_relations(third_level, ['天干五合', '天干相冲', '天干相克'])}

### 原局地支关系（刑冲合害等）
{format_relations(second_level, ['三会', '三合', '半合', '六合', '六冲', '三刑', '六破', '六害', '自刑'])}

### 原局干支关系（伏吟、天克地冲、截脚、盖头）
{format_relations(fourth_level, ['伏吟', '天克地冲', '截脚', '盖头'])}

### 岁运天干关系（冲克合等）
{format_relations(sixth_level.get('岁运天干分析', {}) if sixth_level else {}, ['天干五合', '天干相冲', '天干相克'])}

### 岁运地支关系（刑冲合害等）
{format_relations(sixth_level.get('岁运地支分析', {}) if sixth_level else {}, ['六合', '六冲', '三刑', '六害'])}

### 岁运干支关系（伏吟、天克地冲、截脚、盖头）
{format_relations(sixth_level.get('岁运干支分析', {}) if sixth_level else {}, ['伏吟', '天克地冲', '截脚', '盖头'])}

## 七、大运流年信息
- 当前流年：{liunian_ganzhi}
- 当前大运：{dayun_ganzhi}（{dayun_age}岁）
- 未来五年流年信息：{future_liunian_str}

# 分析步骤（请严格遵守）

1. **格局定性**：先看主格局。这决定了一个人最核心的生存策略与能量发挥方向。
2. **十神能量主导**：依据十神能量占比排序，识别出最强的一到两个十神。解释这些十神所代表的天赋领域。如有特殊格局（如杀印相生、食伤生财、伤官配印等），请重点阐述其带来的独特优势。
3. **五行平衡倾向**：结合五行能量占比与五行旺相，指出五行偏颇或平衡带来的行为偏好
4. **神煞点缀**：选取与天赋直接相关的神煞，说明它们对兴趣的具体修饰，并且点出此人的兴趣点在哪些地方。（例如：华盖→哲学/艺术/孤独创作，桃花→审美/社交/表演）。
5. **动态影响**：参考当前大运、流年及未来五年流年，指出近期可能被激发的天赋方向或兴趣变化。
6. **综合结论**：综合以上，总结该人最可能具备的**3个核心天赋**、**2-3个强烈兴趣爱好**，以及**1个需要警惕的过度倾向**（例如：伤官过旺容易眼高手低，印重容易行动迟缓）。

# 天赋落地应用终极建议

## 1. 职业适配建议
- 核心天赋适配的职业赛道、细分领域、岗位类型

## 2. 学习成长路径
- 匹配天赋特质的学习成长路径、高效学习方法

## 3. 天赋发挥的成长意见
- 基于调候用神，指出调候满足后，综合结论将如何更顺畅释放（例如：食神从空想转向创作，七杀从冲动转向策略）。避免玄学表述，用现代心理与行为语言。

## 4. 短板补全建议
- 短板补全的核心方向，平衡能力结构的实操建议（基于格局成格条件分析）

# 注意事项（基于地支刑冲破害）

## 1. 需要注意的问题
- 刑冲破害可能带来的挑战

## 2. 化解建议
- 如何应对和化解这些不利影响

# 输出格式要求

- 使用中文，分段清晰，每段前加小标题（如【格局定性】、【十神天赋】等）。
- 结尾加上一句"命理仅供参考，天赋需要后天努力与机遇触发"。

# 绝对禁止的内容红线（违反任意一条均视为无效输出）

1. 禁止任何宿命论、绝对化表述，包括但不限于"必定成功""天生富贵""命里带灾"等话术
2. 禁止脱离给定的八字参数，进行无依据的凭空分析、编造信息
3. 禁止涉及封建迷信内容，禁止推广算命、改运等违规内容
4. 禁止跑偏到与天赋无关的内容，包括婚姻、子女、健康、纯财运/官运等非天赋分析范畴
5. 禁止使用晦涩难懂的纯命理黑话，所有专业术语必须配套对应的现代语境解释，确保内容通俗易懂

请你严格遵守以上所有规则，基于我提供的完整八字参数，完成精准、科学、落地的天赋分析。
"""
        return prompt
    
    def analyze_basic(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行基础分析流程（不含AI分析）
        
        Args:
            birth_data: {
                "name": str,
                "year": int, "month": int, "day": int,
                "hour": Optional[int], "minute": int,
                "gender": "male" | "female",
                "province": str, "city": str
            }
        
        Returns:
            基础分析结果字典（四柱、六级论级等）
        """
        # 1. 获取地理位置
        longitude, latitude = self._get_location(
            birth_data.get("province", ""),
            birth_data.get("city", "")
        )
        
        # 2. 真太阳时转换
        hour = birth_data.get("hour")
        if hour is not None:
            adj_year, adj_month, adj_day, adj_hour, adj_minute = self._apply_true_solar_time(
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
        bazi_dict = self._convert_to_bazi(adj_year, adj_month, adj_day, adj_hour, adj_minute)
        
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

        # 5. 组装基础结果
        # bazi_bridge返回的数据结构中：
        # - 'analysis' 包含论级数据（第一、二、三、四、五、六论级）
        # - 'complete_data' 包含四柱、大运表、起运信息等
        lunji_data = analysis_result.get('analysis', {})  # 论级数据
        complete_data = analysis_result.get('complete_data', {})  # 完整打印数据
        
        # 合并数据：论级数据优先，同时保留complete_data中的四柱、大运等信息
        # 确保所有论级数据都在raw_data中
        merged_data = {
            **complete_data,  # 基础信息、四柱、大运表等
            **lunji_data,     # 论级数据（会覆盖complete_data中的同名键）
            # 确保以下键存在（即使为空）
            '第一论级_月令与格局': lunji_data.get('第一论级_月令与格局', {}),
            '第二论级_地支关系': lunji_data.get('第二论级_地支关系', {}),
            '第三论级_天干关系': lunji_data.get('第三论级_天干关系', {}),
            '第四论级_天干与地支的关系': lunji_data.get('第四论级_天干与地支的关系', {}),
            '第五论级_定喜忌': lunji_data.get('第五论级_定喜忌', {}),
            '第五论级_辅助信息': lunji_data.get('第五论级_辅助信息', {}),
            '第六论级_大运流年': lunji_data.get('第六论级_大运流年', {}),
            '格局综合判定': lunji_data.get('格局综合判定', {}),
            # 新增综合分析（从complete_data获取，因为print_analysis()在analyze()之后调用）
            '基础信息综合分析': complete_data.get('基础信息综合分析', {}),
            '命盘综合信息分析': complete_data.get('命盘综合信息分析', {}),
        }
        
        geju_summary = lunji_data.get('格局综合判定', {})
        first_level = lunji_data.get('第一论级_月令与格局', {})
        
        # 构建AI分析提示词（供调试使用）
        user_info = {
            "name": birth_data.get("name", "匿名"),
            "gender": "male" if is_male else "female",
        }
        ai_prompt = self._build_deepseek_prompt(bazi_dict, merged_data, user_info)
        
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
            "raw_data": merged_data,  # 原始完整论级数据，供前端显示和AI分析使用
            "ai_prompt": ai_prompt,  # AI分析提示词，供调试使用
            "ai_report": None  # AI分析结果，初始为None
        }
        
        return result
    
    def analyze_ai(self, report_id: str, basic_result: Dict[str, Any]) -> str:
        """
        执行AI天赋分析
        
        Args:
            report_id: 报告ID
            basic_result: 基础分析结果
            
        Returns:
            AI分析报告文本
        """
        bazi_data = basic_result.get("bazi", {})
        analysis_data = basic_result.get("raw_data", {})
        user_info = {
            "name": basic_result.get("user_info", {}).get("name", "匿名"),
            "gender": "male" if basic_result.get("user_info", {}).get("gender") == "男" else "female",
        }
        
        ai_report = self._call_deepseek(bazi_data, analysis_data, user_info)
        return ai_report
    
    def analyze(self, birth_data: Dict[str, Any], skip_ai: bool = False) -> Dict[str, Any]:
        """
        执行完整分析流程（向后兼容）
        
        Args:
            birth_data: 出生信息
            skip_ai: 是否跳过AI分析
        
        Returns:
            完整的分析结果字典
        """
        # 先执行基础分析
        result = self.analyze_basic(birth_data)
        
        # 如果不跳过AI分析，则执行AI分析
        if not skip_ai:
            ai_report = self.analyze_ai(result["report_id"], result)
            result["ai_report"] = ai_report
        
        return result
