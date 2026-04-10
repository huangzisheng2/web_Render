#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字分析报告生成器 - DeepSeek云端模型版本
将五级论级分析结果发送给DeepSeek云端模型，生成天赋与性格分析报告

功能：
1. 使用Holland职业测试模型形式分析职业倾向
2. 使用加德纳多元智能理论模型形式分析天赋类型
3. 综合五级论级分析结果生成详细报告

作者: Claude AI
创建日期: 2026-02-03
版本: 1.0
"""

import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
import os


class BaziDeepSeekAnalyzer:
    """八字分析器 - DeepSeek云端模型版本"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化分析器
        
        参数:
            api_key: DeepSeek API密钥（如果为None，需要后续设置）
        """
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        
        # 五级论级分析结果存储
        self.analysis_result = {}
    
    def load_api_key_from_env(self, env_var: str = "DEEPSEEK_API_KEY") -> bool:
        """
        从环境变量加载API密钥
        
        参数:
            env_var: 环境变量名
        
        返回:
            是否成功加载
        """
        api_key = os.getenv(env_var)
        if api_key:
            self.api_key = api_key
            return True
        return False
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key
    
    def analyze_bazi(self, bazi_dict: Dict[str, str], liunian_year: Optional[int] = None) -> Dict:
        """
        分析八字并生成报告
        
        参数:
            bazi_dict: 八字字典 {'year_gan': '甲', 'year_zhi': '子', ...}
            liunian_year: 流年年份（可选）
        
        返回:
            包含五级论级分析结果的字典
        """
        # 导入格局分析器
        try:
            from bazi_geju_refactored_v5 import GeJuAnalyzerV5
        except ImportError:
            raise ImportError("无法导入bazi_geju_refactored_v5模块")
        
        # 创建分析器并执行分析
        analyzer = GeJuAnalyzerV5(bazi_dict, liunian_year)
        self.analysis_result = analyzer.analyze()
        
        return self.analysis_result
    
    def generate_prompt(self) -> str:
        """
        生成发送给DeepSeek的提示词
        
        返回:
            包含完整五级论级分析结果的提示词
        """
        # 构建提示词
        prompt = """# 八字分析请求

你是一位精通中国传统命理学、Holland职业测试理论、加德纳多元智能理论的专家分析师。

请根据以下八字五级论级分析结果，为用户生成一份详细的天赋与性格分析报告。

## 用户八字信息

### 1. 四柱信息
- 年柱：{year_gan}{year_zhi}
- 月柱：{month_gan}{month_zhi}
- 日柱：{day_gan}{day_zhi}
- 时柱：{time_gan}{time_zhi}
- 日主：{day_gan}

### 2. 主要格局、喜用神、忌神
- 主要格局：{zhu_geju}
- 次要格局：{ciyao_geju}
- 用神：{yong_shen}
- 喜神：{xi_shen}
- 忌神：{ji_shen}

### 3. 十神能量占比（由高到低）
{shishen_nengliang}

### 4. 五行能量占比（由高到低）
{wuxing_nengliang}

### 5. 日主身强弱信息
- 身强弱判定：{shenqiang_panding}
- 得令：{deling}
- 得地：{dedi}
- 得势：{deshi}

### 6. 暗合与刑冲破害
- 合会：{hehui}
- 冲刑破：{chongxingpo}

### 7. 年月日时柱神煞信息
- 年柱神煞：{shensha_nian}
- 月柱神煞：{shensha_yue}
- 日柱神煞：{shensha_ri}
- 时柱神煞：{shensha_shi}

### 8. 大运流年分析（{current_year}年）
- 当前大运：{dayun_ganzhi}（{dayun_age}岁）
- 当前流年：{liunian_ganzhi}

#### 8a. 十神能量占比（大运流年作用后，由高到低）
{shishen_nengliang_dayun}

#### 8b. 五行能量占比（大运流年作用后，由高到低）
{wuxing_nengliang_dayun}

#### 8c. 日主身强弱信息（大运流年作用后）
{shenqiang_dayun}

