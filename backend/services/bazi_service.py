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
        """构建 DeepSeek 提示词"""
        
        geju_summary = analysis_data.get('格局综合判定', {})
        first_level = analysis_data.get('第一论级_月令与格局', {})
        fifth_level = analysis_data.get('第五论级_定喜忌', {})
        
        # 格式化五行能量
        wuxing = geju_summary.get('五行能量', {})
        wuxing_str = "\n".join([f"  {k}: {v:.1f}" for k, v in sorted(wuxing.items(), key=lambda x: x[1], reverse=True)]) if wuxing else "  暂无数据"
        
        # 格式化十神能量
        shishen = geju_summary.get('十神能量分析', {})
        shishen_str = "\n".join([f"  {k}: {v:.1f}" for k, v in sorted(shishen.items(), key=lambda x: x[1], reverse=True)]) if shishen else "  暂无数据"
        
        gender_str = "男" if user_info.get('gender') == 'male' else "女"
        time_str = f"{bazi_data.get('time_gan', '')}{bazi_data.get('time_zhi', '')}" if bazi_data.get('time_gan') else "未提供"
        
        prompt = f"""# 八字天赋与性格分析报告请求

用户姓名：{user_info.get('name', '匿名')}
性别：{gender_str}

## 【四柱信息】
- 年柱: {bazi_data['year_gan']}{bazi_data['year_zhi']}
- 月柱: {bazi_data['month_gan']}{bazi_data['month_zhi']}
- 日柱: {bazi_data['day_gan']}{bazi_data['day_zhi']} (日主)
- 时柱: {time_str}

## 【第一论级：月令与格局】
- 月令: {first_level.get('月令', '未知')}
- 日主: {first_level.get('日主', bazi_data['day_gan'])}
- 身强身弱: {first_level.get('身强身弱', '未知')}
- 主要格局: {first_level.get('主要格局', geju_summary.get('主格局', '未知'))}

## 【五行能量分析】
{wuxing_str}

## 【十神能量分析】
{shishen_str}

## 【定喜忌】
- 用神: {fifth_level.get('用神', '无')}
- 喜神: {fifth_level.get('喜神', '无')}
- 忌神: {fifth_level.get('忌神', '无')}

## 【分析报告输出要求】

请按照以下结构输出分析报告：

### 一、基础性格分析
结合日主、五行强弱、身强身弱分析核心性格特质。

### 二、天赋与技能分析
1. **核心天赋**：根据十神能量占比，分析最突出的才华领域
2. **适合领域**：结合五行和十神，给出职业/发展方向建议

### 三、成长建议
1. 如何发挥优势
2. 需要注意的短板
3. 个人发展建议

请用专业但易懂的语言撰写，整体控制在1500字左右。
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
