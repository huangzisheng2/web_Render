# -*- coding: utf-8 -*-
"""
PDF 生成桥接模块
为 Android 提供 PDF 生成接口
"""

import json
import os
import sys
from typing import Dict, Optional

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_generator import generate_bazi_report, BaziPDFGenerator


def generate_pdf_from_analysis(
    output_path: str,
    analysis_text: str,
    bazi_json: Optional[str] = None,
    title: str = "八字天赋分析报告"
) -> Dict:
    """
    从分析文本生成 PDF
    
    Args:
        output_path: PDF 输出路径
        analysis_text: AI 分析结果文本
        bazi_json: 四柱信息的 JSON 字符串（可选）
        title: 报告标题
    
    Returns:
        包含生成结果的字典
    """
    try:
        # 解析四柱信息
        bazi_info = {}
        if bazi_json:
            try:
                bazi_data = json.loads(bazi_json)
                bazi_info = {
                    'year': bazi_data.get('year', ''),
                    'month': bazi_data.get('month', ''),
                    'day': bazi_data.get('day', ''),
                    'time': bazi_data.get('time', '')
                }
            except json.JSONDecodeError:
                pass
        
        # 生成 PDF
        result_path = generate_bazi_report(
            output_path=output_path,
            title=title,
            bazi_info=bazi_info,
            analysis_result=analysis_text
        )
        
        return {
            'success': True,
            'pdf_path': result_path,
            'message': 'PDF 生成成功'
        }
        
    except Exception as e:
        return {
            'success': False,
            'pdf_path': None,
            'message': f'PDF 生成失败: {str(e)}'
        }


def generate_pdf_from_json(json_input: str) -> str:
    """
    从 JSON 输入生成 PDF（供外部调用）
    
    Args:
        json_input: JSON 字符串，包含以下字段：
            - output_path: PDF 输出路径（必填）
            - analysis_text: 分析文本（必填）
            - bazi_json: 四柱信息 JSON（可选）
            - title: 报告标题（可选，默认"八字天赋分析报告"）
    
    Returns:
        JSON 字符串，包含生成结果
    """
    try:
        params = json.loads(json_input)
        
        output_path = params.get('output_path')
        analysis_text = params.get('analysis_text')
        bazi_json = params.get('bazi_json')
        title = params.get('title', '八字天赋分析报告')
        
        if not output_path:
            return json.dumps({
                'success': False,
                'message': '缺少输出路径参数: output_path'
            })
        
        if not analysis_text:
            return json.dumps({
                'success': False,
                'message': '缺少分析文本参数: analysis_text'
            })
        
        result = generate_pdf_from_analysis(
            output_path=output_path,
            analysis_text=analysis_text,
            bazi_json=bazi_json,
            title=title
        )
        
        return json.dumps(result, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            'success': False,
            'message': f'JSON 解析错误: {str(e)}'
        })
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'生成失败: {str(e)}'
        })


# 命令行入口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='八字报告 PDF 生成器')
    parser.add_argument('--output', '-o', required=True, help='PDF 输出路径')
    parser.add_argument('--text', '-t', required=True, help='分析文本文件路径或直接文本')
    parser.add_argument('--bazi', '-b', help='四柱信息 JSON 文件路径')
    parser.add_argument('--title', '-T', default='八字天赋分析报告', help='报告标题')
    
    args = parser.parse_args()
    
    # 读取分析文本
    if os.path.exists(args.text):
        with open(args.text, 'r', encoding='utf-8') as f:
            analysis_text = f.read()
    else:
        analysis_text = args.text
    
    # 读取四柱信息
    bazi_json = None
    if args.bazi and os.path.exists(args.bazi):
        with open(args.bazi, 'r', encoding='utf-8') as f:
            bazi_json = f.read()
    
    # 生成 PDF
    result = generate_pdf_from_analysis(
        output_path=args.output,
        analysis_text=analysis_text,
        bazi_json=bazi_json,
        title=args.title
    )
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False))
