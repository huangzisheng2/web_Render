"""
PDF 报告服务
生成 PDF 报告并提供下载链接
"""

import os
import io
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class PDFService:
    """PDF 报告服务"""
    
    def __init__(self):
        # 内存中临时存储报告（生产环境应使用 Redis 或数据库）
        self._reports_cache = {}
        self._cache_ttl = 3600  # 1小时过期
    
    def generate_and_store(self, report_id: str, analysis_data: Dict[str, Any]) -> str:
        """
        生成 PDF 并存储
        
        Returns:
            下载链接
        """
        try:
            # 尝试使用 reportlab 生成 PDF
            pdf_bytes = self._generate_pdf_reportlab(analysis_data)
        except Exception as e:
            print(f"reportlab 生成失败，使用备用方案: {e}")
            # 备用：生成 HTML，前端用 html2pdf 转换
            pdf_bytes = None
        
        # 存储报告数据（包含 HTML 内容供前端使用）
        self._reports_cache[report_id] = {
            "data": analysis_data,
            "pdf_bytes": pdf_bytes,
            "html_content": self._generate_html_report(analysis_data),
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=1)
        }
        
        # 返回下载链接
        return f"/api/download/{report_id}"
    
    def _generate_pdf_reportlab(self, analysis_data: Dict) -> bytes:
        """使用 reportlab 生成 PDF"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.units import cm
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=2*cm, leftMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
        
        styles = getSampleStyleSheet()
        story = []
        
        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # 居中
        )
        story.append(Paragraph("八字天赋与性格分析报告", title_style))
        story.append(Spacer(1, 20))
        
        # 用户信息
        user_info = analysis_data.get("user_info", {})
        birth_time = user_info.get("birth_time", {})
        
        story.append(Paragraph(f"<b>姓名：</b>{user_info.get('name', '匿名')}", styles['Normal']))
        story.append(Paragraph(f"<b>性别：</b>{user_info.get('gender', '未知')}", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # 四柱信息
        bazi = analysis_data.get("bazi", {})
        story.append(Paragraph("<b>【四柱排盘】</b>", styles['Heading2']))
        story.append(Paragraph(f"年柱：{bazi.get('year_pillar', '')}", styles['Normal']))
        story.append(Paragraph(f"月柱：{bazi.get('month_pillar', '')}", styles['Normal']))
        story.append(Paragraph(f"日柱：{bazi.get('day_pillar', '')}", styles['Normal']))
        story.append(Paragraph(f"时柱：{bazi.get('time_pillar', '')}", styles['Normal']))
        story.append(Spacer(1, 15))
        
        # 分析结果
        analysis = analysis_data.get("analysis", {})
        story.append(Paragraph("<b>【命理分析】</b>", styles['Heading2']))
        story.append(Paragraph(f"身强身弱：{analysis.get('strength', '未知')}", styles['Normal']))
        story.append(Paragraph(f"主要格局：{analysis.get('main_pattern', '未知')}", styles['Normal']))
        story.append(Spacer(1, 15))
        
        # AI 报告
        ai_report = analysis_data.get("ai_report", "")
        if ai_report:
            story.append(Paragraph("<b>【AI 分析报告】</b>", styles['Heading2']))
            # 分段处理
            for line in ai_report.split('\n'):
                if line.strip():
                    story.append(Paragraph(line, styles['Normal']))
                    story.append(Spacer(1, 5))
        
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _generate_html_report(self, analysis_data: Dict) -> str:
        """生成 HTML 报告（供前端 html2pdf 使用）"""
        
        user_info = analysis_data.get("user_info", {})
        bazi = analysis_data.get("bazi", {})
        analysis = analysis_data.get("analysis", {})
        ai_report = analysis_data.get("ai_report", "").replace('\n', '<br>')
        
        # 五行能量条
        wuxing_html = ""
        for wx, value in sorted(analysis.get("wuxing_energy", {}).items(), key=lambda x: x[1], reverse=True):
            width = min(value * 2, 100)  # 限制最大宽度
            wuxing_html += f'''
                <div style="margin: 5px 0;">
                    <span style="display:inline-block;width:40px;">{wx}</span>
                    <div style="display:inline-block;width:200px;height:20px;background:#eee;vertical-align:middle;">
                        <div style="width:{width}%;height:100%;background:#4CAF50;"></div>
                    </div>
                    <span style="margin-left:10px;">{value:.1f}</span>
                </div>
            '''
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>八字天赋与性格分析报告</title>
            <style>
                body {{ font-family: "Microsoft YaHei", sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }}
                h1 {{ text-align: center; color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; }}
                h2 {{ color: #4CAF50; margin-top: 30px; }}
                .info-box {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .bazi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }}
                .bazi-item {{ text-align: center; padding: 15px; background: #e8f5e9; border-radius: 8px; }}
                .pillar {{ font-size: 24px; font-weight: bold; color: #2e7d32; }}
                .label {{ font-size: 12px; color: #666; margin-top: 5px; }}
                .report-content {{ line-height: 1.8; text-align: justify; }}
                .footer {{ text-align: center; margin-top: 40px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>八字天赋与性格分析报告</h1>
            
            <div class="info-box">
                <p><strong>姓名：</strong>{user_info.get('name', '匿名')}</p>
                <p><strong>性别：</strong>{user_info.get('gender', '未知')}</p>
                <p><strong>出生时间：</strong>
                    {user_info.get('birth_time', {}).get('original', {}).get('year', '')}年
                    {user_info.get('birth_time', {}).get('original', {}).get('month', '')}月
                    {user_info.get('birth_time', {}).get('original', {}).get('day', '')}日
                    {f"{user_info.get('birth_time', {}).get('original', {}).get('hour', '')}时" if user_info.get('birth_time', {}).get('original', {}).get('hour') else ""}
                </p>
                <p><strong>出生地：</strong>{user_info.get('birth_time', {}).get('location', {}).get('province', '')} {user_info.get('birth_time', {}).get('location', {}).get('city', '')}</p>
            </div>
            
            <h2>【四柱排盘】</h2>
            <div class="bazi-grid">
                <div class="bazi-item">
                    <div class="pillar">{bazi.get('year_pillar', '')}</div>
                    <div class="label">年柱</div>
                </div>
                <div class="bazi-item">
                    <div class="pillar">{bazi.get('month_pillar', '')}</div>
                    <div class="label">月柱</div>
                </div>
                <div class="bazi-item">
                    <div class="pillar">{bazi.get('day_pillar', '')}</div>
                    <div class="label">日柱（日主）</div>
                </div>
                <div class="bazi-item">
                    <div class="pillar">{bazi.get('time_pillar', '')}</div>
                    <div class="label">时柱</div>
                </div>
            </div>
            
            <h2>【命理分析】</h2>
            <p><strong>身强身弱：</strong>{analysis.get('strength', '未知')}</p>
            <p><strong>主要格局：</strong>{analysis.get('main_pattern', '未知')}</p>
            <p><strong>日主：</strong>{bazi.get('day_master', '')}</p>
            
            <h3>五行能量</h3>
            {wuxing_html}
            
            <h2>【AI 分析报告】</h2>
            <div class="report-content">
                {ai_report}
            </div>
            
            <div class="footer">
                <p>本报告由 AI 生成，仅供参考</p>
                <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def get_download_url(self, report_id: str) -> str:
        """
        获取报告下载链接
        
        由于 Render 免费版无持久存储，我们返回 HTML 内容供前端生成 PDF
        """
        report = self._reports_cache.get(report_id)
        
        if not report:
            raise ValueError("报告不存在或已过期")
        
        # 检查是否过期
        if datetime.now() > report.get("expires_at", datetime.now()):
            del self._reports_cache[report_id]
            raise ValueError("报告已过期")
        
        # 如果有 PDF 字节，返回 base64 编码
        if report.get("pdf_bytes"):
            import base64
            pdf_base64 = base64.b64encode(report["pdf_bytes"]).decode('utf-8')
            return f"data:application/pdf;base64,{pdf_base64}"
        
        # 否则返回 HTML 内容标记
        return f"html://{report_id}"
    
    def get_html_content(self, report_id: str) -> str:
        """获取报告 HTML 内容（供前端 html2pdf 使用）"""
        report = self._reports_cache.get(report_id)
        
        if not report:
            return "<html><body><h1>报告不存在或已过期</h1></body></html>"
        
        return report.get("html_content", "")
