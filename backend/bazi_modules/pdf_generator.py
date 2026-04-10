# -*- coding: utf-8 -*-
"""
八字报告 PDF 生成器
基于 reportlab 实现专业 PDF 排版
遵循 typeset skill 的排版原则
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, ListFlowable, ListItem
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


@dataclass
class TypographyConfig:
    """排版配置 - 遵循 typeset skill 原则"""
    # 字体大小层次（5级：caption, secondary, body, subheading, heading）
    title_size: int = 24           # 主标题
    heading_size: int = 14         # 章节标题
    subheading_size: int = 12      # 子标题
    body_size: int = 10            # 正文
    caption_size: int = 8          # 注释/页眉页脚
    
    # 行高
    line_height_title: float = 1.2
    line_height_heading: float = 1.3
    line_height_body: float = 1.6
    
    # 颜色
    color_primary: colors.Color = colors.HexColor('#B71C1C')  # 主色调
    color_heading: colors.Color = colors.HexColor('#B71C1C')  # 标题色
    color_body: colors.Color = colors.HexColor('#333333')     # 正文色
    color_secondary: colors.Color = colors.HexColor('#666666')  # 辅助色
    color_light: colors.Color = colors.HexColor('#999999')    # 浅色
    
    # 间距
    space_before_heading: int = 16
    space_after_heading: int = 8
    space_before_paragraph: int = 6
    space_after_paragraph: int = 6


class BaziPDFGenerator:
    """八字报告 PDF 生成器"""
    
    def __init__(self, output_path: str, page_size=A5, typography: Optional[TypographyConfig] = None):
        """
        初始化 PDF 生成器
        
        Args:
            output_path: PDF 输出路径
            page_size: 页面尺寸，默认 A5（适合手机阅读）
            typography: 排版配置，使用默认配置
        """
        self.output_path = output_path
        self.page_size = page_size
        self.typo = typography or TypographyConfig()
        
        # 注册中文字体
        self._register_fonts()
        
        # 创建文档
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=20*mm,
            bottomMargin=15*mm
        )
        
        # 初始化样式
        self.styles = self._create_styles()
        
        # 内容容器
        self.story = []
    
    def _register_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册系统中文字体
            font_paths = [
                # Windows 字体
                'C:/Windows/Fonts/simhei.ttf',  # 黑体
                'C:/Windows/Fonts/simsun.ttc',  # 宋体
                # macOS 字体
                '/System/Library/Fonts/PingFang.ttc',
                '/Library/Fonts/Arial Unicode.ttf',
                # Linux 字体
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Chinese', font_path))
                        self.font_name = 'Chinese'
                        break
                    except:
                        continue
            else:
                # 如果没有中文字体，使用默认字体
                self.font_name = 'Helvetica'
                
        except Exception as e:
            print(f"字体注册失败: {e}")
            self.font_name = 'Helvetica'
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """创建段落样式 - 遵循 typeset skill 原则"""
        styles = {}
        
        # 主标题样式
        styles['Title'] = ParagraphStyle(
            'Title',
            fontName=self.font_name,
            fontSize=self.typo.title_size,
            textColor=self.typo.color_primary,
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=self.typo.title_size * self.typo.line_height_title,
            wordWrap='CJK'
        )
        
        # 副标题样式（四柱信息）
        styles['Subtitle'] = ParagraphStyle(
            'Subtitle',
            fontName=self.font_name,
            fontSize=11,
            textColor=self.typo.color_secondary,
            alignment=TA_CENTER,
            spaceAfter=6,
            leading=14,
            wordWrap='CJK'
        )
        
        # 章节标题样式
        styles['Heading1'] = ParagraphStyle(
            'Heading1',
            fontName=self.font_name,
            fontSize=self.typo.heading_size,
            textColor=self.typo.color_heading,
            spaceBefore=self.typo.space_before_heading,
            spaceAfter=self.typo.space_after_heading,
            leading=self.typo.heading_size * self.typo.line_height_heading,
            wordWrap='CJK'
        )
        
        # 子标题样式
        styles['Heading2'] = ParagraphStyle(
            'Heading2',
            fontName=self.font_name,
            fontSize=self.typo.subheading_size,
            textColor=self.typo.color_body,
            spaceBefore=10,
            spaceAfter=6,
            leading=self.typo.subheading_size * 1.4,
            wordWrap='CJK'
        )
        
        # 正文样式
        styles['BodyText'] = ParagraphStyle(
            'BodyText',
            fontName=self.font_name,
            fontSize=self.typo.body_size,
            textColor=self.typo.color_body,
            spaceBefore=self.typo.space_before_paragraph,
            spaceAfter=self.typo.space_after_paragraph,
            leading=self.typo.body_size * self.typo.line_height_body,
            alignment=TA_JUSTIFY,
            firstLineIndent=20,  # 首行缩进
            wordWrap='CJK'
        )
        
        # 列表项样式
        styles['ListItem'] = ParagraphStyle(
            'ListItem',
            fontName=self.font_name,
            fontSize=self.typo.body_size,
            textColor=self.typo.color_body,
            spaceBefore=3,
            spaceAfter=3,
            leading=self.typo.body_size * self.typo.line_height_body,
            leftIndent=20,
            wordWrap='CJK'
        )
        
        # 加粗文本样式
        styles['BoldText'] = ParagraphStyle(
            'BoldText',
            fontName=self.font_name,
            fontSize=self.typo.body_size,
            textColor=self.typo.color_body,
            spaceBefore=6,
            spaceAfter=6,
            leading=self.typo.body_size * self.typo.line_height_body,
            wordWrap='CJK'
        )
        
        # 页眉样式
        styles['Header'] = ParagraphStyle(
            'Header',
            fontName=self.font_name,
            fontSize=self.typo.caption_size,
            textColor=self.typo.color_light,
            alignment=TA_LEFT,
            leading=10,
            wordWrap='CJK'
        )
        
        return styles
    
    def add_title(self, title: str, subtitle: Optional[str] = None):
        """添加报告标题"""
        self.story.append(Paragraph(title, self.styles['Title']))
        
        if subtitle:
            self.story.append(Paragraph(subtitle, self.styles['Subtitle']))
        
        # 添加分隔线
        self.story.append(Spacer(1, 10))
    
    def add_section(self, title: str, content: str):
        """添加章节"""
        # 章节标题
        self.story.append(Paragraph(title, self.styles['Heading1']))
        
        # 处理内容
        self._process_content(content)
    
    def _process_content(self, content: str):
        """处理文本内容，识别 Markdown 格式"""
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # 空行
                self.story.append(Spacer(1, 6))
                continue
            
            # 处理 Markdown 格式
            if line.startswith('### ') or line.startswith('## '):
                # 章节标题
                text = line.replace('### ', '').replace('## ', '')
                self.story.append(Paragraph(text, self.styles['Heading1']))
                
            elif line.startswith('#### '):
                # 子标题
                text = line.replace('#### ', '')
                self.story.append(Paragraph(text, self.styles['Heading2']))
                
            elif line.startswith('**') and line.endswith('**'):
                # 加粗文本
                text = line.strip('*')
                self.story.append(Paragraph(f"<b>{text}</b>", self.styles['BoldText']))
                
            elif line.startswith('- ') or line.startswith('• '):
                # 列表项
                text = line[2:]
                self.story.append(Paragraph(f"• {text}", self.styles['ListItem']))
                
            elif line[0].isdigit() and '. ' in line[:4]:
                # 数字列表
                self.story.append(Paragraph(line, self.styles['ListItem']))
                
            else:
                # 普通段落
                self.story.append(Paragraph(line, self.styles['BodyText']))
    
    def add_bazi_info(self, bazi_data: Dict[str, str]):
        """添加四柱信息表格"""
        # 创建表格数据
        data = [
            ['年柱', '月柱', '日柱', '时柱'],
            [
                bazi_data.get('year', ''),
                bazi_data.get('month', ''),
                bazi_data.get('day', ''),
                bazi_data.get('time', '')
            ]
        ]
        
        # 创建表格
        table = Table(data, colWidths=[30*mm]*4)
        
        # 设置表格样式
        table.setStyle(TableStyle([
            # 表头样式
            ('BACKGROUND', (0, 0), (-1, 0), self.typo.color_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # 数据行样式
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FFF8E1')),
            ('TEXTCOLOR', (0, 1), (-1, 1), self.typo.color_body),
            ('FONTNAME', (0, 1), (-1, 1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, 1), 11),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 10),
            
            # 边框
            ('GRID', (0, 0), (-1, -1), 0.5, self.typo.color_light),
            ('BOX', (0, 0), (-1, -1), 1, self.typo.color_primary),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 16))
    
    def add_analysis_result(self, result: str):
        """添加分析结果"""
        self._process_content(result)
    
    def build(self) -> str:
        """
        生成 PDF 文件
        
        Returns:
            生成的 PDF 文件路径
        """
        try:
            self.doc.build(self.story)
            return self.output_path
        except Exception as e:
            print(f"PDF 生成失败: {e}")
            raise


def generate_bazi_report(
    output_path: str,
    title: str,
    bazi_info: Dict[str, str],
    analysis_result: str,
    subtitle: Optional[str] = None
) -> str:
    """
    生成八字报告 PDF
    
    Args:
        output_path: PDF 输出路径
        title: 报告标题
        bazi_info: 四柱信息字典 {'year': '甲子', 'month': '乙丑', ...}
        analysis_result: AI 分析结果文本（支持 Markdown 格式）
        subtitle: 副标题（可选）
    
    Returns:
        生成的 PDF 文件路径
    """
    generator = BaziPDFGenerator(output_path)
    
    # 添加标题
    generator.add_title(title, subtitle)
    
    # 添加四柱信息
    if bazi_info:
        generator.add_bazi_info(bazi_info)
    
    # 添加分析结果
    if analysis_result:
        generator.add_analysis_result(analysis_result)
    
    # 生成 PDF
    return generator.build()


# 测试代码
if __name__ == '__main__':
    # 测试数据
    test_bazi = {
        'year': '甲子',
        'month': '丙寅',
        'day': '戊辰',
        'time': '庚午'
    }
    
    test_analysis = """
### 一、命局概述

**日主戊土**生于寅月，木旺土虚，日主偏弱。

命局特点：
- 年柱甲子：七杀坐财
- 月柱丙寅：印星生身
- 日柱戊辰：日坐比肩
- 时柱庚午：食神生财

### 二、性格分析

#### 1. 主要性格特征

**优点：**
- 为人诚实厚重
- 做事有始有终
- 重视信义承诺

**缺点：**
- 有时过于固执
- 不善言辞表达

### 三、事业财运

适合从事与土相关的行业，如房地产、建筑、农业等。
"""
    
    output = "test_bazi_report.pdf"
    result = generate_bazi_report(
        output_path=output,
        title="八字天赋分析报告",
        bazi_info=test_bazi,
        analysis_result=test_analysis,
        subtitle="测试用户 - 2024年"
    )
    
    print(f"PDF 生成成功: {result}")