#### 8d. 暗合与刑冲破害（大运流年作用）
{anhe_dayun}

#### 8e. 大运、流年神煞信息
- 大运神煞：{shensha_dayun}
- 流年神煞：{shensha_liunian}

## 分析要求

请按照以下两种模型形式输出分析报告：

### 一、Holland职业测试模型形式

请根据八字分析结果，分析用户的职业倾向，按照Holland职业兴趣理论的六大类型（RIASEC）进行描述：

1. **R-实际型（Realistic）**
   - 相关特征描述
   - 适合的职业方向
   - 八字分析依据

2. **I-研究型（Investigative）**
   - 相关特征描述
   - 适合的职业方向
   - 八字分析依据

3. **A-艺术型（Artistic）**
   - 相关特征描述
   - 适合的职业方向
   - 八字分析依据

4. **S-社会型（Social）**
   - 相关特征描述
   - 适合的职业方向
   - 八字分析依据

5. **E-企业型（Enterprising）**
   - 相关特征描述
   - 适合的职业方向
   - 八字分析依据

6. **C-常规型（Conventional）**
   - 相关特征描述
   - 适合的职业方向
   - 八字分析依据

最后给出用户的职业代码（3字母组合，如RIA、AES等）和最佳职业建议。

### 二、加德纳多元智能理论模型形式

请根据八字分析结果，分析用户的多重智能优势，按照加德纳八大智能理论进行描述：

1. **语言智能（Linguistic Intelligence）**
   - 相关特征描述
   - 优势领域
   - 八字分析依据

2. **逻辑-数学智能（Logical-Mathematical Intelligence）**
   - 相关特征描述
   - 优势领域
   - 八字分析依据

3. **空间智能（Spatial Intelligence）**
   - 相关特征描述
   - 优势领域
   - 八字分析依据

4. **身体-动觉智能（Bodily-Kinesthetic Intelligence）**
   - 相关特征描述
   - 优势领域
   - 八字分析依据

5. **音乐智能（Musical Intelligence）**
   - 相关特征描述
   - 优势领域
   - 八字分析依据

6. **人际智能（Interpersonal Intelligence）**
   - 相关特征描述
   - 优势领域
   - 八字分析依据

7. **内省智能（Intrapersonal Intelligence）**
   - 相关特征描述
   - 优势领域
   - 八字分析依据

8. **自然观察智能（Naturalist Intelligence）**
   - 相关特征描述
   - 优势领域
   - 八字分析依据

最后给出用户的主要智能类型、次要智能类型以及发展建议。

### 三、综合性格分析

结合Holland职业测试和加德纳多元智能的分析结果，给出：

1. **核心性格特质**
   - 描述用户的核心性格特征
   - 分析性格的优势与挑战
   - 八字格局对性格的影响

2. **天赋优势**
   - 列出用户的主要天赋优势
   - 分析如何发挥这些优势

3. **成长建议**
   - 基于八字分析给出成长建议
   - 如何利用大运流年的机遇
   - 如何化解潜在挑战

4. **职业发展路径**
   - 推荐的职业发展方向
   - 不同阶段的发展重点
   - 需要培养的能力

请以专业、客观、建设性的语调进行撰写，确保分析结果与八字五级论级分析结果高度一致。
""".format(
            # 1. 四柱信息
            year_gan=self.analysis_result.get('第一论级_月令与格局', {}).get('八字', {}).get('年柱', {}).get('天干', '') if '八字' in self.analysis_result else self.gans[0] if hasattr(self, 'gans') else '',
            year_zhi=self.analysis_result.get('第一论级_月令与格局', {}).get('八字', {}).get('年柱', {}).get('地支', '') if '八字' in self.analysis_result else self.zhis[0] if hasattr(self, 'zhis') else '',
            month_gan=self.analysis_result.get('第一论级_月令与格局', {}).get('八字', {}).get('月柱', {}).get('天干', '') if '八字' in self.analysis_result else self.gans[1] if hasattr(self, 'gans') else '',
            month_zhi=self.analysis_result.get('第一论级_月令与格局', {}).get('八字', {}).get('月柱', {}).get('地支', '') if '八字' in self.analysis_result else self.zhis[1] if hasattr(self, 'zhis') else '',
            day_gan=self.analysis_result.get('第一论级_月令与格局', {}).get('八字', {}).get('日柱', {}).get('天干', '') if '八字' in self.analysis_result else self.gans[2] if hasattr(self, 'gans') else '',
            day_zhi=self.analysis_result.get('第一论级_月令与格局', {}).get('八字', {}).get('日柱', {}).get('地支', '') if '八字' in self.analysis_result else self.zhis[2] if hasattr(self, 'zhis') else '',
            time_gan=self.analysis_result.get('第一论级_月令与格局', {}).get('八字', {}).get('时柱', {}).get('天干', '') if '八字' in self.analysis_result else self.gans[3] if hasattr(self, 'gans') else '',
            time_zhi=self.analysis_result.get('第一论级_月令与格局', {}).get('八字', {}).get('时柱', {}).get('地支', '') if '八字' in self.analysis_result else self.zhis[3] if hasattr(self, 'zhis') else '',
            # 2. 主要格局、喜用神、忌神
            zhu_geju=self.analysis_result.get('格局综合判定', {}).get('主格局', ''),
            ciyao_geju=', '.join(self.analysis_result.get('格局综合判定', {}).get('次要格局', [])) if self.analysis_result.get('格局综合判定', {}).get('次要格局') else '无',
            yong_shen=', '.join(self.analysis_result.get('第五论级_定喜忌', {}).get('用神', [])) if self.analysis_result.get('第五论级_定喜忌', {}).get('用神') else '无',
            xi_shen=', '.join(self.analysis_result.get('第五论级_定喜忌', {}).get('喜神', [])) if self.analysis_result.get('第五论级_定喜忌', {}).get('喜神') else '无',
            ji_shen=', '.join(self.analysis_result.get('第五论级_定喜忌', {}).get('忌神', [])) if self.analysis_result.get('第五论级_定喜忌', {}).get('忌神') else '无',
            # 3. 十神能量占比
            shishen_nengliang=self._format_shishen_energy(self.analysis_result.get('格局综合判定', {}).get('十神能量分析', {})),
            # 4. 五行能量占比
            wuxing_nengliang=self._format_wuxing_energy(self.analysis_result.get('格局综合判定', {}).get('五行能量分析', {})),
            # 5. 日主身强弱信息
            shenqiang_panding=self.analysis_result.get('第一论级_月令与格局', {}).get('身强身弱', '未知'),
            deling='是' if self.analysis_result.get('第一论级_月令与格局', {}).get('身强详情', {}).get('得令') else '否',
            dedi='是' if self.analysis_result.get('第一论级_月令与格局', {}).get('身强详情', {}).get('得地') else '否',
            deshi='是' if self.analysis_result.get('第一论级_月令与格局', {}).get('身强详情', {}).get('得势') else '否',
            # 6. 暗合与刑冲破害
            hehui=self._format_hehui(self.analysis_result.get('第二论级_地支关系', {})),
            chongxingpo=self._format_chongxingpo(self.analysis_result.get('第二论级_地支关系', {})),
            # 7. 年月日时柱神煞信息
            shensha_nian=', '.join(self.analysis_result.get('第五论级_辅助信息', {}).get('神煞', {}).get('年柱', [])) if self.analysis_result.get('第五论级_辅助信息', {}).get('神煞', {}).get('年柱') else '无',
            shensha_yue=', '.join(self.analysis_result.get('第五论级_辅助信息', {}).get('神煞', {}).get('月柱', [])) if self.analysis_result.get('第五论级_辅助信息', {}).get('神煞', {}).get('月柱') else '无',
            shensha_ri=', '.join(self.analysis_result.get('第五论级_辅助信息', {}).get('神煞', {}).get('日柱', [])) if self.analysis_result.get('第五论级_辅助信息', {}).get('神煞', {}).get('日柱') else '无',
            shensha_shi=', '.join(self.analysis_result.get('第五论级_辅助信息', {}).get('神煞', {}).get('时柱', [])) if self.analysis_result.get('第五论级_辅助信息', {}).get('神煞', {}).get('时柱') else '无',
            # 8. 大运流年分析
            current_year=str(datetime.now().year),
            dayun_ganzhi=self.analysis_result.get('第五论级_大运流年', {}).get('大运干支', ''),
            dayun_age=self.analysis_result.get('第五论级_大运流年', {}).get('大运年龄范围', ''),
            liunian_ganzhi=self.analysis_result.get('第五论级_大运流年', {}).get('流年干支', ''),
            # 8a. 十神能量占比（大运流年作用后）
            shishen_nengliang_dayun=self._format_shishen_energy(self.analysis_result.get('格局综合判定', {}).get('大运流年十神能量分析', {})),
            # 8b. 五行能量占比（大运流年作用后）
            wuxing_nengliang_dayun=self._format_wuxing_energy(self.analysis_result.get('格局综合判定', {}).get('大运流年五行能量分析', {})),
            # 8c. 日主身强弱信息（大运流年作用后）
            shenqiang_dayun='已考虑大运流年对原局的影响' if self.analysis_result.get('第六论级') else self.analysis_result.get('第一论级_月令与格局', {}).get('身强身弱', '未知') + '（与原局相同）',
            # 8d. 暗合与刑冲破害（大运流年作用）
            anhe_dayun=self._format_dayun_impact(self.analysis_result.get('第六论级', {}).get('岁运地支分析', {})),
            # 8e. 大运、流年神煞信息
            shensha_dayun=', '.join(self.analysis_result.get('第五论级_大运流年', {}).get('大运神煞', [])) if self.analysis_result.get('第五论级_大运流年', {}).get('大运神煞') else '无',
            shensha_liunian=', '.join(self.analysis_result.get('第五论级_大运流年', {}).get('流年神煞', [])) if self.analysis_result.get('第五论级_大运流年', {}).get('流年神煞') else '无'
        )
        
        return prompt
    
    def call_deepseek_api(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """
        调用DeepSeek API生成报告
        
        参数:
            prompt: 提示词
            temperature: 温度参数（控制创造性，0-1之间）
            max_tokens: 最大生成token数
        
        返回:
            DeepSeek返回的分析报告
        """
        if not self.api_key:
            raise ValueError("未设置API密钥，请先调用set_api_key()方法")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位精通中国传统命理学、Holland职业测试理论、加德纳多元智能理论的专家分析师。请根据提供的八字五级论级分析结果，生成详细的天赋与性格分析报告。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"调用DeepSeek API失败: {str(e)}")
        except KeyError as e:
            raise Exception(f"解析API响应失败: {str(e)}")
    
    def generate_report(self, bazi_dict: Dict[str, str], 
                      liunian_year: Optional[int] = None,
                      api_key: Optional[str] = None,
                      save_to_file: bool = True) -> str:
        """
        生成完整的天赋与性格分析报告
        
        参数:
            bazi_dict: 八字字典
            liunian_year: 流年年份（可选）
            api_key: DeepSeek API密钥
            save_to_file: 是否保存到文件
        
        返回:
            生成的分析报告内容
        """
        # 设置API密钥
        if api_key:
            self.set_api_key(api_key)
        
        # 分析八字
        print("正在分析八字...")
        self.analyze_bazi(bazi_dict, liunian_year)
        
        # 生成提示词
        print("正在生成分析提示词...")
        prompt = self.generate_prompt()
        
        # 调用DeepSeek API
        print("正在调用DeepSeek生成报告...")
        try:
            report = self.call_deepseek_api(prompt)
        except Exception as e:
            print(f"调用DeepSeek失败: {str(e)}")
            print("提示：请检查API密钥是否正确，或网络连接是否正常")
            return ""
        
        # 保存到文件
        if save_to_file:
            filename = f"八字分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"八字天赋与性格分析报告\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"## 八字信息\n\n")
                f.write(f"- 年柱：{bazi_dict['year_gan']}{bazi_dict['year_zhi']}\n")
                f.write(f"- 月柱：{bazi_dict['month_gan']}{bazi_dict['month_zhi']}\n")
                f.write(f"- 日柱：{bazi_dict['day_gan']}{bazi_dict['day_zhi']}\n")
                f.write(f"- 时柱：{bazi_dict['time_gan']}{bazi_dict['time_zhi']}\n")
                if liunian_year:
                    f.write(f"- 分析流年：{liunian_year}年\n")
                f.write(f"\n{report}")
            
            print(f"\n报告已保存到: {filename}")
        
        return report
    
    def print_report(self, report: str):
        """打印报告"""
        print("\n" + "=" * 80)
        print("八字天赋与性格分析报告")
        print("=" * 80 + "\n")
        print(report)
        print("\n" + "=" * 80)
    
    def _format_shishen_energy(self, shishen_scores: Dict) -> str:
        """格式化十神能量占比"""
        if not shishen_scores:
            return "  无数据"
        
        shishen_full_names = {
            '比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官',
            '财': '正财', '才': '偏财', '官': '正官', '杀': '七杀',
            '印': '正印', '枭': '偏印'
        }
        
        # 按能量排序
        sorted_shishen = sorted(shishen_scores.items(), key=lambda x: x[1], reverse=True)
        total_score = sum(max(score, 0) for _, score in sorted_shishen)
        
        lines = []
        for shishen, score in sorted_shishen:
            full_name = shishen_full_names.get(shishen, shishen)
            percentage = (score / total_score * 100) if total_score > 0 else 0
            lines.append(f"  {full_name}({shishen}): {score:.1f}分 (占比{percentage:.1f}%)")
        
        return '\n'.join(lines)
    
    def _format_wuxing_energy(self, wuxing_scores: Dict) -> str:
        """格式化五行能量占比"""
        if not wuxing_scores:
            return "  无数据"
        
        # 按能量排序
        sorted_wuxing = sorted(wuxing_scores.items(), key=lambda x: x[1], reverse=True)
        total_score = sum(max(score, 0) for _, score in sorted_wuxing)
        
        lines = []
        for wuxing, score in sorted_wuxing:
            percentage = (score / total_score * 100) if total_score > 0 else 0
            lines.append(f"  {wuxing}: {score:.1f}分 (占比{percentage:.1f}%)")
        
        return '\n'.join(lines)
    
    def _format_hehui(self, zhi_relations: Dict) -> str:
        """格式化合会信息"""
        if not zhi_relations:
            return "无"
        
        hehui_items = []
        if zhi_relations.get('三会'): hehui_items.extend(zhi_relations['三会'])
        if zhi_relations.get('三合'): hehui_items.extend(zhi_relations['三合'])
        if zhi_relations.get('半合'): hehui_items.extend(zhi_relations['半合'])
        if zhi_relations.get('拱合'): hehui_items.extend(zhi_relations['拱合'])
        if zhi_relations.get('六合'): hehui_items.extend(zhi_relations['六合'])
        if zhi_relations.get('半会'): hehui_items.extend(zhi_relations['半会'])
        if zhi_relations.get('拱会'): hehui_items.extend(zhi_relations['拱会'])
        
        return '; '.join(hehui_items) if hehui_items else "无"
    
    def _format_chongxingpo(self, zhi_relations: Dict) -> str:
        """格式化冲刑破信息"""
        if not zhi_relations:
            return "无"
        
        chongxing_items = []
        if zhi_relations.get('六冲'): chongxing_items.extend(zhi_relations['六冲'])
        if zhi_relations.get('三刑'): chongxing_items.extend(zhi_relations['三刑'])
        if zhi_relations.get('六破'): chongxing_items.extend(zhi_relations['六破'])
        
        return '; '.join(chongxing_items) if chongxing_items else "无"
    
    def _format_dayun_impact(self, zhi_impact: Dict) -> str:
        """格式化大运流年影响"""
        if not zhi_impact:
            return "  无特殊作用"
        
        lines = []
        has_relation = False
        for pillar, impacts in zhi_impact.items():
            if impacts:
                for impact in impacts:
                    if isinstance(impact, dict):
                        impact_type = impact.get('类型', '')
                        desc = impact.get('描述', '')
                        lines.append(f"  {pillar}: {impact_type} - {desc}")
                        has_relation = True
                    else:
                        lines.append(f"  {pillar}: {impact}")
                        has_relation = True
        
        if not has_relation:
            return "  大运流年与原局无明显刑冲克害"
        
        return '\n'.join(lines)


def parse_input(input_str: str):
    """
    解析用户输入的日期时间字符串
    
    支持格式:
    - 年月日时分开: 1990 5 15 10
    - 年月日: 1990 5 15
    - 带分隔符: 1990-05-15 10, 1990/5/15, 1990年5月15日
    - 紧凑格式: 1990051510
    - 八字干支: 甲子 乙丑 丙寅 丁卯
    
    返回:
        (year, month, day, hour) 或 bazi_dict 如果解析失败返回 None
    """
    import re
    
    # 移除多余空格
    input_str = input_str.strip()
    if not input_str:
        return None
    
    # 尝试匹配带分隔符的格式
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
    
    # 尝试匹配空格分隔的格式
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
    
    # 尝试匹配紧凑格式
    if input_str.isdigit() and len(input_str) >= 8:
        year = int(input_str[:4])
        month = int(input_str[4:6])
        day = int(input_str[6:8])
        hour = int(input_str[8:10]) if len(input_str) >= 10 else None
        return ('date', year, month, day, hour)
    
    # 尝试匹配八字干支格式
    # 检查是否包含天干地支字符
    gans = "甲乙丙丁戊己庚辛壬癸"
    zhis = "子丑寅卯辰巳午未申酉戌亥"
    
    # 移除空格后检查
    clean_str = input_str.replace(' ', '')
    if len(clean_str) >= 8:
        # 检查是否都是干支字符
        is_ganzhi = all(c in gans + zhis for c in clean_str)
        if is_ganzhi:
            # 解析为八字字典
            bazi_dict = {
                'year_gan': clean_str[0],
                'year_zhi': clean_str[1],
                'month_gan': clean_str[2],
                'month_zhi': clean_str[3],
                'day_gan': clean_str[4],
                'day_zhi': clean_str[5],
            }
            if len(clean_str) >= 8:
                bazi_dict['time_gan'] = clean_str[6]
                bazi_dict['time_zhi'] = clean_str[7]
            else:
                bazi_dict['time_gan'] = ''
                bazi_dict['time_zhi'] = ''
            return ('bazi', bazi_dict)
    
    # 空格分隔的干支格式: 甲子 乙丑 丙寅 丁卯
    parts = input_str.split()
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
                'time_zhi': parts[3][1],
            }
            return ('bazi', bazi_dict)
    
    return None


def print_bazi_basic_info(bazi_dict: Dict, is_male: bool):
    """打印八字基础信息"""
    from bazi_analyzer import BaziAnalyzer
    
    print("\n" + "=" * 80)
    print("正在分析八字基础信息...")
    print("=" * 80)
    
    analyzer = BaziAnalyzer()
    result = analyzer.analyze_from_ganzhi(bazi_dict, is_male)
    analyzer.print_analysis(result)


def main():
    """主函数：交互式界面"""
    print("=" * 80)
    print("八字命理分析系统".center(80))
    print("=" * 80)
    print("\n支持输入格式:")
    print("  1. 年月日时: 1990 5 15 10")
    print("  2. 年月日: 1990 5 15 (无时柱)")
    print("  3. 带分隔符: 1990-05-15 10, 1990年5月15日")
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
        return
    
    # 获取性别
    print("\n请输入性别：")
    gender_input = input("1-男, 0-女 (默认1): ").strip()
    is_male = gender_input != '0'
    gender_str = "男" if is_male else "女"
    print(f"性别: {gender_str}")
    
    # 处理输入数据
    if parsed[0] == 'date':
        # 日期格式，需要转换为八字
        _, year, month, day, hour = parsed
        from lunar_python import Solar
        
        solar = Solar.fromYmdHms(year, month, day, hour if hour else 12, 0, 0)
        lunar = solar.getLunar()
        ba = lunar.getEightChar()
        
        bazi_dict = {
            'year_gan': ba.getYearGan(),
            'year_zhi': ba.getYearZhi(),
            'month_gan': ba.getMonthGan(),
            'month_zhi': ba.getMonthZhi(),
            'day_gan': ba.getDayGan(),
            'day_zhi': ba.getDayZhi(),
            'time_gan': ba.getTimeGan(),
            'time_zhi': ba.getTimeZhi()
        }
        
        print(f"\n根据出生日期计算得到八字：")
        print(f"  年柱: {bazi_dict['year_gan']}{bazi_dict['year_zhi']}")
        print(f"  月柱: {bazi_dict['month_gan']}{bazi_dict['month_zhi']}")
        print(f"  日柱: {bazi_dict['day_gan']}{bazi_dict['day_zhi']}")
        print(f"  时柱: {bazi_dict['time_gan']}{bazi_dict['time_zhi']}")
        
        if not hour:
            bazi_dict['time_gan'] = ''
            bazi_dict['time_zhi'] = ''
            print("  (无时柱信息)")
    else:
        # 干支格式
        _, bazi_dict = parsed
        print(f"\n输入的八字信息：")
        print(f"  年柱: {bazi_dict['year_gan']}{bazi_dict['year_zhi']}")
        print(f"  月柱: {bazi_dict['month_gan']}{bazi_dict['month_zhi']}")
        print(f"  日柱: {bazi_dict['day_gan']}{bazi_dict['day_zhi']}")
        has_time = bool(bazi_dict.get('time_gan'))
        if has_time:
            print(f"  时柱: {bazi_dict['time_gan']}{bazi_dict['time_zhi']}")
        else:
            print("  时柱: 无")
    
    # 提供选项
    print("\n" + "=" * 80)
    print("请选择操作：")
    print("  1. 结合DeepSeek生成详细分析报告")
    print("  2. 打印八字基础信息")
    print("=" * 80)
    
    while True:
        choice = input("\n请输入选项 (1/2): ").strip()
        if choice in ['1', '2']:
            break
        print("输入错误，请输入 1 或 2")
    
    if choice == '1':
        # 选项1：生成DeepSeek报告
        print("\n您选择了：生成DeepSeek详细分析报告")
        
        # 创建分析器
        analyzer = BaziDeepSeekAnalyzer()
        
        # 获取API密钥
        api_key = input("\n请输入DeepSeek API密钥: ").strip()
        if not api_key:
            print("错误：API密钥不能为空")
            return
        analyzer.set_api_key(api_key)
        
        # 生成报告
        try:
            print("\n正在生成报告，请稍候...")
            report = analyzer.generate_report(bazi_dict, liunian_year=datetime.now().year)
            if report:
                analyzer.print_report(report)
        except Exception as e:
            print(f"\n错误: {str(e)}")
            print("\n请确保：")
            print("1. API密钥正确有效")
            print("2. 网络连接正常")
            print("3. bazi_geju_refactored_v5.py文件在同一目录")
    
    else:
        # 选项2：打印基础信息
        print("\n您选择了：打印八字基础信息")
        try:
            print_bazi_basic_info(bazi_dict, is_male)
        except Exception as e:
            print(f"\n错误: {str(e)}")
            print("\n请确保：")
            print("1. bazi_analyzer.py文件在同一目录")
            print("2. 相关依赖模块已安装")


if __name__ == '__main__':
    main()
